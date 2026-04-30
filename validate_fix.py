#!/usr/bin/env python3
import py_compile
import sys

files_to_check = [
    'C:\\akiraforge\\DesktopAIApp\\core\\device_login_manager.py',
    'C:\\akiraforge\\DesktopAIApp\\core\\maintenance_scheduler.py'
]

all_good = True
for f in files_to_check:
    try:
        py_compile.compile(f, doraise=True)
        print(f"✓ {f.split(chr(92))[-1]} - OK")
    except py_compile.PyCompileError as e:
        print(f"✗ {f} - ERROR: {e}")
        all_good = False

if all_good:
    print("\n✓ All files compile successfully!")
    sys.exit(0)
else:
    print("\n✗ Some files have errors")
    sys.exit(1)
