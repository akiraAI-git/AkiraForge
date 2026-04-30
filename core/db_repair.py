from core.db import get_db_connection

EXPECTED_TABLES = {
    "forge_users": {
        "id": "INT AUTO_INCREMENT PRIMARY KEY",
        "username": "VARCHAR(255) NOT NULL UNIQUE",
        "password_hash": "VARCHAR(255) NOT NULL",
        "role": "ENUM('admin','user') DEFAULT 'user'",
        "failed_attempts": "INT DEFAULT 0",
        "locked_until": "DATETIME NULL",
        "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP"
    },

    "signup_requests": {
        "id": "INT AUTO_INCREMENT PRIMARY KEY",
        "name": "VARCHAR(255)",
        "email": "VARCHAR(255)",
        "desired_username": "VARCHAR(255)",
        "desired_password_hash": "VARCHAR(255)",
        "message": "TEXT",
        "verification_answer": "TEXT",
        "status": "ENUM('pending','approved','declined') DEFAULT 'pending'",
        "email_sent": "BOOLEAN DEFAULT FALSE",
        "submitted_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
        "reviewed_at": "DATETIME NULL"
    },

    "ip_locks": {
        "id": "INT AUTO_INCREMENT PRIMARY KEY",
        "ip_address": "VARCHAR(255) NOT NULL",
        "locked": "BOOLEAN DEFAULT FALSE",
        "reason": "TEXT",
        "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP"
    },

    "user_flags": {
        "id": "INT AUTO_INCREMENT PRIMARY KEY",
        "username": "VARCHAR(255) NOT NULL",
        "flag_count": "INT DEFAULT 0",
        "fully_flagged": "BOOLEAN DEFAULT FALSE",
        "last_ip": "VARCHAR(255)",
        "updated_at": "DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
    },

    "access_pleas": {
        "id": "INT AUTO_INCREMENT PRIMARY KEY",
        "username": "VARCHAR(255) NOT NULL",
        "claimed_identity": "VARCHAR(255)",
        "reason": "TEXT",
        "verification_answer": "TEXT",
        "ip_address": "VARCHAR(255)",
        "submitted_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
        "reviewed": "BOOLEAN DEFAULT FALSE",
        "approved": "BOOLEAN NULL"
    }
    ,
    "notes": {
        "id": "INT AUTO_INCREMENT PRIMARY KEY",
        "title": "LONGBLOB",
        "body": "LONGBLOB",
        "nonce_title": "VARBINARY(24)",
        "nonce_body": "VARBINARY(24)",
        "tags": "TEXT",
        "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
        "updated_at": "DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
    },
    "generated_apps": {
        "id": "INT AUTO_INCREMENT PRIMARY KEY",
        "app_name": "VARCHAR(255) NOT NULL",
        "user_id": "INT NOT NULL DEFAULT 1",
        "user_ip": "VARCHAR(255) DEFAULT 'unknown'",
        "notes": "TEXT",
        "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP"
    },
    "ai_data_mapping": {
        "id": "INT AUTO_INCREMENT PRIMARY KEY",
        "ai_id": "VARCHAR(255) NOT NULL UNIQUE",
        "table_name": "VARCHAR(255) NOT NULL",
        "column_name": "VARCHAR(255) NOT NULL",
        "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP"
    },
     "ai_data_1": {
         "id": "INT AUTO_INCREMENT PRIMARY KEY",
         "user_id": "INT NOT NULL",
         "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
         "updated_at": "DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
     },
     "device_logins": {
         "id": "INT AUTO_INCREMENT PRIMARY KEY",
         "user_id": "INT NOT NULL",
         "machine_uuid": "VARCHAR(255) NOT NULL",
         "device_name": "VARCHAR(255)",
         "auth_token": "VARCHAR(255) NOT NULL",
         "expires_at": "DATETIME NOT NULL",
         "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
         "last_accessed": "DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
     },
     "user_profiles": {
         "id": "INT AUTO_INCREMENT PRIMARY KEY",
         "user_id": "INT NOT NULL UNIQUE",
         "bio": "VARCHAR(500)",
         "profile_picture": "LONGBLOB",
         "profile_picture_nonce": "VARBINARY(24)",
         "profile_picture_updated_at": "DATETIME",
         "created_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
         "updated_at": "DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
     }
}

def repair_database():
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SHOW TABLES")
    existing_tables = {list(row.values())[0] for row in cursor.fetchall()}

    for table_name, columns in EXPECTED_TABLES.items():

        if table_name not in existing_tables:
            print(f"[DB-REPAIR] Creating missing table: {table_name}")

            column_defs = ", ".join([f"{col} {definition}" for col, definition in columns.items()])
            cursor.execute(f"CREATE TABLE {table_name} ({column_defs})")
            db.commit()
            continue

        cursor.execute(f"DESCRIBE {table_name}")
        existing_cols = {row["Field"] for row in cursor.fetchall()}

        for col_name, col_def in columns.items():
            if col_name not in existing_cols:
                print(f"[DB-REPAIR] Adding missing column '{col_name}' to '{table_name}'")
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}")
                db.commit()

    print("[DB-REPAIR] Database schema verified and repaired.")

    cleanup_expired_device_logins(db, cursor)

    cursor.close()
    db.close()

def cleanup_expired_device_logins(db, cursor):
    try:
        cursor.execute("DELETE FROM device_logins WHERE expires_at < NOW()")
        deleted_count = cursor.rowcount
        if deleted_count > 0:
            print(f"[DB-REPAIR] Cleaned up {deleted_count} expired device login tokens")
        db.commit()
    except Exception as e:
        print(f"[DB-REPAIR] Error cleaning expired tokens: {e}")
