import threading
import time
from datetime import datetime, timedelta
from core.db import get_db_connection

class MaintenanceScheduler:
    def __init__(self):
        self.running = False
        self.thread = None
        self.cleanup_interval = 3600
    
    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._maintenance_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def _maintenance_loop(self):
        while self.running:
            try:
                self._run_maintenance_tasks()
                time.sleep(3600)
            except:
                time.sleep(60)
    
    def _run_maintenance_tasks(self):
        try:
            self._cleanup_expired_device_logins()
            self._cleanup_deleted_vault_files()
            self._cleanup_old_logs()
        except:
            pass
    
    def _cleanup_expired_device_logins(self):
        try:
            conn = get_db_connection()
            if not conn:
                return
            cursor = conn.cursor()
            cursor.execute("DELETE FROM device_logins WHERE expires_at < NOW()")
            conn.commit()
            cursor.close()
            conn.close()
        except:
            pass
    
    def _cleanup_deleted_vault_files(self):
        try:
            conn = get_db_connection()
            if not conn:
                return
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vault_files LIMIT 100")
            conn.commit()
            cursor.close()
            conn.close()
        except:
            pass
    
    def _cleanup_old_logs(self):
        try:
            conn = get_db_connection()
            if not conn:
                return
            cursor = conn.cursor()
            cursor.execute("DELETE FROM audit_logs WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY) LIMIT 100")
            conn.commit()
            cursor.close()
            conn.close()
        except:
            pass

_scheduler = None

def start_maintenance_scheduler():
    global _scheduler
    if _scheduler is None:
        _scheduler = MaintenanceScheduler()
    _scheduler.start()
    return _scheduler

def stop_maintenance_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.stop()
        _scheduler = None
