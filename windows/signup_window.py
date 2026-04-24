from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt
from core.db import get_db_connection
from core.email_utils import (
    send_signup_received,
    send_admin_notification
)
import bcrypt

class SignupWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Request Access to Akira Forge")
        self.setMinimumSize(420, 520)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

        title = QLabel("Request Access")
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        layout.addWidget(self.name_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email Address")
        layout.addWidget(self.email_input)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Desired Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Desired Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.verification_input = QLineEdit()
        self.verification_input.setPlaceholderText("Something only Connor would know")
        layout.addWidget(self.verification_input)

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Why do you want access?")
        layout.addWidget(self.message_input)

        submit_btn = QPushButton("Submit Request")
        submit_btn.clicked.connect(self.submit_request)
        layout.addWidget(submit_btn)

    def submit_request(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        verification = self.verification_input.text().strip()
        message = self.message_input.toPlainText().strip()

        if not all([name, email, username, password, verification]):
            QMessageBox.warning(self, "Error", "All fields except message are required.")
            return

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO signup_requests
            (name, email, desired_username, desired_password_hash,
             message, verification_answer)
            VALUES (%s, %s, %s, %s, %s, %s)
