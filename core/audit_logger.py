import os
import json
import hashlib
import hmac
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import threading

class AuditLogger:
    
    def __init__(self, log_dir: Optional[str] = None):
        if log_dir is None:
            log_dir = str(Path.home() / ".akiraforge" / "audit_logs")
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.lock = threading.Lock()
        self.security_key = self._load_or_create_security_key()
        
        self.important_actions = {
            "LOGIN", "LOGOUT", "ADMIN_ACTION", "USER_DELETE", "USER_CREATE",
            "PASSWORD_CHANGE", "PERMISSION_CHANGE", "DATA_EXPORT", "DATA_DELETE",
            "VAULT_ACCESS", "VAULT_FILE_UPLOAD", "VAULT_FILE_DELETE"
        }
    
    def _load_or_create_security_key(self) -> str:
        key_file = self.log_dir / ".audit_key"
        
        if key_file.exists():
            try:
                with open(key_file, 'r') as f:
                    return f.read().strip()
            except Exception as e:
                print(f"[AUDIT] Error reading security key: {e}")
        
        key = hashlib.sha256(os.urandom(32)).hexdigest()
        try:
            with open(key_file, 'w') as f:
                f.write(key)
            os.chmod(key_file, 0o600)
        except Exception as e:
            print(f"[AUDIT] Error creating security key: {e}")
        
        return key
    
    def get_security_key(self) -> str:
        return self.security_key
    
    def log_action(self, username: str, action: str, details: Optional[Dict[str, Any]] = None,
                   is_important: bool = False) -> None:
        with self.lock:
            try:
                if is_important is None:
                    is_important = action.upper() in self.important_actions
                
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "username": username,
                    "action": action,
                    "details": details or {},
                    "is_important": is_important
                }
                
                if is_important:
                    self._write_encrypted_log(log_entry)
                
                self._write_plaintext_log(log_entry, hidden=not is_important)
                
            except Exception as e:
                print(f"[AUDIT] Error logging action: {e}")
    
    def _write_plaintext_log(self, entry: Dict, hidden: bool = False) -> None:
        log_file = self.log_dir / (
            "hidden_actions.log" if hidden else "public_actions.log"
        )
        
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"[AUDIT] Error writing plaintext log: {e}")
    
    def _write_encrypted_log(self, entry: Dict) -> None:
        log_file = self.log_dir / "important_actions.log"
        
        try:
            entry_str = json.dumps(entry)
            signature = hmac.new(
                self.security_key.encode(),
                entry_str.encode(),
                hashlib.sha256
            ).hexdigest()
            
            signed_entry = {
                "data": entry,
                "hmac": signature
            }
            
            with open(log_file, 'a') as f:
                f.write(json.dumps(signed_entry) + "\n")
        except Exception as e:
            print(f"[AUDIT] Error writing encrypted log: {e}")
    
    def verify_important_logs(self, key: str) -> bool:
        log_file = self.log_dir / "important_actions.log"
        
        if not log_file.exists():
            return True
        
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    
                    entry = json.loads(line)
                    data_str = json.dumps(entry["data"])
                    expected_hmac = hmac.new(
                        key.encode(),
                        data_str.encode(),
                        hashlib.sha256
                    ).hexdigest()
                    
                    if entry["hmac"] != expected_hmac:
                        return False
            
            return True
        except Exception as e:
            print(f"[AUDIT] Error verifying logs: {e}")
            return False
    
    def get_important_logs(self, key: str) -> Optional[list]:
        log_file = self.log_dir / "important_actions.log"
        
        if not log_file.exists():
            return []
        
        if not self.verify_important_logs(key):
            print("[AUDIT] Security key invalid or logs tampered with")
            return None
        
        try:
            logs = []
            with open(log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        logs.append(entry["data"])
            return logs
        except Exception as e:
            print(f"[AUDIT] Error reading logs: {e}")
            return None
    
    def get_public_logs(self) -> list:
        log_file = self.log_dir / "public_actions.log"
        
        if not log_file.exists():
            return []
        
        try:
            logs = []
            with open(log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        logs.append(json.loads(line))
            return logs
        except Exception as e:
            print(f"[AUDIT] Error reading public logs: {e}")
            return []

global_audit_logger = None

def get_audit_logger() -> AuditLogger:
    global global_audit_logger
    if global_audit_logger is None:
        global_audit_logger = AuditLogger()
    return global_audit_logger
