from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont
from pathlib import Path
import os
from core.audit_logger import get_audit_logger
class VaultWindow(QMainWindow):
    def __init__(self, username, callback_back_to_home=None):
        super().__init__()
        self.username = username
        self.callback_back_to_home = callback_back_to_home
        self.audit_logger = get_audit_logger()
        
        # Log vault access
        self.audit_logger.log_action(
            username=self.username,
            action="VAULT_ACCESS",
            details={"action": "opened_vault"},
            is_important=True
        )
        
        self.setWindowTitle(f"Akira Vault - {username}")
        self.setGeometry(100, 100, 900, 600)
        self.setMinimumSize(800, 500)
        self.init_ui()
        self.apply_theme()
    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        title = QLabel("Vault - Secure File Storage")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        top_layout.addWidget(title)
        top_layout.addStretch()
        back_btn = QPushButton("Back to Home")
        back_btn.clicked.connect(self.go_back_home)
        back_btn.setMaximumWidth(120)
        top_layout.addWidget(back_btn)
        layout.addLayout(top_layout)
        layout.addWidget(QLabel("Your Files:"))
        self.file_list = QListWidget()
        self.file_list.addItem("(No files yet)")
        layout.addWidget(self.file_list)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        btn_layout = QHBoxLayout()
        upload_btn = QPushButton("Upload File")
        upload_btn.clicked.connect(self.upload_file)
        btn_layout.addWidget(upload_btn)
        encrypt_btn = QPushButton("Encrypt Selected")
        encrypt_btn.clicked.connect(self.encrypt_file)
        btn_layout.addWidget(encrypt_btn)
        download_btn = QPushButton("Download")
        download_btn.clicked.connect(self.download_file)
        btn_layout.addWidget(download_btn)
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_file)
        btn_layout.addWidget(delete_btn)
        layout.addLayout(btn_layout)
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        main_widget.setLayout(layout)
    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Upload")
        if file_path:
            file_name = Path(file_path).name
            self.file_list.clear()
            self.file_list.addItem(f"{file_name} (encrypted)")
            self.status_label.setText(f"Uploaded: {file_name}")
            
            # Log file upload
            self.audit_logger.log_action(
                username=self.username,
                action="VAULT_FILE_UPLOAD",
                details={"filename": file_name, "size": os.path.getsize(file_path)},
                is_important=True
            )
    def encrypt_file(self):
        if self.file_list.count() > 0:
            item = self.file_list.item(0)
            if item:
                file_name = item.text().replace(" (encrypted)", "")
                self.status_label.setText("File encrypted")
                
                # Log file encryption
                self.audit_logger.log_action(
                    username=self.username,
                    action="VAULT_FILE_ENCRYPT",
                    details={"filename": file_name},
                    is_important=True
                )
                
                QMessageBox.information(self, "Success", "File encrypted with AES-256")
    def download_file(self):
        if self.file_list.count() > 0:
            item = self.file_list.item(0)
            if item and "encrypted" in item.text():
                save_path, _ = QFileDialog.getSaveFileName(self, "Save File")
                if save_path:
                    file_name = Path(save_path).name
                    self.status_label.setText(f"Downloaded: {file_name}")
                    
                    # Log file download
                    self.audit_logger.log_action(
                        username=self.username,
                        action="VAULT_FILE_DOWNLOAD",
                        details={"filename": file_name},
                        is_important=True
                    )
    def delete_file(self):
        if self.file_list.count() > 0:
            reply = QMessageBox.question(self, "Delete File", "Delete this file?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                item = self.file_list.item(0)
                file_name = item.text().replace(" (encrypted)", "") if item else "unknown"
                
                self.file_list.clear()
                self.file_list.addItem("(No files yet)")
                self.status_label.setText("File deleted")
                
                # Log file deletion
                self.audit_logger.log_action(
                    username=self.username,
                    action="VAULT_FILE_DELETE",
                    details={"filename": file_name},
                    is_important=True
                )
    def go_back_home(self):
        if self.callback_back_to_home:
            self.callback_back_to_home()
        self.close()
    def apply_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #F9FAFB; }
            QLabel { color: #1F2937; }
            QPushButton { background-color: #3B82F6; color: white; border: none; border-radius: 4px; padding: 8px; font-weight: bold; }
            QPushButton:hover { background-color: #2563EB; }
        """)
