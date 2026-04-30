from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMainWindow, QDialog, QFileDialog, QTextEdit
from PySide6.QtGui import QPixmap, QIcon, QColor, QBrush, QPainter
from PySide6.QtCore import Qt, QSize
from pathlib import Path
import json
class ProfileEditWindow(QDialog):
    def __init__(self, username, bio="", profile_pic_path=None, parent=None):
        super().__init__(parent)
        self.username = username
        self.profile_pic_path = profile_pic_path
        self.new_profile_pic = profile_pic_path
        self.setWindowTitle("Edit Profile")
        self.setGeometry(200, 200, 400, 500)
        layout = QVBoxLayout()
        pic_layout = QHBoxLayout()
        self.profile_pic_label = QLabel()
        self.profile_pic_label.setFixedSize(80, 80)
        self.profile_pic_label.setStyleSheet("border-radius: 40px; border: 2px solid #3B82F6; background-color: #1F2937;")
        if self.profile_pic_path and Path(self.profile_pic_path).exists():
            pixmap = QPixmap(self.profile_pic_path).scaledToWidth(80, Qt.TransformationMode.SmoothTransformation)
            self.profile_pic_label.setPixmap(pixmap)
        pic_layout.addWidget(self.profile_pic_label)
        change_pic_btn = QPushButton("Change Picture")
        change_pic_btn.clicked.connect(self.change_profile_picture)
        pic_layout.addWidget(change_pic_btn)
        layout.addLayout(pic_layout)
        layout.addWidget(QLabel(f"Username: {self.username}"))
        layout.addWidget(QLabel("Bio (About Me):"))
        self.bio_input = QTextEdit()
        self.bio_input.setPlainText(bio)
        self.bio_input.setMaximumHeight(150)
        layout.addWidget(self.bio_input)
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    def change_profile_picture(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Profile Picture", "",
            "Image Files (*.jpg *.jpeg *.png *.gif *.webp)"
        )
        if file_path:
            self.new_profile_pic = file_path
            pixmap = QPixmap(file_path).scaledToWidth(80, Qt.TransformationMode.SmoothTransformation)
            self.profile_pic_label.setPixmap(pixmap)
    def get_profile_data(self):
        return {
            "bio": self.bio_input.toPlainText(),
            "profile_picture": self.new_profile_pic
        }
class HomeScreen(QMainWindow):
    def __init__(self, username, callback_launch_forge=None, callback_launch_vault=None,
                 callback_launch_assistant=None, callback_launch_playboard=None,
                 callback_logout=None, callback_update_profile=None):
        super().__init__()
        self.username = username
        self.callback_launch_forge = callback_launch_forge
        self.callback_launch_vault = callback_launch_vault
        self.callback_launch_assistant = callback_launch_assistant
        self.callback_launch_playboard = callback_launch_playboard
        self.callback_logout = callback_logout
        self.callback_update_profile = callback_update_profile
        self.profile_pic_path = self._get_profile_picture()
        self.bio = self._get_bio()
        self.setWindowTitle("Akira Forge - Home")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)
        self.init_ui()
        self.apply_theme()
    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        self.profile_btn = QPushButton()
        self.profile_btn.setFixedSize(120, 120)
        self.profile_btn.setStyleSheet('''
            QPushButton {
                border-radius: 60px;
                border: 3px solid #3B82F6;
                padding: 2px;
                background-color: #1F2937;
                font-size: 40px;
                color: #FFFFFF;
            }
            QPushButton:hover {
                border: 3px solid #60A5FA;
                background-color: #374151;
            }
        ''')
        self.profile_btn.clicked.connect(self.open_profile_editor)
        if self.profile_pic_path and Path(self.profile_pic_path).exists():
            pixmap = QPixmap(self.profile_pic_path)
            pixmap = pixmap.scaledToWidth(100, Qt.TransformationMode.SmoothTransformation)
            circular = QPixmap(100, 100)
            circular.fill(Qt.GlobalColor.transparent)
            painter = QPainter(circular)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            self.profile_btn.setIcon(QIcon(circular))
            self.profile_btn.setIconSize(QSize(100, 100))
            self.profile_btn.setText("")
        else:
            self.profile_btn.setText("👤")
            self.profile_btn.setIconSize(QSize(100, 100))
        top_layout.addWidget(self.profile_btn)
        info_layout = QVBoxLayout()
        username_label = QLabel(f"Welcome, {self.username}!")
        username_label.setStyleSheet("color: #FFFFFF; font-size: 18px; font-weight: bold;")
        info_layout.addWidget(username_label)
        bio_label = QLabel(self.bio if self.bio else "No bio set yet")
        bio_label.setStyleSheet("color: #A0AEC0; font-size: 12px;")
        info_layout.addWidget(bio_label)
        info_layout.addStretch()
        top_layout.addLayout(info_layout)
        layout.addLayout(top_layout)
        separator = QLabel("─" * 50)
        separator.setStyleSheet("color: #374151;")
        layout.addWidget(separator)
        buttons_layout = QVBoxLayout()
        forge_btn = QPushButton("🔨 Builder - Create AI Projects")
        forge_btn.setMinimumHeight(50)
        forge_btn.clicked.connect(self.launch_forge)
        buttons_layout.addWidget(forge_btn)
        vault_btn = QPushButton("🔒 Vault - Manage Credentials")
        vault_btn.setMinimumHeight(50)
        vault_btn.clicked.connect(self.launch_vault)
        buttons_layout.addWidget(vault_btn)
        assistant_btn = QPushButton("🤖 Assistant - Quick Help")
        assistant_btn.setMinimumHeight(50)
        assistant_btn.clicked.connect(self.launch_assistant)
        buttons_layout.addWidget(assistant_btn)
        playboard_btn = QPushButton("🎮 Playboard - Experiments")
        playboard_btn.setMinimumHeight(50)
        playboard_btn.clicked.connect(self.launch_playboard)
        buttons_layout.addWidget(playboard_btn)
        layout.addLayout(buttons_layout)
        layout.addStretch()
        logout_btn = QPushButton("Logout")
        logout_btn.setMinimumHeight(40)
        logout_btn.setStyleSheet('''
            QPushButton {
                background-color: #DC2626;
                color: #FFFFFF;
                border: 1px solid #991B1B;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #991B1B;
                border-color: #7F1D1D;
            }
        ''')
        logout_btn.clicked.connect(self.do_logout)
        layout.addWidget(logout_btn)
        main_widget.setLayout(layout)
    def open_profile_editor(self):
        dialog = ProfileEditWindow(self.username, self.bio, self.profile_pic_path, self)
        if dialog.exec():
            profile_data = dialog.get_profile_data()
            if self.callback_update_profile:
                self.callback_update_profile(self.username, profile_data)
                self.bio = profile_data.get("bio", "")
                if profile_data.get("profile_picture"):
                    self.profile_pic_path = profile_data["profile_picture"]
                self.update_profile_picture_display()
    def update_profile_picture_display(self):
        if self.profile_pic_path and Path(self.profile_pic_path).exists():
            pixmap = QPixmap(self.profile_pic_path).scaledToWidth(100, Qt.TransformationMode.SmoothTransformation)
            circular = QPixmap(100, 100)
            circular.fill(Qt.GlobalColor.transparent)
            painter = QPainter(circular)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            self.profile_btn.setIcon(QIcon(circular))
        else:
            self.profile_btn.setText("👤")
    def launch_forge(self):
        self.hide()
        if self.callback_launch_forge:
            self.callback_launch_forge()
        self.show()
    def launch_vault(self):
        self.hide()
        if self.callback_launch_vault:
            self.callback_launch_vault()
        self.show()
    def launch_assistant(self):
        self.hide()
        if self.callback_launch_assistant:
            self.callback_launch_assistant()
        self.show()
    def launch_playboard(self):
        self.hide()
        if self.callback_launch_playboard:
            self.callback_launch_playboard()
        self.show()
    def do_logout(self):
        if self.callback_logout:
            self.callback_logout()
        self.close()
    def _get_profile_picture(self):
        profile_pic_dir = Path.home() / ".akiraforge" / "profiles"
        profile_pic_dir.mkdir(parents=True, exist_ok=True)
        pic_path = profile_pic_dir / f"{self.username}_profile.jpg"
        if pic_path.exists():
            return str(pic_path)
        return None
    def _get_bio(self):
        profile_file = Path.home() / ".akiraforge" / f"{self.username}_profile.json"
        if profile_file.exists():
            try:
                with open(profile_file) as f:
                    data = json.load(f)
                    return data.get("bio", "")
            except:
                pass
        return ""
    def apply_theme(self):
        self.setStyleSheet('''
            QMainWindow {
                background-color: #0F172A;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                color: #FFFFFF;
                background-color: #374151;
                border: 1px solid #4B5563;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4B5563;
                border-color: #60A5FA;
            }
            QDialog {
                background-color: #0F172A;
            }
            QTextEdit {
                background-color: #1F2937;
                color: #FFFFFF;
                border: 1px solid #374151;
                border-radius: 4px;
                padding: 5px;
            }
        ''')
