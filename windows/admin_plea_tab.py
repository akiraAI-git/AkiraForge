from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QMessageBox, QTextEdit
)
from PySide6.QtCore import Qt

from core.plea_manager import PleaManager

class AdminPleaTab(QWidget):
    def __init__(self):
        super().__init__()

        self.manager = PleaManager()

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Plea Requests")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ff00ff;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Username", "Claimed Identity", "Reason",
            "Verification Answer", "IP Address"
        ])
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)

        self.approve_btn = QPushButton("Approve Plea")
        self.approve_btn.clicked.connect(self.approve_selected)
        btn_layout.addWidget(self.approve_btn)

        self.decline_btn = QPushButton("Decline Plea")
        self.decline_btn.clicked.connect(self.decline_selected)
        btn_layout.addWidget(self.decline_btn)

        self.detail_view = QTextEdit()
        self.detail_view.setReadOnly(True)
        self.detail_view.setStyleSheet("background-color: #050010; color: #00fff6;")
        layout.addWidget(self.detail_view)

        self.table.itemSelectionChanged.connect(self.update_detail_view)

        self.load_pleas()

    def load_pleas(self):
        pleas = self.manager.get_all_pleas()
        self.table.setRowCount(len(pleas))

        for row, p in enumerate(pleas):
            self.table.setItem(row, 0, QTableWidgetItem(str(p["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(p["username"]))
            self.table.setItem(row, 2, QTableWidgetItem(p["claimed_identity"]))
            self.table.setItem(row, 3, QTableWidgetItem(p["reason"]))
            self.table.setItem(row, 4, QTableWidgetItem(p["verification_answer"]))
            self.table.setItem(row, 5, QTableWidgetItem(p["ip_address"]))

    def get_selected_plea_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return int(self.table.item(row, 0).text())

    def update_detail_view(self):
        row = self.table.currentRow()
        if row < 0:
            self.detail_view.clear()
            return

        username = self.table.item(row, 1).text()
        claimed = self.table.item(row, 2).text()
        reason = self.table.item(row, 3).text()
        verification = self.table.item(row, 4).text()
        ip_addr = self.table.item(row, 5).text()

        text = (
            f"Username: {username}\n"
            f"Claimed Identity: {claimed}\n"
            f"Reason:\n{reason}\n\n"
            f"Verification Answer:\n{verification}\n\n"
            f"IP Address: {ip_addr}\n"
        )
        self.detail_view.setPlainText(text)

    def approve_selected(self):
        plea_id = self.get_selected_plea_id()
        if not plea_id:
            QMessageBox.warning(self, "Error", "No plea selected.")
            return

        ok, msg = self.manager.approve_plea(plea_id)
        if ok:
            QMessageBox.information(self, "Approved", "Plea approved.")
            self.load_pleas()
        else:
            QMessageBox.critical(self, "Error", f"Failed to approve plea: {msg}")

    def decline_selected(self):
        plea_id = self.get_selected_plea_id()
        if not plea_id:
            QMessageBox.warning(self, "Error", "No plea selected.")
            return

        ok, msg = self.manager.decline_plea(plea_id)
        if ok:
            QMessageBox.information(self, "Declined", "Plea declined.")
            self.load_pleas()
        else:
            QMessageBox.critical(self, "Error", f"Failed to decline plea: {msg}")
