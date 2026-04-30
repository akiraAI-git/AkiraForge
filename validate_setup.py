#!/usr/bin/env python
import subprocess

def check_section(title):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"\n{'='*60}")
            print(f"  {title}")
            print('='*60)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@check_section("1. Environment Check")
def check_environment():
    import platform
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    arch = platform.architecture()
    print(f"Python: {py_ver}")
    print(f"Architecture: {arch[0]}")
    print(" Python environment OK")
    return True

@check_section("2. Qt Bindings Check")
def check_qt_bindings():
    qt_available = False
    for pkg in ("PySide6", "PyQt6"):
        try:
            mod = __import__(pkg)
            ver = getattr(mod, '__version__', 'unknown')
            print(f" {pkg}: available (v{ver})")
            qt_available = True
            break
        except Exception as e:
            print(f" {pkg}: not available ({e})")

    if not qt_available:
        print("\n ERROR: No Qt bindings available!")
        return False
    print(" Qt bindings OK")
    return True

@check_section("3. Core Dependencies Check")
def check_dependencies():
    required = {
        'dotenv': 'python-dotenv',
        'pymysql': 'pymysql',
        'bcrypt': 'bcrypt',
        'cryptography': 'cryptography',
        'groq': 'groq',
    }

    all_ok = True
    for import_name, pkg_name in required.items():
        try:
            __import__(import_name)
            print(f" {pkg_name}: OK")
        except ImportError as e:
            print(f" {pkg_name}: MISSING ({e})")
            all_ok = False

    if not all_ok:
        print("\n ERROR: Some dependencies are missing!")
        return False
    print(" All dependencies OK")
    return True

@check_section("4. Core Module Imports Check")
def check_core_imports():
    modules = [
        'core.db',
        'core.config',
        'core.login_manager',
        'core.groq_agent',
        'core.logger',
        'windows.login_window',
        'windows.builder_window',
        'windows.chat_window',
    ]

    all_ok = True
    for module_name in modules:
        try:
            __import__(module_name)
            print(f" {module_name}: OK")
        except Exception as e:
            print(f" {module_name}: FAILED ({type(e).__name__}: {e})")
            all_ok = False

    if not all_ok:
        print("\n ERROR: Some core modules failed to import!")
        return False
    print(" All core modules OK")
    return True

@check_section("5. Qt Widget Instantiation Check")
def check_qt_widgets():
    try:
        from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton
        app = QApplication.instance() or QApplication([])
        widget = QWidget()
        label = QLabel("Test")
        button = QPushButton("Test")
        print(" Created QApplication")
        print(" Created QWidget")
        print(" Created QLabel")
        print(" Created QPushButton")
        print(" Qt widgets OK")
        return True
    except Exception as e:
        print(f" Qt widget creation FAILED: {e}")
        return False

@check_section("6. Configuration Check")
def check_configuration():
    import os
    required_env_vars = ['DB_PASSWORD']
    optional_env_vars = ['DB_USER', 'DB_NAME', 'SENDGRID_API_KEY']

    missing_required = []
    for var in required_env_vars:
        if var not in os.environ:
            missing_required.append(var)
            print(f" {var}: MISSING (required)")
        else:
            val = os.environ[var]
            masked = val[:3] + '*' * max(0, len(val) - 6) if len(val) > 3 else '***'
            print(f" {var}: set ({masked})")

    for var in optional_env_vars:
        if var in os.environ:
            print(f" {var}: set")
        else:
            print(f"⊘ {var}: not set (optional)")

    if missing_required:
        print(f"\n WARNING: Missing required variables: {', '.join(missing_required)}")
        print("  Hint: Create a .env file with these variables before running the app")
        return True  # Don't fail, just warn
    print(" Configuration OK")
    return True

@check_section("SUMMARY")
def summary(results):
    total = len(results)
    passed = sum(1 for r in results if r)
    failed = total - passed

    print(f"\nTotal checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n ALL CHECKS PASSED ")
        print("\nYour Akira Forge environment is ready!")
        print("Run: python main.py")
        return 0
    else:
        print(f"\n {failed} CHECK(S) FAILED ")
        print("\nPlease fix the issues above before running the app.")
        return 1

if __name__ == "__main__":
    results = [
        check_environment(),
        check_qt_bindings(),
        check_dependencies(),
        check_core_imports(),
        check_qt_widgets(),
        check_configuration(),
    ]

    exit_code = summary(results)
    sys.exit(exit_code)
