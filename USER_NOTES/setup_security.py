#!/usr/bin/env python
import os
import sys
import platform
from pathlib import Path

def setup_security_system():
    print("=" * 70)
    print("AKIRA FORGE SECURITY & MIGRATION SYSTEM SETUP")
    print("=" * 70)
    
    print("\n[1/4] Initializing Audit Logger...")
    try:
        from core.audit_logger import get_audit_logger
        logger = get_audit_logger()
        key = logger.get_security_key()
        
        print(f"  ✓ Audit Logger initialized")
        print(f"  ✓ Security key: {key[:16]}...{key[-16:]}")
        print(f"  ✓ Logs location: {logger.log_dir}")
        
        logger.log_action(
            username="system",
            action="SECURITY_SETUP",
            details={"event": "Initialization"},
            is_important=True
        )
        print(f"  ✓ System initialization logged")
    except Exception as e:
        print(f"  ✗ Error initializing audit logger: {e}")
        return False
    
    print("\n[2/4] Setting up Host Security...")
    try:
        from core.host_security import HostSecurityManager
        
        info = HostSecurityManager.get_system_info()
        print(f"  ✓ OS: {info['os']}")
        print(f"  ✓ Hostname: {info['hostname']}")
        print(f"  ✓ Python: {info['python_version']}")
        
        HostSecurityManager.secure_config_files()
        print(f"  ✓ File permissions hardened")
        
        if platform.system() == "Windows":
            print(f"  ℹ Windows detected - Enabling DOS protection...")
            HostSecurityManager.enable_basic_dos_protection()
            print(f"  ✓ DOS protection enabled")
        
    except Exception as e:
        print(f"  ✗ Error setting up host security: {e}")
        return False
    
    print("\n[3/4] Initializing Database Migration Tools...")
    try:
        from tools.db_migration import DatabaseMigrationManager
        
        migrator = DatabaseMigrationManager()
        print(f"  ✓ Database Migration initialized")
        print(f"  ✓ Backup directory: {migrator.backup_dir}")
        
        mysql_version = migrator.get_mysql_version()
        if mysql_version:
            print(f"  ✓ MySQL found: {mysql_version}")
        else:
            print(f"  ℹ MySQL not detected (will be needed for migration)")
        
    except Exception as e:
        print(f"  ✗ Error initializing database migration: {e}")
        return False
    
    print("\n[4/4] Validating Safe Code Cleaner...")
    try:
        from tools.safe_code_cleaner import SafeCodeCleaner
        
        cleaner = SafeCodeCleaner(dry_run=True)
        print(f"  ✓ Safe Code Cleaner ready")
        print(f"  ✓ Use with dry_run=True first to preview changes")
        
    except Exception as e:
        print(f"  ✗ Error validating code cleaner: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("SETUP COMPLETE!")
    print("=" * 70)
    
    print("\nNEXT STEPS:")
    print("-" * 70)
    print("1. SECURITY KEY BACKUP:")
    print(f"   Location: {Path.home() / '.akiraforge' / '.audit_key'}")
    print("   Action: Back up this file to a safe location")
    print()
    print("2. CONFIGURE AUDIT LOGGING:")
    print("   - Integrate logging into login/admin operations")
    print("   - See SECURITY_MIGRATION_GUIDE.py for examples")
    print()
    print("3. DATABASE MIGRATION PREPARATION:")
    print("   - On Ubuntu machine: python tools/db_migration.py")
    print("   - Create backup and migration package")
    print("   - Transfer to target PC")
    print()
    print("4. FIREWALL CONFIGURATION:")
    print("   On target PC, run:")
    if platform.system() == "Windows":
        print("   netsh advfirewall firewall add rule name=\"MySQL\" dir=in action=allow protocol=tcp localport=3306")
    else:
        print("   sudo ufw allow 3306/tcp comment 'MySQL Database'")
    print()
    print("5. TEST AUDIT LOGGER:")
    print("   from core.audit_logger import get_audit_logger")
    print("   logger = get_audit_logger()")
    print("   logger.log_action('test_user', 'TEST_ACTION', is_important=True)")
    print()
    
    return True

def show_quick_reference():
    print("\n" + "=" * 70)
    print("QUICK REFERENCE")
    print("=" * 70)
    
    reference = """
AUDIT LOGGER:
  from core.audit_logger import get_audit_logger
  logger = get_audit_logger()
  logger.log_action('username', 'ACTION_NAME', {'detail': 'value'}, is_important=True)
  
  Unlock logs:
  logs = logger.get_important_logs(logger.get_security_key())

HOST SECURITY:
  from core.host_security import HostSecurityManager
  HostSecurityManager.harden_system()
  info = HostSecurityManager.get_system_info()

DATABASE MIGRATION:
  from tools.db_migration import DatabaseMigrationManager
  migrator = DatabaseMigrationManager()
  
  Backup: migrator.backup_database('db_name', 'user', 'host', 'password')
  Restore: migrator.restore_database(backup_file, 'db_name', 'user', 'host', 'password')
  Create package: migrator.create_migration_package('db_name', 'host', 'user', 'password')

SAFE CODE CLEANUP:
  from tools.safe_code_cleaner import SafeCodeCleaner
  cleaner = SafeCodeCleaner(dry_run=True)  # Preview changes
  cleaner.clean_directory('C:\\path\\to\\code')

LOG LOCATIONS:
  ~/.akiraforge/audit_logs/important_actions.log - Encrypted actions
  ~/.akiraforge/audit_logs/public_actions.log - Public actions
  ~/.akiraforge/db_backups/ - Database backups
  ~/.akiraforge/.audit_key - Security key (KEEP SAFE!)
    """
    print(reference)

if __name__ == "__main__":
    try:
        success = setup_security_system()
        
        if success:
            show_quick_reference()
            sys.exit(0)
        else:
            print("\n[ERROR] Setup failed. Check errors above.")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Setup interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
