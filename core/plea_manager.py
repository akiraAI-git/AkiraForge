import pymysql
from core.db import get_db_connection
from core.logger import log_event

class PleaManager:
    def __init__(self):
        self.db = get_db_connection()
        self.cursor = self.db.cursor(pymysql.cursors.DictCursor)

    def get_all_pleas(self):
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
