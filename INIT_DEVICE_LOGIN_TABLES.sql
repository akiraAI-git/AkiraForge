-- SQL INITIALIZATION SCRIPT FOR AKIRA FORGE v1.4.0
-- Run this after creating the database with existing schema
-- Command: mysql -u forge_user -p akira_forge < this_file.sql

-- ============================================================
-- TABLE 1: device_logins
-- ============================================================
-- Stores device-specific login tokens for "Remember me" feature
-- One token per user + device combination
-- Expires after 5 days

CREATE TABLE IF NOT EXISTS device_logins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    machine_uuid VARCHAR(255) NOT NULL,
    device_name VARCHAR(255),
    auth_token VARCHAR(255) NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Unique constraint: one token per user+device
    UNIQUE KEY unique_user_device (user_id, machine_uuid),

    -- Foreign key to users table
    CONSTRAINT fk_device_logins_user_id
        FOREIGN KEY (user_id)
        REFERENCES forge_users(id)
        ON DELETE CASCADE,

    -- Index for fast lookup
    INDEX idx_machine_uuid (machine_uuid),
    INDEX idx_auth_token (auth_token),
    INDEX idx_expires_at (expires_at),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- TABLE 2: user_profiles
-- ============================================================
-- Stores user profile information (bio, picture)
-- One record per user

CREATE TABLE IF NOT EXISTS user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    bio VARCHAR(500),
    profile_picture LONGBLOB,
    profile_picture_nonce VARBINARY(24),
    profile_picture_updated_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Foreign key to users table
    CONSTRAINT fk_user_profiles_user_id
        FOREIGN KEY (user_id)
        REFERENCES forge_users(id)
        ON DELETE CASCADE,

    -- Index for fast lookup
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- VERIFY TABLES CREATED
-- ============================================================
-- Run these to verify:
-- SELECT * FROM device_logins;
-- SELECT * FROM user_profiles;
-- DESCRIBE device_logins;
-- DESCRIBE user_profiles;

-- ============================================================
-- CLEANUP (Optional - for development testing only)
-- ============================================================
-- Uncomment these if you need to reset the tables during testing:
--
-- DROP TABLE IF EXISTS user_profiles;
-- DROP TABLE IF EXISTS device_logins;

-- ============================================================
-- EXAMPLE QUERIES
-- ============================================================

-- Example 1: Check device login
-- SELECT * FROM device_logins
-- WHERE user_id = 1 AND machine_uuid = 'your-uuid-here'
-- AND expires_at > NOW();

-- Example 2: Create device login
-- INSERT INTO device_logins (user_id, machine_uuid, device_name, auth_token, expires_at)
-- VALUES (1, 'uuid-123', 'DESKTOP-ABC', 'token-hash', DATE_ADD(NOW(), INTERVAL 5 DAY));

-- Example 3: Check expired tokens
-- SELECT * FROM device_logins WHERE expires_at < NOW();

-- Example 4: Delete expired tokens
-- DELETE FROM device_logins WHERE expires_at < NOW();

-- Example 5: Get user profile
-- SELECT * FROM user_profiles WHERE user_id = 1;

-- Example 6: Update user bio
-- UPDATE user_profiles SET bio = 'New bio text' WHERE user_id = 1;

-- ============================================================
-- MAINTENANCE PROCEDURES
-- ============================================================

-- Cleanup expired device logins (run this daily)
-- DELETE FROM device_logins WHERE expires_at < NOW();

-- ============================================================
-- END OF INITIALIZATION SCRIPT
-- ============================================================

COMMIT;

