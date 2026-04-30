from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QTextEdit, QComboBox, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QKeySequence
from datetime import datetime
from pathlib import Path
import os

class MessageInput(QTextEdit):
    def __init__(self, send_callback):
        super().__init__()
        self.send_callback = send_callback

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            self.send_callback()
        else:
            super().keyPressEvent(event)

class AIAssistantWindow(QMainWindow):

    def __init__(self, username, callback_back_to_home=None):
        super().__init__()
        self.username = username
        self.callback_back_to_home = callback_back_to_home
        self.conversations = []
        self.current_conversation = []
        self.uploaded_file_path = None

        self.setWindowTitle(f"Akira AI Assistant - {username}")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(900, 600)

        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QHBoxLayout()

        left_layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        title = QLabel("AI Assistant")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        top_layout.addWidget(title)

        back_btn = QPushButton("← Back to Home")
        back_btn.clicked.connect(self.go_back_home)
        back_btn.setMaximumWidth(120)
        top_layout.addWidget(back_btn)

        left_layout.addLayout(top_layout)

        left_layout.addWidget(QLabel("Conversations:"))
        self.conversation_list = QListWidget()
        self.conversation_list.itemClicked.connect(self.load_conversation)
        left_layout.addWidget(self.conversation_list)

        new_conv_btn = QPushButton("+ New Conversation")
        new_conv_btn.clicked.connect(self.new_conversation)
        left_layout.addWidget(new_conv_btn)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setMaximumWidth(250)

        right_layout = QVBoxLayout()

        prompt_layout = QHBoxLayout()
        prompt_layout.addWidget(QLabel("System Prompt:"))
        self.prompt_combo = QComboBox()
        self.prompt_combo.addItems([
            "General Assistant",
            "Code Helper",
            "Creative Writer",
            "Research Assistant",
            "Business Advisor"
        ])
        prompt_layout.addWidget(self.prompt_combo)
        right_layout.addLayout(prompt_layout)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        right_layout.addWidget(self.chat_display)

        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #FFFFFF; font-size: 11px;")
        right_layout.addWidget(self.file_label)

        input_layout = QHBoxLayout()
        self.message_input = MessageInput(self.send_message)
        self.message_input.setMaximumHeight(80)
        self.message_input.setPlaceholderText("Type your message here... (Press Enter to send, Shift+Enter for newline)")
        input_layout.addWidget(self.message_input)

        upload_btn = QPushButton("Upload File")
        upload_btn.clicked.connect(self.upload_file)
        upload_btn.setMaximumWidth(100)
        input_layout.addWidget(upload_btn)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)
        send_btn.setMaximumWidth(100)
        input_layout.addWidget(send_btn)

        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.export_conversation)
        export_btn.setMaximumWidth(100)
        input_layout.addWidget(export_btn)

        right_layout.addLayout(input_layout)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        layout.addWidget(left_widget)
        layout.addWidget(right_widget, 1)

        main_widget.setLayout(layout)
        self.new_conversation()

    def send_message(self):
        message = self.message_input.toPlainText().strip()
        if not message:
            return

        self.chat_display.append(f"<b>You:</b> {message}")

        if self.uploaded_file_path:
            file_name = Path(self.uploaded_file_path).name
            self.chat_display.append(f"<i>Attached: {file_name}</i>")
            self.uploaded_file_path = None
            self.file_label.setText("No file selected")

        self.current_conversation.append({"role": "user", "content": message})
        self.message_input.clear()

        self.get_ai_response(message)

    def get_ai_response(self, message):
        try:
            from core.groq_agent import StreamingAgent
            agent = StreamingAgent()
            response = agent.send_message(message)
            self.chat_display.append(f"<b>AI:</b> {response}")
            self.current_conversation.append({"role": "assistant", "content": response})
        except Exception as e:
            self.chat_display.append(f"<b>Error:</b> {str(e)}")

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "",
            "All Files (*);;Images (*.jpg *.png);;Documents (*.txt *.pdf);;Code (*.py *.js)"
        )
        if file_path:
            self.uploaded_file_path = file_path
            file_name = Path(file_path).name
            self.file_label.setText(f"Ready to send: {file_name}")

    def new_conversation(self):
        if self.current_conversation:
            self.conversations.append(self.current_conversation)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            item = QListWidgetItem(f"Chat - {timestamp}")
            self.conversation_list.addItem(item)

        self.current_conversation = []
        self.chat_display.clear()
        self.chat_display.setText("New conversation started...")

    def load_conversation(self, item):
        index = self.conversation_list.row(item)
        if 0 <= index < len(self.conversations):
            self.current_conversation = self.conversations[index]
            self.chat_display.clear()
            for msg in self.current_conversation:
                role = "You" if msg["role"] == "user" else "AI"
                self.chat_display.append(f"<b>{role}:</b> {msg['content']}")

    def export_conversation(self):
        if not self.current_conversation:
            QMessageBox.warning(self, "Empty", "No conversation to export")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Export Conversation", "conversation.txt")
        if save_path:
            with open(save_path, 'w') as f:
                for msg in self.current_conversation:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    f.write(f"{role}: {msg['content']}\n\n")
            QMessageBox.information(self, "Success", "Conversation exported!")

    def go_back_home(self):
        if self.callback_back_to_home:
            self.callback_back_to_home()
        self.close()

    def apply_theme(self):
        self.setStyleSheet("""
            QMainWindow {
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
            QListWidget {
                background-color: white;
                color: #1F2937;
                border: 1px solid #E5E7EB;
            }
            QComboBox {
                background-color: white;
                color: #1F2937;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                padding: 5px;
            }
