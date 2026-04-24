from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt

class PleadWindow(QWidget):
    def __init__(self, username, user_ip, on_plea_submitted):
