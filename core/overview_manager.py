import pymysql
import os
from core.db import get_db_connection
from core.logger import log_event
import time

class OverviewManager:
    def __init__(self):
        self.offline_mode = not os.getenv("DB_PASSWORD")
        self.db = None
        self.cursor = None
        
        if not self.offline_mode:
            try:
                self.db = get_db_connection()
                self.cursor = self.db.cursor(pymysql.cursors.DictCursor)
            except Exception as e:
                print(f"[OVERVIEW] Failed to connect to database: {e}")
                self.offline_mode = True

    def ping_database(self):
        if self.offline_mode or not self.db:
            return False, None
            
        start = time.time()
        try:
            self.cursor.execute("SELECT 1")
            self.db.commit()
            latency = (time.time() - start) * 1000
            return True, latency
        except Exception as e:
            log_event("overview", "ERROR", f"DB ping failed: {str(e)}")
            return False, None

    def get_user_stats(self):
        stats = {
            "total_users": 0,
            "locked_users": 0,
            "active_users": 0
        }
        
        if self.offline_mode or not self.db:
            return stats
            
        try:
            self.cursor.execute("SELECT COUNT(*) AS c FROM forge_users")
            stats["total_users"] = self.cursor.fetchone()["c"]

            self.cursor.execute("SELECT COUNT(*) AS c FROM forge_users WHERE locked_until IS NOT NULL")
            stats["locked_users"] = self.cursor.fetchone()["c"]

            stats["active_users"] = 0

        except Exception as e:
            log_event("overview", "ERROR", f"User stats failed: {str(e)}")

        return stats

    def get_signup_stats(self):
        stats = {
            "pending_signups": 0
        }
        
        if self.offline_mode or not self.db:
            return stats
            
        try:
            self.cursor.execute("SELECT COUNT(*) AS c FROM signup_requests WHERE status='pending'")
            stats["pending_signups"] = self.cursor.fetchone()["c"]
        except Exception as e:
            log_event("overview", "ERROR", f"Signup stats failed: {str(e)}")
        return stats

    def get_plea_stats(self):
        stats = {
            "pending_pleas": 0
        }
        
        if self.offline_mode or not self.db:
            return stats
            
        try:
            self.cursor.execute("SELECT COUNT(*) AS c FROM access_pleas")
            stats["pending_pleas"] = self.cursor.fetchone()["c"]
        except Exception as e:
            log_event("overview", "ERROR", f"Plea stats failed: {str(e)}")
        return stats

    def get_overall_health(self):
        db_ok, latency = self.ping_database()
        user_stats = self.get_user_stats()
        signup_stats = self.get_signup_stats()
        plea_stats = self.get_plea_stats()

        health = "GOOD"
        if not db_ok:
            health = "OFFLINE" if self.offline_mode else "CRITICAL"
        elif user_stats["locked_users"] > 0 or signup_stats["pending_signups"] > 5 or plea_stats["pending_pleas"] > 5:
            health = "WARNING"

        return {
            "db_ok": db_ok,
            "latency": latency,
            "user_stats": user_stats,
            "signup_stats": signup_stats,
            "plea_stats": plea_stats,
            "health": health
        }
