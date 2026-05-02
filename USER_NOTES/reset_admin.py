#!/usr/bin/env python3
"""
Reset admin user - delete old and create new
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    import pymysql
    import pymysql.cursors
    import bcrypt
except ImportError as e:
    print(f"ERROR: Missing package - {e}")
    sys.exit(1)


def reset_admin():
    """Reset admin user"""
    
    print("\n" + "=" * 70)
    print("RESETTING ADMIN USER")
    print("=" * 70)
    
    try:
        conn = pymysql.connect(
            host=os.getenv('HOME_DB_HOST', '192.168.4.138'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'forge_user'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'akira_forge'),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = conn.cursor()
        
        print("\nConnected to database!")
        print("\n1. Deleting old admin user...")
        cursor.execute("DELETE FROM forge_users WHERE username = 'admin'")
        deleted = cursor.rowcount
        print(f"   ✓ Deleted {deleted} old admin record(s)")
        
        print("\n2. Creating new admin user...")
        username = "admin"
        password = "treverdb"
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        sql = "INSERT INTO forge_users (username, password_hash, role) VALUES (%s, %s, 'admin')"
        cursor.execute(sql, (username, password_hash))
        conn.commit()
        print(f"   ✓ Created new admin user")
        
        print("\n" + "=" * 70)
        print("✅ LOGIN CREDENTIALS")
        print("=" * 70)
        print(f"\nUsername: admin")
        print(f"Password: treverdb")
        print(f"\nYou can now login!\n")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = reset_admin()
    
    # Self-delete after running
    import os as os2
    try:
        os2.remove(__file__)
    except:
        pass
    
    sys.exit(0 if success else 1)
