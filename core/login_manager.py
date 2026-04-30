from __future__ import annotations
import bcrypt
from datetime import datetime, timedelta
from typing import Tuple
import subprocess
import socket
import os
import uuid
import sys

from core.db import get_db_connection
from core.logger import log_event

class LoginManager:
    SELF_MACHINE_UUID = os.getenv("MACHINE_UUID", "49DC90CC-1E9B-11B2-A85C-D0796FCEA749")

    def __init__(self) -> None:
        self.db_available = False
        self.offline_mode = False
        self.db = None
        self.cursor = None

        try:
            self.db = get_db_connection()
            self.cursor = self.db.cursor()
            self.db_available = True
            print("[LoginManager] Database ONLINE.")
            log_event("system", "INFO", "LoginManager connected to database")
        except Exception as e:
            self.offline_mode = True
            print("[LoginManager] Running in OFFLINE MODE.", e)
            log_event("system", "ERROR", f"LoginManager failed DB connection: {e}")

    def get_machine_id(self) -> str:
        """Get the machine UUID"""
        return self.SELF_MACHINE_UUID
    
    def _ensure_connection(self) -> bool:
        """Ensure database connection is active, reconnect if needed"""
        if self.offline_mode:
            return False
        
        try:
            # Try to ping the connection
            if self.db:
                self.db.ping(reconnect=True)
                return True
        except Exception as e:
            print(f"[LoginManager] Connection lost, reconnecting: {e}")
            try:
                # Reconnect
                self.db = get_db_connection()
                self.cursor = self.db.cursor()
                self.db_available = True
                print("[LoginManager] Reconnected successfully")
                return True
            except Exception as e2:
                print(f"[LoginManager] Reconnection failed: {e2}")
                self.offline_mode = True
                return False
        
        return False
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, str, str]:
        """Authenticate user with username and password
        
        Returns:
            Tuple of (success: bool, username: str, role: str)
        """
        if self.offline_mode:
            return False, "", ""
        
        # Ensure connection is active
        if not self._ensure_connection():
            return False, "", ""
        
        try:
            # Query user from database (using forge_users table)
            self.cursor.execute("SELECT password_hash, role FROM forge_users WHERE username = %s", (username,))
            result = self.cursor.fetchone()
            
            if not result:
                return False, "", ""
            
            # Handle both dict cursor (from db.py) and regular cursor
            if isinstance(result, dict):
                stored_hash = result['password_hash']
                role = result['role']
            else:
                stored_hash = result[0]
                role = result[1]
            
            if bcrypt.checkpw(password.encode(), stored_hash.encode()):
                return True, username, role
            else:
                return False, "", ""
        except Exception as e:
            print(f"[LoginManager] Auth error: {type(e).__name__}: {e}")
            return False, "", ""
    
    def remember_device(self, username: str) -> bool:
        """Remember device login for 5 days"""
        if self.offline_mode:
            return False
        
        # Ensure connection is active
        if not self._ensure_connection():
            return False
        
        try:
            # Get user_id
            self.cursor.execute("SELECT id FROM forge_users WHERE username = %s", (username,))
            user_result = self.cursor.fetchone()
            if not user_result:
                return False
            
            # Handle both dict and tuple results
            user_id = user_result['id'] if isinstance(user_result, dict) else user_result[0]
            
            device_token = str(uuid.uuid4())
            expires = datetime.now() + timedelta(days=5)
            
            sql = """INSERT INTO device_logins 
                     (user_id, machine_uuid, auth_token, expires_at)
                     VALUES (%s, %s, %s, %s)"""
            
            self.cursor.execute(sql, (user_id, self.SELF_MACHINE_UUID, device_token, expires))
            self.db.commit()
            return True
        except Exception as e:
            print(f"[LoginManager] Remember device error: {e}")
            return False
    
    def check_device_login(self) -> Tuple[str, str]:
        """Check if device is remembered for auto-login
        
        Returns:
            Tuple of (username: str, role: str) or ("", "") if not found
        """
        if self.offline_mode:
            return "", ""
        
        # Ensure connection is active
        if not self._ensure_connection():
            return "", ""
        
        try:
            self.cursor.execute(
                "SELECT u.username, u.role FROM device_logins d JOIN forge_users u ON d.user_id = u.id WHERE d.machine_uuid = %s AND d.expires_at > NOW() LIMIT 1",
                (self.SELF_MACHINE_UUID,)
            )
            result = self.cursor.fetchone()
            if result:
                # Handle both dict and tuple results
                if isinstance(result, dict):
                    return result['username'], result['role']
                else:
                    return result[0], result[1]
            return "", ""
        except Exception as e:
            print(f"[LoginManager] Check device error: {e}")
            return "", ""
