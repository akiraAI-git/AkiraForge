#!/usr/bin/env python3
"""
Rate Limiting System
====================

Prevents abuse by limiting sensitive operations (vault access, admin actions, etc.)
to a maximum number per time period.

Features:
  - Per-user rate limiting
  - Per-action rate limiting
  - Configurable limits and time windows
  - Thread-safe operation
  - Detailed tracking and reporting
"""

import time
import os
import logging
from collections import defaultdict
from datetime import datetime, timedelta
import threading
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter for sensitive operations."""
    
    def __init__(self):
        """Initialize rate limiter."""
        self.lock = threading.Lock()
        self.user_actions = defaultdict(list)  # {user: [(timestamp, action)]}
        self.action_limits = {
            # Action: (max_count, time_window_seconds)
            "VAULT_ACCESS": (
                int(os.getenv("RATE_LIMIT_VAULT_ACCESS_COUNT", "10")),
                int(os.getenv("RATE_LIMIT_VAULT_ACCESS_WINDOW", "3600"))
            ),
            "VAULT_FILE_UPLOAD": (
                int(os.getenv("RATE_LIMIT_VAULT_UPLOAD_COUNT", "20")),
                int(os.getenv("RATE_LIMIT_VAULT_UPLOAD_WINDOW", "3600"))
            ),
            "VAULT_FILE_DELETE": (
                int(os.getenv("RATE_LIMIT_VAULT_DELETE_COUNT", "10")),
                int(os.getenv("RATE_LIMIT_VAULT_DELETE_WINDOW", "3600"))
            ),
            "ADMIN_ACCESS": (
                int(os.getenv("RATE_LIMIT_ADMIN_COUNT", "50")),
                int(os.getenv("RATE_LIMIT_ADMIN_WINDOW", "3600"))
            ),
            "USER_DELETE": (
                int(os.getenv("RATE_LIMIT_USER_DELETE_COUNT", "5")),
                int(os.getenv("RATE_LIMIT_USER_DELETE_WINDOW", "86400"))
            ),
            "PASSWORD_CHANGE": (
                int(os.getenv("RATE_LIMIT_PASSWORD_COUNT", "5")),
                int(os.getenv("RATE_LIMIT_PASSWORD_WINDOW", "3600"))
            ),
            "PERMISSION_CHANGE": (
                int(os.getenv("RATE_LIMIT_PERMISSION_COUNT", "20")),
                int(os.getenv("RATE_LIMIT_PERMISSION_WINDOW", "3600"))
            ),
        }
        logger.info("Rate limiter initialized with configured limits")
    
    def set_limit(self, action: str, max_count: int, time_window_seconds: int):
        """
        Set rate limit for an action.
        
        Args:
            action: Action type (e.g., 'VAULT_ACCESS')
            max_count: Maximum number of occurrences
            time_window_seconds: Time window in seconds
        """
        self.action_limits[action] = (max_count, time_window_seconds)
        logger.debug(f"Rate limit set: {action} = {max_count} per {time_window_seconds}s")
    
    def check_rate_limit(self, username: str, action: str) -> Tuple[bool, str]:
        """
        Check if action is allowed for user.
        
        Args:
            username: Username
            action: Action type
            
        Returns:
            Tuple[bool, str]: (allowed, message)
        """
        with self.lock:
            current_time = time.time()
            
            # Get rate limit for action
            if action not in self.action_limits:
                return True, ""  # No limit set
            
            max_count, time_window = self.action_limits[action]
            
            # Get user's action history
            recent_actions = [
                (ts, act) for ts, act in self.user_actions[username]
                if (current_time - ts) < time_window and act == action
            ]
            
            # Check if limit exceeded
            if len(recent_actions) >= max_count:
                logger.warning(f"Rate limit exceeded for {username}: {action} ({len(recent_actions)}/{max_count})")
                return False, (f"Rate limit exceeded for {action}. "
                             f"Max {max_count} per {time_window} seconds.")
            
            # Record this action
            self.user_actions[username].append((current_time, action))
            
            # Clean up old entries
            self._cleanup_old_entries(username)
            
            return True, ""
    
    def _cleanup_old_entries(self, username: str):
        """Remove old entries older than 24 hours."""
        current_time = time.time()
        cutoff = current_time - (24 * 3600)
        
        self.user_actions[username] = [
            (ts, act) for ts, act in self.user_actions[username]
            if ts > cutoff
        ]
    
    def get_user_stats(self, username: str) -> Dict:
        """Get rate limit statistics for a user."""
        with self.lock:
            current_time = time.time()
            stats = {
                "username": username,
                "actions": {}
            }
            
            for action, (max_count, time_window) in self.action_limits.items():
                recent = [
                    (ts, act) for ts, act in self.user_actions[username]
                    if (current_time - ts) < time_window and act == action
                ]
                
                stats["actions"][action] = {
                    "count": len(recent),
                    "limit": max_count,
                    "time_window_seconds": time_window,
                    "remaining": max_count - len(recent)
                }
            
            return stats
    
    def reset_user(self, username: str):
        """Reset rate limit counters for a user."""
        with self.lock:
            if username in self.user_actions:
                del self.user_actions[username]
                logger.info(f"Rate limit reset for user: {username}")
    
    def get_metrics(self) -> Dict:
        """Get rate limiter metrics."""
        with self.lock:
            return {
                "total_users_tracked": len(self.user_actions),
                "total_actions_recorded": sum(len(actions) for actions in self.user_actions.values()),
                "configured_limits": len(self.action_limits)
            }
    
    def check_rate_limit(self, username: str, action: str) -> Tuple[bool, str]:
        """
        Check if action is allowed for user.
        
        Args:
            username: Username
            action: Action type
            
        Returns:
            Tuple[bool, str]: (allowed, message)
        """
        with self.lock:
            current_time = time.time()
            
            # Get rate limit for action
            if action not in self.action_limits:
                return True, ""  # No limit set
            
            max_count, time_window = self.action_limits[action]
            
            # Get user's action history
            recent_actions = [
                (ts, act) for ts, act in self.user_actions[username]
                if (current_time - ts) < time_window and act == action
            ]
            
            # Check if limit exceeded
            if len(recent_actions) >= max_count:
                logger.warning(f"Rate limit exceeded for {username}: {action} ({len(recent_actions)}/{max_count})")
                return False, (f"Rate limit exceeded for {action}. "
                             f"Max {max_count} per {time_window} seconds.")
            
            # Record this action
            self.user_actions[username].append((current_time, action))
            
            # Clean up old entries
            self._cleanup_old_entries(username)
            
            return True, ""
    
    def _cleanup_old_entries(self, username: str):
        """Remove old entries older than 24 hours."""
        current_time = time.time()
        cutoff = current_time - (24 * 3600)
        
        self.user_actions[username] = [
            (ts, act) for ts, act in self.user_actions[username]
            if ts > cutoff
        ]
    
    def get_user_stats(self, username: str) -> Dict:
        """Get rate limit statistics for a user."""
        with self.lock:
            current_time = time.time()
            stats = {
                "username": username,
                "actions": {}
            }
            
            for action, (max_count, time_window) in self.action_limits.items():
                recent = [
                    (ts, act) for ts, act in self.user_actions[username]
                    if (current_time - ts) < time_window and act == action
                ]
                
                stats["actions"][action] = {
                    "count": len(recent),
                    "limit": max_count,
                    "time_window_seconds": time_window,
                    "remaining": max_count - len(recent)
                }
            
            return stats
    
    def reset_user(self, username: str):
        """Reset rate limit counters for a user."""
        with self.lock:
            if username in self.user_actions:
                del self.user_actions[username]
                logger.info(f"Rate limit reset for user: {username}")
    
    def get_metrics(self) -> Dict:
        """Get rate limiter metrics."""
        with self.lock:
            return {
                "total_users_tracked": len(self.user_actions),
                "total_actions_recorded": sum(len(actions) for actions in self.user_actions.values()),
                "configured_limits": len(self.action_limits)
            }

# Global instance
_global_rate_limiter = None

def get_rate_limiter() -> RateLimiter:
    """Get or create global rate limiter."""
    global _global_rate_limiter
    if _global_rate_limiter is None:
        _global_rate_limiter = RateLimiter()
    return _global_rate_limiter

def check_rate_limit(username: str, action: str) -> Tuple[bool, str]:
    """Check if action is rate-limited."""
    limiter = get_rate_limiter()
    return limiter.check_rate_limit(username, action)
