from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class RoleSelectPopup(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select User Role")
        self.setMinimumSize(300, 150)

        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("Select role for this user:")
        layout.addWidget(label)

        self.selected_role = None

        user_btn = QPushButton("User")
        admin_btn = QPushButton("Admin")

        user_btn.clicked.connect(lambda: self.choose("user"))
        admin_btn.clicked.connect(lambda: self.choose("admin"))

        layout.addWidget(user_btn)
        layout.addWidget(admin_btn)

    def choose(self, role):
        self.selected_role = role
        self.accept()
