"""
Configuration Management for VLC Integration.

:copyright: (c) 2025 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

_LOG = logging.getLogger(__name__)


class Config:
    """Configuration management for VLC integration."""

    def __init__(self, config_dir: str = None):
        """Initialize configuration manager."""
        if config_dir is None:
            config_dir = os.getenv("UC_CONFIG_HOME", ".")
        
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "config.json")
        self._data: Dict[str, Any] = {}
        self._devices: Dict[str, Dict[str, Any]] = {}
        
        # Ensure config directory exists
        os.makedirs(config_dir, exist_ok=True)

    def load(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
                    self._devices = self._data.get("devices", {})
                _LOG.info("Configuration loaded from %s", self.config_file)
            else:
                _LOG.info("No configuration file found, using defaults")
                self._data = {}
                self._devices = {}
        except Exception as e:
            _LOG.error("Failed to load configuration: %s", e)
            self._data = {}
            self._devices = {}

    def reload_from_disk(self):
        """Reload configuration from disk (for reboot survival)."""
        self.load()

    def save(self):
        """Save configuration to file."""
        try:
            self._data["devices"] = self._devices
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2)
            _LOG.info("Configuration saved to %s", self.config_file)
        except Exception as e:
            _LOG.error("Failed to save configuration: %s", e)

    def add_device(self, device_id: str, host: str, port: int, password: str, device_name: str):
        """Add a VLC device configuration."""
        self._devices[device_id] = {
            "host": host,
            "port": port,
            "password": password,
            "device_name": device_name
        }
        self.save()

    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device configuration by ID."""
        return self._devices.get(device_id)

    def get_all_devices(self) -> Dict[str, Dict[str, Any]]:
        """Get all configured devices."""
        return self._devices.copy()

    def remove_device(self, device_id: str):
        """Remove a device configuration."""
        if device_id in self._devices:
            del self._devices[device_id]
            self.save()

    def is_configured(self) -> bool:
        """Check if at least one device is configured."""
        return len(self._devices) > 0

    def clear(self):
        """Clear all configuration."""
        self._data = {}
        self._devices = {}
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        _LOG.info("Configuration cleared")

    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self._data.copy()