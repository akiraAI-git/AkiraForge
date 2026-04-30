#!/usr/bin/env python3
import os
import sys
import pymysql
import bcrypt
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Reset admin user
conn = pymysql.connect(
    host=os.getenv('HOME_DB_HOST', '192.168.4.138'),
    user=os.getenv('DB_USER', 'forge_user'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME', 'akira_forge'),
    charset='utf8mb4'
)

cursor = conn.cursor()
cursor.execute("DELETE FROM forge_users WHERE username = %s", ('admin',))
ph = bcrypt.hashpw(b'treverdb', bcrypt.gensalt()).decode()
cursor.execute("INSERT INTO forge_users (username, password_hash, role) VALUES (%s, %s, %s)", 
               ('admin', ph, 'admin'))
conn.commit()
cursor.close()
conn.close()

# Clean up all temporary scripts
scripts_to_delete = [
    'reset_admin.py', 'do_reset.py', 'test_db.py', 'final_reset.py'
]

for script in scripts_to_delete:
    try:
        Path(script).unlink()
    except:
        pass
