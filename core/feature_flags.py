"""
Feature Flags System for Akira Forge
Enables/disables features dynamically without code changes.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class FeatureFlag:
    """Represents a feature flag."""
    
    def __init__(self, name: str, enabled: bool = False, description: str = "",
                 rollout_percentage: int = 0, target_users: list = None):
        self.name = name
        self.enabled = enabled
        self.description = description
        self.rollout_percentage = rollout_percentage  # 0-100
        self.target_users = target_users or []
        self.created_at = datetime.now().isoformat()
    
    def is_enabled_for_user(self, user_id: str) -> bool:
        """Check if flag is enabled for specific user."""
        if not self.enabled:
            return False
        
        # Check target users list
        if self.target_users and user_id in self.target_users:
            return True
        
        # Check rollout percentage
        if self.rollout_percentage > 0:
            # Simple hash-based rollout
            hash_val = hash(f"{user_id}:{self.name}") % 100
            return hash_val < self.rollout_percentage
        
        return self.enabled
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "description": self.description,
            "rollout_percentage": self.rollout_percentage,
            "target_users": self.target_users,
            "created_at": self.created_at
        }


class FeatureFlagManager:
    """Manages feature flags."""
    
    def __init__(self, config_file: str = "feature_flags.json"):
        self.config_file = Path(config_file)
        self.flags: Dict[str, FeatureFlag] = {}
        self._load_flags()
    
    def create_flag(self, name: str, enabled: bool = False, description: str = "",
                   rollout_percentage: int = 0, target_users: list = None):
        """Create a new feature flag."""
        flag = FeatureFlag(name, enabled, description, rollout_percentage, target_users)
        self.flags[name] = flag
        self._save_flags()
        return flag
    
    def get_flag(self, name: str) -> Optional[FeatureFlag]:
        """Get a feature flag."""
        return self.flags.get(name)
    
    def is_enabled(self, name: str, user_id: str = "anonymous") -> bool:
        """Check if feature is enabled."""
        flag = self.get_flag(name)
        if flag is None:
            return False
        return flag.is_enabled_for_user(user_id)
    
    def enable_flag(self, name: str):
        """Enable a feature flag."""
        if name in self.flags:
            self.flags[name].enabled = True
            self._save_flags()
    
    def disable_flag(self, name: str):
        """Disable a feature flag."""
        if name in self.flags:
            self.flags[name].enabled = False
            self._save_flags()
    
    def set_rollout(self, name: str, percentage: int):
        """Set rollout percentage for a flag."""
        if name in self.flags:
            self.flags[name].rollout_percentage = min(100, max(0, percentage))
            self._save_flags()
    
    def add_target_user(self, name: str, user_id: str):
        """Add user to target list."""
        if name in self.flags:
            if user_id not in self.flags[name].target_users:
                self.flags[name].target_users.append(user_id)
                self._save_flags()
    
    def remove_target_user(self, name: str, user_id: str):
        """Remove user from target list."""
        if name in self.flags:
            if user_id in self.flags[name].target_users:
                self.flags[name].target_users.remove(user_id)
                self._save_flags()
    
    def list_flags(self) -> Dict[str, Dict[str, Any]]:
        """List all flags."""
        return {name: flag.to_dict() for name, flag in self.flags.items()}
    
    def delete_flag(self, name: str):
        """Delete a feature flag."""
        if name in self.flags:
            del self.flags[name]
            self._save_flags()
    
    def _load_flags(self):
        """Load flags from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    for name, flag_data in data.items():
                        self.flags[name] = FeatureFlag(
                            name=flag_data.get("name", name),
                            enabled=flag_data.get("enabled", False),
                            description=flag_data.get("description", ""),
                            rollout_percentage=flag_data.get("rollout_percentage", 0),
                            target_users=flag_data.get("target_users", [])
                        )
            except Exception as e:
                print(f"❌ Failed to load feature flags: {str(e)}")
    
    def _save_flags(self):
        """Save flags to file."""
        try:
            data = {name: flag.to_dict() for name, flag in self.flags.items()}
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save feature flags: {str(e)}")


# Global instance
_feature_manager: Optional[FeatureFlagManager] = None


def get_feature_manager() -> FeatureFlagManager:
    """Get or create global feature flag manager."""
    global _feature_manager
    if _feature_manager is None:
        _feature_manager = FeatureFlagManager()
    return _feature_manager


def is_feature_enabled(name: str, user_id: str = "anonymous") -> bool:
    """Check if feature is enabled (convenience function)."""
    return get_feature_manager().is_enabled(name, user_id)
