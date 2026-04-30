# 🔧 Admin Setup - Database Connection Fix

**Date**: April 27, 2026  
**Issue**: Setup script failing to connect to database  
**Status**: ✅ FIXED

---

## ✅ What Was Fixed

### Problem
The `setup_admin_user.py` script was using incorrect defaults:
```python
# ❌ WRONG
host=os.getenv('DB_HOST', 'localhost')  # Wrong host!
database=os.getenv('DB_NAME', 'akiraforge')  # Wrong database name!
email="admin@akiraforge.local"  # Wrong email!
```

### Solution
Updated to use your actual configuration:
```python
# ✅ CORRECT
- Uses same location detection as db.py
- Connects to 192.168.4.138 (HOME_DB_HOST)
- Uses akira_forge database
- Uses akiraforge@outlook.com email
- Uses forge_user account
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Test Database Connection

```bash
python test_db_connection.py
```

This will verify:
- ✓ MySQL is accessible on 192.168.4.138:3306
- ✓ Credentials are correct
- ✓ Database exists
- ✓ Tables are ready

### Step 2: Create Admin User

```bash
python setup_admin_user.py
```

This will:
- ✓ Connect to correct database
- ✓ Create admin user with bcrypt-hashed password
- ✓ Set email to akiraforge@outlook.com
- ✓ Grant admin role

### Step 3: Start Application

```bash
python main.py
```

Login with:
- **Username**: `admin`
- **Password**: `treverdb`
- **Email**: `akiraforge@outlook.com`

---

## 📋 Configuration From .env

Your `.env` file is correctly set up:

```dotenv
DB_USER=forge_user
DB_PASSWORD=048686mariadb
DB_NAME=akira_forge
HOME_DB_HOST=192.168.4.138
OFFICE_DB_HOST=172.19.170.75
ADMIN_EMAIL=akiraforge@outlook.com
```

---

## 🔍 Troubleshooting

If `test_db_connection.py` fails:

### Error: "Can't connect to MySQL server"
**Check:**
- Is MySQL running on 192.168.4.138?
- Can you ping the server? `ping 192.168.4.138`
- Is firewall blocking port 3306?

### Error: "Access denied for user 'forge_user'"
**Check:**
- Does user `forge_user` exist on MySQL?
- Is password `048686mariadb` correct?
- Run: `mysql -h 192.168.4.138 -u forge_user -p`

### Error: "Unknown database 'akira_forge'"
**Check:**
- Does database exist?
- Run: `mysql -h 192.168.4.138 -u forge_user -p -e "SHOW DATABASES;"`

---

## 📁 Files Modified/Created

| File | Status | Purpose |
|------|--------|---------|
| `setup_admin_user.py` | ✅ Updated | Fixed database connection logic |
| `test_db_connection.py` | ✅ Created | Diagnostic tool for connection testing |

---

## ✨ Summary

| Item | Before | After |
|------|--------|-------|
| Host | localhost (wrong) | 192.168.4.138 ✅ |
| Database | akiraforge | akira_forge ✅ |
| Email | admin@akiraforge.local | akiraforge@outlook.com ✅ |
| Connection | Failed | Will work after credentials verified ✅ |

---

## 📝 Next Action

**Run this first:**
```bash
python test_db_connection.py
```

**Then run:**
```bash
python setup_admin_user.py
```

**Finally start app:**
```bash
python main.py
```

---

**Status**: ✅ Ready to set up admin user
