#!/usr/bin/env python3
"""
Direct admin password update script
Updates the admin user password hash directly
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
    print("Install with: pip install pymysql bcrypt")
    sys.exit(1)


def update_admin_password():
    """Directly update admin user password"""
    
    print("\n" + "=" * 70)
    print("ADMIN PASSWORD UPDATE")
    print("=" * 70)
    
    username = "admin"
    password = "treverdb"
    
    print(f"\nUsername: {username}")
    print(f"New Password: {password}")
    
    try:
        print("\nConnecting to database...")
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
        print("✓ Connected!")
        
        # Hash the password
        print(f"\nGenerating bcrypt hash...")
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        print(f"✓ Hash generated")
        
        # Update the admin user
        print(f"\nUpdating admin user password...")
        sql = "UPDATE forge_users SET password_hash = %s WHERE username = %s"
        cursor.execute(sql, (password_hash, username))
        conn.commit()
        
        print(f"✓ Password updated!")
        
        # Verify
        print(f"\nVerifying update...")
        cursor.execute("SELECT username, role, password_hash FROM forge_users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user:
            print(f"✓ Admin user confirmed:")
            print(f"   Username: {user['username']}")
            print(f"   Role: {user['role']}")
            print(f"   Password Hash: SET ✓")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ LOGIN CREDENTIALS")
        print("=" * 70)
        print(f"\nUsername: admin")
        print(f"Password: treverdb")
        print("\nRun: python main.py\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = update_admin_password()
    sys.exit(0 if success else 1)
