from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt

from core.signup_manager import SignupManager
from windows.role_select_popup import RoleSelectPopup

class AdminSignupTab(QWidget):
    def __init__(self):
        super().__init__()

        self.manager = SignupManager()

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Signup Requests")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Username"])
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)

        self.approve_btn = QPushButton("Approve")
        self.approve_btn.clicked.connect(self.approve_selected)
        btn_layout.addWidget(self.approve_btn)

        self.decline_btn = QPushButton("Decline")
        self.decline_btn.clicked.connect(self.decline_selected)
        btn_layout.addWidget(self.decline_btn)

        self.load_requests()

    def load_requests(self):
        requests = self.manager.get_all_requests()
        self.table.setRowCount(len(requests))

        for row, req in enumerate(requests):
            self.table.setItem(row, 0, QTableWidgetItem(str(req["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(req["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(req["email"]))
            self.table.setItem(row, 3, QTableWidgetItem(req["desired_username"]))

    def get_selected_request_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def approve_selected(self):
        req_id = self.get_selected_request_id()
        if not req_id:
            QMessageBox.warning(self, "Error", "No request selected.")
            return

        popup = RoleSelectPopup()
        from PySide6.QtWidgets import QDialog

        if popup.exec() != QDialog.DialogCode.Accepted:
            return

        role = popup.selected_role

        success, message = self.manager.approve_request(req_id, role)

        if success:
            QMessageBox.information(self, "Approved", "Signup request approved.")
            self.load_requests()
        else:
            QMessageBox.critical(self, "Error", f"Failed to approve: {message}")

    def decline_selected(self):
        req_id = self.get_selected_request_id()
        if not req_id:
            QMessageBox.warning(self, "Error", "No request selected.")
            return

        success, message = self.manager.decline_request(req_id)

        if success:
            QMessageBox.information(self, "Declined", "Signup request declined.")
            self.load_requests()
        else:
            QMessageBox.critical(self, "Error", f"Failed to decline: {message}")
