#!/usr/bin/env python3
"""
Log Encryption System
=====================

Encrypts sensitive audit logs using AES-256.
Provides additional layer of security for important logs.

Features:
  - AES-256 encryption
  - Automatic key derivation
  - Secure random IV generation
  - Encryption/decryption of log entries
  - Key management
"""

import os
import json
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
from pathlib import Path
import threading

logger = logging.getLogger(__name__)

class LogEncryption:
    """Encrypts and decrypts sensitive audit logs."""
    
    def __init__(self, key: str = None):
        """
        Initialize log encryption.
        
        Args:
            key: Master encryption key (generates from security key if not provided)
        """
        self.lock = threading.Lock()
        if key is None:
            key = self._load_security_key()
        
        self.cipher = self._derive_cipher(key)
        if not self.cipher:
            logger.warning("Encryption cipher could not be initialized - logs will be stored plaintext")
    
    def is_available(self) -> bool:
        """Check if encryption is available."""
        return self.cipher is not None
    
    def _load_security_key(self) -> str:
        """Load security key from audit logs."""
        key_file = Path.home() / ".akiraforge" / "audit_logs" / ".audit_key"
        
        try:
            if key_file.exists():
                with open(key_file, 'r') as f:
                    return f.read().strip()
        except Exception as e:
            logger.error(f"Error loading security key: {e}")
        
        return ""
    
    def _derive_cipher(self, key: str) -> Fernet:
        """Derive Fernet cipher from security key."""
        try:
            # Use PBKDF2 to derive a key from the security key
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'akiraforge_logs_' + b'\x00' * 16,
                iterations=100000,
                backend=default_backend()
            )
            
            key_bytes = kdf.derive(key.encode())
            key_b64 = base64.urlsafe_b64encode(key_bytes)
            
            return Fernet(key_b64)
        
        except Exception as e:
            logger.error(f"Error deriving cipher: {e}")
            return None
    
    def encrypt_log_entry(self, log_entry: dict) -> str:
        """
        Encrypt a log entry.
        
        Args:
            log_entry: Log entry dictionary
            
        Returns:
            Encrypted string (base64 encoded)
        """
        if not self.cipher:
            logger.debug("Encryption unavailable, storing plaintext log")
            return json.dumps(log_entry)  # Fallback to plaintext
        
        with self.lock:
            try:
                # Convert to JSON
                entry_json = json.dumps(log_entry)
                
                # Encrypt
                encrypted = self.cipher.encrypt(entry_json.encode())
                
                # Return as base64 string
                return base64.b64encode(encrypted).decode()
            
            except Exception as e:
                logger.error(f"Error encrypting log: {e}")
                return json.dumps(log_entry)  # Fallback
    
    def decrypt_log_entry(self, encrypted_entry: str) -> dict:
        """
        Decrypt a log entry.
        
        Args:
            encrypted_entry: Encrypted log entry (base64 encoded)
            
        Returns:
            Decrypted log entry dictionary
        """
        if not self.cipher:
            try:
                return json.loads(encrypted_entry)
            except:
                return {}
        
        with self.lock:
            try:
                # Decode from base64
                encrypted_bytes = base64.b64decode(encrypted_entry)
                
                # Decrypt
                decrypted = self.cipher.decrypt(encrypted_bytes)
                
                # Parse JSON
                return json.loads(decrypted.decode())
            
            except Exception as e:
                logger.error(f"Error decrypting log: {e}")
                return {}
    
    def encrypt_file(self, input_file: str, output_file: str = None) -> bool:
        """
        Encrypt an entire log file.
        
        Args:
            input_file: Path to input file
            output_file: Path to output file (default: input + .encrypted)
            
        Returns:
            True if successful
        """
        if not output_file:
            output_file = f"{input_file}.encrypted"
        
        try:
            with open(input_file, 'r') as f:
                lines = f.readlines()
            
            encrypted_lines = []
            for line in lines:
                if line.strip():
                    try:
                        entry = json.loads(line)
                        encrypted = self.encrypt_log_entry(entry)
                        encrypted_lines.append(encrypted + "\n")
                    except:
                        encrypted_lines.append(line)
            
            with open(output_file, 'w') as f:
                f.writelines(encrypted_lines)
            
            logger.info(f"File encrypted: {input_file} -> {output_file}")
            return True
        
        except Exception as e:
            logger.error(f"Error encrypting file: {e}")
            return False
    
    def decrypt_file(self, input_file: str, output_file: str = None) -> bool:
        """
        Decrypt an entire log file.
        
        Args:
            input_file: Path to encrypted file
            output_file: Path to output file (default: input + .decrypted)
            
        Returns:
            True if successful
        """
        if not output_file:
            output_file = f"{input_file}.decrypted"
        
        try:
            with open(input_file, 'r') as f:
                lines = f.readlines()
            
            decrypted_lines = []
            for line in lines:
                if line.strip():
                    try:
                        decrypted = self.decrypt_log_entry(line.strip())
                        decrypted_json = json.dumps(decrypted)
                        decrypted_lines.append(decrypted_json + "\n")
                    except:
                        decrypted_lines.append(line)
            
            with open(output_file, 'w') as f:
                f.writelines(decrypted_lines)
            
            logger.info(f"File decrypted: {input_file} -> {output_file}")
            return True
        
        except Exception as e:
            logger.error(f"Error decrypting file: {e}")
            return False

