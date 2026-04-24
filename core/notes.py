from __future__ import annotations
from pathlib import Path
import json
import os
from typing import List, Optional
from datetime import datetime

from core.db import get_db_connection
from core.crypto import derive_key, encrypt_text, decrypt_text

class NotesManager:
    def __init__(self):
        self.db = get_db_connection()
        self.cursor = self.db.cursor()

        self.passphrase = os.getenv('NOTES_PASSPHRASE')
        salt_b64 = os.getenv('NOTES_SALT')
        if not self.passphrase or not salt_b64:
            self.key = None
        else:
            try:
                salt = bytes.fromhex(salt_b64)
            except Exception:
                salt = salt_b64.encode('utf-8')
            self.key = derive_key(self.passphrase, salt)

    def enabled(self) -> bool:
        return self.key is not None

    def create_note(self, title: str, body: str, tags: Optional[List[str]] = None) -> int:
        if not self.key:
            raise RuntimeError('Notes not configured; set NOTES_PASSPHRASE and NOTES_SALT')

        nonce_t, ct_t = encrypt_text(self.key, title)
        nonce_b, ct_b = encrypt_text(self.key, body)

        tags_json = json.dumps(tags or [])

        self.cursor.execute(
        )
        self.db.commit()
        return self.cursor.lastrowid

    def list_notes(self) -> List[dict]:
        self.cursor.execute("SELECT id, title, nonce_title, tags, created_at FROM notes ORDER BY updated_at DESC")
        rows = self.cursor.fetchall()
        out = []
        for r in rows:
            try:
                title = decrypt_text(self.key, r['nonce_title'], r['title']) if self.key else '(locked)'
            except Exception:
                title = '(decryption failed)'
            out.append({
                'id': r['id'],
                'title': title,
                'tags': json.loads(r['tags'] or '[]'),
                'created_at': r['created_at']
            })
        return out

    def get_note(self, note_id: int) -> Optional[dict]:
        self.cursor.execute("SELECT * FROM notes WHERE id=%s", (note_id,))
        r = self.cursor.fetchone()
        if not r:
            return None
        try:
            title = decrypt_text(self.key, r['nonce_title'], r['title']) if self.key else '(locked)'
            body = decrypt_text(self.key, r['nonce_body'], r['body']) if self.key else '(locked)'
        except Exception:
            title = '(decryption failed)'
            body = '(decryption failed)'

        return {
            'id': r['id'],
            'title': title,
            'body': body,
            'tags': json.loads(r['tags'] or '[]'),
            'created_at': r['created_at'],
            'updated_at': r['updated_at']
        }

    def delete_note(self, note_id: int) -> bool:
        self.cursor.execute("DELETE FROM notes WHERE id=%s", (note_id,))
        self.db.commit()
        return True
