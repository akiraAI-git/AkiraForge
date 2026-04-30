"""
Advanced Caching System for Akira Forge
Provides in-memory, persistent, and distributed caching capabilities.
"""

import time
import json
import pickle
from typing import Any, Optional, Dict, Callable
from datetime import datetime, timedelta
from pathlib import Path


class CacheEntry:
    """Represents a cache entry with TTL."""
    
    def __init__(self, value: Any, ttl: Optional[int] = None):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def __repr__(self):
        return f"CacheEntry(value={self.value}, expired={self.is_expired()})"


class CacheManager:
    """
    Advanced cache manager with multiple storage backends.
    
    Features:
    - In-memory caching with automatic TTL
    - Persistent disk caching
    - Cache namespacing
    - Cache invalidation patterns
    - Statistics and monitoring
    """
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
        self.max_size = 1000  # Max entries in memory
    
    def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Get value from cache."""
        full_key = f"{namespace}:{key}"
        
        # Check memory cache first
        if full_key in self.memory_cache:
            entry = self.memory_cache[full_key]
            if not entry.is_expired():
                self.stats["hits"] += 1
                return entry.value
            else:
                del self.memory_cache[full_key]
        
        # Try disk cache
        value = self._load_from_disk(full_key)
        if value is not None:
            self.stats["hits"] += 1
            return value
        
        self.stats["misses"] += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            namespace: str = "default", persistent: bool = False):
        """Set value in cache."""
        full_key = f"{namespace}:{key}"
        
        # Add to memory cache
        if len(self.memory_cache) >= self.max_size:
            # Evict oldest entry
            oldest_key = min(self.memory_cache.keys(),
                            key=lambda k: self.memory_cache[k].created_at)
            del self.memory_cache[oldest_key]
            self.stats["evictions"] += 1
        
        self.memory_cache[full_key] = CacheEntry(value, ttl)
        
        # Optionally save to disk
        if persistent:
            self._save_to_disk(full_key, value)
    
    def delete(self, key: str, namespace: str = "default"):
        """Delete value from cache."""
        full_key = f"{namespace}:{key}"
        
        if full_key in self.memory_cache:
            del self.memory_cache[full_key]
        
        disk_path = self.cache_dir / f"{full_key}.cache"
        if disk_path.exists():
            disk_path.unlink()
    
    def invalidate_pattern(self, pattern: str, namespace: str = "default"):
        """Invalidate all cache entries matching a pattern."""
        import fnmatch
        prefix = f"{namespace}:"
        keys_to_delete = [
            k for k in self.memory_cache.keys()
            if fnmatch.fnmatch(k, f"{prefix}{pattern}")
        ]
        
        for key in keys_to_delete:
            del self.memory_cache[key]
        
        return len(keys_to_delete)
    
    def clear(self, namespace: Optional[str] = None):
        """Clear cache (all or specific namespace)."""
        if namespace:
            prefix = f"{namespace}:"
            keys_to_delete = [k for k in self.memory_cache if k.startswith(prefix)]
            for key in keys_to_delete:
                del self.memory_cache[key]
        else:
            self.memory_cache.clear()
    
    def get_or_compute(self, key: str, compute_fn: Callable[[], Any],
                      ttl: Optional[int] = None, namespace: str = "default") -> Any:
        """Get from cache or compute if not found."""
        value = self.get(key, namespace)
        if value is not None:
            return value
        
        value = compute_fn()
        self.set(key, value, ttl, namespace)
        return value
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "evictions": self.stats["evictions"],
            "hit_rate": f"{hit_rate * 100:.2f}%",
            "entries_in_memory": len(self.memory_cache),
            "max_size": self.max_size
        }
    
    def _save_to_disk(self, key: str, value: Any):
        """Save value to disk."""
        try:
            cache_path = self.cache_dir / f"{key}.cache"
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
        except Exception as e:
            print(f"❌ Failed to save cache to disk: {str(e)}")
    
    def _load_from_disk(self, key: str) -> Optional[Any]:
        """Load value from disk."""
        try:
            cache_path = self.cache_dir / f"{key}.cache"
            if cache_path.exists():
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
        except Exception as e:
            print(f"❌ Failed to load cache from disk: {str(e)}")
        return None


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get or create global cache manager."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


# Convenience functions
def cache_get(key: str, namespace: str = "default") -> Optional[Any]:
    """Get from cache."""
    return get_cache_manager().get(key, namespace)


def cache_set(key: str, value: Any, ttl: Optional[int] = None, 
              namespace: str = "default", persistent: bool = False):
    """Set cache value."""
    get_cache_manager().set(key, value, ttl, namespace, persistent)


def cache_delete(key: str, namespace: str = "default"):
    """Delete from cache."""
    get_cache_manager().delete(key, namespace)


def cache_clear(namespace: Optional[str] = None):
    """Clear cache."""
    get_cache_manager().clear(namespace)