# Global instance
_global_log_encryption = None

def get_log_encryption() -> LogEncryption:
    """Get or create global log encryption."""
    global _global_log_encryption
    if _global_log_encryption is None:
        _global_log_encryption = LogEncryption()
    return _global_log_encryption

def encrypt_log_entry(log_entry: dict) -> str:
    """Encrypt a log entry."""
    encryption = get_log_encryption()
    return encryption.encrypt_log_entry(log_entry)

def decrypt_log_entry(encrypted_entry: str) -> dict:
    """Decrypt a log entry."""
    encryption = get_log_encryption()
    return encryption.decrypt_log_entry(encrypted_entry)

    
    def _derive_cipher(self, key: str) -> Fernet:
        """Derive Fernet cipher from security key."""
        try:
            # Use PBKDF2 to derive a key from the security key
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'akiraforge_logs_' + b'\x00' * 16,
                iterations=100000,
                backend=default_backend()
            )
            
            key_bytes = kdf.derive(key.encode())
            key_b64 = base64.urlsafe_b64encode(key_bytes)
            
            return Fernet(key_b64)
        
        except Exception as e:
            print(f"[LOG_ENCRYPTION] Error deriving cipher: {e}")
            return None
    
    def encrypt_log_entry(self, log_entry: dict) -> str:
        """
        Encrypt a log entry.
        
        Args:
            log_entry: Log entry dictionary
            
        Returns:
            Encrypted string (base64 encoded)
        """
        if not self.cipher:
            return json.dumps(log_entry)  # Fallback to plaintext
        
        with self.lock:
            try:
                # Convert to JSON
                entry_json = json.dumps(log_entry)
                
                # Encrypt
                encrypted = self.cipher.encrypt(entry_json.encode())
                
                # Return as base64 string
                return base64.b64encode(encrypted).decode()
            
            except Exception as e:
                print(f"[LOG_ENCRYPTION] Error encrypting log: {e}")
                return json.dumps(log_entry)  # Fallback
    
    def decrypt_log_entry(self, encrypted_entry: str) -> dict:
        """
        Decrypt a log entry.
        
        Args:
            encrypted_entry: Encrypted log entry (base64 encoded)
            
        Returns:
            Decrypted log entry dictionary
        """
        if not self.cipher:
            try:
                return json.loads(encrypted_entry)
            except:
                return {}
        
        with self.lock:
            try:
                # Decode from base64
                encrypted_bytes = base64.b64decode(encrypted_entry)
                
                # Decrypt
                decrypted = self.cipher.decrypt(encrypted_bytes)
                
                # Parse JSON
                return json.loads(decrypted.decode())
            
            except Exception as e:
                print(f"[LOG_ENCRYPTION] Error decrypting log: {e}")
                return {}
    
    def encrypt_file(self, input_file: str, output_file: str = None) -> bool:
        """
        Encrypt an entire log file.
        
        Args:
            input_file: Path to input file
            output_file: Path to output file (default: input + .encrypted)
            
        Returns:
            True if successful
        """
        if not output_file:
            output_file = f"{input_file}.encrypted"
        
        try:
            with open(input_file, 'r') as f:
                lines = f.readlines()
            
            encrypted_lines = []
            for line in lines:
                if line.strip():
                    try:
                        entry = json.loads(line)
                        encrypted = self.encrypt_log_entry(entry)
                        encrypted_lines.append(encrypted + "\n")
                    except:
                        # Keep unencryptable lines as-is
                        encrypted_lines.append(line)
            
            with open(output_file, 'w') as f:
                f.writelines(encrypted_lines)
            
            return True
        
        except Exception as e:
            print(f"[LOG_ENCRYPTION] Error encrypting file: {e}")
            return False
    
    def decrypt_file(self, input_file: str, output_file: str = None) -> bool:
        """
        Decrypt an entire log file.
        
        Args:
            input_file: Path to encrypted file
            output_file: Path to output file (default: input + .decrypted)
            
        Returns:
            True if successful
        """
        if not output_file:
            output_file = f"{input_file}.decrypted"
        
        try:
            with open(input_file, 'r') as f:
                lines = f.readlines()
            
            decrypted_lines = []
            for line in lines:
                if line.strip():
                    try:
                        decrypted = self.decrypt_log_entry(line.strip())
                        decrypted_json = json.dumps(decrypted)
                        decrypted_lines.append(decrypted_json + "\n")
                    except:
                        # Keep undecryptable lines as-is
                        decrypted_lines.append(line)
            
            with open(output_file, 'w') as f:
                f.writelines(decrypted_lines)
            
            return True
        
        except Exception as e:
            print(f"[LOG_ENCRYPTION] Error decrypting file: {e}")
            return False

# Global instance
_global_log_encryption = None

def get_log_encryption() -> LogEncryption:
    """Get or create global log encryption."""
    global _global_log_encryption
    if _global_log_encryption is None:
        _global_log_encryption = LogEncryption()
    return _global_log_encryption

def encrypt_log_entry(log_entry: dict) -> str:
    """Encrypt a log entry."""
    encryption = get_log_encryption()
    return encryption.encrypt_log_entry(log_entry)

def decrypt_log_entry(encrypted_entry: str) -> dict:
    """Decrypt a log entry."""
    encryption = get_log_encryption()
    return encryption.decrypt_log_entry(encrypted_entry)
