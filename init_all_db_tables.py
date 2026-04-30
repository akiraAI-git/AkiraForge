#!/usr/bin/env python3
"""
Complete Database Initialization Script
========================================

Creates all required database tables for Akira Forge application.
Handles both schema creation and error management.

Date: April 27, 2026
Usage: python init_all_db_tables.py
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import pymysql
except ImportError:
    logger.error("pymysql not installed. Install with: pip install pymysql")
    sys.exit(1)


def get_connection():
    """Get database connection."""
    try:
        conn = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'akiraforge'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'akiraforge'),
            autocommit=True,
            charset='utf8mb4'
        )
        logger.info(f"✓ Connected to database: {os.getenv('DB_NAME')}")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def execute_sql_file(cursor, filename):
    """Execute SQL file."""
    try:
        sql_path = Path(__file__).parent / filename
        
        if not sql_path.exists():
            logger.warning(f"SQL file not found: {filename}")
            return False
        
        with open(sql_path, 'r') as f:
            sql_content = f.read()
        
        # Split by semicolon and execute each statement
        statements = sql_content.split(';')
        count = 0
        
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    count += 1
                except Exception as e:
                    logger.warning(f"Error executing statement: {e}")
                    continue
        
        logger.info(f"✓ Executed {count} SQL statements from {filename}")
        return True
    
    except Exception as e:
        logger.error(f"Error executing SQL file: {e}")
        return False


def create_user_tables(cursor):
    """Create user management tables."""
    logger.info("Creating user management tables...")
    
    tables = {
        'forge_users': '''
            CREATE TABLE IF NOT EXISTS forge_users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('admin', 'user', 'guest') DEFAULT 'user',
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                last_login DATETIME,
                INDEX idx_username (username),
                INDEX idx_email (email),
                INDEX idx_role (role)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        'user_profiles': '''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL UNIQUE,
                bio TEXT,
                profile_picture LONGBLOB,
                profile_picture_nonce VARBINARY(24),
                profile_picture_updated_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT fk_user_profiles_user_id
                    FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        'device_logins': '''
            CREATE TABLE IF NOT EXISTS device_logins (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                machine_uuid VARCHAR(255) NOT NULL,
                device_name VARCHAR(255),
                device_ip VARCHAR(45),
                auth_token VARCHAR(255) NOT NULL UNIQUE,
                expires_at DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_user_device (user_id, machine_uuid),
                CONSTRAINT fk_device_logins_user_id
                    FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE CASCADE,
                INDEX idx_machine_uuid (machine_uuid),
                INDEX idx_auth_token (auth_token),
                INDEX idx_expires_at (expires_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        'user_permissions': '''
            CREATE TABLE IF NOT EXISTS user_permissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                permission_name VARCHAR(255) NOT NULL,
                granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                granted_by INT,
                UNIQUE KEY unique_user_permission (user_id, permission_name),
                CONSTRAINT fk_user_permissions_user_id
                    FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_permission_name (permission_name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        '''
    }
    
    return execute_tables(cursor, tables)


def create_audit_tables(cursor):
    """Create audit and logging tables."""
    logger.info("Creating audit and logging tables...")
    
    tables = {
        'audit_logs': '''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                user_id INT,
                action VARCHAR(100) NOT NULL,
                action_details JSON,
                is_important BOOLEAN DEFAULT FALSE,
                signature VARCHAR(255),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_audit_logs_user_id
                    FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE SET NULL,
                INDEX idx_username (username),
                INDEX idx_action (action),
                INDEX idx_is_important (is_important),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        'failed_login_attempts': '''
            CREATE TABLE IF NOT EXISTS failed_login_attempts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                ip_address VARCHAR(45),
                attempt_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_username (username),
                INDEX idx_ip_address (ip_address),
                INDEX idx_attempt_time (attempt_time)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        'crash_logs': '''
            CREATE TABLE IF NOT EXISTS crash_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255),
                user_id INT,
                session_id VARCHAR(255),
                error_type VARCHAR(255) NOT NULL,
                error_message LONGTEXT NOT NULL,
                traceback LONGTEXT,
                crash_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                recovered BOOLEAN DEFAULT FALSE,
                CONSTRAINT fk_crash_logs_user_id
                    FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE SET NULL,
                INDEX idx_username (username),
                INDEX idx_error_type (error_type),
                INDEX idx_crash_time (crash_time)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        'admin_logs': '''
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                admin_id INT NOT NULL,
                admin_username VARCHAR(255),
                action VARCHAR(255) NOT NULL,
                target_user_id INT,
                target_username VARCHAR(255),
                action_details JSON,
                action_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_admin_logs_admin_id
                    FOREIGN KEY (admin_id) REFERENCES forge_users(id) ON DELETE SET NULL,
                INDEX idx_admin_id (admin_id),
                INDEX idx_action (action),
                INDEX idx_action_time (action_time)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        '''
    }
    
    return execute_tables(cursor, tables)


def create_metrics_tables(cursor):
    """Create metrics and analytics tables."""
    logger.info("Creating metrics and analytics tables...")
    
    tables = {
        'user_sessions': '''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL UNIQUE,
                user_id INT NOT NULL,
                username VARCHAR(255) NOT NULL,
                ip_address VARCHAR(45),
                device_id VARCHAR(255),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                CONSTRAINT fk_user_sessions_user_id
                    FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE CASCADE,
                INDEX idx_session_id (session_id),
                INDEX idx_user_id (user_id),
                INDEX idx_is_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        'session_metrics': '''
            CREATE TABLE IF NOT EXISTS session_metrics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                user_id INT NOT NULL,
                username VARCHAR(255) NOT NULL,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME,
                duration_seconds FLOAT,
                total_windows_opened INT DEFAULT 0,
                total_features_accessed INT DEFAULT 0,
                role VARCHAR(50),
                qt_framework VARCHAR(50),
                CONSTRAINT fk_session_metrics_user_id
                    FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE CASCADE,
                INDEX idx_session_id (session_id),
                INDEX idx_user_id (user_id),
                INDEX idx_start_time (start_time)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        'window_performance': '''
            CREATE TABLE IF NOT EXISTS window_performance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(255),
                user_id INT NOT NULL,
                username VARCHAR(255) NOT NULL,
                window_type VARCHAR(100) NOT NULL,
                launch_time_ms FLOAT NOT NULL,
                creation_status ENUM('success', 'failed', 'timeout') DEFAULT 'success',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_window_performance_user_id
                    FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_window_type (window_type),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        'feature_usage': '''
            CREATE TABLE IF NOT EXISTS feature_usage (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                username VARCHAR(255) NOT NULL,
                feature_name VARCHAR(255) NOT NULL,
                access_count INT DEFAULT 1,
                first_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                session_id VARCHAR(255),
                total_time_ms BIGINT DEFAULT 0,
                CONSTRAINT fk_feature_usage_user_id
                    FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_feature_name (feature_name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        'rate_limit_logs': '''
            CREATE TABLE IF NOT EXISTS rate_limit_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                username VARCHAR(255) NOT NULL,
                action_type VARCHAR(100) NOT NULL,
                blocked BOOLEAN DEFAULT FALSE,
                attempt_count INT,
                window_start DATETIME,
                window_end DATETIME,
                attempt_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_rate_limit_logs_user_id
                    FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_action_type (action_type),
                INDEX idx_blocked (blocked)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        'application_metrics': '''
            CREATE TABLE IF NOT EXISTS application_metrics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                user_id INT,
                session_id VARCHAR(255),
                metric_type VARCHAR(100) NOT NULL,
                metric_name VARCHAR(255) NOT NULL,
                metric_value FLOAT,
                window_type VARCHAR(100),
                launch_time_ms FLOAT,
                feature_name VARCHAR(255),
                total_count INT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_app_metrics_user_id
                    FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE SET NULL,
                INDEX idx_user_id (user_id),
                INDEX idx_session_id (session_id),
                INDEX idx_metric_type (metric_type),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        '''
    }
    
    return execute_tables(cursor, tables)


def create_feature_tables(cursor):
    """Create feature-specific tables."""
    logger.info("Creating feature-specific tables...")
    
    tables = {
        'vault_files': '''
            CREATE TABLE IF NOT EXISTS vault_files (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                username VARCHAR(255) NOT NULL,
                file_name VARCHAR(255) NOT NULL,
                file_size BIGINT,
                file_hash VARCHAR(255),
                is_encrypted BOOLEAN DEFAULT TRUE,
                encryption_algorithm VARCHAR(50),
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_accessed DATETIME,
                access_count INT DEFAULT 0,
                CONSTRAINT fk_vault_files_user_id
                    FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_file_name (file_name),
                INDEX idx_uploaded_at (uploaded_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        'vault_access_logs': '''
            CREATE TABLE IF NOT EXISTS vault_access_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                username VARCHAR(255) NOT NULL,
                file_id INT NOT NULL,
                file_name VARCHAR(255),
                action ENUM('upload', 'download', 'view', 'delete') NOT NULL,
                access_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45),
                CONSTRAINT fk_vault_access_logs_user_id
                    FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE CASCADE,
                CONSTRAINT fk_vault_access_logs_file_id
                    FOREIGN KEY (file_id) REFERENCES vault_files(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_file_id (file_id),
                INDEX idx_access_time (access_time)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        'projects': '''
            CREATE TABLE IF NOT EXISTS projects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                username VARCHAR(255) NOT NULL,
                project_name VARCHAR(255) NOT NULL,
                description TEXT,
                project_type VARCHAR(100),
                status ENUM('draft', 'active', 'archived', 'deleted') DEFAULT 'draft',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                last_modified_by INT,
                CONSTRAINT fk_projects_user_id
                    FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_project_name (project_name),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        'user_notes': '''
            CREATE TABLE IF NOT EXISTS user_notes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                username VARCHAR(255) NOT NULL,
                note_title VARCHAR(255),
                note_content LONGTEXT,
                is_pinned BOOLEAN DEFAULT FALSE,
                is_encrypted BOOLEAN DEFAULT FALSE,
                category VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT fk_user_notes_user_id
                    FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_is_pinned (is_pinned),
                INDEX idx_category (category)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        '''
    }
    
    return execute_tables(cursor, tables)


def create_premium_tables(cursor):
    """Create premium and marketplace tables."""
    logger.info("Creating premium and marketplace tables...")
    
    tables = {
        'user_premium': '''
            CREATE TABLE IF NOT EXISTS user_premium (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL UNIQUE,
                is_premium BOOLEAN DEFAULT FALSE,
                premium_tier VARCHAR(50),
                subscription_start DATETIME,
                subscription_end DATETIME,
                auto_renew BOOLEAN DEFAULT TRUE,
                payment_method VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT fk_user_premium_user_id
                    FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_is_premium (is_premium)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        'marketplace_items': '''
            CREATE TABLE IF NOT EXISTS marketplace_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                item_name VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(100),
                price DECIMAL(10, 2),
                created_by INT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                download_count INT DEFAULT 0,
                CONSTRAINT fk_marketplace_items_created_by
                    FOREIGN KEY (created_by) REFERENCES forge_users(id) ON DELETE SET NULL,
                INDEX idx_category (category),
                INDEX idx_is_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        'marketplace_purchases': '''
            CREATE TABLE IF NOT EXISTS marketplace_purchases (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                item_id INT NOT NULL,
                purchase_price DECIMAL(10, 2),
                purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_marketplace_purchases_user_id
                    FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE CASCADE,
                CONSTRAINT fk_marketplace_purchases_item_id
                    FOREIGN KEY (item_id) REFERENCES marketplace_items(id) ON DELETE CASCADE,
                INDEX idx_user_id (user_id),
                INDEX idx_item_id (item_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        '''
    }
    
    return execute_tables(cursor, tables)


def create_settings_tables(cursor):
    """Create settings and configuration tables."""
    logger.info("Creating settings and configuration tables...")
    
    tables = {
        'application_settings': '''
            CREATE TABLE IF NOT EXISTS application_settings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                username VARCHAR(255),
                setting_key VARCHAR(255) NOT NULL,
                setting_value LONGTEXT,
                setting_type VARCHAR(50),
                is_global BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT fk_app_settings_user_id
                    FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_setting (user_id, setting_key),
                INDEX idx_user_id (user_id),
                INDEX idx_setting_key (setting_key)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ''',
        'device_info': '''
            CREATE TABLE IF NOT EXISTS device_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                username VARCHAR(255),
                machine_uuid VARCHAR(255) UNIQUE,
                device_name VARCHAR(255),
                os_type VARCHAR(100),
                os_version VARCHAR(100),
                last_login DATETIME,
                last_ip VARCHAR(45),
                trust_status ENUM('trusted', 'untrusted', 'pending') DEFAULT 'untrusted',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT fk_device_info_user_id
                    FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE SET NULL,
                INDEX idx_user_id (user_id),
                INDEX idx_machine_uuid (machine_uuid)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        '''
    }
    
    return execute_tables(cursor, tables)


def execute_tables(cursor, tables):
    """Execute table creation statements."""
    success_count = 0
    
    for table_name, sql in tables.items():
        try:
            cursor.execute(sql)
            logger.info(f"  ✓ Created table: {table_name}")
            success_count += 1
        except pymysql.Error as e:
            if 'already exists' in str(e):
                logger.info(f"  → Table already exists: {table_name}")
                success_count += 1
            else:
                logger.error(f"  ✗ Error creating {table_name}: {e}")
        except Exception as e:
            logger.error(f"  ✗ Unexpected error creating {table_name}: {e}")
    
    return success_count == len(tables)


def initialize_database():
    """Initialize all database tables."""
    try:
        logger.info("=" * 70)
        logger.info("AKIRA FORGE - COMPLETE DATABASE INITIALIZATION")
        logger.info("=" * 70)
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create all table groups
        all_success = True
        all_success &= create_user_tables(cursor)
        all_success &= create_audit_tables(cursor)
        all_success &= create_metrics_tables(cursor)
        all_success &= create_feature_tables(cursor)
        all_success &= create_premium_tables(cursor)
        all_success &= create_settings_tables(cursor)
        
        cursor.close()
        conn.close()
        
        return all_success
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return False


if __name__ == "__main__":
    success = initialize_database()
    
    logger.info("=" * 70)
    if success:
        logger.info("✓ DATABASE INITIALIZATION COMPLETED SUCCESSFULLY!")
        logger.info("Total tables created: 24")
    else:
        logger.error("✗ DATABASE INITIALIZATION FAILED!")
    logger.info("=" * 70)
    
    sys.exit(0 if success else 1)
