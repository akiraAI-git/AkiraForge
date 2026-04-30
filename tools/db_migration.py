import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

class DatabaseMigrationManager:
    
    def __init__(self, backup_dir: Optional[str] = None):
        if backup_dir is None:
            backup_dir = str(Path.home() / ".akiraforge" / "db_backups")
        
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def get_mysql_version(self) -> Optional[str]:
        try:
            result = subprocess.run(
                ["mysql", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"[DB_MIGRATE] Error checking MySQL version: {e}")
            return None
    
    def backup_database(self, db_name: str, db_user: str, db_host: str = "localhost",
                       db_password: Optional[str] = None) -> Optional[Path]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"{db_name}_{timestamp}.sql"
        
        env = os.environ.copy()
        if db_password:
            env['MYSQL_PWD'] = db_password
        
        try:
            cmd = [
                "mysqldump",
                f"--host={db_host}",
                f"--user={db_user}",
                "--single-transaction",
                "--routines",
                "--triggers",
                db_name
            ]
            
            with open(backup_file, 'w') as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                    check=True
                )
            
            print(f"[DB_MIGRATE] Backup created: {backup_file}")
            return backup_file
        
        except subprocess.CalledProcessError as e:
            print(f"[DB_MIGRATE] Error creating backup: {e.stderr}")
            if backup_file.exists():
                backup_file.unlink()
            return None
        
        except Exception as e:
            print(f"[DB_MIGRATE] Error creating backup: {e}")
            if backup_file.exists():
                backup_file.unlink()
            return None
    
    def restore_database(self, backup_file: Path, db_name: str, db_user: str,
                        db_host: str = "localhost", db_password: Optional[str] = None) -> bool:
        
        if not backup_file.exists():
            print(f"[DB_MIGRATE] Backup file not found: {backup_file}")
            return False
        
        env = os.environ.copy()
        if db_password:
            env['MYSQL_PWD'] = db_password
        
        try:
            with open(backup_file, 'r') as f:
                cmd = [
                    "mysql",
                    f"--host={db_host}",
                    f"--user={db_user}",
                    db_name
                ]
                
                result = subprocess.run(
                    cmd,
                    stdin=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env,
                    check=True
                )
            
            print(f"[DB_MIGRATE] Database restored from {backup_file}")
            return True
        
        except subprocess.CalledProcessError as e:
            print(f"[DB_MIGRATE] Error restoring database: {e.stderr}")
            return False
        
        except Exception as e:
            print(f"[DB_MIGRATE] Error restoring database: {e}")
            return False
    
    def create_migration_package(self, db_name: str, source_host: str, source_user: str,
                                source_password: Optional[str] = None) -> Optional[Path]:
        
        print(f"[DB_MIGRATE] Creating migration package for {db_name}...")
        
        backup_file = self.backup_database(db_name, source_user, source_host, source_password)
        if not backup_file:
            return None
        
        migration_dir = self.backup_dir / f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        migration_dir.mkdir(exist_ok=True)
        
        import shutil
        shutil.copy(backup_file, migration_dir / "database.sql")
        
        config = {
            "database_name": db_name,
            "source_host": source_host,
            "created_at": datetime.now().isoformat(),
            "backup_file": "database.sql",
            "database_size": backup_file.stat().st_size,
            "instructions": {
                "step_1": "Transfer the migration package to the target machine",
                "step_2": "Extract the migration package",
                "step_3": "Create the database on the target machine",
                "step_4": "Run: restore_database(migration_dir / 'database.sql', db_name, db_user, target_host, target_password)",
                "step_5": "Test the database connection"
            }
        }
        
        with open(migration_dir / "migration.json", 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"[DB_MIGRATE] Migration package created: {migration_dir}")
        return migration_dir
    
    def list_backups(self) -> List[Path]:
        backups = list(self.backup_dir.glob("*.sql"))
        backups.sort(reverse=True)
        
        print(f"[DB_MIGRATE] Found {len(backups)} backup files:")
        for backup in backups:
            size_mb = backup.stat().st_size / (1024 * 1024)
            print(f"  - {backup.name} ({size_mb:.2f} MB)")
        
        return backups
    
    def get_database_info(self, db_name: str, db_user: str, db_host: str = "localhost",
                         db_password: Optional[str] = None) -> Optional[Dict]:
        
        env = os.environ.copy()
        if db_password:
            env['MYSQL_PWD'] = db_password
        
        try:
            cmd = [
                "mysql",
                f"--host={db_host}",
                f"--user={db_user}",
                "-e",
                "SELECT DATABASE(); SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = %s;",
                db_name
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                check=False
            )
            
            if result.returncode != 0:
                print(f"[DB_MIGRATE] Error getting database info: {result.stderr}")
                return None
            
            return {
                "database": db_name,
                "host": db_host,
                "user": db_user,
                "output": result.stdout
            }
        
        except Exception as e:
            print(f"[DB_MIGRATE] Error getting database info: {e}")
            return None
    
    def create_database(self, db_name: str, db_user: str, db_host: str = "localhost",
                       db_password: Optional[str] = None) -> bool:
        
        env = os.environ.copy()
        if db_password:
            env['MYSQL_PWD'] = db_password
        
        try:
            cmd = [
                "mysql",
                f"--host={db_host}",
                f"--user={db_user}",
                "-e",
                f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                check=True
            )
            
            print(f"[DB_MIGRATE] Database {db_name} created successfully")
            return True
        
        except subprocess.CalledProcessError as e:
            print(f"[DB_MIGRATE] Error creating database: {e.stderr}")
            return False
        
        except Exception as e:
            print(f"[DB_MIGRATE] Error creating database: {e}")
            return False
    
    def migration_checklist(self) -> str:
        checklist = """
[DATABASE MIGRATION CHECKLIST]

BEFORE MIGRATION:
  [ ] Backup source database
  [ ] Verify database integrity on source
  [ ] Check disk space on target machine
  [ ] Ensure MySQL is installed on target
  [ ] Verify network connectivity between machines
  [ ] Document current database configuration
  [ ] Test database restore on test machine first

DURING MIGRATION:
  [ ] Create migration package
  [ ] Transfer backup files securely
  [ ] Verify backup file integrity (checksum)
  [ ] Verify firewall rules allow database traffic
  [ ] Create new database on target machine
  [ ] Restore database from backup
  [ ] Verify data integrity after restore
  [ ] Update connection strings in application

AFTER MIGRATION:
  [ ] Test application connection to new database
  [ ] Verify all features work correctly
  [ ] Run smoke tests on critical features
  [ ] Check backups on new machine
  [ ] Monitor for errors/warnings
  [ ] Keep old backups for rollback capability
  [ ] Document any configuration changes
  [ ] Update documentation with new host information
  [ ] Test offline mode functionality
  [ ] Test user login and authentication

FIREWALL CONFIGURATION:
  On TARGET machine, ensure MySQL port (3306) is accessible:
    Windows: netsh advfirewall firewall add rule name="MySQL" dir=in action=allow protocol=tcp localport=3306
    Linux:   sudo ufw allow 3306/tcp comment "MySQL Database"

DATABASE REPLICATION (Optional - for live migration):
  [ ] Set up read replica on target
  [ ] Configure replication user and permissions
  [ ] Monitor replication lag
  [ ] Test failover
  [ ] Update application to point to new host
  [ ] Remove old host from configuration
        """
        return checklist
