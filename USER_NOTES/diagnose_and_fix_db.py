#!/usr/bin/env python3
"""
Complete MySQL diagnosis and repair tool
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    import pymysql
    import pymysql.cursors
except ImportError:
    print("ERROR: pymysql not installed. Install with: pip install pymysql")
    sys.exit(1)


def get_connection():
    """Get database connection."""
    return pymysql.connect(
        host=os.getenv('HOME_DB_HOST', '192.168.4.138'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'forge_user'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'akira_forge'),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )


def diagnose():
    """Diagnose database issues"""
    
    print("\n" + "=" * 70)
    print("DATABASE DIAGNOSIS & FIX")
    print("=" * 70)
    
    try:
        print("\n1. Testing connection...")
        conn = get_connection()
        print("   ✓ Connected to 192.168.4.138:akira_forge")
        
        cursor = conn.cursor()
        
        print("\n2. Checking forge_users table structure...")
        cursor.execute("DESCRIBE forge_users")
        columns = cursor.fetchall()
        
        column_names = [col['Field'] for col in columns]
        print(f"   ✓ Found {len(columns)} columns:")
        for col in columns:
            print(f"     - {col['Field']:<20} ({col['Type']})")
        
        # Check what columns we have
        has_email = 'email' in column_names
        has_role = 'role' in column_names
        has_password_hash = 'password_hash' in column_names
        has_is_active = 'is_active' in column_names
        
        print(f"\n3. Checking required columns:")
        print(f"   {'✓' if has_password_hash else '✗'} password_hash")
        print(f"   {'✓' if has_role else '✗'} role")
        print(f"   {'✓' if has_email else '✗'} email")
        print(f"   {'✓' if has_is_active else '✗'} is_active")
        
        print(f"\n4. Checking existing admin user...")
        cursor.execute("SELECT * FROM forge_users WHERE username = 'admin'")
        admin = cursor.fetchone()
        
        if admin:
            print(f"   ✓ Admin user exists:")
            for key, value in admin.items():
                if key != 'password_hash':
                    print(f"     - {key}: {value}")
                else:
                    print(f"     - password_hash: {'SET' if value else 'NOT SET'}")
        else:
            print(f"   ⊘ No admin user found")
        
        # Now fix/create admin
        print(f"\n5. Creating/Updating admin user...")
        
        import bcrypt
        password = "treverdb"
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        if admin:
            # Update existing
            print(f"   Updating existing admin user...")
            
            # Build UPDATE statement based on available columns
            update_parts = ["password_hash = %s"]
            values = [password_hash]
            
            if has_role:
                update_parts.append("role = %s")
                values.append('admin')
            
            # Only add column if it exists in the table
            if has_is_active:
                update_parts.append("is_active = %s")
                values.append(1)
            
            values.append('admin')  # WHERE clause
            
            sql = f"UPDATE forge_users SET {', '.join(update_parts)} WHERE username = %s"
            cursor.execute(sql, values)
            print(f"   ✓ Updated password hash and role")
            
        else:
            # Create new
            print(f"   Creating new admin user...")
            
            # Build INSERT statement based on available columns
            fields = ['username', 'password_hash']
            values = ['admin', password_hash]
            
            if has_role:
                fields.append('role')
                values.append('admin')
            
            if has_email:
                fields.append('email')
                values.append('akiraforge@outlook.com')
            
            # Only add if it exists
            if has_is_active:
                fields.append('is_active')
                values.append(1)
            
            placeholders = ', '.join(['%s'] * len(fields))
            sql = f"INSERT INTO forge_users ({', '.join(fields)}) VALUES ({placeholders})"
            cursor.execute(sql, values)
            print(f"   ✓ Created new admin user")
        
        conn.commit()
        
        print(f"   ✓ Admin user configured!")
        print(f"\n6. Login credentials:")
        print(f"   Username: admin")
        print(f"   Password: treverdb")
        if has_email:
            print(f"   Email: akiraforge@outlook.com")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS - Database ready for login!")
        print("=" * 70)
        print("\nNext: python main.py\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 70)
        print("TROUBLESHOOTING")
        print("=" * 70)
        print("\n1. Check MySQL status on 192.168.4.138")
        print("2. Verify credentials in .env:")
        print(f"   - DB_USER: forge_user")
        print(f"   - DB_PASSWORD: (check .env)")
        print(f"   - DB_NAME: akira_forge")
        print("\n3. Try connecting manually:")
        print(f"   mysql -h 192.168.4.138 -u forge_user -p akira_forge")
        print()
        return False


if __name__ == "__main__":
    success = diagnose()
    sys.exit(0 if success else 1)
