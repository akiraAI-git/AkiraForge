@staticmethod
    def is_offline_mode() -> bool:
        return not os.getenv("DB_PASSWORD")
    
    @staticmethod
    def save_ai_message(ai_id: str, user_id: int, role: str, content: str, metadata: Optional[Dict] = None) -> bool:
        storage = get_offline_storage()
        
        try:
            ai_data = storage.get_ai_data(ai_id)
            if not ai_data:
                ai_data = {
                    'id': ai_id,
                    'created_at': None,
                    'conversations': {},
                    'preferences': {},
                    'metadata': metadata or {}
                }
            
            if 'conversations' not in ai_data:
                ai_data['conversations'] = {}
            
            user_key = str(user_id)
            if user_key not in ai_data['conversations']:
                ai_data['conversations'][user_key] = []
            
            message = {
                'role': role,
                'content': content,
                'metadata': metadata or {}
            }
            
            ai_data['conversations'][user_key].append(message)
            return storage.save_ai_data(ai_id, ai_data)
        except Exception as e:
            print(f"[OFFLINE AI] Error saving message: {e}")
            return False
    
    @staticmethod
    def get_conversation_history(ai_id: str, user_id: int) -> List[Dict]:
        storage = get_offline_storage()
        
        try:
            ai_data = storage.get_ai_data(ai_id)
            if ai_data:
                conversations = ai_data.get('conversations', {})
                user_key = str(user_id)
                return conversations.get(user_key, [])
        except Exception as e:
            print(f"[OFFLINE AI] Error getting conversation: {e}")
        
        return []
    
    @staticmethod
    def save_ai_preferences(ai_id: str, user_id: int, preferences: Dict) -> bool:
        storage = get_offline_storage()
        
        try:
            ai_data = storage.get_ai_data(ai_id)
            if not ai_data:
                ai_data = {
                    'id': ai_id,
                    'conversations': {},
                    'preferences': {}
                }
            
            if 'preferences' not in ai_data:
                ai_data['preferences'] = {}
            
            user_key = str(user_id)
            ai_data['preferences'][user_key] = preferences
            
            return storage.save_ai_data(ai_id, ai_data)
        except Exception as e:
            print(f"[OFFLINE AI] Error saving preferences: {e}")
            return False
    
    @staticmethod
    def get_ai_preferences(ai_id: str, user_id: int) -> Optional[Dict]:
        storage = get_offline_storage()
        
        try:
            ai_data = storage.get_ai_data(ai_id)
            if ai_data:
                preferences = ai_data.get('preferences', {})
                user_key = str(user_id)
                return preferences.get(user_key)
        except Exception as e:
            print(f"[OFFLINE AI] Error getting preferences: {e}")
        
        return None
    
    @staticmethod
    def save_ai_metadata(ai_id: str, metadata: Dict) -> bool:
        storage = get_offline_storage()
        
        try:
            ai_data = storage.get_ai_data(ai_id)
            if not ai_data:
                ai_data = {
                    'id': ai_id,
                    'conversations': {},
                    'metadata': {}
                }
            
            ai_data['metadata'] = metadata
            return storage.save_ai_data(ai_id, ai_data)
        except Exception as e:
            print(f"[OFFLINE AI] Error saving metadata: {e}")
            return False
    
    @staticmethod
    def get_ai_metadata(ai_id: str) -> Optional[Dict]:
        storage = get_offline_storage()
        
        try:
            ai_data = storage.get_ai_data(ai_id)
            if ai_data:
                return ai_data.get('metadata', {})
        except Exception as e:
            print(f"[OFFLINE AI] Error getting metadata: {e}")
        
        return None
    
    @staticmethod
    def get_all_ais() -> List[Dict]:
        storage = get_offline_storage()
        data = storage._read_json(storage.ai_data_file)
        
        ais = []
        for ai_id, ai_data in data.get('ai_instances', {}).items():
            ais.append({
                'id': ai_id,
                'metadata': ai_data.get('metadata', {}),
                'conversation_count': len(ai_data.get('conversations', {}))
            })
        
        return ais
    
    @staticmethod
    def delete_ai(ai_id: str) -> bool:
        storage = get_offline_storage()
        
        try:
            data = storage._read_json(storage.ai_data_file)
            if 'ai_instances' in data:
                data['ai_instances'].pop(ai_id, None)
                storage._write_json(storage.ai_data_file, data)
                return True
        except Exception as e:
            print(f"[OFFLINE AI] Error deleting AI: {e}")
        
        return False
    
    @staticmethod
    def clear_conversation(ai_id: str, user_id: int) -> bool:
        storage = get_offline_storage()
        
        try:
            ai_data = storage.get_ai_data(ai_id)
            if ai_data and 'conversations' in ai_data:
                user_key = str(user_id)
                ai_data['conversations'][user_key] = []
                return storage.save_ai_data(ai_id, ai_data)
        except Exception as e:
            print(f"[OFFLINE AI] Error clearing conversation: {e}")
        
        return False
    
    @staticmethod
    def export_ai_data(ai_id: str, export_path) -> bool:
        storage = get_offline_storage()
        
        try:
            ai_data = storage.get_ai_data(ai_id)
            if ai_data:
                import json
                with open(export_path, 'w') as f:
                    json.dump(ai_data, f, indent=2)
                return True
        except Exception as e:
            print(f"[OFFLINE AI] Error exporting AI data: {e}")
        
        return False
    
    @staticmethod
    def import_ai_data(ai_id: str, import_path) -> bool:
        storage = get_offline_storage()
        
        try:
            import json
            with open(import_path, 'r') as f:
                ai_data = json.load(f)
            
            ai_data['id'] = ai_id
            return storage.save_ai_data(ai_id, ai_data)
        except Exception as e:
            print(f"[OFFLINE AI] Error importing AI data: {e}")
        
        return False

class OfflineProjectStore:
    
    @staticmethod
    def save_project(project_id: str, project_data: Dict) -> bool:
        storage = get_offline_storage()
        return storage.save_project(project_id, project_data)
    
    @staticmethod
    def get_project(project_id: str) -> Optional[Dict]:
        storage = get_offline_storage()
        return storage.get_project(project_id)
    
    @staticmethod
    def get_all_projects(user_id: Optional[int] = None) -> List[Dict]:
        storage = get_offline_storage()
        projects = storage.get_all_projects()
        
        if user_id:
            projects = [p for p in projects if p.get('user_id') == user_id]
        
        return projects
    
    @staticmethod
    def delete_project(project_id: str) -> bool:
        storage = get_offline_storage()
        return storage.delete_project(project_id)
    
    @staticmethod
    def list_projects() -> List[str]:
        storage = get_offline_storage()
        projects = storage.get_all_projects()
        return [p.get('id') for p in projects]
