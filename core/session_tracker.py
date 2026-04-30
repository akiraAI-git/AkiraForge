#!/usr/bin/env python3
"""
Session Tracking & IP Detection
================================

Tracks user sessions and captures IP/location information
for security and audit purposes.

Features:
  - Session creation and tracking
  - IP address capture
  - Session timeout handling
  - Device identification
  - Security scoring
"""

import uuid
import os
import socket
import logging
import time
from datetime import datetime, timedelta
from collections import defaultdict
import threading
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class SessionTracker:
    """Tracks user sessions and activity."""
    
    def __init__(self, session_timeout_minutes=None):
        """
        Initialize session tracker.
        
        Args:
            session_timeout_minutes: Timeout for inactive sessions (default: from env or 120)
        """
        self.sessions = {}  # {session_id: session_data}
        self.user_sessions = defaultdict(list)  # {username: [session_ids]}
        
        # Get timeout from environment or use default
        if session_timeout_minutes is None:
            session_timeout_minutes = int(os.getenv("SESSION_TIMEOUT_MINUTES", "120"))
        
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.lock = threading.Lock()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(
            target=self._auto_cleanup,
            daemon=True
        )
        self.cleanup_thread.start()
        logger.info(f"Session tracker initialized: {session_timeout_minutes} minute timeout")
    
    def _auto_cleanup(self):
        """Periodically cleanup expired sessions."""
        while True:
            try:
                time.sleep(3600)  # Every hour
                cleaned = self.cleanup_expired_sessions()
                if cleaned > 0:
                    logger.info(f"Cleaned up {cleaned} expired sessions")
            except Exception as e:
                logger.error(f"Error in cleanup thread: {e}")
    
    def create_session(self, username: str, ip_address: Optional[str] = None,
                      user_agent: Optional[str] = None) -> str:
        """
        Create a new session for user.
        
        Args:
            username: Username
            ip_address: Client IP address (optional)
            user_agent: Client user agent (optional)
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        current_time = datetime.utcnow()
        
        session_data = {
            "session_id": session_id,
            "username": username,
            "ip_address": ip_address or self._get_local_ip(),
            "user_agent": user_agent or "Unknown",
            "created_at": current_time.isoformat(),
            "last_activity": current_time.isoformat(),
            "active": True,
            "device_id": self._generate_device_id(ip_address, user_agent),
            "actions_count": 0
        }
        
        with self.lock:
            self.sessions[session_id] = session_data
            self.user_sessions[username].append(session_id)
        
        logger.debug(f"Session created: {username} from {ip_address}")
        return session_id
    
    def record_activity(self, session_id: str, action: str) -> bool:
        """
        Record activity for a session.
        
        Args:
            session_id: Session ID
            action: Action performed
            
        Returns:
            True if recorded, False if session expired/not found
        """
        with self.lock:
            if session_id not in self.sessions:
                logger.warning(f"Activity recorded for non-existent session: {session_id}")
                return False
            
            session = self.sessions[session_id]
            current_time = datetime.utcnow()
            last_activity = datetime.fromisoformat(session["last_activity"])
            
            # Check if session expired
            if current_time - last_activity > self.session_timeout:
                session["active"] = False
                logger.info(f"Session expired: {session_id}")
                return False
            
            # Update activity
            session["last_activity"] = current_time.isoformat()
            session["actions_count"] += 1
            
            return True
    
    def end_session(self, session_id: str) -> bool:
        """
        End a session.
        
        Args:
            session_id: Session ID to end
            
        Returns:
            True if successful
        """
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id]["active"] = False
                logger.debug(f"Session ended: {session_id}")
                return True
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session information."""
        with self.lock:
            return self.sessions.get(session_id, None)
    
    def get_user_sessions(self, username: str) -> list:
        """Get all sessions for a user."""
        with self.lock:
            session_ids = self.user_sessions.get(username, [])
            return [self.sessions.get(sid) for sid in session_ids if sid in self.sessions]
    
    def get_active_user_sessions(self, username: str) -> list:
        """Get active sessions for a user."""
        sessions = self.get_user_sessions(username)
        return [s for s in sessions if s and s["active"]]
    
    def _get_local_ip(self) -> str:
        """Get local machine IP address."""
        try:
            # Connect to external server to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def _generate_device_id(self, ip: Optional[str], user_agent: Optional[str]) -> str:
        """Generate a device identifier from IP and user agent."""
        import hashlib
        device_data = f"{ip or 'unknown'}:{user_agent or 'unknown'}"
        return hashlib.sha256(device_data.encode()).hexdigest()[:16]
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions."""
        with self.lock:
            current_time = datetime.utcnow()
            expired = []
            
            for session_id, session in list(self.sessions.items()):
                last_activity = datetime.fromisoformat(session["last_activity"])
                
                if current_time - last_activity > self.session_timeout:
                    expired.append(session_id)
            
            for session_id in expired:
                del self.sessions[session_id]
            
            if expired:
                logger.info(f"Cleaned up {len(expired)} expired sessions")
            
            return len(expired)
    
    def get_session_stats(self) -> Dict:
        """Get session statistics."""
        with self.lock:
            active_count = sum(1 for s in self.sessions.values() if s["active"])
            unique_users = len(self.user_sessions)
            
            return {
                "total_sessions": len(self.sessions),
                "active_sessions": active_count,
                "unique_users": unique_users,
                "session_timeout_minutes": int(self.session_timeout.total_seconds() / 60)
            }
    
    def get_metrics(self) -> Dict:
        """Get session tracker metrics."""
        with self.lock:
            return {
                "total_sessions": len(self.sessions),
                "active_sessions": sum(1 for s in self.sessions.values() if s["active"]),
                "tracked_users": len(self.user_sessions),
                "average_actions_per_session": round(
                    sum(s["actions_count"] for s in self.sessions.values()) / max(len(self.sessions), 1), 2
                )
            }

# ... rest of file unchanged ...
    
    def create_session(self, username: str, ip_address: Optional[str] = None,
                      user_agent: Optional[str] = None) -> str:
        """
        Create a new session for user.
        
        Args:
            username: Username
            ip_address: Client IP address (optional)
            user_agent: Client user agent (optional)
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        current_time = datetime.utcnow()
        
        session_data = {
            "session_id": session_id,
            "username": username,
            "ip_address": ip_address or self._get_local_ip(),
            "user_agent": user_agent or "Unknown",
            "created_at": current_time.isoformat(),
            "last_activity": current_time.isoformat(),
            "active": True,
            "device_id": self._generate_device_id(ip_address, user_agent),
            "actions_count": 0
        }
        
        with self.lock:
            self.sessions[session_id] = session_data
            self.user_sessions[username].append(session_id)
        
        return session_id
    
    def record_activity(self, session_id: str, action: str) -> bool:
        """
        Record activity for a session.
        
        Args:
            session_id: Session ID
            action: Action performed
            
        Returns:
            True if recorded, False if session expired/not found
        """
        with self.lock:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            current_time = datetime.utcnow()
            last_activity = datetime.fromisoformat(session["last_activity"])
            
            # Check if session expired
            if current_time - last_activity > self.session_timeout:
                session["active"] = False
                return False
            
            # Update activity
            session["last_activity"] = current_time.isoformat()
            session["actions_count"] += 1
            
            return True
    
    def end_session(self, session_id: str) -> bool:
        """
        End a session.
        
        Args:
            session_id: Session ID to end
            
        Returns:
            True if successful
        """
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id]["active"] = False
                return True
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session information."""
        with self.lock:
            return self.sessions.get(session_id, None)
    
    def get_user_sessions(self, username: str) -> list:
        """Get all sessions for a user."""
        with self.lock:
            session_ids = self.user_sessions.get(username, [])
            return [self.sessions.get(sid) for sid in session_ids if sid in self.sessions]
    
    def get_active_user_sessions(self, username: str) -> list:
        """Get active sessions for a user."""
        sessions = self.get_user_sessions(username)
        return [s for s in sessions if s and s["active"]]
    
    def _get_local_ip(self) -> str:
        """Get local machine IP address."""
        try:
            # Connect to external server to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def _generate_device_id(self, ip: Optional[str], user_agent: Optional[str]) -> str:
        """Generate a device identifier from IP and user agent."""
        import hashlib
        device_data = f"{ip or 'unknown'}:{user_agent or 'unknown'}"
        return hashlib.sha256(device_data.encode()).hexdigest()[:16]
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        with self.lock:
            current_time = datetime.utcnow()
            expired = []
            
            for session_id, session in list(self.sessions.items()):
                last_activity = datetime.fromisoformat(session["last_activity"])
                
                if current_time - last_activity > self.session_timeout:
                    expired.append(session_id)
            
            for session_id in expired:
                del self.sessions[session_id]
            
            return len(expired)
    
    def get_session_stats(self) -> Dict:
        """Get session statistics."""
        with self.lock:
            active_count = sum(1 for s in self.sessions.values() if s["active"])
            unique_users = len(self.user_sessions)
            
            return {
                "total_sessions": len(self.sessions),
                "active_sessions": active_count,
                "unique_users": unique_users,
                "session_timeout_minutes": self.session_timeout.total_seconds() / 60
            }

# Global instance
_global_session_tracker = None

def get_session_tracker() -> SessionTracker:
    """Get or create global session tracker."""
    global _global_session_tracker
    if _global_session_tracker is None:
        _global_session_tracker = SessionTracker()
    return _global_session_tracker

def create_session(username: str, ip_address: Optional[str] = None) -> str:
    """Create a new session."""
    tracker = get_session_tracker()
    return tracker.create_session(username, ip_address)

def record_activity(session_id: str, action: str) -> bool:
    """Record activity for a session."""
    tracker = get_session_tracker()
    return tracker.record_activity(session_id, action)
