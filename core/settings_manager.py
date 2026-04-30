#!/usr/bin/env python3
"""
Settings Manager
================

Manages application settings and preferences.
Handles window positions, sizes, user preferences.
"""

import logging
from pathlib import Path
import json
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SettingsManager:
    """Manages application settings and preferences."""
    
    def __init__(self, app_name: str = "AkiraForge"):
        """
        Initialize settings manager.
        
        Args:
            app_name: Application name for settings file
        """
        self.app_name = app_name
        self.settings_dir = Path.home() / f".{app_name.lower()}"
        self.settings_file = self.settings_dir / "settings.json"
        
        # Ensure settings directory exists
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing settings
        self.settings = self._load_settings()
        logger.info(f"SettingsManager initialized: {self.settings_file}")
    
    def _load_settings(self) -> dict:
        """Load settings from file."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                logger.debug(f"Loaded {len(settings)} settings")
                return settings
        except Exception as e:
            logger.warning(f"Failed to load settings: {e}")
        
        return self._default_settings()
    
    def _default_settings(self) -> dict:
        """Get default settings."""
        return {
            "window_geometry": {
                "login": {"width": 400, "height": 500},
                "home": {"width": 1000, "height": 700, "x": 0, "y": 0},
                "admin": {"width": 1400, "height": 850, "x": 0, "y": 0},
                "builder": {"width": 1200, "height": 800, "x": 0, "y": 0},
                "vault": {"width": 1000, "height": 700, "x": 0, "y": 0},
                "assistant": {"width": 900, "height": 600, "x": 0, "y": 0},
            },
            "user_preferences": {
                "theme": "dark",
                "auto_login": False,
                "remember_username": False,
            },
            "feature_flags": {
                "enable_metrics": True,
                "enable_crash_recovery": True,
                "enable_auto_save": True,
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: Setting key (supports dot notation: section.key)
            default: Default value if key not found
            
        Returns:
            Setting value
        """
        keys = key.split(".")
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set a setting value.
        
        Args:
            key: Setting key (supports dot notation: section.key)
            value: Value to set
            
        Returns:
            True if successful
        """
        try:
            keys = key.split(".")
            settings = self.settings
            
            # Navigate to parent
            for k in keys[:-1]:
                if k not in settings:
                    settings[k] = {}
                settings = settings[k]
            
            # Set value
            settings[keys[-1]] = value
            
            # Save to file
            return self._save_settings()
        
        except Exception as e:
            logger.error(f"Error setting {key}: {e}")
            return False
    
    def _save_settings(self) -> bool:
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            logger.debug("Settings saved")
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False
    
    def save_window_geometry(self, window_type: str, geometry: dict) -> bool:
        """
        Save window geometry.
        
        Args:
            window_type: Type of window
            geometry: Window geometry (width, height, x, y)
            
        Returns:
            True if successful
        """
        return self.set(f"window_geometry.{window_type}", geometry)
    
    def load_window_geometry(self, window_type: str) -> dict:
        """
        Load window geometry.
        
        Args:
            window_type: Type of window
            
        Returns:
            Window geometry dictionary
        """
        default = self.get("window_geometry", {}).get(window_type, {})
        return self.get(f"window_geometry.{window_type}", default)
    
    def save_preference(self, pref_name: str, value: Any) -> bool:
        """
        Save user preference.
        
        Args:
            pref_name: Preference name
            value: Preference value
            
        Returns:
            True if successful
        """
        return self.set(f"user_preferences.{pref_name}", value)
    
    def load_preference(self, pref_name: str, default: Any = None) -> Any:
        """
        Load user preference.
        
        Args:
            pref_name: Preference name
            default: Default value
            
        Returns:
            Preference value
        """
        return self.get(f"user_preferences.{pref_name}", default)
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults."""
        try:
            self.settings = self._default_settings()
            return self._save_settings()
        except Exception as e:
            logger.error(f"Error resetting settings: {e}")
            return False
