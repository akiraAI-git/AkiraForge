def init_ui(self):
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
        self.bio_input.setPlainText(self.bio)
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
        self.profile_btn.setStyleSheet("""
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
                background-color: #1F2937;
                border: 2px solid #374151;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                color: #60A5FA;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #374151;
                border: 2px solid #60A5FA;
            }
            QPushButton:pressed {
                background-color: #4B5563;
            }
            pixmap = QPixmap(self.profile_pic_path)
            pixmap = pixmap.scaledToWidth(100, Qt.TransformationMode.SmoothTransformation)

            from PySide6.QtGui import QBrush, QPalette, QColor, QPainter
            circular = QPixmap(100, 100)
            circular.fill(Qt.GlobalColor.transparent)

            painter = QPainter(circular)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setClipRegion(circular.rect(), Qt.ClipOperation.IntersectClip)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()

            self.profile_btn.setIcon(QIcon(circular))
            self.profile_btn.setIconSize(QSize(100, 100))
            self.profile_btn.setText("")
        else:
            self.profile_btn.setText("")
            self.profile_btn.setIconSize(QSize(100, 100))

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
        self.setStyleSheet("""
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
