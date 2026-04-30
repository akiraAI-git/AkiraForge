import os
import datetime
from core.db import get_db_connection

LOG_FILE = "akira_logs.txt"

def log_event(category: str, level: str, message: str, username: str = None, ip: str = None):
    timestamp = datetime.datetime.now()

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{category.upper()}] [{level.upper()}] {message}")
        if username:
            f.write(f" (user={username})")
        if ip:
            f.write(f" (ip={ip})")
        f.write("\n")

    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO audit_logs (category, level, message, username, ip_address, created_at) VALUES (%s, %s, %s, %s, %s, NOW())",
            (category, level, message, username, ip)
        )
        db.commit()
    except Exception as e:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [LOGGER] [ERROR] Failed to write to DB: {e}\n")
