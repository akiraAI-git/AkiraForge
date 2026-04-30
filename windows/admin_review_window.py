from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QTextEdit,
    QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Qt

class AdminReviewWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.manager = None  # mock mode for now

        self.setWindowTitle("Akira Forge - Admin Review Panel")
        self.setMinimumSize(900, 600)

        layout = QVBoxLayout()

        title = QLabel("Plea Review Panel")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Username", "Identity", "IP", "Timestamp"
        ])
        self.table.cellClicked.connect(self.load_plea_details)
        layout.addWidget(self.table)

        self.details_box = QTextEdit()
        self.details_box.setReadOnly(True)
        layout.addWidget(self.details_box)

        btn_row = QHBoxLayout()

        self.approve_btn = QPushButton("Approve Plea (Unlock)")
        self.approve_btn.clicked.connect(self.approve_plea)
        btn_row.addWidget(self.approve_btn)

        self.deny_btn = QPushButton("Deny Plea")
        self.deny_btn.clicked.connect(self.deny_plea)
        btn_row.addWidget(self.deny_btn)

        layout.addLayout(btn_row)

        self.setLayout(layout)

        self.load_pleas()

        self.selected_plea = None

    def load_pleas(self):
        self.table.setRowCount(0)

        if self.manager is None or not getattr(self.manager, "db_available", False):
            mock = [
                {
                    "id": 1,
                    "username": "test_user",
                    "claimed_identity": "John Doe",
                    "reason": "I forgot my password",
                    "verification_answer": "We met at school",
                    "ip_address": "123.45.67.89",
                    "timestamp": "2026-04-09 10:00:00"
                }
            ]
            pleas = mock
        else:
            self.manager.cursor.execute(
                "SELECT * FROM access_pleas WHERE reviewed=FALSE"
            )
            pleas = self.manager.cursor.fetchall()

        for row_index, plea in enumerate(pleas):
            self.table.insertRow(row_index)
            self.table.setItem(row_index, 0, QTableWidgetItem(str(plea["id"])))
            self.table.setItem(row_index, 1, QTableWidgetItem(plea["username"]))
            self.table.setItem(row_index, 2, QTableWidgetItem(plea["claimed_identity"]))
            self.table.setItem(row_index, 3, QTableWidgetItem(plea["ip_address"]))

            ts = plea.get('timestamp') or plea.get('submitted_at')
            self.table.setItem(row_index, 4, QTableWidgetItem(str(ts)))

        self.pleas = pleas

    def load_plea_details(self, row, col):
        plea = self.pleas[row]
        self.selected_plea = plea

        ts = plea.get('timestamp') or plea.get('submitted_at')

        text = (
            f"Username: {plea['username']}\n"
            f"Identity: {plea['claimed_identity']}\n"
            f"IP Address: {plea['ip_address']}\n"
            f"Timestamp: {ts}\n\n"

            f"Reason:\n{plea['reason']}\n\n"

            f"Verification Answer:\n{plea['verification_answer']}"
        )

        self.details_box.setText(text)

    def approve_plea(self):
        if not self.selected_plea:
            QMessageBox.warning(self, "No Selection", "Select a plea first.")
            return

        plea = self.selected_plea

        if self.manager is None or not getattr(self.manager, "db_available", False):
            QMessageBox.information(self, "Mock Mode", "Plea approved (mock).")
            return

        username = plea["username"]
        ip = plea["ip_address"]

        self.manager.cursor.execute(
            "UPDATE forge_users SET locked_until=NULL, failed_attempts=0 WHERE username=%s",
            (username,)
        )

        self.manager.cursor.execute(
            "DELETE FROM ip_locks WHERE ip_address=%s",
            (ip,)
        )

        self.manager.cursor.execute(
            "UPDATE access_pleas SET reviewed=TRUE, approved=TRUE WHERE id=%s",
            (plea["id"],)
        )

        self.manager.db.commit()

        QMessageBox.information(self, "Approved", "Account + IP unlocked.")
        self.load_pleas()
        self.details_box.clear()

    def deny_plea(self):
        if not self.selected_plea:
            QMessageBox.warning(self, "No Selection", "Select a plea first.")
            return

        plea = self.selected_plea

        if self.manager is None or not getattr(self.manager, "db_available", False):
            QMessageBox.information(self, "Mock Mode", "Plea denied (mock).")
            return

        self.manager.cursor.execute(
            "UPDATE access_pleas SET reviewed=TRUE, approved=FALSE WHERE id=%s",
            (plea["id"],)
        )
        self.manager.db.commit()

        QMessageBox.information(self, "Denied", "Plea denied.")
        self.load_pleas()
        self.details_box.clear()
