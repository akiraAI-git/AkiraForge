from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt
import os

LOG_FILE = "akira_logs.txt"   # or whatever your logger writes to

class AdminLogsTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("System Console / Logs")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)

        self.load_logs()

    def load_logs(self):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                self.log_view.setText(f.read())
        else:
            self.log_view.setText("No logs found.")
