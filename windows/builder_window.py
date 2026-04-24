from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QMessageBox, QProgressBar, QTextEdit, QInputDialog
)
from PySide6.QtCore import Qt, QThread, Signal
from pathlib import Path

from core.project_generator import ProjectGenerator
from core.build_exe import build_exe

class GenerateProjectWorker(QThread):
    progress = Signal(int)
    finished = Signal(bool, str, str)  # success, message, path

    def __init__(self, project_path, description, api_key, model, user_id):
        super().__init__()
        self.project_path = project_path
        self.description = description
        self.api_key = api_key
        self.model = model
        self.user_id = user_id

    def run(self):
        try:
            self.progress.emit(10)
            self.progress.emit(20)

            self.progress.emit(50)
            generated_path = ProjectGenerator.generate_project(
                self.project_path, self.description, self.api_key, self.model, self.user_id
            )

            self.progress.emit(90)
            self.progress.emit(100)
            self.finished.emit(True, "Project generated successfully!", str(generated_path))
        except Exception as e:
            self.finished.emit(False, str(e), "")

class BuildExeWorker(QThread):
    progress = Signal(int)
    finished = Signal(bool, str)

    def __init__(self, project_path: Path, exe_name: str, icon_path: Path):
        super().__init__()
        self.project_path = project_path
        self.exe_name = exe_name
        self.icon_path = icon_path

    def run(self):
        try:
            self.progress.emit(10)
            build_exe(self.project_path, self.exe_name, self.icon_path)
            self.progress.emit(100)
            self.finished.emit(True, "Build completed successfully.")
        except Exception as e:
            self.finished.emit(False, str(e))

class TestAIWorker(QThread):
    finished = Signal(bool, str)

    def __init__(self, project_path: Path):
        super().__init__()
        self.project_path = project_path

    def run(self):
        try:
            import subprocess
            subprocess.Popen(["python", "main.py"], cwd=self.project_path)
            self.finished.emit(True, "AI launched successfully.")
        except Exception as e:
            self.finished.emit(False, str(e))

