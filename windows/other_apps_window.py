from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt
from core.theme_manager import ThemeManager

class OtherAppsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Akira Forge - Other Apps")
        self.setMinimumSize(800, 600)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(15)
        self.setLayout(main_layout)

        title = QLabel("Akira Forge Ecosystem")
        title.setObjectName("title")
        main_layout.addWidget(title)

        desc = QLabel("Access integrated Akira applications for enhanced productivity")
        desc.setObjectName("subtitle")
        main_layout.addWidget(desc)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QGridLayout()
        scroll_widget.setLayout(scroll_layout)

        notes_btn = self.create_app_button(
            " Akira Notes",
            "Encrypted note-taking with full-text search",
            self.open_akira_notes
        )
        scroll_layout.addWidget(notes_btn, 0, 0)

        vault_btn = self.create_app_button(
            " Akira Vault",
            "Secure file storage and encryption management",
            self.open_akira_vault
        )
        scroll_layout.addWidget(vault_btn, 0, 1)

        assistant_btn = self.create_app_button(
            " Akira AI Assistant",
            "Database-aware AI with user knowledge",
            self.open_akira_assistant
        )
        scroll_layout.addWidget(assistant_btn, 1, 0)

        playboard_btn = self.create_app_button(
            " Akira Playboard",
            "Creative studio for testing and editing AI",
            self.open_akira_playboard
        )
        scroll_layout.addWidget(playboard_btn, 1, 1)

        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        ThemeManager.apply_to_widget(self)

    def create_app_button(self, title, description, callback):
        btn_widget = QWidget()
        btn_widget.setObjectName("card")
        btn_widget.setStyleSheet("""
            QWidget#card {
                background-color: #1A1A1A;
                border: 2px solid #333333;
                border-radius: 8px;
                padding: 15px;
            }
            QWidget#card:hover {
                border: 2px solid #00D4FF;
                background-color: #262626;
            }
