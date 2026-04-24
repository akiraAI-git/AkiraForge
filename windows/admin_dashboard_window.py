from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QLabel, QMainWindow, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import os

from windows.admin_overview_tab import AdminOverviewTab
from windows.admin_signup_tab import AdminSignupTab
from windows.admin_plea_tab import AdminPleaTab
from windows.admin_user_management_tab import AdminUserManagementTab
from windows.admin_logs_tab import AdminLogsTab

class AdminDashboardWindow(QMainWindow):
    def __init__(self, username, back_to_forge_callback=None):
        super().__init__()

        self.username = username
        self.back_to_forge_callback = back_to_forge_callback
        self.offline_mode = not os.getenv("DB_PASSWORD")

        self.setWindowTitle("Akira Forge - Admin Control Deck")
        self.setMinimumSize(1400, 850)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        sidebar_widget = QFrame()
        sidebar_widget.setStyleSheet("""
            QFrame {
                background-color: #1F2937;
                border-right: 1px solid #374151;
            }
                background-color: #0F172A;
            }
            QFrame {
                background-color: #0F172A;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #1F2937;
                color: #FFFFFF;
                border: 1px solid #374151;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #374151;
                border-color: #4B5563;
                color: #60A5FA;
            }
            QPushButton:pressed {
                background-color: #4B5563;
            }
            QWidget {
                background-color: #0F172A;
            }
