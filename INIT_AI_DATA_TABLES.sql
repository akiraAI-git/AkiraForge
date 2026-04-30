-- ============================================================================
-- AKIRA FORGE - AI DATA SYSTEM DATABASE INITIALIZATION
-- ============================================================================
-- This script creates all tables needed for the dynamic AI column system.
-- Run this on your MySQL database (akira_forge) ONCE to initialize.
--
-- Database: akira_forge
-- Tables: ai_data_mapping, ai_data_1
-- ============================================================================

USE akira_forge;

-- ============================================================================
-- 1. AI DATA MAPPING TABLE
-- ============================================================================
-- Purpose: Registry that maps each AI to its storage location (table + column)
--
-- Columns:
--   id: Auto-increment primary key
--   ai_id: Unique ID of the generated AI (e.g., "surfinstructor")
--   table_name: Name of the table storing data (e.g., "ai_data_1")
--   column_name: Name of the column in that table (e.g., "ai_surfinstructor")
--   created_at: Timestamp when mapping was created
--
-- This table is ESSENTIAL - without it, the system cannot find where to store AI data.

CREATE TABLE IF NOT EXISTS ai_data_mapping (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique mapping ID',
    ai_id VARCHAR(255) NOT NULL UNIQUE COMMENT 'Generated AI unique identifier',
    table_name VARCHAR(255) NOT NULL COMMENT 'Table name where data is stored (ai_data_1, ai_data_2, etc)',
    column_name VARCHAR(60) NOT NULL COMMENT 'Column name in the table for this AI (max 60 chars)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'When this mapping was created',

    INDEX idx_ai_id (ai_id),
    INDEX idx_table_name (table_name)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='Maps generated AIs to their data storage locations';


-- ============================================================================
-- 2. FIRST AI DATA TABLE (ai_data_1)
-- ============================================================================
-- Purpose: Stores user-specific data for multiple AIs in dynamic columns
--
-- Base Columns:
--   id: Row identifier
--   user_id: Links data to a specific user (one row per user for all AIs)
--   created_at: When row was created
--   updated_at: When row was last modified
--
-- Dynamic Columns Added:
--   When a new AI is created, a column is added here:
--   - Column name: ai_[lowercased_ai_id]
--   - Column type: LONGTEXT (stores JSON data)
--   - Example: ai_surfinstructor, ai_travel_buddy, ai_coding_mentor
--
-- Maximum Columns:
--   MySQL limit: 4096 columns total
--   System columns: 4
--   AI data columns: up to 900 (by design choice in AIDataStore.py)
--   After 900 AI columns, system creates ai_data_2, ai_data_3, etc.
--
-- Data Format:
--   Each AI column stores JSON:
--   {
--     "ai_id": "surfinstructor",
--     "user_id": 1,
--     "interactions": [...],
--     "preferences": {...},
--     "metadata": {...}
--   }

CREATE TABLE IF NOT EXISTS ai_data_1 (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Row unique identifier',
    user_id INT NOT NULL COMMENT 'User ID - one row per user contains all their AI data',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'When this row was created',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last modified timestamp',

    INDEX idx_user_id (user_id),
    CONSTRAINT UNIQUE_user_id UNIQUE (user_id) COMMENT 'Only one row per user'
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci
COMMENT='Dynamic AI data storage - AI-specific columns are added here (up to 900)';


-- ============================================================================
-- 3. VERIFICATION QUERIES (Optional - for testing)
-- ============================================================================

-- Show all tables created
-- SELECT * FROM INFORMATION_SCHEMA.TABLES
-- WHERE TABLE_SCHEMA = 'akira_forge' AND TABLE_NAME LIKE 'ai_data%';

-- Check column count in ai_data_1
-- SELECT COUNT(*) as total_columns FROM INFORMATION_SCHEMA.COLUMNS
-- WHERE TABLE_SCHEMA = 'akira_forge' AND TABLE_NAME = 'ai_data_1';

-- Show current mappings
-- SELECT * FROM ai_data_mapping ORDER BY created_at DESC;

-- ============================================================================
-- DONE
-- ============================================================================
-- Tables created successfully!
--
-- Next steps:
--   1. Generate an AI using Akira Forge
--   2. The system will automatically:
--      - Create a column in ai_data_1
--      - Add a mapping entry
--      - Store user interactions
--   3. When ai_data_1 reaches 900 columns, ai_data_2 is created automatically
--
-- Monitoring:
--   - Check ai_data_mapping to see where each AI's data is stored
--   - Check ai_data_1, ai_data_2, etc. to see columns
--   - Use DESCRIBE ai_data_1 to see current columns
-- ============================================================================

