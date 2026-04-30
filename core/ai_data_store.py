"""
AI Data Store - Store and retrieve AI interaction data
"""
import json
from datetime import datetime
from core.db import get_db_connection

class AIDataStore:
    """Stores and retrieves AI interaction data"""
    
    @staticmethod
    def store_ai_data(ai_id: str, user_id: int, data: dict) -> bool:
        """Store AI data to database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            json_data = json.dumps(data)
            
            cursor.execute(
                """INSERT INTO ai_data (ai_id, user_id, data) 
                   VALUES (%s, %s, %s)
                   ON DUPLICATE KEY UPDATE data = %s""",
                (ai_id, user_id, json_data, json_data)
            )
            conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            print(f"[AI_DATA_STORE] Error storing data: {e}")
            return False
    
    @staticmethod
    def retrieve_ai_data(ai_id: str, user_id: int) -> dict:
        """Retrieve AI data from database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT data FROM ai_data WHERE ai_id = %s AND user_id = %s",
                (ai_id, user_id)
            )
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                data = result['data'] if isinstance(result, dict) else result[0]
                return json.loads(data) if data else {}
            
            return {}
            
        except Exception as e:
            print(f"[AI_DATA_STORE] Error retrieving data: {e}")
            return {}
    
    @staticmethod
    def append_interaction(ai_id: str, user_id: int, interaction: dict) -> bool:
        """Append interaction to AI data"""
        try:
            current_data = AIDataStore.retrieve_ai_data(ai_id, user_id)
            
            if not current_data:
                current_data = {
                    "ai_id": ai_id,
                    "user_id": user_id,
                    "interactions": [],
                    "preferences": {},
                    "metadata": {}
                }
            
            if "interactions" not in current_data:
                current_data["interactions"] = []
            
            interaction["timestamp"] = datetime.now().isoformat()
            current_data["interactions"].append(interaction)
            
            # Limit to last 1000 interactions
            if len(current_data["interactions"]) > 1000:
                current_data["interactions"] = current_data["interactions"][-1000:]
            
            return AIDataStore.store_ai_data(ai_id, user_id, current_data)
            
        except Exception as e:
            print(f"[AI_DATA_STORE] Error appending interaction: {e}")
            return False
    
    @staticmethod
    def update_preferences(ai_id: str, user_id: int, preferences: dict) -> bool:
        """Update AI preferences"""
        try:
            current_data = AIDataStore.retrieve_ai_data(ai_id, user_id)
            
            if not current_data:
                current_data = {
                    "ai_id": ai_id,
                    "user_id": user_id,
                    "interactions": [],
                    "preferences": {},
                    "metadata": {}
                }
            
            current_data["preferences"].update(preferences)
            return AIDataStore.store_ai_data(ai_id, user_id, current_data)
            
        except Exception as e:
            print(f"[AI_DATA_STORE] Error updating preferences: {e}")
            return False
    
    @staticmethod
    def get_interactions(ai_id: str, user_id: int, limit: int = 50) -> list:
        """Get recent interactions"""
        try:
            data = AIDataStore.retrieve_ai_data(ai_id, user_id)
            interactions = data.get("interactions", [])
            return interactions[-limit:] if interactions else []
            
        except Exception as e:
            print(f"[AI_DATA_STORE] Error getting interactions: {e}")
            return []

