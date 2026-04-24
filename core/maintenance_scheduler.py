import threading
import time
from datetime import datetime, timedelta
from core.db import get_db_connection

class MaintenanceScheduler:

    def __init__(self):
        self.running = False
        self.thread = None
        self.cleanup_interval = 3600  # 1 hour between full cleanup cycles

    def start(self):
        if self.running:
            print("[MAINTENANCE] Scheduler already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._maintenance_loop, daemon=True)
        self.thread.start()
        print("[MAINTENANCE] Scheduler started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("[MAINTENANCE] Scheduler stopped")

    def _maintenance_loop(self):
        last_cleanup_time = datetime.now()

        while self.running:
            try:
                current_time = datetime.now()

                if (current_time - last_cleanup_time).total_seconds() >= self.cleanup_interval:
                    self._run_maintenance_tasks()
                    last_cleanup_time = current_time

                time.sleep(60)  # Check every minute if cleanup is needed

            except Exception as e:
                print(f"[MAINTENANCE] Error in maintenance loop: {e}")
                time.sleep(60)

    def _run_maintenance_tasks(self):
        try:
            print(f"\n[MAINTENANCE]  Running maintenance tasks at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            self._cleanup_expired_device_logins()

            self._cleanup_deleted_vault_files()

            self._archive_old_conversations()

            self._cleanup_old_logs()

            print("[MAINTENANCE] Maintenance tasks completed\n")

        except Exception as e:
            print(f"[MAINTENANCE] Error during maintenance: {e}\n")

    def _cleanup_expired_device_logins(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM device_logins 
                WHERE expires_at < NOW()
            conn = get_db_connection()
            cursor = conn.cursor()

            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                DELETE FROM vault_files 
                WHERE deleted_at IS NOT NULL AND deleted_at < %s
            conn = get_db_connection()
            cursor = conn.cursor()

            ninety_days_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                UPDATE ai_conversations 
                SET updated_at = NOW() 
                WHERE updated_at < %s 
                LIMIT 100
                WHERE created_at < %s
    if _scheduler is None:
        _scheduler = MaintenanceScheduler()
    _scheduler.start()
    return _scheduler

def stop_maintenance_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.stop()
        _scheduler = None
