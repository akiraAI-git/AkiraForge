#!/usr/bin/env python3
"""Cleanup script to remove test files"""
import os
from pathlib import Path

repo_path = Path(__file__).parent

# Files to delete
files_to_delete = [
    "test_ai_system.py",
    "test_offline_mode.py",
    "test_syntax.py",
    "validate_fix.py",
]

# Directories to delete
dirs_to_delete = [
    "tests",
]

print("🧹 Cleaning up test files...\n")

# Delete files
for filename in files_to_delete:
    filepath = repo_path / filename
    if filepath.exists():
        filepath.unlink()
        print(f"✓ Deleted: {filename}")
    else:
        print(f"⊘ Not found: {filename}")

# Delete directories
for dirname in dirs_to_delete:
    dirpath = repo_path / dirname
    if dirpath.exists():
        import shutil
        shutil.rmtree(dirpath)
        print(f"✓ Deleted directory: {dirname}")
    else:
        print(f"⊘ Not found: {dirname}")

# Delete test file in tools
tools_test = repo_path / "tools" / "test_db_migration.py"
if tools_test.exists():
    tools_test.unlink()
    print(f"✓ Deleted: tools/test_db_migration.py")

print("\n✅ Cleanup complete!")
print("\n📋 Remaining files should only include:")
print("  - create_version_branch.py (version management tool)")
print("  - VERSION (version file)")
print("  - core/__version__.py (version module)")
print("  - VERSION_MANAGEMENT.md (documentation)")
