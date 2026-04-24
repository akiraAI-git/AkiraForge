from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt

class PremiumWindow(QMainWindow):

    def __init__(self, username=None, callback_back_to_home=None):
        super().__init__()
        self.username = username
        self.callback_back_to_home = callback_back_to_home

        self.setWindowTitle("Akira Forge - All Features Free!")
        self.setGeometry(100, 100, 600, 300)

        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel(" All Premium Features Are Now FREE!")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #60A5FA;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        info = QLabel("Enjoy unlimited access to all features:\n\n"
                      " Unlimited conversations\n"
                      " Unlimited AI creation\n"
                      " Marketplace access\n"
                      " Code editor\n"
                      " Everything else\n\n"
                      "No upgrades needed. Everything is included!")
        info.setStyleSheet("font-size: 13px; color: #FFFFFF;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        layout.addStretch()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

class SubscriptionPlan:
    pass
