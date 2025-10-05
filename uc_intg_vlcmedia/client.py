"""
VLC HTTP API client for media control and metadata retrieval.

:copyright: (c) 2025 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import base64
import json
import logging
from typing import Any, Dict, Optional
import aiohttp

_LOG = logging.getLogger(__name__)


class VLCClient:
    """VLC HTTP API client."""
    
    def __init__(self, host: str, port: int, password: str):
        """Initialize VLC HTTP client."""
        self.host = host
        self.port = port
        self.password = password
        self.base_url = f"http://{host}:{port}"
        
        # Create auth header
        auth_string = f":{password}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        self.headers = {
            "Authorization": f"Basic {auth_b64}"
        }
        
        self._is_connected = False
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def connect(self) -> bool:
        """Test connection to VLC HTTP interface."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/requests/status.json",
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        # Verify we can parse the response
                        text = await response.text()
                        try:
                            json.loads(text)
                            self._is_connected = True
                            _LOG.info("Successfully connected to VLC at %s:%d", self.host, self.port)
                            return True
                        except json.JSONDecodeError:
                            _LOG.error("VLC returned invalid JSON - check HTTP interface is enabled")
                            return False
                    else:
                        _LOG.error("Connection failed with status %d", response.status)
                        return False
        except Exception as e:
            _LOG.error("Failed to connect to VLC: %s", e)
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from VLC."""
        self._is_connected = False
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    async def get_status(self) -> Optional[Dict[str, Any]]:
        """Get current playback status and metadata."""
        if not self._is_connected:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/requests/status.json",
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        # Force content type to application/json to avoid mimetype error
                        text = await response.text()
                        try:
                            return json.loads(text)
                        except json.JSONDecodeError as e:
                            _LOG.error("Failed to parse VLC response as JSON: %s", e)
                            _LOG.debug("Response text: %s", text[:200])
                            return None
                    else:
                        _LOG.warning("Failed to get status: HTTP %d", response.status)
                        return None
        except Exception as e:
            _LOG.error("Error getting status: %s", e)
            return None
    
    async def get_album_art(self) -> Optional[bytes]:
        """Get current media album artwork as bytes."""
        if not self._is_connected:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/art",
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        _LOG.debug("No album art available: HTTP %d", response.status)
                        return None
        except Exception as e:
            _LOG.debug("Error getting album art: %s", e)
            return None
    
    def get_album_art_url(self) -> str:
        """Get URL for album art endpoint."""
        return f"{self.base_url}/art"
    
    async def send_command(self, command: str, params: Dict[str, Any] = None) -> bool:
        """Send a command to VLC."""
        if not self._is_connected:
            return False
        
        try:
            url = f"{self.base_url}/requests/status.json?command={command}"
            if params:
                for key, value in params.items():
                    url += f"&{key}={value}"
            
            _LOG.debug("Sending VLC command: %s", url)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        _LOG.debug("Command '%s' sent successfully", command)
                        return True
                    else:
                        _LOG.warning("Command '%s' failed: HTTP %d", command, response.status)
                        return False
        except Exception as e:
            _LOG.error("Error sending command '%s': %s", command, e)
            return False
    
    # Playback control methods
    async def play(self) -> bool:
        """Resume playback."""
        return await self.send_command("pl_forceresume")
    
    async def pause(self) -> bool:
        """Pause playback."""
        return await self.send_command("pl_forcepause")
    
    async def play_pause_toggle(self) -> bool:
        """Toggle play/pause."""
        return await self.send_command("pl_pause")
    
    async def stop(self) -> bool:
        """Stop playback - using pl_stop command."""
        _LOG.info("STOP: Sending pl_stop command to VLC")
        result = await self.send_command("pl_stop")
        _LOG.info("STOP: Command result = %s", result)
        return result
    
    async def next_track(self) -> bool:
        """Play next track in playlist."""
        _LOG.info("NEXT: Sending pl_next command to VLC")
        result = await self.send_command("pl_next")
        _LOG.info("NEXT: Command result = %s", result)
        return result
    
    async def previous_track(self) -> bool:
        """Play previous track in playlist."""
        _LOG.info("PREVIOUS: Sending pl_previous command to VLC")
        result = await self.send_command("pl_previous")
        _LOG.info("PREVIOUS: Command result = %s", result)
        return result
    
    async def seek(self, position_seconds: int) -> bool:
        """Seek to position in seconds."""
        return await self.send_command("seek", {"val": position_seconds})
    
    async def seek_relative(self, offset_seconds: int) -> bool:
        """Seek relative to current position."""
        prefix = "+" if offset_seconds > 0 else ""
        return await self.send_command("seek", {"val": f"{prefix}{offset_seconds}"})
    
    # Volume control methods
    async def set_volume(self, volume: int) -> bool:
        """Set volume (0-512, where 256 = 100%)."""
        # VLC uses 0-512 range (256 = 100%)
        # Convert from 0-100 to 0-512
        vlc_volume = int((volume / 100) * 512)
        return await self.send_command("volume", {"val": vlc_volume})
    
    async def volume_up(self) -> bool:
        """Increase volume."""
        return await self.send_command("volume", {"val": "+20"})
    
    async def volume_down(self) -> bool:
        """Decrease volume."""
        return await self.send_command("volume", {"val": "-20"})
    
    async def mute_toggle(self) -> bool:
        """Toggle mute - VLC has no direct mute toggle in HTTP API."""
        # Get current status to check if muted
        status = await self.get_status()
        if status:
            current_volume = status.get("volume", 256)
            if current_volume == 0:
                # Currently muted, unmute to 256 (100%)
                return await self.send_command("volume", {"val": "256"})
            else:
                # Not muted, mute it
                return await self.send_command("volume", {"val": "0"})
        return False
    
    async def mute(self) -> bool:
        """Mute audio - store current volume first."""
        status = await self.get_status()
        if status:
            current_volume = status.get("volume", 256)
            if current_volume > 0:
                # Store volume and mute
                self._stored_volume = current_volume
                return await self.send_command("volume", {"val": "0"})
        return False
    
    async def unmute(self) -> bool:
        """Unmute audio - restore previous volume."""
        # Try to restore stored volume, default to 256 (100%)
        restore_volume = getattr(self, '_stored_volume', 256)
        return await self.send_command("volume", {"val": str(restore_volume)})
    
    # Playlist control
    async def clear_playlist(self) -> bool:
        """Clear the playlist."""
        return await self.send_command("pl_empty")
    
    async def shuffle_toggle(self) -> bool:
        """Toggle shuffle mode."""
        return await self.send_command("pl_random")
    
    async def repeat_toggle(self) -> bool:
        """Toggle repeat mode."""
        return await self.send_command("pl_repeat")
    
    async def loop_toggle(self) -> bool:
        """Toggle loop mode."""
        return await self.send_command("pl_loop")
    
    async def fullscreen_toggle(self) -> bool:
        """Toggle fullscreen."""
        return await self.send_command("fullscreen")
    
    @property
    def is_connected(self) -> bool:
        """Check if connected to VLC."""
        return self._is_connected