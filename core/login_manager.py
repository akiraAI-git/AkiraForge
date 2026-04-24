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
            (username, claimed_identity, reason, verification_answer, ip_address)
            VALUES (%s, %s, %s, %s, %s)
