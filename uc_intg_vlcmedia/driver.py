#!/usr/bin/env python3
"""
VLC integration driver for Unfolded Circle Remote Two/Three.

:copyright: (c) 2025 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import asyncio
import hashlib
import logging
import os
import sys
from typing import Any, List

import ucapi
from ucapi import (
    DeviceStates, Events, IntegrationSetupError, SetupComplete, SetupError
)

from uc_intg_vlcmedia.config import Config
from uc_intg_vlcmedia.client import VLCClient
from uc_intg_vlcmedia.media_player import VLCMediaPlayer

# Set up logging
logging.basicConfig(level=logging.DEBUG)
_LOG = logging.getLogger(__name__)

# Global variables
api: ucapi.IntegrationAPI = None
config: Config = None

# Store clients and media players by device_id
clients = {}
media_players = {}
entities_ready = False
initialization_lock = asyncio.Lock()


async def setup_handler(msg: ucapi.SetupDriver) -> ucapi.SetupAction:
    """Handle setup requests for adding VLC devices."""
    global config, entities_ready
    
    if isinstance(msg, ucapi.DriverSetupRequest):
        _LOG.info("Setting up VLC device")
        
        # Extract setup data
        setup_data = msg.setup_data
        host = setup_data.get("host", "").strip()
        port = int(setup_data.get("port", 8080))
        password = setup_data.get("password", "").strip()
        device_name = setup_data.get("device_name", "").strip()
        
        if not all([host, password, device_name]):
            _LOG.error("Missing required setup parameters")
            return SetupError(IntegrationSetupError.OTHER)
        
        _LOG.info("Testing connection to VLC at %s:%d", host, port)
        
        try:
            # Test connection
            test_client = VLCClient(host, port, password)
            if not await test_client.connect():
                _LOG.error("Failed to connect to VLC")
                await test_client.disconnect()
                return SetupError(IntegrationSetupError.CONNECTION_REFUSED)
            
            # Create unique device ID
            device_id = hashlib.md5(f"{host}:{port}".encode()).hexdigest()[:8]
            
            # Save device configuration
            config.add_device(device_id, host, port, password, device_name)
            
            await test_client.disconnect()
            
            # Re-initialize entities with new device
            entities_ready = False
            await _initialize_entities()
            
            _LOG.info("VLC device setup completed successfully: %s", device_name)
            return SetupComplete()
            
        except Exception as e:
            _LOG.error("Setup failed: %s", e)
            return SetupError(IntegrationSetupError.OTHER)
    
    return SetupError(IntegrationSetupError.OTHER)


async def _initialize_entities():
    """Initialize entities after successful setup or connection - WITH REBOOT SURVIVAL."""
    global api, config, clients, media_players, entities_ready
    
    async with initialization_lock:
        if entities_ready:
            _LOG.debug("Entities already initialized")
            return
        
        devices = config.get_all_devices()
        if not devices:
            _LOG.info("No devices configured, skipping entity initialization")
            await api.set_device_state(DeviceStates.DISCONNECTED)
            return
        
        _LOG.info("Initializing VLC entities for %d device(s)...", len(devices))
        await api.set_device_state(DeviceStates.CONNECTING)
        
        try:
            # Clear existing entities
            clients.clear()
            media_players.clear()
            api.available_entities.clear()
            
            # Create client and entity for each device
            for device_id, device_config in devices.items():
                try:
                    host = device_config["host"]
                    port = device_config["port"]
                    password = device_config["password"]
                    device_name = device_config["device_name"]
                    
                    # Create client
                    client = VLCClient(host, port, password)
                    
                    if not await client.connect():
                        _LOG.error("Failed to connect to VLC device: %s", device_name)
                        continue
                    
                    clients[device_id] = client
                    
                    # Create media player entity
                    entity_id = f"vlc_{device_id}_media_player"
                    media_player = VLCMediaPlayer(entity_id, device_name, client)
                    media_player._integration_api = api
                    
                    # Connect and add
                    if media_player.connect():
                        media_players[device_id] = media_player
                        api.available_entities.add(media_player)
                        _LOG.info("Created media player entity: %s for %s", entity_id, device_name)
                    else:
                        _LOG.error("Failed to connect media player for device: %s", device_name)
                        
                except Exception as e:
                    _LOG.error("Failed to initialize device %s: %s", device_id, e, exc_info=True)
                    continue
            
            if media_players:
                entities_ready = True
                await api.set_device_state(DeviceStates.CONNECTED)
                _LOG.info("VLC integration setup completed - %d media player(s) created", len(media_players))
            else:
                await api.set_device_state(DeviceStates.ERROR)
                _LOG.error("No media players could be created")
                
        except Exception as e:
            _LOG.error("Entity initialization failed: %s", e, exc_info=True)
            await api.set_device_state(DeviceStates.ERROR)


async def _monitor_connection():
    """Monitor connection status and reconnect if needed."""
    global clients, api, entities_ready
    
    while True:
        try:
            if clients and entities_ready:
                all_connected = True
                
                for device_id, client in clients.items():
                    # Test connection with actual API call
                    status = await client.get_status()
                    if not status:
                        all_connected = False
                        _LOG.warning("Connection lost for device %s - attempting reconnection", device_id)
                        
                        # Try to reconnect
                        if await client.connect():
                            _LOG.info("Reconnection successful for device %s", device_id)
                        else:
                            _LOG.error("Reconnection failed for device %s", device_id)
                
                # Update overall state
                if all_connected:
                    if api.device_state != DeviceStates.CONNECTED:
                        await api.set_device_state(DeviceStates.CONNECTED)
                else:
                    await api.set_device_state(DeviceStates.CONNECTING)
            
            await asyncio.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            _LOG.error("Connection monitoring error: %s", e)
            await asyncio.sleep(60)


async def on_subscribe_entities(entity_ids: List[str]):
    """Handle entity subscription events - CRITICAL TIMING with race condition protection."""
    global media_players, entities_ready, config
    
    _LOG.info("Entities subscribed: %s", entity_ids)
    
    # Race condition protection
    if not entities_ready:
        _LOG.error("RACE CONDITION: Subscription before entities ready! Attempting recovery...")
        if config and config.is_configured():
            await _initialize_entities()
        else:
            _LOG.error("Cannot recover - no configuration available")
            return
    
    for entity_id in entity_ids:
        # Find and start monitoring for subscribed entity
        for device_id, media_player in media_players.items():
            if media_player.id == entity_id:
                _LOG.info("Entity subscribed, pushing initial state: %s", entity_id)
                # Push initial state
                await media_player.push_update()
                # Start monitoring
                await media_player.start_monitoring()
                break
    
    # Background monitoring message
    if not hasattr(on_subscribe_entities, '_monitoring_started'):
        on_subscribe_entities._monitoring_started = True
        _LOG.info("Background monitoring started")


async def on_unsubscribe_entities(entity_ids: List[str]):
    """Handle entity unsubscription."""
    _LOG.info("Entities unsubscribed: %s", entity_ids)
    
    # Stop monitoring for unsubscribed entities
    for entity_id in entity_ids:
        for device_id, media_player in media_players.items():
            if media_player.id == entity_id:
                media_player.stop_monitoring()
                break


async def on_connect():
    """Handle Remote Two connection - ENHANCED FOR REBOOT SURVIVAL."""
    global config
    
    _LOG.info("Remote Two connected")
    
    # Reload configuration from disk for reboot survival
    if not config:
        config = Config()
    config.reload_from_disk()
    
    if config.is_configured():
        _LOG.info("Configuration found, initializing entities")
        
        # Check if entities already exist, recreate if missing
        if not entities_ready or not api.available_entities:
            await _initialize_entities()
        else:
            # Entities already ready - just set connected
            await api.set_device_state(DeviceStates.CONNECTED)
        
        # Start connection monitoring task
        asyncio.create_task(_monitor_connection())
    else:
        _LOG.info("No configuration found, waiting for setup")
        await api.set_device_state(DeviceStates.DISCONNECTED)


async def on_disconnect():
    """Handle Remote Two disconnection."""
    _LOG.info("Remote Two disconnected")


async def main():
    """Main entry point - REBOOT SURVIVAL PATTERN."""
    global api, config
    
    _LOG.info("Starting VLC Integration Driver")
    
    try:
        # Load configuration
        config = Config()
        config.load()
        
        # Set up UC API
        driver_path = os.path.join(os.path.dirname(__file__), "..", "driver.json")
        loop = asyncio.get_running_loop()
        api = ucapi.IntegrationAPI(loop)
        
        # PRE-INITIALIZE for reboot survival
        if config.is_configured():
            _LOG.info("Found existing configuration, pre-initializing entities for reboot survival")
            loop.create_task(_initialize_entities())
        
        # Initialize UC API
        await api.init(driver_path, setup_handler)
        
        # Register event listeners
        api.add_listener(Events.CONNECT, on_connect)
        api.add_listener(Events.DISCONNECT, on_disconnect)
        api.add_listener(Events.SUBSCRIBE_ENTITIES, on_subscribe_entities)
        api.add_listener(Events.UNSUBSCRIBE_ENTITIES, on_unsubscribe_entities)
        
        if not config.is_configured():
            _LOG.info("No devices configured, waiting for setup...")
            await api.set_device_state(DeviceStates.DISCONNECTED)
        
        # Keep running
        await asyncio.Future()
        
    except Exception as e:
        _LOG.error("Fatal error: %s", e, exc_info=True)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _LOG.info("Integration stopped by user")
    except Exception as e:
        _LOG.error("Integration crashed: %s", e, exc_info=True)
        sys.exit(1)