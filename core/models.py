from core.db import get_db_connection

def log_generated_app(app_name, user_id=1, user_ip="unknown", notes=None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO generated_apps (app_name, user_id, user_ip, notes) VALUES (%s, %s, %s, %s)",
            (app_name, user_id, user_ip, notes)
        )

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Warning: Could not log generated app to database: {e}")

def get_generated_apps():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, app_name, timestamp FROM generated_apps ORDER BY id DESC")
        rows = cursor.fetchall()

        conn.close()
        return rows
    except Exception as e:
        print(f"Warning: Could not retrieve generated apps from database: {e}")
        return []
