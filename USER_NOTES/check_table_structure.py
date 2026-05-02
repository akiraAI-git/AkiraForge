#!/usr/bin/env python3
"""
Check forge_users table structure
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    import pymysql
except ImportError:
    print("ERROR: pymysql not installed")
    sys.exit(1)


def check_table_structure():
    """Check the actual structure of forge_users table"""
    
    try:
        conn = pymysql.connect(
            host=os.getenv('HOME_DB_HOST', '192.168.4.138'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'forge_user'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'akira_forge'),
            charset="utf8mb4"
        )
        
        cursor = conn.cursor()
        
        print("=" * 70)
        print("FORGE_USERS TABLE STRUCTURE")
        print("=" * 70)
        
        # Get table structure
        cursor.execute("DESCRIBE forge_users")
        columns = cursor.fetchall()
        
        print("\nColumns in forge_users table:")
        print("-" * 70)
        for col in columns:
            col_name = col[0]
            col_type = col[1]
            nullable = col[2]
            key = col[3] if col[3] else ""
            extra = col[5] if len(col) > 5 else ""
            
            print(f"  {col_name:<20} {col_type:<20} NULL={nullable}")
        
        # Check current admin user
        print("\n" + "-" * 70)
        print("Current admin user (if exists):")
        print("-" * 70)
        
        cursor.execute("SELECT * FROM forge_users WHERE username = 'admin'")
        admin = cursor.fetchone()
        
        if admin:
            # Get column names
            cursor.execute("DESCRIBE forge_users")
            col_names = [col[0] for col in cursor.fetchall()]
            
            print("\nAdmin user data:")
            for i, col_name in enumerate(col_names):
                if i < len(admin):
                    print(f"  {col_name:<20}: {admin[i]}")
        else:
            print("  No admin user found")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print()
    check_table_structure()
    print()
