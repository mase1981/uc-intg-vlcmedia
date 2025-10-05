"""
VLC media player entity implementation.

:copyright: (c) 2025 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

import ucapi
from ucapi import MediaPlayer

from uc_intg_vlcmedia.client import VLCClient

_LOG = logging.getLogger(__name__)


class VLCMediaPlayer(MediaPlayer):
    """VLC media player entity."""
    
    def __init__(self, entity_id: str, device_name: str, client: VLCClient):
        """Initialize VLC media player."""
        self._device_name = device_name
        self._client = client
        
        # State management
        self._attr_state = ucapi.media_player.States.OFF
        self._attr_volume = 0
        self._attr_muted = False
        self._attr_media_position = 0
        self._attr_media_duration = 0
        self._attr_media_title = ""
        self._attr_media_artist = ""
        self._attr_media_album = ""
        self._attr_media_image_url = ""
        self._attr_repeat = ucapi.media_player.RepeatMode.OFF
        self._attr_shuffle = False
        
        self._update_task: Optional[asyncio.Task] = None
        self._connected = True
        self._monitoring = False
        self._integration_api = None
        
        features = [
            # Basic playback control
            ucapi.media_player.Features.PLAY_PAUSE,
            ucapi.media_player.Features.STOP,
            
            # Track navigation
            ucapi.media_player.Features.NEXT,
            ucapi.media_player.Features.PREVIOUS,
            
            # Volume control
            ucapi.media_player.Features.VOLUME,
            ucapi.media_player.Features.VOLUME_UP_DOWN,
            ucapi.media_player.Features.MUTE_TOGGLE,
            ucapi.media_player.Features.UNMUTE,
            ucapi.media_player.Features.MUTE,
            
            # Seeking functionality
            ucapi.media_player.Features.SEEK,
            ucapi.media_player.Features.FAST_FORWARD,
            ucapi.media_player.Features.REWIND,
            
            # Media information display
            ucapi.media_player.Features.MEDIA_TITLE,
            ucapi.media_player.Features.MEDIA_ARTIST,
            ucapi.media_player.Features.MEDIA_ALBUM,
            ucapi.media_player.Features.MEDIA_IMAGE_URL,
            ucapi.media_player.Features.MEDIA_POSITION,
            ucapi.media_player.Features.MEDIA_DURATION,
            
            # Additional features
            ucapi.media_player.Features.REPEAT,
            ucapi.media_player.Features.SHUFFLE,
        ]
        
        # Initial attributes
        attributes = {
            ucapi.media_player.Attributes.STATE: self._attr_state,
            ucapi.media_player.Attributes.VOLUME: self._attr_volume,
            ucapi.media_player.Attributes.MUTED: self._attr_muted,
            ucapi.media_player.Attributes.MEDIA_POSITION: self._attr_media_position,
            ucapi.media_player.Attributes.MEDIA_DURATION: self._attr_media_duration,
            ucapi.media_player.Attributes.MEDIA_TITLE: self._attr_media_title,
            ucapi.media_player.Attributes.MEDIA_ARTIST: self._attr_media_artist,
            ucapi.media_player.Attributes.MEDIA_ALBUM: self._attr_media_album,
            ucapi.media_player.Attributes.MEDIA_IMAGE_URL: self._attr_media_image_url,
            ucapi.media_player.Attributes.REPEAT: self._attr_repeat,
            ucapi.media_player.Attributes.SHUFFLE: self._attr_shuffle
        }
        
        super().__init__(
            entity_id,
            device_name,
            features,
            attributes,
            device_class=ucapi.media_player.DeviceClasses.STREAMING_BOX,
            cmd_handler=self.command_handler
        )
    
    async def command_handler(self, entity, cmd_id: str, params: Dict[str, Any] = None) -> ucapi.StatusCodes:
        """Handle media player commands."""
        _LOG.info("=== COMMAND RECEIVED === cmd_id='%s' for device '%s' params=%s", cmd_id, self._device_name, params)
        
        if not self._connected:
            _LOG.error("Cannot execute command - client not connected")
            return ucapi.StatusCodes.SERVICE_UNAVAILABLE
        
        try:
            success = False
            
            # Basic playback commands
            if cmd_id == ucapi.media_player.Commands.PLAY_PAUSE:
                _LOG.info(">>> PLAY_PAUSE command detected")
                success = await self._client.play_pause_toggle()
                    
            elif cmd_id == ucapi.media_player.Commands.STOP:
                _LOG.info(">>> STOP command detected")
                success = await self._client.stop()
            
            # Track navigation commands
            elif cmd_id == ucapi.media_player.Commands.NEXT:
                _LOG.info(">>> NEXT TRACK command detected (NOT fast forward)")
                success = await self._client.next_track()
                
            elif cmd_id == ucapi.media_player.Commands.PREVIOUS:
                _LOG.info(">>> PREVIOUS TRACK command detected (NOT rewind)")
                success = await self._client.previous_track()
            
            # Volume commands
            elif cmd_id == ucapi.media_player.Commands.VOLUME:
                volume = params.get("volume", 50) if params else 50
                success = await self._client.set_volume(volume)
                _LOG.info("Sent VOLUME command: %d", volume)
                
            elif cmd_id == ucapi.media_player.Commands.VOLUME_UP:
                success = await self._client.volume_up()
                _LOG.info("Sent VOLUME_UP command")
                
            elif cmd_id == ucapi.media_player.Commands.VOLUME_DOWN:
                success = await self._client.volume_down()
                _LOG.info("Sent VOLUME_DOWN command")
            
            # Mute commands
            elif cmd_id == ucapi.media_player.Commands.MUTE_TOGGLE:
                success = await self._client.mute_toggle()
                _LOG.info("Sent MUTE_TOGGLE command")
                
            elif cmd_id == ucapi.media_player.Commands.MUTE:
                success = await self._client.mute()
                _LOG.info("Sent MUTE command")
                
            elif cmd_id == ucapi.media_player.Commands.UNMUTE:
                success = await self._client.unmute()
                _LOG.info("Sent UNMUTE command")
            
            # Seeking commands - FF and REW working correctly
            elif cmd_id == ucapi.media_player.Commands.SEEK:
                position = params.get("media_position", 0) if params else 0
                success = await self._client.seek(int(position))
                _LOG.info("Sent SEEK command: %d seconds", position)
                
            elif cmd_id == ucapi.media_player.Commands.FAST_FORWARD:
                success = await self._client.seek_relative(30)
                _LOG.info("Sent FAST_FORWARD command: +30s")
                
            elif cmd_id == ucapi.media_player.Commands.REWIND:
                success = await self._client.seek_relative(-30)
                _LOG.info("Sent REWIND command: -30s")
            
            # Repeat and shuffle commands
            elif cmd_id == ucapi.media_player.Commands.REPEAT:
                success = await self._client.repeat_toggle()
                _LOG.info("Sent REPEAT command")
                
            elif cmd_id == ucapi.media_player.Commands.SHUFFLE:
                success = await self._client.shuffle_toggle()
                _LOG.info("Sent SHUFFLE command")
                
            else:
                _LOG.warning("Unsupported command: %s", cmd_id)
                return ucapi.StatusCodes.NOT_IMPLEMENTED
            
            # Force immediate state update after command
            if success:
                await asyncio.sleep(0.5)
                await self.update_attributes()
            
            return ucapi.StatusCodes.OK if success else ucapi.StatusCodes.SERVER_ERROR
            
        except Exception as e:
            _LOG.error("Command execution failed: %s", e)
            return ucapi.StatusCodes.SERVER_ERROR
    
    def connect(self) -> bool:
        """Connect to VLC - using shared client."""
        self._connected = True
        _LOG.info("Media player connected for device %s", self._device_name)
        return True
    
    async def update_status(self) -> None:
        """Update status from VLC HTTP API."""
        if not self._connected:
            _LOG.debug("Not connected, skipping status update for %s", self.id)
            return
            
        try:
            status = await self._client.get_status()
            
            if not status:
                _LOG.warning("Failed to get status for %s", self.id)
                self._attr_state = ucapi.media_player.States.UNAVAILABLE
                return
            
            # Parse state
            state = status.get("state", "stopped")
            if state == "playing":
                self._attr_state = ucapi.media_player.States.PLAYING
            elif state == "paused":
                self._attr_state = ucapi.media_player.States.PAUSED
            elif state == "stopped":
                self._attr_state = ucapi.media_player.States.OFF
            else:
                self._attr_state = ucapi.media_player.States.ON
            
            # Parse position and duration
            self._attr_media_position = status.get("time", 0)
            self._attr_media_duration = status.get("length", 0)
            
            # Parse volume (VLC: 0-512, convert to 0-100)
            vlc_volume = status.get("volume", 256)
            self._attr_volume = int((vlc_volume / 512) * 100)
            self._attr_muted = (vlc_volume == 0)
            
            # Parse metadata from information.category.meta
            info = status.get("information", {})
            category = info.get("category", {})
            meta = category.get("meta", {})
            
            if meta:
                self._attr_media_title = meta.get("title", meta.get("filename", ""))
                self._attr_media_artist = meta.get("artist", "")
                self._attr_media_album = meta.get("album", "")
                
                # Set album art URL if available
                if self._attr_media_title and self._attr_state != ucapi.media_player.States.OFF:
                    self._attr_media_image_url = self._client.get_album_art_url()
                else:
                    self._attr_media_image_url = ""
            else:
                # No metadata - clear everything
                self._attr_media_title = ""
                self._attr_media_artist = ""
                self._attr_media_album = ""
                self._attr_media_image_url = ""
            
            # Parse repeat mode
            if status.get("loop", False):
                self._attr_repeat = ucapi.media_player.RepeatMode.ALL
            elif status.get("repeat", False):
                self._attr_repeat = ucapi.media_player.RepeatMode.ONE
            else:
                self._attr_repeat = ucapi.media_player.RepeatMode.OFF
            
            # Parse shuffle
            self._attr_shuffle = status.get("random", False)
            
            _LOG.debug("Updated status for %s: state=%s, title=%s, artist=%s", 
                      self.id, self._attr_state, self._attr_media_title, self._attr_media_artist)
            
        except Exception as e:
            _LOG.error("Status update failed for %s: %s", self.id, e)
            self._attr_state = ucapi.media_player.States.UNAVAILABLE
    
    async def update_attributes(self):
        """Update attributes and push to Remote."""
        # First update status from VLC
        await self.update_status()
        
        # Build attributes dictionary
        attributes = {
            ucapi.media_player.Attributes.STATE: self._attr_state,
            ucapi.media_player.Attributes.VOLUME: self._attr_volume,
            ucapi.media_player.Attributes.MUTED: self._attr_muted,
            ucapi.media_player.Attributes.MEDIA_POSITION: self._attr_media_position,
            ucapi.media_player.Attributes.MEDIA_DURATION: self._attr_media_duration,
            ucapi.media_player.Attributes.MEDIA_TITLE: self._attr_media_title,
            ucapi.media_player.Attributes.MEDIA_ARTIST: self._attr_media_artist,
            ucapi.media_player.Attributes.MEDIA_ALBUM: self._attr_media_album,
            ucapi.media_player.Attributes.MEDIA_IMAGE_URL: self._attr_media_image_url,
            ucapi.media_player.Attributes.REPEAT: self._attr_repeat,
            ucapi.media_player.Attributes.SHUFFLE: self._attr_shuffle
        }
        
        # Update the entity's attributes
        self.attributes.update(attributes)
        
        # Force integration API update if available
        if self._integration_api and hasattr(self._integration_api, 'configured_entities'):
            try:
                self._integration_api.configured_entities.update_attributes(self.id, attributes)
                _LOG.debug("Forced integration API update for %s - State: %s", self.id, self._attr_state)
            except Exception as e:
                _LOG.debug("Could not force integration API update: %s", e)
        
        _LOG.info("Attributes updated for %s - State: %s, Title: %s", 
                  self.id, self._attr_state, self._attr_media_title)
    
    async def push_update(self):
        """Explicitly push current state to Remote (for subscription)."""
        await self.update_attributes()
        _LOG.info("Pushed initial state for %s", self.id)
    
    async def start_monitoring(self):
        """Start periodic monitoring - called during subscription."""
        if not self._monitoring:
            self._monitoring = True
            self._update_task = asyncio.create_task(self._periodic_update())
            _LOG.info("Started monitoring for media player %s", self.id)
    
    async def _periodic_update(self) -> None:
        """Periodically update VLC status."""
        while self._connected and self._monitoring:
            try:
                await asyncio.sleep(3)  # Update every 3 seconds
                if self._monitoring:
                    await self.update_attributes()
            except asyncio.CancelledError:
                break
            except Exception as e:
                _LOG.error("Periodic update error: %s", e)
                if self._monitoring:
                    await asyncio.sleep(10)
    
    def stop_monitoring(self):
        """Stop periodic monitoring."""
        if self._monitoring:
            self._monitoring = False
            if self._update_task and not self._update_task.done():
                self._update_task.cancel()
                self._update_task = None
            _LOG.info("Stopped monitoring for media player %s", self.id)
    
    async def disconnect(self) -> None:
        """Disconnect from VLC."""
        self.stop_monitoring()
        self._connected = False
    
    @property
    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected