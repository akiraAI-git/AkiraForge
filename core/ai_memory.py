from core.db import get_db_connection
import json
from datetime import datetime

class AIMemory:
    
    MAX_COLUMNS_PER_TABLE = 50  # Create new table when exceeding this
    
    def __init__(self, ai_name: str):
        self.ai_name = ai_name
        self.db = get_db_connection()
        self.cursor = self.db.cursor()
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        table_name = self._get_or_create_table()
        
        self.cursor.execute(f"DESCRIBE {table_name}")
        columns = {row["Field"] for row in self.cursor.fetchall()}
        
        if self.ai_name not in columns:
            print(f"[AIMemory] Adding column for AI '{self.ai_name}'")
            self.cursor.execute(
                f"ALTER TABLE {table_name} ADD COLUMN `{self.ai_name}` LONGBLOB"
            )
            self.db.commit()
        
        self.table_name = table_name
    
    def _get_or_create_table(self) -> str:
        self.cursor.execute("SHOW TABLES LIKE 'ai_memory_%'")
        existing_tables = [row[0] for row in self.cursor.fetchall()]
        
        if not existing_tables:
            table_name = "ai_memory_1"
            print(f"[AIMemory] Creating table {table_name}")
            self.cursor.execute(f"""
                CREATE TABLE {table_name} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    person_id VARCHAR(255) UNIQUE,
                    person_name VARCHAR(255),
                    first_met DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
        self.cursor.execute(
            f"SELECT id FROM {self.table_name} WHERE person_id = %s",
            (person_id,)
        )
        
        if not self.cursor.fetchone():
            self.cursor.execute(
                f"INSERT INTO {self.table_name} (person_id, person_name) VALUES (%s, %s)",
                (person_id, person_name)
            )
            self.db.commit()
        
        data_json = json.dumps(data)
        self.cursor.execute(
            f"UPDATE {self.table_name} SET `{self.ai_name}` = %s WHERE person_id = %s",
            (data_json, person_id)
        )
        self.db.commit()
    
    def recall_person(self, person_id: str) -> dict:
        self.cursor.execute(
            f"SELECT `{self.ai_name}` FROM {self.table_name} WHERE person_id = %s",
            (person_id,)
        )
        
        result = self.cursor.fetchone()
        if not result or not result.get(self.ai_name):
            return {}
        
        try:
            return json.loads(result[self.ai_name])
        except:
            return {}
    
    def recall_all_people(self) -> list:
        self.cursor.execute(
            f"SELECT person_id, person_name, `{self.ai_name}` FROM {self.table_name} WHERE `{self.ai_name}` IS NOT NULL"
        )
        
        people = []
        for row in self.cursor.fetchall():
            person_id, person_name, data_json = row.values() if hasattr(row, 'values') else [row[0], row[1], row[2]]
            
            try:
                data = json.loads(data_json) if data_json else {}
            except:
                data = {}
            
            people.append({
                "person_id": person_id,
                "person_name": person_name,
                "data": data
            })
        
        return people
    
    def update_interaction(self, person_id: str, person_name: str, interaction: dict):
        existing = self.recall_person(person_id)
        
        if "interactions" not in existing:
            existing["interactions"] = []
        
        interaction["timestamp"] = datetime.now().isoformat()
        existing["interactions"].append(interaction)
        
        if len(existing["interactions"]) > 50:
            existing["interactions"] = existing["interactions"][-50:]
        
        self.remember_person(person_id, person_name, existing)
    
    def get_context_for_person(self, person_id: str) -> str:
        data = self.recall_person(person_id)
        
        if not data:
            return ""
        
        context_parts = []
        
        if "preferences" in data:
            prefs = data["preferences"]
            context_parts.append(f"Known preferences: {', '.join(prefs) if isinstance(prefs, list) else prefs}")
        
        if "interests" in data:
            interests = data["interests"]
            context_parts.append(f"Known interests: {', '.join(interests) if isinstance(interests, list) else interests}")
        
        if "interactions" in data and data["interactions"]:
            last_interaction = data["interactions"][-1]
            if "topic" in last_interaction:
                context_parts.append(f"Last discussed: {last_interaction['topic']}")
        
        return "\n".join(context_parts)
    
    def close(self):
        try:
            self.cursor.close()
            self.db.close()
        except:
            pass
