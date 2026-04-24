from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from pathlib import Path

from core.config import ConfigManager, AppConfig

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Settings")
        self.setMinimumSize(450, 300)

        self.cfg = ConfigManager.load_config()

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Groq API Key:"))
        self.api_input = QLineEdit(self.cfg.api_key)
        layout.addWidget(self.api_input)

        layout.addWidget(QLabel("Default Model:"))
        self.model_input = QLineEdit(self.cfg.default_model)
        layout.addWidget(self.model_input)

        layout.addWidget(QLabel("Default Project Folder:"))
        self.folder_input = QLineEdit(self.cfg.project_directory)
        layout.addWidget(self.folder_input)

        btn_browse = QPushButton("Change Folder")
        btn_browse.clicked.connect(self.pick_folder)
        layout.addWidget(btn_browse)

        btn_reset = QPushButton("Reset to Default Folder")
        btn_reset.clicked.connect(self.reset_folder)
        layout.addWidget(btn_reset)

        btn_save = QPushButton("Save Settings")
        btn_save.clicked.connect(self.save_settings)
        layout.addWidget(btn_save)

        self.setLayout(layout)

    def pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_input.setText(folder)

    def reset_folder(self):
        default = str(Path.home() / "Documents" / "MyAIs")
        self.folder_input.setText(default)

    def save_settings(self):
        new_cfg = AppConfig(
            api_key=self.api_input.text().strip(),
            default_model=self.model_input.text().strip(),
            project_directory=self.folder_input.text().strip()
        )

        ConfigManager.save_config(new_cfg)
        QMessageBox.information(self, "Saved", "Settings updated successfully.")
