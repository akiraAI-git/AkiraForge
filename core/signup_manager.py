import pymysql
from core.db import get_db_connection
from core.logger import log_event
from core.email_utils import (
    send_signup_approved,
    send_signup_rejected,
    send_admin_notification
)

class SignupManager:
    def __init__(self):
        self.db = get_db_connection()
        self.cursor = self.db.cursor(pymysql.cursors.DictCursor)

    def get_all_requests(self):
        self.cursor.execute("""
            SELECT
                id,
                name,
                email,
                desired_username,
                desired_password_hash,
                message,
                status,
                email_sent,
                submitted_at,
                reviewed_at,
                verification_answer
            FROM signup_requests
            WHERE status='pending'
                VALUES (%s, %s, %s)
