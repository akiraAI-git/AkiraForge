#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

load_dotenv()

try:
    import pymysql
    import pymysql.cursors
    import bcrypt
    
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
    
    # Delete old admin
    cursor.execute("DELETE FROM forge_users WHERE username = 'admin'")
    
    # Create new admin
    password_hash = bcrypt.hashpw(b"treverdb", bcrypt.gensalt()).decode()
    cursor.execute("INSERT INTO forge_users (username, password_hash, role) VALUES (%s, %s, 'admin')",
                   ("admin", password_hash))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("SUCCESS: Admin user reset")
    print("Username: admin")
    print("Password: treverdb")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

sys.exit(0)
