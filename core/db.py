import os
import pymysql
import pymysql.cursors

print("USING DB.PY FROM:", __file__)

connection = None
OFFLINE_MODE = False
DB_HOST = None

def _get_db_host():
    global DB_HOST
    if DB_HOST:
        return DB_HOST
    
    from core.location_detector import detect_location
    location = detect_location()

    HOME_DB_HOST = os.getenv("HOME_DB_HOST", "192.168.4.138")
    OFFICE_DB_HOST = os.getenv("OFFICE_DB_HOST", "172.19.170.75")

    if location == "home":
        DB_HOST = HOME_DB_HOST
        print("[DB] Location detected: HOME -> Using host:", DB_HOST)
    elif location == "office":
        DB_HOST = OFFICE_DB_HOST
        print("[DB] Location detected: OFFICE -> Using host:", DB_HOST)
    else:
        DB_HOST = HOME_DB_HOST
        print("[DB] Location UNKNOWN -> Falling back to HOME host:", DB_HOST)
    
    return DB_HOST

def get_db_connection():
    global connection, OFFLINE_MODE

    if connection:
        try:
            connection.ping(reconnect=True)
            return connection
        except Exception:
            try:
                connection.close()
            except Exception:
                pass
            connection = None

    DB_USER = os.getenv("DB_USER", "forge_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME", "akira_forge")

    if not DB_PASSWORD:
        OFFLINE_MODE = True
        print("[DB] [OFFLINE] No DB_PASSWORD in environment - OFFLINE MODE ACTIVATED")
        raise RuntimeError(
            "DB_PASSWORD environment variable is not set.\n"
            "Running in OFFLINE MODE. Only machine-locked admin can log in.\n"
            "To enable online mode, set DB_PASSWORD in your .env file."
        )

    db_host = _get_db_host()

    try:
        connection = pymysql.connect(
            host=db_host,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        print(f"[DB] [OK] Connected to database at {db_host}")
        OFFLINE_MODE = False
    except Exception as e:
        OFFLINE_MODE = True
        print(f"[DB] [OFFLINE] Connection failed - OFFLINE MODE ACTIVATED: {e}")
        raise RuntimeError(
            f"Database connection failed: {e}\n"
            "Running in OFFLINE MODE. Only machine-locked admin can log in."
        )

    return connection

def init_db():
    print("[DB] Initializing database...")

    try:
        conn = get_db_connection()
    except Exception as e:
        print(f"[DB] [OFFLINE] Running in OFFLINE MODE - Database unavailable")
        print("[DB] [OFFLINE] Only machine-locked admin can log in")
        return

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("[DB] [OK] Database connection verified")
    except Exception as e:
        print(f"[DB] [WARNING] Could not verify database: {e}")
        return

    try:
        from core.db_repair import repair_database
        print("[DB] Running auto-repair...")
        repair_database()
        print("[DB] [OK] Auto-repair complete")
    except Exception as e:
        print(f"[DB] [WARNING] Auto-repair encountered an issue: {e}")
