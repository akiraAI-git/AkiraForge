-- ============================================================
-- AKIRA FORGE COMPLETE DATABASE INITIALIZATION
-- ============================================================
-- Date: April 27, 2026
-- Purpose: Initialize all required tables for the application
-- Run: mysql -u user -p database_name < this_file.sql
-- ============================================================

-- ============================================================
-- SECTION 1: USER MANAGEMENT TABLES
-- ============================================================

-- Users table (core authentication)
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User profiles
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Device logins (Remember me feature)
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
    INDEX idx_expires_at (expires_at),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User permissions/roles
CREATE TABLE IF NOT EXISTS user_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    permission_name VARCHAR(255) NOT NULL,
    granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    granted_by INT,
    
    UNIQUE KEY unique_user_permission (user_id, permission_name),
    CONSTRAINT fk_user_permissions_user_id
        FOREIGN KEY (user_id) REFERENCES forge_users(id) ON DELETE CASCADE,
    CONSTRAINT fk_user_permissions_granted_by
        FOREIGN KEY (granted_by) REFERENCES forge_users(id) ON DELETE SET NULL,
    
    INDEX idx_user_id (user_id),
    INDEX idx_permission_name (permission_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- SECTION 2: AUDIT & LOGGING TABLES
-- ============================================================

-- Audit logs (all actions)
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Failed login attempts
CREATE TABLE IF NOT EXISTS failed_login_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45),
    attempt_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_username (username),
    INDEX idx_ip_address (ip_address),
    INDEX idx_attempt_time (attempt_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Crash logs
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- SECTION 3: SESSION & METRICS TABLES
-- ============================================================

-- User sessions
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
    INDEX idx_is_active (is_active),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Session metrics
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Window performance tracking
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Feature usage tracking
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
    INDEX idx_feature_name (feature_name),
    INDEX idx_session_id (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Application metrics (comprehensive)
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Rate limiting logs
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- SECTION 4: APPLICATION SETTINGS & CONFIGURATION
-- ============================================================

-- Application settings
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
    INDEX idx_setting_key (setting_key),
    INDEX idx_is_global (is_global)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- SECTION 5: VAULT & SECURITY TABLES
-- ============================================================

-- Vault storage
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Vault access logs
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- SECTION 6: PROJECT & BUILDER TABLES
-- ============================================================

-- Projects
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
    CONSTRAINT fk_projects_last_modified_by
        FOREIGN KEY (last_modified_by) REFERENCES forge_users(id) ON DELETE SET NULL,
    
    INDEX idx_user_id (user_id),
    INDEX idx_project_name (project_name),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Project versions
CREATE TABLE IF NOT EXISTS project_versions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    version_number INT,
    version_data LONGTEXT,
    created_by INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(500),
    
    CONSTRAINT fk_project_versions_project_id
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    CONSTRAINT fk_project_versions_created_by
        FOREIGN KEY (created_by) REFERENCES forge_users(id) ON DELETE SET NULL,
    
    INDEX idx_project_id (project_id),
    INDEX idx_version_number (version_number),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- SECTION 7: NOTES TABLES
-- ============================================================

-- User notes
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
    INDEX idx_category (category),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- SECTION 8: PREMIUM & MARKETPLACE TABLES
-- ============================================================

-- User premium status
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Marketplace items
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
    INDEX idx_is_active (is_active),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User marketplace purchases
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
    INDEX idx_item_id (item_id),
    INDEX idx_purchase_date (purchase_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- SECTION 9: ADMIN & MANAGEMENT TABLES
-- ============================================================

-- Admin logs
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
    CONSTRAINT fk_admin_logs_target_user_id
        FOREIGN KEY (target_user_id) REFERENCES forge_users(id) ON DELETE SET NULL,
    
    INDEX idx_admin_id (admin_id),
    INDEX idx_target_user_id (target_user_id),
    INDEX idx_action (action),
    INDEX idx_action_time (action_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- SECTION 10: DEVICE INFO TABLE
-- ============================================================

-- Device information tracking
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
    INDEX idx_machine_uuid (machine_uuid),
    INDEX idx_trust_status (trust_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- SECTION 11: CREATE INDEXES FOR PERFORMANCE
-- ============================================================

-- Create additional performance indexes
ALTER TABLE audit_logs ADD FULLTEXT INDEX ft_action_details (action);
ALTER TABLE vault_files ADD FULLTEXT INDEX ft_file_name (file_name);
ALTER TABLE projects ADD FULLTEXT INDEX ft_project_name (project_name);
ALTER TABLE user_notes ADD FULLTEXT INDEX ft_note_content (note_content);

-- ============================================================
-- SECTION 12: VERIFY TABLES CREATED
-- ============================================================

-- Show all created tables
-- SHOW TABLES;

-- Count tables
-- SELECT COUNT(*) as total_tables FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = DATABASE();

-- ============================================================
-- COMPLETION
-- ============================================================

COMMIT;

-- All tables have been created successfully!
-- Total tables: 24
-- The database is now ready for use.

-- ============================================================
-- NOTES
-- ============================================================
-- - All tables use InnoDB for transaction support
-- - UTF-8 collation for international character support
-- - Foreign keys enforce referential integrity
-- - Indexes optimize query performance
-- - Timestamps track creation and modification
-- - Soft deletes can be implemented with status fields
-- - Additional tables can be added as features expand

-- ============================================================
-- END OF DATABASE INITIALIZATION
-- ============================================================
