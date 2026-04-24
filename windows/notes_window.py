from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
    QTextEdit, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt

from core.notes import NotesManager

class NotesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Akira Forge - Encrypted Notes")
        self.setMinimumSize(700, 500)

        layout = QHBoxLayout()
        self.setLayout(layout)

        left = QVBoxLayout()
        layout.addLayout(left, 1)

        self.list_widget = QListWidget()
        left.addWidget(QLabel("Notes"))
        left.addWidget(self.list_widget)

        btn_row = QHBoxLayout()
        self.btn_new = QPushButton("New")
        self.btn_new.clicked.connect(self.new_note)
        btn_row.addWidget(self.btn_new)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.clicked.connect(self.delete_note)
        btn_row.addWidget(self.btn_delete)

        left.addLayout(btn_row)

        right = QVBoxLayout()
        layout.addLayout(right, 2)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Title")
        right.addWidget(self.title_input)

        self.body_input = QTextEdit()
        right.addWidget(self.body_input)

        action_row = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_note)
        action_row.addWidget(self.save_btn)

        self.unlock_label = QLabel("")
        action_row.addWidget(self.unlock_label)

        right.addLayout(action_row)

        self.manager = NotesManager()
        if not self.manager.enabled():
            self.unlock_label.setText("Notes disabled: set NOTES_PASSPHRASE and NOTES_SALT in environment")
            self.btn_new.setEnabled(False)
            self.save_btn.setEnabled(False)
        else:
            self.reload()

        self.current_note_id = None

    def reload(self):
        self.list_widget.clear()
        notes = self.manager.list_notes()
        for n in notes:
            self.list_widget.addItem(f"{n['id']}: {n['title']}")
        self.list_widget.itemClicked.connect(self.load_selected)

    def load_selected(self, item):
        text = item.text()
        note_id = int(text.split(':', 1)[0])
        note = self.manager.get_note(note_id)
        if note:
            self.current_note_id = note['id']
            self.title_input.setText(note['title'])
            self.body_input.setPlainText(note['body'])

    def new_note(self):
        self.current_note_id = None
        self.title_input.clear()
        self.body_input.clear()

    def save_note(self):
        title = self.title_input.text().strip()
        body = self.body_input.toPlainText().strip()
        if not title and not body:
            QMessageBox.warning(self, "Error", "Note is empty")
            return
        if self.current_note_id:
            self.manager.delete_note(self.current_note_id)
        nid = self.manager.create_note(title, body)
        QMessageBox.information(self, "Saved", f"Note saved (id={nid})")
        self.reload()

    def delete_note(self):
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Select a note first")
            return
        note_id = int(item.text().split(':', 1)[0])
        self.manager.delete_note(note_id)
        QMessageBox.information(self, "Deleted", "Note deleted")
        self.reload()
