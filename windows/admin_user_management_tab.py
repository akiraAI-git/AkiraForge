from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QMessageBox, QLineEdit, QComboBox
)
from PySide6.QtCore import Qt
from core.db import get_db_connection
from core.logger import log_event
import bcrypt
import secrets
import string

class AdminUserManagementTab(QWidget):
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
            QTableWidget {
                background-color: #000000;
                color: #00ffea;
                gridline-color: #00ffaa;
            }