class BuilderWindow(QWidget):
    def __init__(self, username=None, back_to_home_callback=None):
        super().__init__()
        self.username = username
        self.back_to_home_callback = back_to_home_callback

        self.setWindowTitle("Akira Forge - AI Project Builder")
        self.setMinimumSize(1000, 700)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar")
        sidebar_widget.setMaximumWidth(250)
        sidebar = QVBoxLayout()
        sidebar.setContentsMargins(15, 20, 15, 20)
        sidebar.setSpacing(10)
        sidebar.setAlignment(Qt.AlignmentFlag.AlignTop)
        sidebar_widget.setLayout(sidebar)
        main_layout.addWidget(sidebar_widget)

        user_label = QLabel(f"Welcome,\n{self.username or 'User'}")
        user_label.setObjectName("title")
        user_label.setStyleSheet("color: #00D4FF; font-size: 14pt;")
        sidebar.addWidget(user_label)

        sidebar.addSpacing(15)

        divider = QLabel("" * 20)
        divider.setAlignment(Qt.AlignmentFlag.AlignCenter)
        divider.setObjectName("muted")
        sidebar.addWidget(divider)

        back_btn = QPushButton("← Back to Home")
        back_btn.clicked.connect(self.back_to_home)
        sidebar.addWidget(back_btn)

        sidebar.addSpacing(10)

        self.generate_btn = QPushButton("Generate AI")
        self.generate_btn.clicked.connect(self.show_generate_ui)
        sidebar.addWidget(self.generate_btn)

        self.build_btn = QPushButton("Build EXE")
        self.build_btn.clicked.connect(self.build_exe_action)
        self.build_btn.setEnabled(False)
        sidebar.addWidget(self.build_btn)

        self.test_btn = QPushButton("Test AI")
        self.test_btn.clicked.connect(self.test_ai_action)
        self.test_btn.setEnabled(False)
        sidebar.addWidget(self.test_btn)

        sidebar.addSpacing(15)

        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(self.open_settings)
        sidebar.addWidget(self.settings_btn)

        self.other_apps_btn = QPushButton("Other Apps")
        self.other_apps_btn.clicked.connect(self.open_other_apps)
        sidebar.addWidget(self.other_apps_btn)

        sidebar.addStretch()

        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(30, 20, 30, 20)
        content_layout.setSpacing(15)
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget, 1)

        self.project_path_label = QLabel("No project selected")
        self.project_path_label.setObjectName("muted")
        content_layout.addWidget(self.project_path_label)

        self.generate_widget = QWidget()
        generate_layout = QVBoxLayout()
        self.generate_widget.setLayout(generate_layout)

        gen_title = QLabel("Create New AI Project")
        gen_title.setObjectName("title")
        generate_layout.addWidget(gen_title)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Project Name:"))
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("e.g., MyChatbot")
        name_layout.addWidget(self.project_name_input)
        generate_layout.addLayout(name_layout)

        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("AI Purpose:"))
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Describe what your AI should do...")
        self.description_input.setMaximumHeight(100)
        desc_layout.addWidget(self.description_input)
        generate_layout.addLayout(desc_layout)

        self.do_generate_btn = QPushButton("Generate Project")
        self.do_generate_btn.clicked.connect(self.generate_project)
        generate_layout.addWidget(self.do_generate_btn)

        content_layout.addWidget(self.generate_widget)
        self.generate_widget.hide()  # Hide initially

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        content_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setObjectName("muted")
        content_layout.addWidget(self.status_label)

        self.current_project_path = None

    def back_to_home(self):
        if self.back_to_home_callback:
            self.back_to_home_callback()
        self.hide()

    def show_generate_ui(self):
        self.generate_widget.show()
        self.status_label.setText("Fill in the details and click Generate.")

    def generate_project(self):
        name = self.project_name_input.text().strip()
        description = self.description_input.toPlainText().strip()

        if not name or not description:
            QMessageBox.warning(self, "Error", "Please provide both project name and description.")
            return

        from core.config import ConfigManager
        cfg = ConfigManager.load_config()

        if not cfg.api_key:
            QMessageBox.warning(self, "Error", "Please set your Groq API key in Settings first.")
            return

        try:
            user_id = 1  # Default
            if self.username:
                try:
                    from core.db import get_db_connection
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM forge_users WHERE username = %s", (self.username,))
                    result = cursor.fetchone()
                    if result:
                        user_id = result['id']
                    conn.close()
                except Exception as e:
                    print(f"[Builder] Could not fetch user ID: {e}")

            from core.config import AppConfig
            base_dir = Path(cfg.project_directory)
            project_path = base_dir / name

            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText("Generating AI project...")
            self.do_generate_btn.setEnabled(False)

            self.gen_worker = GenerateProjectWorker(
                project_path, description, cfg.api_key, cfg.default_model, user_id
            )
            self.gen_worker.progress.connect(self.progress_bar.setValue)
            self.gen_worker.finished.connect(self.on_generate_finished)
            self.gen_worker.start()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start generation: {str(e)}")
            self.progress_bar.setVisible(False)
            self.do_generate_btn.setEnabled(True)

    def on_generate_finished(self, success, message, path):
        self.do_generate_btn.setEnabled(True)
        if success:
            self.current_project_path = Path(path)
            self.project_path_label.setText(f"Project: {self.current_project_path}")
            self.build_btn.setEnabled(True)
            self.test_btn.setEnabled(True)
            self.generate_widget.hide()
            self.status_label.setText("Project generated successfully!")
            QMessageBox.information(self, "Success", f"AI project created at:\n{path}")
        else:
            self.status_label.setText(f"Error: {message}")
            QMessageBox.critical(self, "Error", f"Failed to generate project: {message}")

        self.progress_bar.setVisible(False)

    def build_exe_action(self):
        if not self.current_project_path:
            QMessageBox.warning(self, "Error", "No project selected.")
            return

        exe_name, ok = QInputDialog.getText(self, "EXE Name", "Enter executable name:", text=f"{self.current_project_path.name}.exe")
        if not ok or not exe_name.strip():
            return

        icon_path, _ = QFileDialog.getOpenFileName(self, "Select Icon", "", "Icon Files (*.ico *.png)")
        if not icon_path:
            icon_path = str(Path("assets/app_icon.png"))  # Default icon

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Building EXE...")

        self.build_worker = BuildExeWorker(self.current_project_path, exe_name, Path(icon_path))
        self.build_worker.progress.connect(self.progress_bar.setValue)
        self.build_worker.finished.connect(self.on_build_finished)
        self.build_worker.start()

    def on_build_finished(self, success, message):
        self.progress_bar.setVisible(False)
        self.status_label.setText(message)
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)

    def test_ai_action(self):
        if not self.current_project_path:
            QMessageBox.warning(self, "Error", "No project selected.")
            return

        self.status_label.setText("Launching AI for testing...")

        self.test_worker = TestAIWorker(self.current_project_path)
        self.test_worker.finished.connect(self.on_test_finished)
        self.test_worker.start()

    def on_test_finished(self, success, message):
        self.status_label.setText(message)
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)

    def open_settings(self):
        from windows.settings_window import SettingsWindow
        self.settings_window = SettingsWindow()
        self.settings_window.show()

    def open_other_apps(self):
        from windows.other_apps_window import OtherAppsWindow
        self.other_apps_window = OtherAppsWindow()
        self.other_apps_window.show()
