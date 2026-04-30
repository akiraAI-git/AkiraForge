import pymysql
from core.db import get_db_connection
from core.logger import log_event

class PleaManager:
    def __init__(self):
        self.db = get_db_connection()
        self.cursor = self.db.cursor(pymysql.cursors.DictCursor)

    def get_all_pleas(self):
        try:
            self.cursor.execute("""
                SELECT
                    id,
                    username,
                    claimed_identity,
                    reason,
                    verification_answer,
                    ip_address,
                    submitted_at
                FROM access_pleas
                WHERE reviewed=FALSE
                ORDER BY submitted_at DESC
            """)
            return self.cursor.fetchall() or []
        except Exception as e:
            print(f"[PleaManager] Error fetching pleas: {e}")
            return []

    def approve_plea(self, plea_id):
        try:
            self.cursor.execute(
                "UPDATE access_pleas SET reviewed=TRUE WHERE id=%s",
                (plea_id,)
            )
            self.db.commit()
            return True
        except Exception as e:
            print(f"[PleaManager] Error approving plea: {e}")
            return False

    def reject_plea(self, plea_id):
        try:
            self.cursor.execute(
                "UPDATE access_pleas SET reviewed=TRUE, rejected=TRUE WHERE id=%s",
                (plea_id,)
            )
            self.db.commit()
            return True
        except Exception as e:
            print(f"[PleaManager] Error rejecting plea: {e}")
            return False
