import pymysql
from core.db import get_db_connection
from core.logger import log_event

# Email utilities removed - to be added when needed
# from core.email_utils import (
#     send_signup_approved,
#     send_signup_rejected,
#     send_admin_notification
# )

class SignupManager:
    def __init__(self):
        self.db = get_db_connection()
        self.cursor = self.db.cursor(pymysql.cursors.DictCursor)

    def get_all_requests(self):
        try:
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
            """)
            return self.cursor.fetchall() or []
        except Exception as e:
            print(f"[SignupManager] Error fetching requests: {e}")
            return []

    def approve_request(self, request_id):
        try:
            self.cursor.execute(
                "UPDATE signup_requests SET status='approved', reviewed_at=NOW() WHERE id=%s",
                (request_id,)
            )
            self.db.commit()
            return True
        except Exception as e:
            print(f"[SignupManager] Error approving request: {e}")
            return False

    def reject_request(self, request_id):
        try:
            self.cursor.execute(
                "UPDATE signup_requests SET status='rejected', reviewed_at=NOW() WHERE id=%s",
                (request_id,)
            )
            self.db.commit()
            return True
        except Exception as e:
            print(f"[SignupManager] Error rejecting request: {e}")
            return False
