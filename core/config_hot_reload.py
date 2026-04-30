"""
Configuration Hot-Reload System for Akira Forge
Enables configuration changes without application restart.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime


class ConfigWatcher(FileSystemEventHandler):
    """Watches configuration files for changes."""
    
    def __init__(self, callback: Callable):
        self.callback = callback
    
    def on_modified(self, event):
        """Called when file is modified."""
        if not event.is_directory and event.src_path.endswith(('.toml', '.json', '.yaml', '.yml')):
            self.callback(event.src_path)


class ConfigurationManager:
    """
    Dynamic configuration manager with hot-reload.
    
    Features:
    - Load TOML, JSON, YAML configurations
    - Hot-reload on file changes
    - Configuration validation
    - Configuration versioning
    - Rollback support
    - Environment variable substitution
    """
    
    def __init__(self, config_path: str = "config.toml"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.config_history: List[Dict[str, Any]] = []
        self.callbacks: List[Callable] = []
        self.observer: Optional[Observer] = None
        self.watch_enabled = False
        
        # Load initial configuration
        self.load_config()
    
    def load_config(self):
        """Load configuration from file."""
        if not self.config_path.exists():
            print(f"⚠️  Config file not found: {self.config_path}")
            return
        
        try:
            if self.config_path.suffix == '.json':
                with open(self.config_path, 'r') as f:
                    new_config = json.load(f)
            elif self.config_path.suffix in ['.yaml', '.yml']:
                with open(self.config_path, 'r') as f:
                    new_config = yaml.safe_load(f) or {}
            elif self.config_path.suffix == '.toml':
                import tomli
                with open(self.config_path, 'rb') as f:
                    new_config = tomli.load(f)
            else:
                print(f"❌ Unsupported config format: {self.config_path.suffix}")
                return
            
            # Save to history for rollback
            if self.config:
                self.config_history.append(self.config.copy())
            
            # Apply environment variable substitution
            self.config = self._substitute_env_vars(new_config)
            print(f"✓ Loaded configuration from {self.config_path}")
            
            # Trigger callbacks
            self._notify_callbacks()
            
        except Exception as e:
            print(f"❌ Failed to load config: {str(e)}")
    
    def reload_config(self):
        """Reload configuration from file."""
        print("🔄 Reloading configuration...")
        self.load_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self._notify_callbacks()
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values."""
        for key, value in updates.items():
            self.set(key, value)
    
    def register_callback(self, callback: Callable):
        """Register callback for config changes."""
        self.callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable):
        """Unregister callback."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def start_watching(self):
        """Start watching config file for changes."""
        if self.watch_enabled:
            return
        
        self.observer = Observer()
        watcher = ConfigWatcher(lambda path: self.reload_config())
        self.observer.schedule(watcher, str(self.config_path.parent))
        self.observer.start()
        self.watch_enabled = True
        print(f"👁️  Watching {self.config_path.parent} for changes")
    
    def stop_watching(self):
        """Stop watching config file."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.watch_enabled = False
            print("⏹️  Stopped watching for config changes")
    
    def rollback(self, steps: int = 1) -> bool:
        """Rollback to previous configuration."""
        if len(self.config_history) < steps:
            print(f"⚠️  Cannot rollback {steps} steps (history too short)")
            return False
        
        self.config = self.config_history.pop(-steps)
        print(f"↩️  Rolled back {steps} step(s)")
        self._notify_callbacks()
        return True
    
    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration."""
        return self.config.copy()
    
    def export(self, output_path: str):
        """Export configuration to file."""
        try:
            output_file = Path(output_path)
            
            if output_file.suffix == '.json':
                with open(output_file, 'w') as f:
                    json.dump(self.config, f, indent=2)
            elif output_file.suffix in ['.yaml', '.yml']:
                with open(output_file, 'w') as f:
                    yaml.dump(self.config, f, default_flow_style=False)
            else:
                print(f"❌ Unsupported export format: {output_file.suffix}")
                return
            
            print(f"✓ Exported configuration to {output_path}")
        except Exception as e:
            print(f"❌ Failed to export config: {str(e)}")
    
    def validate(self, schema: Dict[str, Any]) -> List[str]:
        """Validate configuration against schema."""
        errors = []
        
        def check_keys(config, schema, path=""):
            for key, value_type in schema.items():
                if key not in config:
                    errors.append(f"Missing key: {path}.{key}")
                elif isinstance(value_type, dict):
                    if isinstance(config[key], dict):
                        check_keys(config[key], value_type, f"{path}.{key}")
                    else:
                        errors.append(f"Expected dict at {path}.{key}")
                elif not isinstance(config[key], value_type):
                    errors.append(f"Wrong type at {path}.{key}: expected {value_type.__name__}")
        
        check_keys(self.config, schema)
        return errors
    
    def _substitute_env_vars(self, config: Any) -> Any:
        """Substitute environment variables in config."""
        import os
        import re
        
        if isinstance(config, dict):
            return {k: self._substitute_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Replace ${VAR_NAME} with environment variable
            def replace_env(match):
                var_name = match.group(1)
                return os.getenv(var_name, match.group(0))
            
            return re.sub(r'\$\{([^}]+)\}', replace_env, config)
        else:
            return config
    
    def _notify_callbacks(self):
        """Notify registered callbacks of changes."""
        for callback in self.callbacks:
            try:
                callback(self.config)
            except Exception as e:
                print(f"❌ Config callback error: {str(e)}")


# Global instance
_config_manager: Optional[ConfigurationManager] = None


def get_config_manager(config_path: str = "config.toml") -> ConfigurationManager:
    """Get or create global config manager."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager(config_path)
    return _config_manager


# Convenience functions
def config_get(key: str, default: Any = None) -> Any:
    """Get config value (convenience function)."""
    return get_config_manager().get(key, default)


def config_set(key: str, value: Any):
    """Set config value (convenience function)."""
    return get_config_manager().set(key, value)
