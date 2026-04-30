import socket
import platform
import subprocess
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime
import json

class FirewallRule:
    def __init__(self, name: str, port: int, protocol: str = "tcp", 
                 direction: str = "inbound", action: str = "allow",
                 description: str = "", remote_ip: Optional[str] = None):
        self.name = name
        self.port = port
        self.protocol = protocol.lower()
        self.direction = direction.lower()
        self.action = action.lower()
        self.description = description
        self.remote_ip = remote_ip
        self.created_at = datetime.now().isoformat()
        self.enabled = True

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "port": self.port,
            "protocol": self.protocol,
            "direction": self.direction,
            "action": self.action,
            "description": self.description,
            "remote_ip": self.remote_ip,
            "created_at": self.created_at,
            "enabled": self.enabled
        }

class FirewallManager:
    
    WINDOWS = "Windows"
    LINUX = "Linux"
    
    AKIRA_RULES = [
        FirewallRule("MySQL-DB", 3306, "tcp", "inbound", "allow", 
                    "MySQL database access"),
        FirewallRule("API-Server", 8000, "tcp", "inbound", "allow",
                    "Akira API server"),
        FirewallRule("HTTPS-Web", 443, "tcp", "inbound", "allow",
                    "HTTPS web server"),
        FirewallRule("HTTP-Web", 80, "tcp", "inbound", "allow",
                    "HTTP web server"),
        FirewallRule("SSH-Admin", 22, "tcp", "inbound", "allow",
                    "SSH remote administration"),
    ]
    
    def __init__(self, rules_file: Optional[str] = None):
        if rules_file is None:
            rules_file = str(Path.home() / ".akiraforge" / "firewall_rules.json")
        
        self.rules_file = Path(rules_file)
        self.rules_file.parent.mkdir(parents=True, exist_ok=True)
        self.os_type = self._detect_os()
        self.rules: List[FirewallRule] = self._load_rules()
        
    def _detect_os(self) -> str:
        system = platform.system()
        if "Windows" in system:
            return self.WINDOWS
        elif "Linux" in system:
            return self.LINUX
        else:
            return system
    
    def _load_rules(self) -> List[FirewallRule]:
        if self.rules_file.exists():
            try:
                data = json.loads(self.rules_file.read_text())
                rules = []
                for rule_data in data:
                    rule = FirewallRule(
                        name=rule_data.get("name"),
                        port=rule_data.get("port"),
                        protocol=rule_data.get("protocol", "tcp"),
                        direction=rule_data.get("direction", "inbound"),
                        action=rule_data.get("action", "allow"),
                        description=rule_data.get("description", ""),
                        remote_ip=rule_data.get("remote_ip")
                    )
                    rule.enabled = rule_data.get("enabled", True)
                    rules.append(rule)
                return rules
            except Exception as e:
                print(f"[FIREWALL] Error loading rules: {e}")
                return list(self.AKIRA_RULES)
        return list(self.AKIRA_RULES)
    
    def _save_rules(self) -> bool:
        try:
            rules_data = [rule.to_dict() for rule in self.rules]
            self.rules_file.write_text(json.dumps(rules_data, indent=2))
            return True
        except Exception as e:
            print(f"[FIREWALL] Error saving rules: {e}")
            return False
    
    def add_rule(self, rule: FirewallRule) -> bool:
        if any(r.name == rule.name for r in self.rules):
            print(f"[FIREWALL] Rule '{rule.name}' already exists")
            return False
        
        self.rules.append(rule)
        return self._save_rules()
    
    def remove_rule(self, name: str) -> bool:
        self.rules = [r for r in self.rules if r.name != name]
        return self._save_rules()
    
    def enable_rule(self, name: str) -> bool:
        for rule in self.rules:
            if rule.name == name:
                rule.enabled = True
                return self._save_rules()
        return False
    
    def disable_rule(self, name: str) -> bool:
        for rule in self.rules:
            if rule.name == name:
                rule.enabled = False
                return self._save_rules()
        return False
    
    def get_rule(self, name: str) -> Optional[FirewallRule]:
        for rule in self.rules:
            if rule.name == name:
                return rule
        return None
    
    def list_rules(self) -> List[Dict]:
        return [rule.to_dict() for rule in self.rules if rule.enabled]
    
    def apply_rules_windows(self) -> Dict[str, bool]:
        results = {}
        
        try:
            subprocess.run(
                ["netsh", "advfirewall", "set", "allprofiles", "state", "on"],
                capture_output=True,
                check=False
            )
            print("[FIREWALL] Windows Firewall enabled")
        except Exception as e:
            print(f"[FIREWALL] Error enabling Windows Firewall: {e}")
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            try:
                cmd = [
                    "netsh", "advfirewall", "firewall", "add", "rule",
                    f"name={rule.name}",
                    f"dir={rule.direction}",
                    f"action={rule.action}",
                    f"protocol={rule.protocol}",
                    f"localport={rule.port}",
                    f"description={rule.description}"
                ]
                
                if rule.remote_ip:
                    cmd.append(f"remoteip={rule.remote_ip}")
                
                subprocess.run(cmd, capture_output=True, check=False)
                results[rule.name] = True
                print(f"[FIREWALL] Applied Windows rule: {rule.name}")
            except Exception as e:
                results[rule.name] = False
                print(f"[FIREWALL] Error applying Windows rule {rule.name}: {e}")
        
        return results
    
    def apply_rules_linux(self) -> Dict[str, bool]:
        results = {}
        
        try:
            subprocess.run(
                ["sudo", "ufw", "enable"],
                capture_output=True,
                check=False
            )
            print("[FIREWALL] UFW enabled")
        except Exception as e:
            print(f"[FIREWALL] Error enabling UFW: {e}")
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            try:
                cmd = [
                    "sudo", "ufw", "allow",
                    f"{rule.port}/{rule.protocol}",
                    "comment", rule.description
                ]
                
                if rule.remote_ip:
                    cmd = [
                        "sudo", "ufw", "allow", "from",
                        rule.remote_ip, "to", "any", "port",
                        str(rule.port), "comment", rule.description
                    ]
                
                subprocess.run(cmd, capture_output=True, check=False)
                results[rule.name] = True
                print(f"[FIREWALL] Applied Linux rule: {rule.name}")
            except Exception as e:
                results[rule.name] = False
                print(f"[FIREWALL] Error applying Linux rule {rule.name}: {e}")
        
        return results
    
    def apply_rules(self) -> Dict[str, bool]:
        if self.os_type == self.WINDOWS:
            return self.apply_rules_windows()
        elif self.os_type == self.LINUX:
            return self.apply_rules_linux()
        else:
            print(f"[FIREWALL] Unsupported OS: {self.os_type}")
            return {}
    
    def check_port_open(self, host: str, port: int, timeout: int = 3) -> bool:
        try:
            socket.setdefaulttimeout(timeout)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex((host, port))
                return result == 0
        except Exception:
            return False
    
    def get_open_ports(self, host: str = "localhost") -> List[int]:
        common_ports = [22, 80, 443, 3306, 5432, 8000, 8080, 8443, 9000]
        open_ports = []
        
        for port in common_ports:
            if self.check_port_open(host, port):
                open_ports.append(port)
        
        return open_ports
    
    def verify_firewall_status(self) -> Dict[str, any]:
        status = {
            "os": self.os_type,
            "firewall_enabled": False,
            "rules_count": len(self.rules),
            "enabled_rules_count": len([r for r in self.rules if r.enabled]),
            "open_ports": self.get_open_ports(),
            "rules": self.list_rules()
        }
        
        if self.os_type == self.WINDOWS:
            try:
                result = subprocess.run(
                    ["netsh", "advfirewall", "show", "allprofiles"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                status["firewall_enabled"] = "ON" in result.stdout
            except Exception:
                pass
        
        elif self.os_type == self.LINUX:
            try:
                result = subprocess.run(
                    ["sudo", "ufw", "status"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                status["firewall_enabled"] = "active" in result.stdout.lower()
            except Exception:
                pass
        
        return status
    
    def reset_rules(self) -> bool:
        self.rules = list(self.AKIRA_RULES)
        return self._save_rules()
    
    def export_rules(self, filepath: str) -> bool:
        try:
            rules_data = [rule.to_dict() for rule in self.rules]
            Path(filepath).write_text(json.dumps(rules_data, indent=2))
            print(f"[FIREWALL] Rules exported to {filepath}")
            return True
        except Exception as e:
            print(f"[FIREWALL] Error exporting rules: {e}")
            return False
    
    def import_rules(self, filepath: str) -> bool:
        try:
            data = json.loads(Path(filepath).read_text())
            self.rules = []
            for rule_data in data:
                rule = FirewallRule(
                    name=rule_data.get("name"),
                    port=rule_data.get("port"),
                    protocol=rule_data.get("protocol", "tcp"),
                    direction=rule_data.get("direction", "inbound"),
                    action=rule_data.get("action", "allow"),
                    description=rule_data.get("description", ""),
                    remote_ip=rule_data.get("remote_ip")
                )
                self.rules.append(rule)
            return self._save_rules()
        except Exception as e:
            print(f"[FIREWALL] Error importing rules: {e}")
            return False

def setup_akira_firewall() -> FirewallManager:
    fm = FirewallManager()
    results = fm.apply_rules()
    
    print("\n[FIREWALL] Setup Complete")
    print(f"[FIREWALL] OS Detected: {fm.os_type}")
    print(f"[FIREWALL] Rules Applied: {sum(1 for v in results.values() if v)} / {len(results)}")
    
    return fm

if __name__ == "__main__":
    fm = setup_akira_firewall()
    status = fm.verify_firewall_status()
    
    print("\n[FIREWALL] Status Report:")
    print(f"  Firewall Enabled: {status['firewall_enabled']}")
    print(f"  Total Rules: {status['rules_count']}")
    print(f"  Enabled Rules: {status['enabled_rules_count']}")
    print(f"  Open Ports: {status['open_ports']}")
