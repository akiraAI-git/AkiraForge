import subprocess
import sys
from pathlib import Path

def build_exe(project_path: Path, exe_name: str = "Akira AI", icon_path: Path | None = None):
    project_path = project_path.resolve()
    gui_file = project_path / "gui_runner.py"
    config_file = project_path / "config.json"
    agent_file = project_path / "agent.py"
    gui_folder = project_path / "gui"

    if not gui_file.exists():
        raise FileNotFoundError(f"gui_runner.py not found in {project_path}")
    if not config_file.exists():
        raise FileNotFoundError(f"config.json not found in {project_path}")
    if not agent_file.exists():
        raise FileNotFoundError(f"agent.py not found in {project_path}")
    if not gui_folder.exists():
        raise FileNotFoundError(f"gui folder not found in {project_path}")

    separator = ';' if sys.platform == 'win32' else ':'

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        f"--name={exe_name}",
        f"--add-data={config_file}{separator}.",
        f"--add-data={gui_folder}{separator}gui",
        str(gui_file),
    ]

    if icon_path and icon_path.exists():
        cmd.insert(-1, f"--icon={icon_path}")

    print(f"Building {exe_name}.exe with PyInstaller...")
    print(f"Command: {' '.join(cmd)}")

    subprocess.check_call(cmd, cwd=project_path)
    print(f"Build complete! EXE saved to: {project_path / 'dist' / f'{exe_name}.exe'}")
