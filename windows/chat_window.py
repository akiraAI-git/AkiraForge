from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QLabel, QScrollArea, QFileDialog
)
from PySide6.QtCore import Qt, QThread, pyqtSignal
from PySide6.QtGui import QKeySequence

from core.groq_agent import StreamingAgent

class CustomQLineEdit(QLineEdit):
    send_signal = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                self.setText(self.text() + "\n")
            else:
                self.send_signal.emit()
        else:
            super().keyPressEvent(event)

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Chat")
        self.setMinimumSize(700, 600)
        self.uploaded_files = []

        layout = QVBoxLayout()

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        self.file_label = QLabel("No files attached")
        self.file_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.file_label)

        input_layout = QHBoxLayout()

        self.input_box = CustomQLineEdit()
        self.input_box.setPlaceholderText("Type message (Enter to send, Shift+Enter for new line)...")
        self.input_box.send_signal.connect(self.send_message)
        input_layout.addWidget(self.input_box)

        file_btn = QPushButton(" Attach File")
        file_btn.setMaximumWidth(100)
        file_btn.clicked.connect(self.attach_file)
        input_layout.addWidget(file_btn)

        send_btn = QPushButton("Send")
        send_btn.setMaximumWidth(80)
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)

        layout.addLayout(input_layout)
        self.setLayout(layout)

        self.thread = None
        self.agent = None

    def attach_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Attach File",
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp);;Text Files (*.txt *.md);;All Files (*)"
        )

        if file_path:
            self.uploaded_files.append(file_path)
            file_name = file_path.split("/")[-1]
            self.file_label.setText(f"Attached: {', '.join([f.split('/')[-1] for f in self.uploaded_files])}")
            self.chat_display.append(f"<i> File attached: {file_name}</i>")

    def send_message(self):
        user_msg = self.input_box.text().strip()
        if not user_msg and not self.uploaded_files:
            return

        msg_display = f"<b>You:</b> {user_msg}"
        if self.uploaded_files:
            msg_display += f"<br><i> Files: {', '.join([f.split('/')[-1] for f in self.uploaded_files])}</i>"

        self.chat_display.append(msg_display)
        self.input_box.clear()
        self.uploaded_files = []
        self.file_label.setText("No files attached")

        self.thread = QThread()
        self.agent = StreamingAgent()
        self.agent.moveToThread(self.thread)

        self.thread.started.connect(lambda: self.agent.send_message(user_msg))
        self.agent.token_received.connect(self.stream_token)
        self.agent.response_finished.connect(self.finish_stream)

        self.thread.start()

        self.chat_display.append("<b>AI:</b> ")
        self.current_ai_text = ""

    def stream_token(self, token: str):
        self.current_ai_text += token
        self._update_last_line(self.current_ai_text)

    def finish_stream(self):
        self.thread.quit()
        self.thread.wait()

    def _update_last_line(self, new_text: str):
