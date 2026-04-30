#!/usr/bin/env python3
"""Verify syntax fixes"""
import sys

print("=" * 60)
print("Testing syntax fixes...")
print("=" * 60)

# Test 1: Import LoginManager
try:
    from core.login_manager import LoginManager
    print("✓ LoginManager imports successfully!")
except SyntaxError as e:
    print(f"✗ SyntaxError in LoginManager: {e}")
    sys.exit(1)
except Exception as e:
    print(f"⊘ Other error (may be expected): {type(e).__name__}: {e}")

# Test 2: Import LoginWindow
try:
    from windows.login_window import LoginWindow
    print("✓ LoginWindow imports successfully!")
except SyntaxError as e:
    print(f"✗ SyntaxError in LoginWindow: {e}")
    sys.exit(1)
except Exception as e:
    print(f"⊘ Other error (may be expected): {type(e).__name__}: {e}")

# Test 3: Check LoginManager methods
try:
    assert hasattr(LoginManager, 'authenticate'), "Missing authenticate method"
    assert hasattr(LoginManager, 'remember_device'), "Missing remember_device method"
    assert hasattr(LoginManager, 'check_device_login'), "Missing check_device_login method"
    assert hasattr(LoginManager, 'get_machine_id'), "Missing get_machine_id method"
    print("✓ All required LoginManager methods present!")
except AssertionError as e:
    print(f"✗ Method check failed: {e}")
    sys.exit(1)

print("=" * 60)
print("✅ All syntax checks passed!")
print("=" * 60)
