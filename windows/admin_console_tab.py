from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit,
    QHBoxLayout, QLineEdit, QComboBox, QFileDialog, QCheckBox, QDialog
)
from PySide6.QtCore import Qt, QTimer
from core.db import get_db_connection
from core.logger import LOG_FILE

class AdminConsoleTab(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #00ffea;
                font-family: Consolas, monospace;
                font-size: 14px;
            }
            QLineEdit, QComboBox {
                background-color: #0d0d0d;
                border: 1px solid #00ffaa;
                padding: 4px;
                color: #00ffea;
            }
            QPushButton {
                background-color: #001a1a;
                border: 1px solid #00ffaa;
                padding: 6px;
                color: #00ffea;
            }
            QPushButton:hover {
                background-color: #003333;
            }
            QTextEdit {
                background-color: #000000;
                border: 1px solid #00ffaa;
                color: #00ffea;
            }
