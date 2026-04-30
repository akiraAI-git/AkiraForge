from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from windows.builder_window import BuilderWindow
from windows.chat_window import ChatWindow
from windows.settings_window import SettingsWindow

class LauncherWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(500, 400)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo = QLabel()
        pix = QPixmap("assets/company_logo.png")
        if not pix.isNull():
            logo.setPixmap(pix.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Akira Forge")
        title.setStyleSheet("font-size: 22pt; font-weight: bold;")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Build and package your own AI desktop apps")
        subtitle.setStyleSheet("font-size: 10pt;")
        layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_builder = QPushButton("Open AI Builder")
        btn_builder.clicked.connect(self.open_builder)
        layout.addWidget(btn_builder)

        btn_chat = QPushButton("Open Chat Window")
        btn_chat.clicked.connect(self.open_chat)
        layout.addWidget(btn_chat)

        btn_settings = QPushButton("Settings")
        btn_settings.clicked.connect(self.open_settings)
        layout.addWidget(btn_settings)

        btn_exit = QPushButton("Exit")
        btn_exit.clicked.connect(self.close)
        layout.addWidget(btn_exit)

        self.setLayout(layout)

        self.builder_window = None
        self.chat_window = None
        self.settings_window = None

    def open_builder(self):
        self.builder_window = BuilderWindow()
        self.builder_window.show()

    def open_chat(self):
        self.chat_window = ChatWindow()
        self.chat_window.show()

    def open_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()
