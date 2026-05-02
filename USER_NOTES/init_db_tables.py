#!/usr/bin/env python3
"""
Database Table Initialization
=============================

Creates required database tables for the application.
Run this script to initialize the database schema.

Date: April 26, 2026
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import pymysql
except ImportError:
    logger.error("pymysql not installed. Install with: pip install pymysql")
    sys.exit(1)


def get_connection():
    """Get database connection."""
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'akiraforge'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'akiraforge')
    )


def create_metrics_table(cursor):
    """Create application metrics table."""
    sql = '''
    CREATE TABLE IF NOT EXISTS tablestoadd26_4 (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        session_id VARCHAR(255),
        metric_type VARCHAR(100) NOT NULL,
        metric_name VARCHAR(255) NOT NULL,
        metric_value FLOAT,
        window_type VARCHAR(100),
        launch_time_ms FLOAT,
        feature_name VARCHAR(255),
        total_count INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_username (username),
        INDEX idx_session_id (session_id),
        INDEX idx_metric_type (metric_type),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    '''
    
    try:
        cursor.execute(sql)
        logger.info("✓ Created table: tablestoadd26_4 (Application Metrics)")
    except pymysql.Error as e:
        logger.error(f"Error creating tablestoadd26_4: {e}")
        raise


def create_window_performance_table(cursor):
    """Create window performance tracking table."""
    sql = '''
    CREATE TABLE IF NOT EXISTS window_performance (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        window_type VARCHAR(100) NOT NULL,
        launch_time_ms FLOAT NOT NULL,
        creation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_username (username),
        INDEX idx_window_type (window_type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    '''
    
    try:
        cursor.execute(sql)
        logger.info("✓ Created table: window_performance")
    except pymysql.Error as e:
        logger.error(f"Error creating window_performance: {e}")
        raise


def create_feature_usage_table(cursor):
    """Create feature usage tracking table."""
    sql = '''
    CREATE TABLE IF NOT EXISTS feature_usage (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        feature_name VARCHAR(255) NOT NULL,
        access_count INT DEFAULT 1,
        first_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        session_id VARCHAR(255),
        INDEX idx_username (username),
        INDEX idx_feature_name (feature_name),
        INDEX idx_session_id (session_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    '''
    
    try:
        cursor.execute(sql)
        logger.info("✓ Created table: feature_usage")
    except pymysql.Error as e:
        logger.error(f"Error creating feature_usage: {e}")
        raise


def create_session_metrics_table(cursor):
    """Create session metrics table."""
    sql = '''
    CREATE TABLE IF NOT EXISTS session_metrics (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        session_id VARCHAR(255) NOT NULL UNIQUE,
        start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        end_time DATETIME,
        duration_seconds FLOAT,
        total_windows_opened INT DEFAULT 0,
        total_features_accessed INT DEFAULT 0,
        role VARCHAR(50),
        qt_framework VARCHAR(50),
        INDEX idx_username (username),
        INDEX idx_session_id (session_id),
        INDEX idx_start_time (start_time)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    '''
    
    try:
        cursor.execute(sql)
        logger.info("✓ Created table: session_metrics")
    except pymysql.Error as e:
        logger.error(f"Error creating session_metrics: {e}")
        raise


def create_crash_logs_table(cursor):
    """Create crash logs table."""
    sql = '''
    CREATE TABLE IF NOT EXISTS crash_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255),
        session_id VARCHAR(255),
        error_type VARCHAR(255) NOT NULL,
        error_message LONGTEXT NOT NULL,
        traceback LONGTEXT,
        crash_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        recovered BOOLEAN DEFAULT FALSE,
        INDEX idx_username (username),
        INDEX idx_error_type (error_type),
        INDEX idx_crash_time (crash_time)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    '''
    
    try:
        cursor.execute(sql)
        logger.info("✓ Created table: crash_logs")
    except pymysql.Error as e:
        logger.error(f"Error creating crash_logs: {e}")
        raise


def create_application_settings_table(cursor):
    """Create application settings table."""
    sql = '''
    CREATE TABLE IF NOT EXISTS application_settings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        setting_key VARCHAR(255) NOT NULL,
        setting_value LONGTEXT,
        setting_type VARCHAR(50),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY unique_user_setting (username, setting_key),
        INDEX idx_username (username),
        INDEX idx_setting_key (setting_key)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    '''
    
    try:
        cursor.execute(sql)
        logger.info("✓ Created table: application_settings")
    except pymysql.Error as e:
        logger.error(f"Error creating application_settings: {e}")
        raise


def initialize_database():
    """Initialize all database tables."""
    try:
        logger.info("Connecting to database...")
        conn = get_connection()
        cursor = conn.cursor()
        
        logger.info("Creating tables...")
        create_metrics_table(cursor)
        create_window_performance_table(cursor)
        create_feature_usage_table(cursor)
        create_session_metrics_table(cursor)
        create_crash_logs_table(cursor)
        create_application_settings_table(cursor)
        
        conn.commit()
        logger.info("✓ All tables created successfully!")
        cursor.close()
        conn.close()
        
        return True
    
    except pymysql.Error as e:
        logger.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Database Table Initialization")
    logger.info("=" * 60)
    
    success = initialize_database()
    
    if success:
        logger.info("=" * 60)
        logger.info("✓ Database initialization completed successfully!")
        logger.info("=" * 60)
        sys.exit(0)
    else:
        logger.error("=" * 60)
        logger.error("✗ Database initialization failed!")
        logger.error("=" * 60)
        sys.exit(1)
