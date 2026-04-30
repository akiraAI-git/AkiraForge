"""
Plugin System for Akira Forge
Allows third-party extensions and plugins to extend application functionality.
"""

import os
import sys
import json
import importlib.util
from pathlib import Path
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass
from enum import Enum


class PluginStatus(Enum):
    """Plugin status enumeration."""
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


@dataclass
class PluginMetadata:
    """Plugin metadata information."""
    name: str
    version: str
    author: str
    description: str
    requires_version: str = "1.0.0"
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class PluginInterface:
    """Base interface for all plugins."""
    
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        raise NotImplementedError
    
    def on_load(self):
        """Called when plugin is loaded."""
        pass
    
    def on_unload(self):
        """Called when plugin is unloaded."""
        pass
    
    def execute(self, command: str, **kwargs) -> Any:
        """Execute a plugin command."""
        raise NotImplementedError


class PluginManager:
    """Manages plugin lifecycle and execution."""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(exist_ok=True)
        self.loaded_plugins: Dict[str, PluginInterface] = {}
        self.plugin_status: Dict[str, PluginStatus] = {}
        self.hooks: Dict[str, List[Callable]] = {}
    
    def discover_plugins(self) -> List[Path]:
        """Discover available plugins."""
        return list(self.plugins_dir.glob("**/plugin.py"))
    
    def load_plugin(self, plugin_path: str) -> bool:
        """Load a plugin from file."""
        try:
            spec = importlib.util.spec_from_file_location("plugin", plugin_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot load {plugin_path}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules["plugin"] = module
            spec.loader.exec_module(module)
            
            # Get plugin class
            plugin_class = getattr(module, "Plugin", None)
            if plugin_class is None:
                raise ValueError(f"Plugin must define 'Plugin' class in {plugin_path}")
            
            # Instantiate and load
            plugin = plugin_class()
            plugin.on_load()
            
            metadata = plugin.get_metadata()
            self.loaded_plugins[metadata.name] = plugin
            self.plugin_status[metadata.name] = PluginStatus.ENABLED
            
            print(f"✓ Loaded plugin: {metadata.name} v{metadata.version}")
            return True
            
        except Exception as e:
            plugin_name = Path(plugin_path).parent.name
            self.plugin_status[plugin_name] = PluginStatus.ERROR
            print(f"❌ Failed to load plugin {plugin_name}: {str(e)}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        try:
            if plugin_name not in self.loaded_plugins:
                return False
            
            plugin = self.loaded_plugins[plugin_name]
            plugin.on_unload()
            del self.loaded_plugins[plugin_name]
            self.plugin_status[plugin_name] = PluginStatus.DISABLED
            print(f"✓ Unloaded plugin: {plugin_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to unload plugin {plugin_name}: {str(e)}")
            return False
    
    def load_all_plugins(self) -> int:
        """Load all discovered plugins."""
        plugins = self.discover_plugins()
        loaded = 0
        
        for plugin_path in plugins:
            if self.load_plugin(str(plugin_path)):
                loaded += 1
        
        print(f"\n✓ Loaded {loaded}/{len(plugins)} plugins")
        return loaded
    
    def register_hook(self, hook_name: str, callback: Callable):
        """Register a hook callback."""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)
    
    def trigger_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Trigger all callbacks registered for a hook."""
        results = []
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    result = callback(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    print(f"❌ Hook {hook_name} error: {str(e)}")
        return results
    
    def execute_plugin_command(self, plugin_name: str, command: str, **kwargs) -> Any:
        """Execute a command in a plugin."""
        if plugin_name not in self.loaded_plugins:
            raise ValueError(f"Plugin {plugin_name} not loaded")
        
        plugin = self.loaded_plugins[plugin_name]
        return plugin.execute(command, **kwargs)
    
    def get_plugin_list(self) -> Dict[str, Dict[str, Any]]:
        """Get list of all plugins with metadata."""
        plugins_info = {}
        for name, plugin in self.loaded_plugins.items():
            metadata = plugin.get_metadata()
            plugins_info[name] = {
                "version": metadata.version,
                "author": metadata.author,
                "description": metadata.description,
                "status": self.plugin_status.get(name, PluginStatus.DISABLED).value,
                "dependencies": metadata.dependencies
            }
        return plugins_info


# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get or create global plugin manager."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager
