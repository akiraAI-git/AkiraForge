pic_layout = QHBoxLayout()
        pic_layout.addWidget(QLabel("Profile Picture:"))

        self.pic_button = QPushButton()
        self.pic_button.setFixedSize(100, 100)
        self.pic_button.setText("Click to upload\npicture")
        self.pic_button.setStyleSheet("""
            QPushButton {
                border-radius: 50px;
                border: 2px solid #3B82F6;
                background-color: white;
            }
            self, "Select Profile Picture", "",
            "Images (*.jpg *.png *.gif *.webp)"
        )

        if file_path:
            self.profile_pic_path = file_path

            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaledToWidth(100, Qt.TransformationMode.SmoothTransformation)

            circular = QPixmap(100, 100)
            circular.fill(Qt.GlobalColor.transparent)

            from PySide6.QtGui import QPainter
            painter = QPainter(circular)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()

            self.pic_button.setIcon(QIcon(circular))
            self.pic_button.setIconSize(QSize(100, 100))
            self.pic_button.setText("")

    def save_profile(self):
        bio = self.bio_input.toPlainText()

        if len(bio) > 500:
            QMessageBox.warning(self, "Error", "Bio is too long (max 500 characters)")
            return

        QMessageBox.information(self, "Success", "Profile updated successfully!")
        self.close()

    def apply_theme(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #F9FAFB;
            }
            QLabel {
                color: #1F2937;
            }
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QTextEdit {
                background-color: white;
                color: #1F2937;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                padding: 8px;
            }
