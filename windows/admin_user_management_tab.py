from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QMessageBox, QLineEdit, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from core.db import get_db_connection
from core.logger import log_event
from core.audit_logger import get_audit_logger
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
        """)
        
        self.audit_logger = get_audit_logger()
        
        layout = QVBoxLayout()
        
        title = QLabel("User Management")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(["Username", "Email", "Role", "Actions"])
        layout.addWidget(self.user_table)
        
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add User")
        add_btn.clicked.connect(self.add_user)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Edit Selected")
        edit_btn.clicked.connect(self.edit_user)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_user)
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.load_users()
    
    def load_users(self):
        """Load users from database."""
        try:
            db = get_db_connection()
            cursor = db.cursor()
            cursor.execute("SELECT username, email, role FROM users LIMIT 10")
            users = cursor.fetchall()
            cursor.close()
            db.close()
            
            self.user_table.setRowCount(len(users) if users else 0)
            if users:
                for row, user in enumerate(users):
                    for col, value in enumerate(user):
                        self.user_table.setItem(row, col, QTableWidgetItem(str(value)))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load users: {str(e)}")
    
    def add_user(self):
        """Add new user."""
        self.audit_logger.log_action(
            username="admin",
            action="ADMIN_ACTION",
            details={"action": "open_add_user_dialog"},
            is_important=True
        )
        QMessageBox.information(self, "Add User", "User addition dialog would open here")
    
    def edit_user(self):
        """Edit selected user."""
        self.audit_logger.log_action(
            username="admin",
            action="ADMIN_ACTION",
            details={"action": "open_edit_user_dialog"},
            is_important=True
        )
        QMessageBox.information(self, "Edit User", "User edit dialog would open here")
    
    def delete_user(self):
        """Delete selected user."""
        self.audit_logger.log_action(
            username="admin",
            action="USER_DELETE",
            details={"action": "delete_user_request"},
            is_important=True
        )
        reply = QMessageBox.question(self, "Delete User", "Are you sure?")
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Deleted", "User would be deleted here")