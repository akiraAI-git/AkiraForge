from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont
from core.login_manager import LoginManager
from core.device_login_manager import DeviceLoginManager

class LoginWindow(QWidget):
    def __init__(self, login_success_callback):
        super().__init__()

        self.login_success_callback = login_success_callback
        self.manager = LoginManager()

        self.setWindowTitle("Akira Forge")
        self.setMinimumSize(500, 550)
        self.setMaximumSize(600, 650)
        self.setWindowIcon(self._load_icon())

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        title = QLabel("Akira Forge")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        layout.addWidget(title)

        subtitle = QLabel("Deploy and manage your AI applications")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet("color: #666;")
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumHeight(45)
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(45)
        layout.addWidget(self.password_input)

        self.remember_checkbox = QCheckBox("Remember my account for 5 days on this device")
        layout.addWidget(self.remember_checkbox)

        layout.addSpacing(10)

        login_btn = QPushButton("Login")
        login_btn.setMinimumHeight(45)
        login_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        login_btn.clicked.connect(self.attempt_login)
        layout.addWidget(login_btn)

        signup_btn = QPushButton("Request Access")
        signup_btn.setMinimumHeight(45)
        signup_btn.setFont(QFont("Arial", 12))
        signup_btn.clicked.connect(self.open_signup)
        layout.addWidget(signup_btn)

        contact_admin_btn = QPushButton("? Contact Admin - Locked Out?")
        contact_admin_btn.setMinimumHeight(40)
        contact_admin_btn.setFont(QFont("Arial", 11))
        contact_admin_btn.clicked.connect(self.contact_admin)
        layout.addWidget(contact_admin_btn)

        self.offline_label = QLabel("")
        self.offline_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.offline_label.setStyleSheet("color: #EF4444; font-size: 12px;")
        layout.addWidget(self.offline_label)

        if not self.manager.db_available:
            self.offline_label.setText("[OFFLINE MODE] Database Unreachable")

        layout.addStretch()

        self._apply_theme()

        self.check_device_login()

    def _apply_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #0F172A;
            }
            QLabel#title {
                color: #FFFFFF;
                font-weight: bold;
            }
            QLabel#subtitle {
                color: #D1D5DB;
            }
            QLineEdit {
                background-color: #1F2937;
                color: #FFFFFF;
                border: 2px solid #374151;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #3B82F6;
                outline: none;
            }
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
            QCheckBox {
                color: #FFFFFF;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }

    def contact_admin(self):
        from PySide6.QtWidgets import QDialog, QTextEdit, QLabel
        from PySide6.QtCore import Qt

        dialog = QDialog(self)
        dialog.setWindowTitle("Contact Admin")
        dialog.setGeometry(300, 300, 500, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #0F172A;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 13px;
            }
            QTextEdit {
                background-color: #1F2937;
                color: #FFFFFF;
                border: 1px solid #4B5563;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
                background-color: #6B7280;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
        message = self.admin_message_text.toPlainText().strip()

        if not message:
            QMessageBox.warning(self, "Error", "Please describe your issue.")
            return

        try:
            import json
            from pathlib import Path
            from datetime import datetime

            admin_messages_file = Path("data/admin_messages.json")
            admin_messages_file.parent.mkdir(parents=True, exist_ok=True)

            messages = []
            if admin_messages_file.exists():
                messages = json.loads(admin_messages_file.read_text())

            messages.append({
                "timestamp": datetime.now().isoformat(),
                "username": "Unknown",
                "message": message,
                "status": "new"
            })

            admin_messages_file.write_text(json.dumps(messages, indent=2))

            QMessageBox.information(self, "Success", "Your message has been sent to the admin.\nThey will review it shortly.")
            dialog.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send message: {str(e)}")

    def open_signup(self):
        from windows.signup_window import SignupWindow
        self.signup_window = SignupWindow()
        self.signup_window.show()

    def _load_icon(self):
        try:
            return QIcon("assets/app_icon.png.png")
        except:
            return QIcon()
