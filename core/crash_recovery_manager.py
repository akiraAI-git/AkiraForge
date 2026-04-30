#!/usr/bin/env python3
"""
Crash Recovery Manager
======================

Handles crash recovery and session state restoration.
Saves session state before crashes and restores on restart.
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class CrashRecoveryManager:
    """Manages crash recovery and session state restoration."""
    
    def __init__(self):
        """Initialize crash recovery manager."""
        self.recovery_dir = Path.home() / ".akiraforge" / "recovery"
        self.recovery_dir.mkdir(parents=True, exist_ok=True)
        self.recovery_file = self.recovery_dir / "session_state.json"
        logger.info("CrashRecoveryManager initialized")
    
    def save_session_state(self, username: str, session_id: str, window_type: str = None) -> bool:
        """
        Save current session state.
        
        Args:
            username: Current username
            session_id: Current session ID
            window_type: Current active window
            
        Returns:
            True if successful
        """
        try:
            state = {
                "username": username,
                "session_id": session_id,
                "window_type": window_type,
                "timestamp": datetime.now().isoformat(),
            }
            
            with open(self.recovery_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.debug(f"Session state saved for user '{username}'")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save session state: {e}")
            return False
    
    def load_session_state(self) -> Optional[Dict]:
        """
        Load saved session state.
        
        Returns:
            Session state dictionary or None
        """
        try:
            if not self.recovery_file.exists():
                return None
            
            with open(self.recovery_file, 'r') as f:
                state = json.load(f)
            
            logger.info(f"Loaded session state for user '{state.get('username')}'")
            return state
        
        except Exception as e:
            logger.warning(f"Failed to load session state: {e}")
            return None
    
    def clear_session_state(self) -> bool:
        """
        Clear saved session state.
        
        Returns:
            True if successful
        """
        try:
            if self.recovery_file.exists():
                self.recovery_file.unlink()
                logger.debug("Session state cleared")
            return True
        
        except Exception as e:
            logger.error(f"Failed to clear session state: {e}")
            return False
    
    def has_recovery_state(self) -> bool:
        """Check if recovery state exists."""
        return self.recovery_file.exists()
    
    def save_crash_log(self, error_type: str, error_message: str, traceback: str) -> bool:
        """
        Save crash log for debugging.
        
        Args:
            error_type: Type of error
            error_message: Error message
            traceback: Full traceback
            
        Returns:
            True if successful
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            crash_log_file = self.recovery_dir / f"crash_{timestamp}.log"
            
            with open(crash_log_file, 'w') as f:
                f.write(f"Crash Time: {datetime.now().isoformat()}\n")
                f.write(f"Error Type: {error_type}\n")
                f.write(f"Error Message: {error_message}\n")
                f.write(f"\nTraceback:\n{traceback}\n")
            
            logger.info(f"Crash log saved: {crash_log_file}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save crash log: {e}")
            return False
    
    def get_recent_crashes(self, limit: int = 10) -> list:
        """
        Get recent crash logs.
        
        Args:
            limit: Maximum number of crashes to return
            
        Returns:
            List of crash log files
        """
        try:
            crash_logs = sorted(
                self.recovery_dir.glob("crash_*.log"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            return crash_logs[:limit]
        
        except Exception as e:
            logger.error(f"Failed to get recent crashes: {e}")
            return []
    
    def cleanup_old_crashes(self, keep_count: int = 5) -> int:
        """
        Clean up old crash logs.
        
        Args:
            keep_count: Number of crashes to keep
            
        Returns:
            Number of deleted crash logs
        """
        try:
            crash_logs = sorted(
                self.recovery_dir.glob("crash_*.log"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            deleted = 0
            for crash_log in crash_logs[keep_count:]:
                try:
                    crash_log.unlink()
                    deleted += 1
                except Exception as e:
                    logger.warning(f"Failed to delete {crash_log}: {e}")
            
            if deleted > 0:
                logger.info(f"Cleaned up {deleted} old crash logs")
            
            return deleted
        
        except Exception as e:
            logger.error(f"Failed to cleanup crashes: {e}")
            return 0
