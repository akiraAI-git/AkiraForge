import os
from typing import Dict, List, Optional
from core.offline_ai_store import OfflineAIDataStore

class SmartAIDataStore:
    @staticmethod
    def _is_offline() -> bool:
        return not os.getenv("DB_PASSWORD")
    
    @staticmethod
    def save_ai_message(ai_id: str, user_id: int, role: str, content: str, metadata: Optional[Dict] = None) -> bool:
        if SmartAIDataStore._is_offline():
            return OfflineAIDataStore.save_ai_message(ai_id, user_id, role, content, metadata)
        else:
            try:
                from core.ai_data_store import AIDataStore
                return AIDataStore.store_ai_message(ai_id, user_id, role, content, metadata)
            except Exception as e:
                print(f"[SMART] Database failed, falling back to JSON: {e}")
                return OfflineAIDataStore.save_ai_message(ai_id, user_id, role, content, metadata)
    
    @staticmethod
    def get_conversation_history(ai_id: str, user_id: int) -> List[Dict]:
        if SmartAIDataStore._is_offline():
            return OfflineAIDataStore.get_conversation_history(ai_id, user_id)
        else:
            try:
                from core.ai_data_store import AIDataStore
                return AIDataStore.get_conversation(ai_id, user_id)
            except Exception:
                return OfflineAIDataStore.get_conversation_history(ai_id, user_id)
    
    @staticmethod
    def save_ai_preferences(ai_id: str, user_id: int, preferences: Dict) -> bool:
        if SmartAIDataStore._is_offline():
            return OfflineAIDataStore.save_ai_preferences(ai_id, user_id, preferences)
        else:
            try:
                from core.ai_data_store import AIDataStore
                return AIDataStore.update_ai_preferences(ai_id, user_id, preferences)
            except Exception:
                return OfflineAIDataStore.save_ai_preferences(ai_id, user_id, preferences)
    
    @staticmethod
    def get_ai_preferences(ai_id: str, user_id: int) -> Optional[Dict]:
        if SmartAIDataStore._is_offline():
            return OfflineAIDataStore.get_ai_preferences(ai_id, user_id)
        else:
            try:
                from core.ai_data_store import AIDataStore
                return AIDataStore.get_preferences(ai_id, user_id)
            except Exception:
                return OfflineAIDataStore.get_ai_preferences(ai_id, user_id)
    
    @staticmethod
    def save_ai_metadata(ai_id: str, metadata: Dict) -> bool:
        if SmartAIDataStore._is_offline():
            return OfflineAIDataStore.save_ai_metadata(ai_id, metadata)
        else:
            try:
                from core.ai_data_store import AIDataStore
                return AIDataStore.save_metadata(ai_id, metadata)
            except Exception:
                return OfflineAIDataStore.save_ai_metadata(ai_id, metadata)
    
    @staticmethod
    def get_ai_metadata(ai_id: str) -> Optional[Dict]:
        if SmartAIDataStore._is_offline():
            return OfflineAIDataStore.get_ai_metadata(ai_id)
        else:
            try:
                from core.ai_data_store import AIDataStore
                return AIDataStore.get_metadata(ai_id)
            except Exception:
                return OfflineAIDataStore.get_ai_metadata(ai_id)
    
    @staticmethod
    def get_all_ais() -> List[Dict]:
        if SmartAIDataStore._is_offline():
            return OfflineAIDataStore.get_all_ais()
        else:
            try:
                from core.ai_data_store import AIDataStore
                return AIDataStore.get_all_ais()
            except Exception:
                return OfflineAIDataStore.get_all_ais()
    
    @staticmethod
    def delete_ai(ai_id: str) -> bool:
        if SmartAIDataStore._is_offline():
            return OfflineAIDataStore.delete_ai(ai_id)
        else:
            try:
                from core.ai_data_store import AIDataStore
                return AIDataStore.delete_ai(ai_id)
            except Exception:
                return OfflineAIDataStore.delete_ai(ai_id)
    
    @staticmethod
    def clear_conversation(ai_id: str, user_id: int) -> bool:
        if SmartAIDataStore._is_offline():
            return OfflineAIDataStore.clear_conversation(ai_id, user_id)
        else:
            try:
                from core.ai_data_store import AIDataStore
                return AIDataStore.clear_conversation(ai_id, user_id)
            except Exception:
                return OfflineAIDataStore.clear_conversation(ai_id, user_id)
