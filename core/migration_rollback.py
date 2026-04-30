#!/usr/bin/env python3
"""
Automated Database Rollback System
===================================

Provides automated rollback capability for failed database migrations.

Features:
  - Backup before migration
  - Automated rollback on failure
  - Rollback verification
  - Point-in-time recovery
  - Migration rollback history
"""

import os
import subprocess
import logging
from pathlib import Path
from datetime import datetime
import json
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class MigrationRollback:
    """Manages database migration rollbacks."""
    
    def __init__(self, backup_dir: str = None):
        """
        Initialize rollback manager.
        
        Args:
            backup_dir: Directory for migration backups
        """
        self.backup_dir = Path(backup_dir or (Path.home() / ".akiraforge" / "migration_backups"))
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.rollback_history_file = self.backup_dir / "rollback_history.json"
        logger.info(f"Migration rollback manager initialized: {self.backup_dir}")
    
    def create_pre_migration_backup(self, db_name: str = None) -> Tuple[bool, str]:
        """
        Create backup before migration.
        
        Args:
            db_name: Database name
            
        Returns:
            Tuple[bool, str]: (success, backup_file_path)
        """
        db_name = db_name or os.getenv("DB_NAME", "akiraforge")
        db_user = os.getenv("DB_USER", "akiraforge")
        db_host = os.getenv("DB_HOST", "localhost")
        db_password = os.getenv("DB_PASSWORD", "")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"pre_migration_{db_name}_{timestamp}.sql"
        
        try:
            pwd_arg = f" --password={db_password}" if db_password else ""
            cmd = (f"mysqldump -h {db_host} -u {db_user}{pwd_arg} "
                   f"--single-transaction --quick {db_name} > {backup_file}")
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and backup_file.exists():
                logger.info(f"Pre-migration backup created: {backup_file}")
                return True, str(backup_file)
            else:
                logger.error(f"Backup failed: {result.stderr}")
                return False, ""
        
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False, ""
    
    def perform_rollback(self, backup_file: str, db_name: str = None) -> Tuple[bool, str]:
        """
        Perform rollback to backup.
        
        Args:
            backup_file: Path to backup file
            db_name: Database name
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        db_name = db_name or os.getenv("DB_NAME", "akiraforge")
        db_user = os.getenv("DB_USER", "akiraforge")
        db_host = os.getenv("DB_HOST", "localhost")
        db_password = os.getenv("DB_PASSWORD", "")
        
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                return False, f"Backup file not found: {backup_file}"
            
            pwd_arg = f" --password={db_password}" if db_password else ""
            cmd = (f"mysql -h {db_host} -u {db_user}{pwd_arg} "
                   f"{db_name} < {backup_file}")
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3600)
            
            if result.returncode == 0:
                self._record_rollback(backup_file, db_name, True)
                logger.info(f"Rollback completed: {db_name}")
                return True, f"Successfully rolled back to {backup_path.name}"
            else:
                self._record_rollback(backup_file, db_name, False)
                logger.error(f"Rollback failed: {result.stderr}")
                return False, f"Rollback failed: {result.stderr}"
        
        except subprocess.TimeoutExpired:
            logger.error("Rollback timed out (>1 hour)")
            return False, "Rollback timed out (greater than 1 hour)"
        except Exception as e:
            logger.error(f"Error performing rollback: {e}")
            return False, str(e)
    
    def verify_backup(self, backup_file: str) -> Dict:
        """
        Verify backup integrity.
        
        Args:
            backup_file: Path to backup file
            
        Returns:
            Verification details
        """
        try:
            backup_path = Path(backup_file)
            
            if not backup_path.exists():
                return {"valid": False, "error": "File not found"}
            
            with open(backup_path, 'r') as f:
                content = f.read(1000)  # Read first 1000 chars
            
            checks = {
                "file_exists": backup_path.exists(),
                "file_size_mb": round(backup_path.stat().st_size / (1024 * 1024), 2),
                "has_mysqldump_header": "-- MySQL dump" in content,
                "has_create_table": "CREATE TABLE" in content,
                "is_readable": True
            }
            
            valid = all(checks.values())
            logger.debug(f"Backup verification: valid={valid}, size={checks['file_size_mb']}MB")
            
            return {
                "valid": valid,
                "checks": checks,
                "file_size_mb": checks["file_size_mb"]
            }
        
        except Exception as e:
            logger.error(f"Error verifying backup: {e}")
            return {"valid": False, "error": str(e)}
    
    def _record_rollback(self, backup_file: str, db_name: str, success: bool):
        """Record rollback event in history."""
        try:
            history = []
            if self.rollback_history_file.exists():
                with open(self.rollback_history_file, 'r') as f:
                    history = json.load(f)
            
            history.append({
                "timestamp": datetime.now().isoformat(),
                "backup_file": backup_file,
                "database": db_name,
                "success": success
            })
            
            with open(self.rollback_history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            logger.info(f"Rollback recorded: {db_name} - {'SUCCESS' if success else 'FAILED'}")
        
        except Exception as e:
            logger.error(f"Error recording rollback: {e}")
    
    def get_rollback_history(self) -> list:
        """Get rollback history."""
        try:
            if self.rollback_history_file.exists():
                with open(self.rollback_history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error reading history: {e}")
        
        return []
    
    def list_available_backups(self) -> list:
        """List available backup files."""
        try:
            backups = []
            for backup_file in sorted(self.backup_dir.glob("pre_migration_*.sql")):
                backups.append({
                    "filename": backup_file.name,
                    "path": str(backup_file),
                    "size_mb": round(backup_file.stat().st_size / (1024 * 1024), 2),
                    "created": datetime.fromtimestamp(
                        backup_file.stat().st_mtime
                    ).isoformat()
                })
            
            return sorted(backups, key=lambda x: x["created"], reverse=True)
        
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []
    
    def cleanup_old_backups(self, keep_count: int = 5):
        """Keep only most recent backups."""
        backups = sorted(
            self.backup_dir.glob("pre_migration_*.sql"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        for old_backup in backups[keep_count:]:
            try:
                old_backup.unlink()
                logger.info(f"Cleaned up old backup: {old_backup.name}")
            except Exception as e:
                logger.error(f"Error cleaning backup: {e}")
    
    def get_metrics(self) -> dict:
        """Get rollback manager metrics."""
        backups = self.list_available_backups()
        return {
            "available_backups": len(backups),
            "total_backup_size_mb": round(sum(b["size_mb"] for b in backups), 2),
            "oldest_backup": backups[-1]["created"] if backups else None,
            "newest_backup": backups[0]["created"] if backups else None
        }
    
    def create_pre_migration_backup(self, db_name: str = None) -> Tuple[bool, str]:
        """
        Create backup before migration.
        
        Args:
            db_name: Database name
            
        Returns:
            Tuple[bool, str]: (success, backup_file_path)
        """
        db_name = db_name or os.getenv("DB_NAME", "akiraforge")
        db_user = os.getenv("DB_USER", "akiraforge")
        db_host = os.getenv("DB_HOST", "localhost")
        db_password = os.getenv("DB_PASSWORD", "")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"pre_migration_{db_name}_{timestamp}.sql"
        
        try:
            pwd_arg = f" --password={db_password}" if db_password else ""
            cmd = (f"mysqldump -h {db_host} -u {db_user}{pwd_arg} "
                   f"--single-transaction --quick {db_name} > {backup_file}")
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and backup_file.exists():
                self.logger.info(f"✓ Pre-migration backup created: {backup_file}")
                return True, str(backup_file)
            else:
                self.logger.error(f"✗ Backup failed: {result.stderr}")
                return False, ""
        
        except Exception as e:
            self.logger.error(f"✗ Error creating backup: {e}")
            return False, ""
    
    def perform_rollback(self, backup_file: str, db_name: str = None) -> Tuple[bool, str]:
        """
        Perform rollback to backup.
        
        Args:
            backup_file: Path to backup file
            db_name: Database name
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        db_name = db_name or os.getenv("DB_NAME", "akiraforge")
        db_user = os.getenv("DB_USER", "akiraforge")
        db_host = os.getenv("DB_HOST", "localhost")
        db_password = os.getenv("DB_PASSWORD", "")
        
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                return False, f"Backup file not found: {backup_file}"
            
            pwd_arg = f" --password={db_password}" if db_password else ""
            cmd = (f"mysql -h {db_host} -u {db_user}{pwd_arg} "
                   f"{db_name} < {backup_file}")
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3600)
            
            if result.returncode == 0:
                self._record_rollback(backup_file, db_name, True)
                self.logger.info(f"✓ Rollback completed: {db_name}")
                return True, f"Successfully rolled back to {backup_path.name}"
            else:
                self._record_rollback(backup_file, db_name, False)
                self.logger.error(f"✗ Rollback failed: {result.stderr}")
                return False, f"Rollback failed: {result.stderr}"
        
        except subprocess.TimeoutExpired:
            self.logger.error("✗ Rollback timed out")
            return False, "Rollback timed out (greater than 1 hour)"
        except Exception as e:
            self.logger.error(f"✗ Error performing rollback: {e}")
            return False, str(e)
    
    def verify_backup(self, backup_file: str) -> Dict:
        """
        Verify backup integrity.
        
        Args:
            backup_file: Path to backup file
            
        Returns:
            Verification details
        """
        try:
            backup_path = Path(backup_file)
            
            if not backup_path.exists():
                return {"valid": False, "error": "File not found"}
            
            with open(backup_path, 'r') as f:
                content = f.read(1000)  # Read first 1000 chars
            
            checks = {
                "file_exists": backup_path.exists(),
                "file_size_mb": round(backup_path.stat().st_size / (1024 * 1024), 2),
                "has_mysqldump_header": "-- MySQL dump" in content,
                "has_create_table": "CREATE TABLE" in content,
                "is_readable": True
            }
            
            valid = all(checks.values())
            
            return {
                "valid": valid,
                "checks": checks,
                "file_size_mb": checks["file_size_mb"]
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def _record_rollback(self, backup_file: str, db_name: str, success: bool):
        """Record rollback event in history."""
        try:
            history = []
            if self.rollback_history_file.exists():
                with open(self.rollback_history_file, 'r') as f:
                    history = json.load(f)
            
            history.append({
                "timestamp": datetime.now().isoformat(),
                "backup_file": backup_file,
                "database": db_name,
                "success": success
            })
            
            with open(self.rollback_history_file, 'w') as f:
                json.dump(history, f, indent=2)
        
        except Exception as e:
            self.logger.error(f"Error recording rollback: {e}")
    
    def get_rollback_history(self) -> list:
        """Get rollback history."""
        try:
            if self.rollback_history_file.exists():
                with open(self.rollback_history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error reading history: {e}")
        
        return []
    
    def list_available_backups(self) -> list:
        """List available backup files."""
        try:
            backups = []
            for backup_file in sorted(self.backup_dir.glob("pre_migration_*.sql")):
                backups.append({
                    "filename": backup_file.name,
                    "path": str(backup_file),
                    "size_mb": round(backup_file.stat().st_size / (1024 * 1024), 2),
                    "created": datetime.fromtimestamp(
                        backup_file.stat().st_mtime
                    ).isoformat()
                })
            
            return sorted(backups, key=lambda x: x["created"], reverse=True)
        
        except Exception as e:
            self.logger.error(f"Error listing backups: {e}")
            return []
    
    def cleanup_old_backups(self, keep_count: int = 5):
        """Keep only most recent backups."""
        backups = sorted(
            self.backup_dir.glob("pre_migration_*.sql"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        for old_backup in backups[keep_count:]:
            try:
                old_backup.unlink()
                self.logger.info(f"Cleaned up old backup: {old_backup.name}")
            except Exception as e:
                self.logger.error(f"Error cleaning backup: {e}")

# Global instance
_global_rollback = None

def get_migration_rollback() -> MigrationRollback:
    """Get or create global rollback manager."""
    global _global_rollback
    if _global_rollback is None:
        _global_rollback = MigrationRollback()
    return _global_rollback
