import subprocess
import os
from PySide6.QtWidgets import QMessageBox

def launch_akira_ai(parent=None):
    akira_path = r"C:\akira\dist\AkiraAI.exe"

    if not os.path.exists(akira_path):
        if parent:
            QMessageBox.warning(parent, "Not Found", f"Akira AI EXE not found:\n{akira_path}")
        return

    try:
        subprocess.Popen([akira_path])
    except Exception as e:
        if parent:
            QMessageBox.warning(parent, "Error", str(e))
