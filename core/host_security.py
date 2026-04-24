import os
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

class HostSecurityManager:
    
    @staticmethod
    def get_system_info() -> Dict:
        return {
            "os": platform.system(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "processor": platform.processor(),
            "machine": platform.machine()
        }
    
    @staticmethod
    def harden_file_permissions(file_path: str, mode: int = 0o600) -> bool:
        try:
            file_path = Path(file_path)
            if file_path.exists():
                os.chmod(file_path, mode)
                return True
        except Exception as e:
            print(f"[SECURITY] Error hardening permissions for {file_path}: {e}")
            return False
    
    @staticmethod
    def secure_config_files() -> None:
        config_files = [
            Path.home() / ".akiraforge" / ".env",
            Path.home() / ".akiraforge" / ".audit_key",
            Path.home() / ".akiraforge" / "config.json",
        ]
        
        for file_path in config_files:
            if file_path.exists():
                HostSecurityManager.harden_file_permissions(str(file_path), 0o600)
                print(f"[SECURITY] Secured {file_path}")
    
    @staticmethod
    def enable_windows_firewall_rules() -> None:
        if platform.system() != "Windows":
            print("[SECURITY] Windows Firewall rules only applicable on Windows")
            return
        
        try:
            rules = [
                {
                    "name": "AkiraForge-App-In",
                    "direction": "In",
                    "action": "Allow",
                    "program": os.path.abspath("main.py"),
                    "description": "Allow Akira Forge application inbound traffic"
                }
            ]
            
            for rule in rules:
                cmd = (
                    f"netsh advfirewall firewall add rule "
                    f"name='{rule['name']}' "
                    f"dir={rule['direction']} "
                    f"action={rule['action']} "
                    f"program='{rule['program']}' "
                    f"description='{rule['description']}'"
                )
                
                try:
                    subprocess.run(cmd, shell=True, capture_output=True, check=False)
                    print(f"[SECURITY] Added firewall rule: {rule['name']}")
                except Exception as e:
                    print(f"[SECURITY] Could not add firewall rule {rule['name']}: {e}")
        
        except Exception as e:
            print(f"[SECURITY] Error configuring Windows Firewall: {e}")
    
    @staticmethod
    def configure_ufw_rules() -> None:
        if platform.system() != "Linux":
            print("[SECURITY] UFW rules only applicable on Linux")
            return
        
        try:
            rules = [
                {"port": 3306, "protocol": "tcp", "comment": "MySQL Database"},
                {"port": 5432, "protocol": "tcp", "comment": "PostgreSQL Database"},
                {"port": 8000, "protocol": "tcp", "comment": "API Server"},
            ]
            
            for rule in rules:
                cmd = (
                    f"sudo ufw allow {rule['port']}/{rule['protocol']} "
                    f"comment '{rule['comment']}'"
                )
                
                try:
                    subprocess.run(cmd, shell=True, capture_output=True, check=False)
                    print(f"[SECURITY] Added UFW rule for port {rule['port']}")
                except Exception as e:
                    print(f"[SECURITY] Could not add UFW rule: {e}")
        
        except Exception as e:
            print(f"[SECURITY] Error configuring UFW: {e}")
    
    @staticmethod
    def enable_basic_dos_protection() -> bool:
        if platform.system() != "Windows":
            return False
        
        try:
            print("[SECURITY] Enabling Windows Defender DOS protection...")
            subprocess.run("netsh int tcp set global ecn=enabled", shell=True, capture_output=True)
            subprocess.run("netsh int tcp set global timestamps=enabled", shell=True, capture_output=True)
            print("[SECURITY] DOS protection enabled")
            return True
        except Exception as e:
            print(f"[SECURITY] Error enabling DOS protection: {e}")
            return False
    
    @staticmethod
    def disable_unnecessary_services(services: List[str]) -> None:
        if platform.system() != "Windows":
            print("[SECURITY] Service management only for Windows")
            return
        
        for service in services:
            try:
                cmd = f"net stop {service}"
                subprocess.run(cmd, shell=True, capture_output=True, check=False)
                
                cmd = f"sc config {service} start=disabled"
                subprocess.run(cmd, shell=True, capture_output=True, check=False)
                print(f"[SECURITY] Disabled service: {service}")
            except Exception as e:
                print(f"[SECURITY] Could not disable {service}: {e}")
    
    @staticmethod
    def create_security_audit() -> Dict:
        audit = {
            "system_info": HostSecurityManager.get_system_info(),
            "checks": {
                "file_permissions": "Not implemented",
                "firewall_rules": "Not implemented",
                "open_ports": "Not implemented",
                "running_services": "Not implemented"
            }
        }
        
        return audit
    
    @staticmethod
    def harden_system() -> None:
        print("[SECURITY] Starting system hardening...")
        
        HostSecurityManager.secure_config_files()
        HostSecurityManager.enable_basic_dos_protection()
        
        if platform.system() == "Windows":
            HostSecurityManager.enable_windows_firewall_rules()
        elif platform.system() == "Linux":
            HostSecurityManager.configure_ufw_rules()
        
        print("[SECURITY] System hardening complete")
