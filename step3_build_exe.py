import os
from dotenv import load_dotenv
from pathlib import Path
import sys
import subprocess

load_dotenv()

project_path = Path("C:/akiraforge/test_projects/TestSurfInstructor")

print("STEP 3: BUILD GENERATED PROJECT TO EXE")
print("="*60)
print(f"Project path: {project_path}")
print()

try:
    os.chdir(project_path)

    print("Checking PyInstaller installation...")
    result = subprocess.run([sys.executable, "-m", "PyInstaller", "--version"],
                          capture_output=True, text=True)
    if result.returncode == 0:
        print(f"PyInstaller version: {result.stdout.strip()}")
    else:
        print("PyInstaller not found, attempting to install...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    print("\nBuilding EXE from gui_runner.py...")
    print("This may take a few minutes...")
    print()

    from core.build_exe import build_exe

    build_exe(
        project_path=project_path,
        exe_name="TestSurfInstructor",
        icon_path=None
    )

    dist_dir = project_path / "dist"
    exe_file = dist_dir / "TestSurfInstructor.exe"

    if exe_file.exists():
        file_size_mb = exe_file.stat().st_size / (1024 * 1024)
        print(f"\nEXE created successfully!")
        print(f"Location: {exe_file}")
        print(f"Size: {file_size_mb:.2f} MB")
        print("\nSTEP 3 STATUS: SUCCESS")
    else:
        print(f"ERROR: EXE file not created at {exe_file}")
        print("STEP 3 STATUS: FAILED")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\nSTEP 3 STATUS: FAILED")
