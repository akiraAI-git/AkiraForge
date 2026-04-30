#!/usr/bin/env python3
"""Device Login Manager."""
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from uuid import getnode as get_mac
logger = logging.getLogger(__name__)
try:
    from core.db import get_db_connection
except ImportError:
    def get_db_connection():
        return None
class DeviceLoginManager:
    @staticmethod
    def get_machine_uuid():
        try:
            return hex(get_mac())[2:]
        except:
            return None
    @staticmethod
    def save_device_login(user_id, username, token, remember_days=5):
        try:
            machine_uuid = DeviceLoginManager.get_machine_uuid()
            if not machine_uuid:
                return False
            conn = get_db_connection()
            if not conn:
                DeviceLoginManager._save_local_token(username, token, remember_days)
                return True
            cursor = conn.cursor()
            expires_at = datetime.now() + timedelta(days=remember_days)
            cursor.execute("""INSERT INTO device_logins (user_id, machine_uuid, auth_token, expires_at, device_name)
                VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE auth_token = %s, expires_at = %s, last_accessed = NOW()""",
                (user_id, machine_uuid, token, expires_at, username, token, expires_at))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except:
            return False
    @staticmethod
    def verify_device_login(username):
        try:
            machine_uuid = DeviceLoginManager.get_machine_uuid()
            if not machine_uuid:
                return False, None
            conn = get_db_connection()
            if not conn:
                return False, None
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM device_logins WHERE machine_uuid = %s AND expires_at > NOW()", (machine_uuid,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return (True, result[0]) if result else (False, None)
        except:
            return False, None
    @staticmethod
    def clear_device_login(username):
        try:
            machine_uuid = DeviceLoginManager.get_machine_uuid()
            if not machine_uuid:
                return False
            conn = get_db_connection()
            if not conn:
                return True
            cursor = conn.cursor()
            cursor.execute("DELETE FROM device_logins WHERE machine_uuid = %s", (machine_uuid,))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except:
            return False
    @staticmethod
    def _save_local_token(username, token, remember_days=5):
        try:
            token_dir = Path.home() / ".akiraforge"
            token_dir.mkdir(parents=True, exist_ok=True)
            token_file = token_dir / f"{username}_token.json"
            expires_at = datetime.now() + timedelta(days=remember_days)
            with open(token_file, "w") as f:
                json.dump({"token": token, "expires_at": expires_at.isoformat()}, f)
        except:
            pass
    @staticmethod
    def _get_local_token(username):
        try:
            token_file = Path.home() / ".akiraforge" / f"{username}_token.json"
            if token_file.exists():
                with open(token_file) as f:
                    return json.load(f)
        except:
            pass
        return None
    @staticmethod
    def _clear_local_token(username):
        try:
            token_file = Path.home() / ".akiraforge" / f"{username}_token.json"
            if token_file.exists():
                token_file.unlink()
        except:
            pass
