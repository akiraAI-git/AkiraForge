#!/usr/bin/env python3
"""
Window Factory
==============

Factory for creating application windows.
Handles lazy loading and window instantiation.
"""

import logging
import time
from typing import Callable

logger = logging.getLogger(__name__)


class WindowFactory:
    """Factory for creating application windows."""
    
    # Cache for loaded window classes
    _class_cache = {}
    
    @staticmethod
    def load_window_class(module_path: str, class_name: str):
        """
        Load a window class with caching.
        
        Args:
            module_path: Module path (e.g., 'windows.login_window')
            class_name: Class name to import
            
        Returns:
            Window class
        """
        cache_key = f"{module_path}.{class_name}"
        
        # Return from cache if available
        if cache_key in WindowFactory._class_cache:
            logger.debug(f"Loaded {class_name} from cache")
            return WindowFactory._class_cache[cache_key]
        
        try:
            logger.debug(f"Loading {class_name} from {module_path}...")
            module = __import__(module_path, fromlist=[class_name])
            window_class = getattr(module, class_name)
            
            # Cache the class
            WindowFactory._class_cache[cache_key] = window_class
            logger.info(f"Successfully loaded {class_name}")
            
            return window_class
        
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load {class_name} from {module_path}: {e}")
            raise
    
    @staticmethod
    def create_window(module_path: str, class_name: str, *args, **kwargs):
        """
        Create a window instance.
        
        Args:
            module_path: Module path
            class_name: Class name
            *args: Arguments for window constructor
            **kwargs: Keyword arguments for window constructor
            
        Returns:
            Window instance
        """
        try:
            start_time = time.time()
            
            # Load window class
            window_class = WindowFactory.load_window_class(module_path, class_name)
            
            # Create instance
            window = window_class(*args, **kwargs)
            
            elapsed = time.time() - start_time
            logger.info(f"Created {class_name} in {elapsed:.3f}s")
            
            return window
        
        except Exception as e:
            logger.error(f"Failed to create window {class_name}: {e}")
            raise
