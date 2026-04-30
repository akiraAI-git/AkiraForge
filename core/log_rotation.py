#!/usr/bin/env python3
"""
Log Rotation & Archiving System
================================

Manages audit log rotation, archiving, and compression.
Prevents logs from growing indefinitely and saves disk space.

Features:
  - Automatic monthly log rotation
  - Log archiving with timestamps
  - Optional GZIP compression
  - Cleanup of old archives (configurable retention)
  - Thread-safe operations
"""

import os
import gzip
import shutil
import logging
from pathlib import Path
from datetime import datetime, timedelta
import threading
import json

logger = logging.getLogger(__name__)

class LogRotationManager:
    """Manages audit log rotation and archiving."""
    
    def __init__(self, log_dir=None, retention_days=90, compress=True):
        """
        Initialize log rotation manager.
        
        Args:
            log_dir: Directory containing audit logs (default: ~/.akiraforge/audit_logs)
            retention_days: Keep archives for this many days (default: 90)
            compress: Whether to compress archived logs (default: True)
        """
        self.log_dir = Path(log_dir or (Path.home() / ".akiraforge" / "audit_logs"))
        self.archive_dir = self.log_dir / "archive"
        self.retention_days = retention_days
        self.compress = compress
        self.lock = threading.Lock()
        
        # Create archive directory if needed
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Log rotation manager initialized: {self.archive_dir}, {retention_days}d retention, compress={compress}")
    
    def should_rotate(self, log_file):
        """Check if log file should be rotated (is older than 30 days)."""
        if not log_file.exists():
            return False
        
        # Get file modification time
        mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
        age_days = (datetime.now() - mod_time).days
        
        # Rotate if file is older than 30 days
        return age_days >= 30
    
    def rotate_log(self, log_file_name):
        """
        Rotate a specific log file.
        
        Args:
            log_file_name: Name of log file (e.g., 'public_actions.log')
        """
        with self.lock:
            try:
                log_file = self.log_dir / log_file_name
                
                if not log_file.exists():
                    return False
                
                # Create archive filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_name = f"{log_file_name.replace('.log', '')}_{timestamp}"
                archive_path = self.archive_dir / archive_name
                
                if self.compress:
                    archive_path = Path(str(archive_path) + ".gz")
                    self._compress_file(log_file, archive_path)
                else:
                    # Copy file to archive
                    shutil.copy2(log_file, archive_path)
                
                # Clear original log file
                log_file.truncate(0)
                logger.info(f"Log rotated: {log_file_name} -> {archive_path.name}")
                
                return True
            
            except Exception as e:
                logger.error(f"Error rotating {log_file_name}: {e}")
                return False
    
    def _compress_file(self, source, destination):
        """Compress a file using GZIP."""
        try:
            with open(source, 'rb') as f_in:
                with gzip.open(destination, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            logger.debug(f"File compressed: {source} -> {destination}")
        except Exception as e:
            logger.error(f"Error compressing file: {e}")
    
    def cleanup_old_archives(self):
        """Remove archived logs older than retention period."""
        with self.lock:
            try:
                cutoff_date = datetime.now() - timedelta(days=self.retention_days)
                deleted_count = 0
                
                for archive_file in self.archive_dir.glob("*"):
                    if archive_file.is_file():
                        mod_time = datetime.fromtimestamp(archive_file.stat().st_mtime)
                        
                        if mod_time < cutoff_date:
                            archive_file.unlink()
                            deleted_count += 1
                
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} old archives (>{self.retention_days} days)")
                
                return deleted_count
            
            except Exception as e:
                logger.error(f"Error cleaning up archives: {e}")
                return 0
    
    def rotate_all(self):
        """Rotate all audit log files."""
        log_files = [
            'public_actions.log',
            'important_actions.log',
            'hidden_actions.log'
        ]
        
        rotated = 0
        for log_file in log_files:
            if self.should_rotate(self.log_dir / log_file):
                if self.rotate_log(log_file):
                    rotated += 1
        
        # Clean up old archives
        self.cleanup_old_archives()
        
        if rotated > 0:
            logger.info(f"Rotated {rotated} log files")
        
        return rotated
    
    def get_archive_stats(self):
        """Get statistics about archived logs."""
        try:
            total_size = 0
            file_count = 0
            oldest_date = None
            newest_date = None
            
            for archive_file in self.archive_dir.glob("*"):
                if archive_file.is_file():
                    file_count += 1
                    total_size += archive_file.stat().st_size
                    
                    mod_time = datetime.fromtimestamp(archive_file.stat().st_mtime)
                    
                    if oldest_date is None or mod_time < oldest_date:
                        oldest_date = mod_time
                    if newest_date is None or mod_time > newest_date:
                        newest_date = mod_time
            
            return {
                "file_count": file_count,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "oldest": oldest_date.isoformat() if oldest_date else None,
                "newest": newest_date.isoformat() if newest_date else None,
                "retention_days": self.retention_days
            }
        
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def get_metrics(self) -> dict:
        """Get rotation manager metrics."""
        stats = self.get_archive_stats()
        return {
            "archived_files": stats.get("file_count", 0),
            "total_archive_size_mb": stats.get("total_size_mb", 0),
            "archive_retention_days": self.retention_days,
            "compression_enabled": self.compress
        }
    
    def should_rotate(self, log_file):
        """Check if log file should be rotated (is older than 30 days)."""
        if not log_file.exists():
            return False
        
        # Get file modification time
        mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
        age_days = (datetime.now() - mod_time).days
        
        # Rotate if file is older than 30 days
        return age_days >= 30
    
    def rotate_log(self, log_file_name):
        """
        Rotate a specific log file.
        
        Args:
            log_file_name: Name of log file (e.g., 'public_actions.log')
        """
        with self.lock:
            try:
                log_file = self.log_dir / log_file_name
                
                if not log_file.exists():
                    return False
                
                # Create archive filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_name = f"{log_file_name.replace('.log', '')}_{timestamp}"
                archive_path = self.archive_dir / archive_name
                
                if self.compress:
                    archive_path = Path(str(archive_path) + ".gz")
                    self._compress_file(log_file, archive_path)
                else:
                    # Copy file to archive
                    shutil.copy2(log_file, archive_path)
                
                # Clear original log file
                log_file.truncate(0)
                
                return True
            
            except Exception as e:
                print(f"[LOG_ROTATION] Error rotating {log_file_name}: {e}")
                return False
    
    def _compress_file(self, source, destination):
        """Compress a file using GZIP."""
        try:
            with open(source, 'rb') as f_in:
                with gzip.open(destination, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        except Exception as e:
            print(f"[LOG_ROTATION] Error compressing file: {e}")
    
    def cleanup_old_archives(self):
        """Remove archived logs older than retention period."""
        with self.lock:
            try:
                cutoff_date = datetime.now() - timedelta(days=self.retention_days)
                deleted_count = 0
                
                for archive_file in self.archive_dir.glob("*"):
                    if archive_file.is_file():
                        mod_time = datetime.fromtimestamp(archive_file.stat().st_mtime)
                        
                        if mod_time < cutoff_date:
                            archive_file.unlink()
                            deleted_count += 1
                
                if deleted_count > 0:
                    print(f"[LOG_ROTATION] Cleaned up {deleted_count} old archives")
                
                return deleted_count
            
            except Exception as e:
                print(f"[LOG_ROTATION] Error cleaning up archives: {e}")
                return 0
    
    def rotate_all(self):
        """Rotate all audit log files."""
        log_files = [
            'public_actions.log',
            'important_actions.log',
            'hidden_actions.log'
        ]
        
        rotated = 0
        for log_file in log_files:
            if self.should_rotate(self.log_dir / log_file):
                if self.rotate_log(log_file):
                    rotated += 1
        
        # Clean up old archives
        self.cleanup_old_archives()
        
        return rotated
    
    def get_archive_stats(self):
        """Get statistics about archived logs."""
        try:
            total_size = 0
            file_count = 0
            oldest_date = None
            newest_date = None
            
            for archive_file in self.archive_dir.glob("*"):
                if archive_file.is_file():
                    file_count += 1
                    total_size += archive_file.stat().st_size
                    
                    mod_time = datetime.fromtimestamp(archive_file.stat().st_mtime)
                    
                    if oldest_date is None or mod_time < oldest_date:
                        oldest_date = mod_time
                    if newest_date is None or mod_time > newest_date:
                        newest_date = mod_time
            
            return {
                "file_count": file_count,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "oldest": oldest_date.isoformat() if oldest_date else None,
                "newest": newest_date.isoformat() if newest_date else None,
                "retention_days": self.retention_days
            }
        
        except Exception as e:
            print(f"[LOG_ROTATION] Error getting stats: {e}")
            return {}

# Global instance
_global_rotation_manager = None

def get_log_rotation_manager(retention_days=90, compress=True):
    """Get or create global log rotation manager."""
    global _global_rotation_manager
    if _global_rotation_manager is None:
        _global_rotation_manager = LogRotationManager(
            retention_days=retention_days,
            compress=compress
        )
    return _global_rotation_manager
