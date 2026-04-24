def __init__(self):
        self.offline_dir = Path.home() / ".akiraforge" / "offline_data"
        self.offline_dir.mkdir(parents=True, exist_ok=True)
        
        self.projects_file = self.offline_dir / "projects.json"
        self.conversations_file = self.offline_dir / "conversations.json"
        self.ai_data_file = self.offline_dir / "ai_data.json"
        self.user_profile_file = self.offline_dir / "user_profile.json"
        self.notes_file = self.offline_dir / "notes.json"
        
        self._init_files()
    
    def _init_files(self):
        files = {
            self.projects_file: {"projects": []},
            self.conversations_file: {"conversations": []},
            self.ai_data_file: {"ai_instances": {}},
            self.user_profile_file: {"users": {}},
            self.notes_file: {"notes": []},
        }
        
        for file_path, default_data in files.items():
            if not file_path.exists():
                self._write_json(file_path, default_data)
    
    def _write_json(self, file_path: Path, data: Dict) -> None:
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[OFFLINE] Error writing {file_path}: {e}")
    
    def _read_json(self, file_path: Path) -> Dict:
        try:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[OFFLINE] Error reading {file_path}: {e}")
        return {}
    
    
    def save_project(self, project_id: str, project_data: Dict) -> bool:
        try:
            data = self._read_json(self.projects_file)
            
            project_data['id'] = project_id
            project_data['saved_at'] = datetime.now().isoformat()
            
            data['projects'] = [p for p in data.get('projects', []) if p.get('id') != project_id]
            data['projects'].append(project_data)
            
            self._write_json(self.projects_file, data)
            print(f"[OFFLINE] Project saved: {project_id}")
            return True
        except Exception as e:
            print(f"[OFFLINE] Error saving project: {e}")
            return False
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        try:
            data = self._read_json(self.projects_file)
            for project in data.get('projects', []):
                if project.get('id') == project_id:
                    return project
        except Exception as e:
            print(f"[OFFLINE] Error retrieving project: {e}")
        return None
    
    def get_all_projects(self) -> List[Dict]:
        try:
            data = self._read_json(self.projects_file)
            return data.get('projects', [])
        except Exception as e:
            print(f"[OFFLINE] Error getting projects: {e}")
            return []
    
    def delete_project(self, project_id: str) -> bool:
        try:
            data = self._read_json(self.projects_file)
            data['projects'] = [p for p in data.get('projects', []) if p.get('id') != project_id]
            self._write_json(self.projects_file, data)
            return True
        except Exception as e:
            print(f"[OFFLINE] Error deleting project: {e}")
            return False
    
    
    def save_ai_data(self, ai_id: str, ai_data: Dict) -> bool:
        try:
            data = self._read_json(self.ai_data_file)
            
            if 'ai_instances' not in data:
                data['ai_instances'] = {}
            
            ai_data['updated_at'] = datetime.now().isoformat()
            data['ai_instances'][ai_id] = ai_data
            
            self._write_json(self.ai_data_file, data)
            print(f"[OFFLINE] AI data saved: {ai_id}")
            return True
        except Exception as e:
            print(f"[OFFLINE] Error saving AI data: {e}")
            return False
    
    def get_ai_data(self, ai_id: str) -> Optional[Dict]:
        try:
            data = self._read_json(self.ai_data_file)
            return data.get('ai_instances', {}).get(ai_id)
        except Exception as e:
            print(f"[OFFLINE] Error retrieving AI data: {e}")
            return None
    
    def store_ai_message(self, ai_id: str, user_id: str, role: str, content: str) -> bool:
        try:
            ai_data = self.get_ai_data(ai_id)
            if not ai_data:
                ai_data = {
                    'id': ai_id,
                    'conversations': {}
                }
            
            if 'conversations' not in ai_data:
                ai_data['conversations'] = {}
            
            user_key = str(user_id)
            if user_key not in ai_data['conversations']:
                ai_data['conversations'][user_key] = []
            
            message = {
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat()
            }
            
            ai_data['conversations'][user_key].append(message)
            return self.save_ai_data(ai_id, ai_data)
        except Exception as e:
            print(f"[OFFLINE] Error storing AI message: {e}")
            return False
    
    def get_ai_conversation(self, ai_id: str, user_id: str) -> List[Dict]:
        try:
            ai_data = self.get_ai_data(ai_id)
            if ai_data:
                return ai_data.get('conversations', {}).get(str(user_id), [])
        except Exception as e:
            print(f"[OFFLINE] Error retrieving conversation: {e}")
        return []
    
    
    def save_conversation(self, conv_id: str, conv_data: Dict) -> bool:
        try:
            data = self._read_json(self.conversations_file)
            
            conv_data['id'] = conv_id
            conv_data['saved_at'] = datetime.now().isoformat()
            
            data['conversations'] = [c for c in data.get('conversations', []) if c.get('id') != conv_id]
            data['conversations'].append(conv_data)
            
            self._write_json(self.conversations_file, data)
            return True
        except Exception as e:
            print(f"[OFFLINE] Error saving conversation: {e}")
            return False
    
    def get_conversations(self, user_id: str) -> List[Dict]:
        try:
            data = self._read_json(self.conversations_file)
            return [c for c in data.get('conversations', []) if c.get('user_id') == user_id]
        except Exception as e:
            print(f"[OFFLINE] Error retrieving conversations: {e}")
            return []
    
    
    def save_user_profile(self, username: str, profile_data: Dict) -> bool:
        try:
            data = self._read_json(self.user_profile_file)
            
            if 'users' not in data:
                data['users'] = {}
            
            profile_data['updated_at'] = datetime.now().isoformat()
            data['users'][username] = profile_data
            
            self._write_json(self.user_profile_file, data)
            return True
        except Exception as e:
            print(f"[OFFLINE] Error saving user profile: {e}")
            return False
    
    def get_user_profile(self, username: str) -> Optional[Dict]:
        try:
            data = self._read_json(self.user_profile_file)
            return data.get('users', {}).get(username)
        except Exception as e:
            print(f"[OFFLINE] Error retrieving user profile: {e}")
            return None
    
    
    def save_note(self, note_id: str, note_data: Dict) -> bool:
        try:
            data = self._read_json(self.notes_file)
            
            note_data['id'] = note_id
            note_data['saved_at'] = datetime.now().isoformat()
            
            data['notes'] = [n for n in data.get('notes', []) if n.get('id') != note_id]
            data['notes'].append(note_data)
            
            self._write_json(self.notes_file, data)
            return True
        except Exception as e:
            print(f"[OFFLINE] Error saving note: {e}")
            return False
    
    def get_notes(self, user_id: str) -> List[Dict]:
        try:
            data = self._read_json(self.notes_file)
            return [n for n in data.get('notes', []) if n.get('user_id') == user_id]
        except Exception as e:
            print(f"[OFFLINE] Error retrieving notes: {e}")
            return []
    
    
    def clear_all_offline_data(self) -> bool:
        try:
            for file_path in [self.projects_file, self.conversations_file, 
                             self.ai_data_file, self.user_profile_file, self.notes_file]:
                if file_path.exists():
                    file_path.unlink()
            self._init_files()
            print("[OFFLINE] All offline data cleared")
            return True
        except Exception as e:
            print(f"[OFFLINE] Error clearing offline data: {e}")
            return False
    
    def get_offline_storage_size(self) -> str:
        try:
            total_size = 0
            for file_path in self.offline_dir.glob('*.json'):
                total_size += file_path.stat().st_size
            
            if total_size < 1024:
                return f"{total_size} B"
            elif total_size < 1024 * 1024:
                return f"{total_size / 1024:.2f} KB"
            else:
                return f"{total_size / (1024 * 1024):.2f} MB"
        except Exception as e:
            print(f"[OFFLINE] Error getting storage size: {e}")
            return "Unknown"
    
    def export_offline_data(self, export_path: Path) -> bool:
        try:
            backup_data = {
                'projects': self._read_json(self.projects_file),
                'conversations': self._read_json(self.conversations_file),
                'ai_data': self._read_json(self.ai_data_file),
                'user_profile': self._read_json(self.user_profile_file),
                'notes': self._read_json(self.notes_file),
                'exported_at': datetime.now().isoformat()
            }
            
            with open(export_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            print(f"[OFFLINE] Data exported to {export_path}")
            return True
        except Exception as e:
            print(f"[OFFLINE] Error exporting data: {e}")
            return False

_offline_storage_instance = None

def get_offline_storage() -> OfflineStorage:
    global _offline_storage_instance
    if _offline_storage_instance is None:
        _offline_storage_instance = OfflineStorage()
    return _offline_storage_instance
