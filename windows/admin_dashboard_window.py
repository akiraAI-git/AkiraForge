from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QLabel, QMainWindow, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import os

from core.audit_logger import get_audit_logger

class AdminDashboardWindow(QMainWindow):
    def __init__(self, username, back_to_forge_callback=None):
        super().__init__()

        self.username = username
        self.back_to_forge_callback = back_to_forge_callback
        self.offline_mode = not os.getenv("DB_PASSWORD")
        self.audit_logger = get_audit_logger()
        
        # Log admin dashboard access
        self.audit_logger.log_action(
            username=self.username,
            action="ADMIN_ACCESS",
            details={"dashboard": "admin_control_deck"},
            is_important=True
        )

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
        """)
        
        sidebar_layout = QVBoxLayout()
        sidebar_widget.setLayout(sidebar_layout)
        
        title_label = QLabel("Admin Control Panel")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        sidebar_layout.addWidget(title_label)
        sidebar_layout.addSpacing(20)
        
        self.stacked_widget = QStackedWidget()
        
        buttons = [
            ("📊 Overview", None),
            ("📝 Signups", None),
            ("🙏 Pleas", None),
            ("👥 Users", None),
            ("📋 Logs", None),
        ]
        
        # Create tab widgets with error handling
        tab_widgets = {}
        try:
            from windows.admin_overview_tab import AdminOverviewTab
            tab_widgets["overview"] = AdminOverviewTab()
        except Exception as e:
            print(f"[ADMIN] Error loading AdminOverviewTab: {e}")
        
        try:
            from windows.admin_signup_tab import AdminSignupTab
            tab_widgets["signup"] = AdminSignupTab()
        except Exception as e:
            print(f"[ADMIN] Error loading AdminSignupTab: {e}")
        
        try:
            from windows.admin_plea_tab import AdminPleaTab
            tab_widgets["plea"] = AdminPleaTab()
        except Exception as e:
            print(f"[ADMIN] Error loading AdminPleaTab: {e}")
        
        try:
            from windows.admin_user_management_tab import AdminUserManagementTab
            tab_widgets["user_mgmt"] = AdminUserManagementTab()
        except Exception as e:
            print(f"[ADMIN] Error loading AdminUserManagementTab: {e}")
        
        try:
            from windows.admin_logs_tab import AdminLogsTab
            tab_widgets["logs"] = AdminLogsTab()
        except Exception as e:
            print(f"[ADMIN] Error loading AdminLogsTab: {e}")
        
        # Create buttons for available tabs
        tab_keys = ["overview", "signup", "plea", "user_mgmt", "logs"]
        button_info = [
            ("📊 Overview", "overview"),
            ("📝 Signups", "signup"),
            ("🙏 Pleas", "plea"),
            ("👥 Users", "user_mgmt"),
            ("📋 Logs", "logs"),
        ]
        
        for button_label, tab_key in button_info:
            if tab_key in tab_widgets and tab_widgets[tab_key]:
                btn = QPushButton(button_label)
                btn.setMinimumHeight(50)
                widget = tab_widgets[tab_key]
                btn.clicked.connect(lambda checked, w=widget: self.stacked_widget.setCurrentWidget(w))
                sidebar_layout.addWidget(btn)
                self.stacked_widget.addWidget(widget)
            else:
                # Create placeholder for failed tab
                btn = QPushButton(button_label + " (Unavailable)")
                btn.setMinimumHeight(50)
                btn.setEnabled(False)
                sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        back_btn = QPushButton("Back to Forge")
        back_btn.setMinimumHeight(40)
        back_btn.clicked.connect(self.go_back)
        sidebar_layout.addWidget(back_btn)
        
        main_layout.addWidget(sidebar_widget, 1)
        main_layout.addWidget(self.stacked_widget, 4)
    
    def go_back(self):
        if self.back_to_forge_callback:
            self.back_to_forge_callback()
        self.close()
