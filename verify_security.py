#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import re

class SecurityChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = []
        self.root = Path(__file__).parent
        
    def run_all_checks(self):
        print("\n" + "="*60)
        print("AKIRA FORGE - SECURITY VERIFICATION")
        print("="*60 + "\n")
        
        self.check_env_file_excluded()
        self.check_no_hardcoded_passwords()
        self.check_no_hardcoded_api_keys()
        self.check_no_hardcoded_hosts()
        self.check_gitignore_exists()
        self.check_env_example_safe()
        
        self.print_results()
        
    def check_env_file_excluded(self):
        gitignore_path = self.root / ".gitignore"
        
        if not gitignore_path.exists():
            self.warnings.append(".gitignore file not found")
            return
            
        content = gitignore_path.read_text()
        if ".env" in content:
            self.passed.append("[OK] .env files are in .gitignore")
        else:
            self.errors.append("[ERROR] .env not found in .gitignore - would commit secrets!")
    
    def check_no_hardcoded_passwords(self):
        patterns = [
            r'password\s*=\s*["\'][^"\']*["\']',
            r'DB_PASSWORD\s*=\s*["\'][^"\']*["\']',
            r'pwd\s*=\s*["\'][^"\']*["\']',
        ]
        
        findings = self.search_files(patterns, exclude=[r'.env', r'tools/generate'])
        
        if not findings:
            self.passed.append("[OK] No hardcoded passwords found")
        else:
            for file, line, content in findings:
                self.errors.append(f"[ERROR] Possible hardcoded password in {file}:{line}")
                self.errors.append(f"  {content.strip()}")
    
    def check_no_hardcoded_api_keys(self):
        patterns = [
            r'sk_live_[a-zA-Z0-9]{20,}',      # Stripe live key
            r'sk_test_[a-zA-Z0-9]{20,}',      # Stripe test key
            r'pk_live_[a-zA-Z0-9]{20,}',      # Stripe public live
            r'pk_test_[a-zA-Z0-9]{20,}',      # Stripe public test
            r'gsk_[a-zA-Z0-9]{30,}',          # Groq key
            r'SG\.[a-zA-Z0-9\-_]{20,}',       # SendGrid key
            r'api_key\s*=\s*["\'][a-z0-9]{20,}["\']',
        ]
        
        findings = self.search_files(patterns, exclude=['.env.example', 'tools/'])
        
        if not findings:
            self.passed.append("[OK] No hardcoded API keys found")
        else:
            for file, line, content in findings:
                self.errors.append(f"[ERROR] Possible API key in {file}:{line}")
                self.errors.append(f"  {content.strip()[:60]}...")
    
    def check_no_hardcoded_hosts(self):
        py_files = list(self.root.rglob("*.py"))
        db_host_pattern = r'host\s*=\s*["\'](?!.*getenv)[0-9.]{7,}["\']'
        
        findings = []
        for py_file in py_files:
            if any(x in str(py_file) for x in ['.venv', '__pycache__', '.git']):
                continue
                
            try:
                content = py_file.read_text()
                for i, line in enumerate(content.split('\n'), 1):
                    if re.search(db_host_pattern, line):
                        findings.append((str(py_file), i, line))
            except Exception:
                pass
        
        if not findings:
            self.passed.append("[OK] No hardcoded database hosts found")
        else:
            for file, line, content in findings:
                self.errors.append(f"[ERROR] Hardcoded host in {file}:{line}")
    
    def check_gitignore_exists(self):
        if (self.root / ".gitignore").exists():
            self.passed.append("[OK] .gitignore file exists")
        else:
            self.warnings.append("[WARNING] .gitignore file not found")
    
    def check_env_example_safe(self):
        env_example = self.root / ".env.example"
        
        if not env_example.exists():
            self.warnings.append("[WARNING] .env.example not found (recommended but not required)")
            return
        
        content = env_example.read_text()
        
        dangerous_patterns = [
            r'password=(?!.*supersecret|.*your_|.*example)',
            r'_KEY=(?!.*your_|.*example|\.\.\.)',
        ]
        
        dangerous_found = []
        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                dangerous_found.append(pattern)
        
        if dangerous_found:
            self.warnings.append("[WARNING] .env.example might contain real values instead of placeholders")
        else:
            self.passed.append("[OK] .env.example contains only placeholder values")
    
    def search_files(self, patterns, exclude=None):
        findings = []
        py_files = list(self.root.rglob("*.py"))
        exclude = exclude or []
        
        for py_file in py_files:
            file_str = str(py_file)
            
            if any(exc in file_str for exc in exclude + ['.venv', '__pycache__', '.git']):
                continue
            
            try:
                content = py_file.read_text()
                for i, line in enumerate(content.split('\n'), 1):
                    for pattern in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            findings.append((file_str, i, line))
                            break
            except Exception:
                pass
        
        return findings
    
    def print_results(self):
        print("\n" + "PASSED CHECKS:")
        print("-" * 60)
        for check in self.passed:
            print(f"  {check}")
        
        if self.warnings:
            print("\n" + "WARNINGS:")
            print("-" * 60)
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.errors:
            print("\n" + "ERRORS (FIX BEFORE PUSHING):")
            print("-" * 60)
            for error in self.errors:
                print(f"  {error}")
        
        print("\n" + "="*60)
        
        if self.errors:
            print("STATUS: [FAILED] - Fix errors before pushing to GitHub")
            print("="*60 + "\n")
            return False
        else:
            print("STATUS: [PASSED] - Safe to push to GitHub!")
            print("="*60 + "\n")
            return True

if __name__ == "__main__":
    checker = SecurityChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)
