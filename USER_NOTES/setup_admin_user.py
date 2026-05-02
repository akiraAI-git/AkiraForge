#!/usr/bin/env python3
"""
Admin User Setup Script
Creates or updates the admin user with password hashing
"""

import os
import sys
import bcrypt
from dotenv import load_dotenv

# Load environment
load_dotenv()

try:
    import pymysql
except ImportError:
    print("ERROR: pymysql not installed. Install with: pip install pymysql")
    sys.exit(1)


def get_db_host():
    """Get database host using same logic as db.py"""
    try:
        from core.location_detector import detect_location
        location = detect_location()
        
        HOME_DB_HOST = os.getenv("HOME_DB_HOST", "192.168.4.138")
        OFFICE_DB_HOST = os.getenv("OFFICE_DB_HOST", "172.19.170.75")
        
        if location == "home":
            host = HOME_DB_HOST
            print(f"[INFO] Location detected: HOME -> Using host: {host}")
        elif location == "office":
            host = OFFICE_DB_HOST
            print(f"[INFO] Location detected: OFFICE -> Using host: {host}")
        else:
            host = HOME_DB_HOST
            print(f"[INFO] Location UNKNOWN -> Using HOME host: {host}")
        
        return host
    except Exception as e:
        # Fallback to explicit HOST env var or default
        host = os.getenv('DB_HOST', '192.168.4.138')
        print(f"[INFO] Using DB_HOST from environment: {host}")
        return host


def get_connection():
    """Get database connection."""
    db_host = get_db_host()
    
    return pymysql.connect(
        host=db_host,
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'forge_user'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'akira_forge')
    )


def create_admin_user():
    """Create or update admin user with password."""
    
    username = "admin"
    password = "treverdb"
    email = "akiraforge@outlook.com"
    
    # Hash the password
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    print("=" * 60)
    print("ADMIN USER SETUP")
    print("=" * 60)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Email: {email}")
    print(f"Role: admin")
    print("=" * 60)
    
    try:
        print("\nConnecting to database...")
        conn = get_connection()
        cursor = conn.cursor()
        
        print("Connected! Setting up admin user...")
        
        # Check if admin already exists
        cursor.execute("SELECT id FROM forge_users WHERE username = %s", (username,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"Admin user '{username}' already exists. Updating password...")
            # Try to update with email column, if that fails, update without it
            try:
                sql = """UPDATE forge_users 
                         SET password_hash = %s, email = %s, is_active = TRUE, role = 'admin'
                         WHERE username = %s"""
                cursor.execute(sql, (password_hash, email, username))
                print("  ✓ Updated password, email, and role")
            except pymysql.Error as e:
                if "Unknown column 'email'" in str(e):
                    print("  Note: email column not available, updating password and role only")
                    sql = """UPDATE forge_users 
                             SET password_hash = %s, is_active = TRUE, role = 'admin'
                             WHERE username = %s"""
                    cursor.execute(sql, (password_hash, username))
                    print("  ✓ Updated password and role")
                else:
                    raise
        else:
            print(f"Creating new admin user '{username}'...")
            # Try to insert with email, if that fails, insert without it
            try:
                sql = """INSERT INTO forge_users 
                         (username, email, password_hash, role, is_active, is_verified)
                         VALUES (%s, %s, %s, 'admin', TRUE, TRUE)"""
                cursor.execute(sql, (username, email, password_hash))
                print("  ✓ Created with email")
            except pymysql.Error as e:
                if "Unknown column 'email'" in str(e):
                    print("  Note: email column not available, creating without email")
                    sql = """INSERT INTO forge_users 
                             (username, password_hash, role, is_active, is_verified)
                             VALUES (%s, %s, 'admin', TRUE, TRUE)"""
                    cursor.execute(sql, (username, password_hash))
                    print("  ✓ Created without email")
                else:
                    raise
        
        conn.commit()
        
        print("\n✓ Admin user configured successfully!")
        print(f"\nYou can now login with:")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        if email:
            print(f"  Email: {email}")
        
        cursor.close()
        conn.close()
        return True
        
    except pymysql.Error as e:
        print(f"ERROR: Database error: {e}")
        print(f"\nTroubleshooting:")
        print(f"  1. Run: python check_table_structure.py")
        print(f"     (to see the actual table columns)")
        print(f"  2. Check if MySQL is running on 192.168.4.138:3306")
        print(f"  3. Verify DB_USER and DB_PASSWORD in .env file")
        print(f"  4. Ensure database 'akira_forge' exists")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n")
    success = create_admin_user()
    print("\n" + "=" * 60)
    
    if success:
        print("✓ Setup completed successfully!")
    else:
        print("✗ Setup failed! Check the errors above.")
        sys.exit(1)
    
    print("=" * 60 + "\n")

