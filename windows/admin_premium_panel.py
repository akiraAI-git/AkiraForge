from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class AdminPremiumPanel(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Premium Management - Disabled")
        self.setGeometry(200, 200, 500, 300)
        self.setModal(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel(" Premium Management Disabled")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #60A5FA;")
        layout.addWidget(title)

        info = QLabel("All Premium Features Are Now FREE\n\n"
                      "There is no longer a need to manage premium users.\n"
                      "Everyone has unlimited access to all features!\n\n"
                      " All features free\n"
                      " No upgrades needed\n"
                      " Unlimited for everyone")
        info.setStyleSheet("color: #FFFFFF; font-size: 11px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        layout.addStretch()
        self.setLayout(layout)

    def init_ui(self):
        pass

    def verify_admin(self):
        pass

    def add_premium_user(self):
        pass

    def remove_premium_user(self):
        pass

    def apply_theme(self):
        pass
