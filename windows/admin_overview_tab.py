from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QTimer

from core.overview_manager import OverviewManager
from windows.neon_health_indicator import NeonHealthIndicator

class AdminOverviewTab(QWidget):
    def __init__(self):
        super().__init__()

        self.manager = OverviewManager()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

        title = QLabel("SYSTEM OVERVEIW")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #ff00ff;")
        layout.addWidget(title)

        health_layout = QVBoxLayout()
        health_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.health_circle = NeonHealthIndicator()
        self.health_circle.setFixedSize(180, 180)
        health_layout.addWidget(self.health_circle)

        self.health_text = QLabel("System Health: ...")
        self.health_text.setStyleSheet("font-size: 16px; color: #00fff6; margin-top: 10px;")
        self.health_text.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        health_layout.addWidget(self.health_text)

        layout.addLayout(health_layout)

        grid = QGridLayout()
        grid.setSpacing(20)
        layout.addLayout(grid)

        def neon_label(text):
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 16px; color: #00fff6;")
            return lbl

        self.db_status = neon_label("Database: ...")
        self.db_latency = neon_label("Latency: ...")
        self.total_users = neon_label("Total Users: ...")
        self.locked_users = neon_label("Locked Users: ...")
        self.active_users = neon_label("Active Users: ...")
        self.pending_signups = neon_label("Pending Signups: ...")
        self.pending_pleas = neon_label("Pending Pleas: ...")

        grid.addWidget(self.db_status, 0, 0)
        grid.addWidget(self.db_latency, 0, 1)
        grid.addWidget(self.total_users, 1, 0)
        grid.addWidget(self.locked_users, 1, 1)
        grid.addWidget(self.active_users, 2, 0)
        grid.addWidget(self.pending_signups, 2, 1)
        grid.addWidget(self.pending_pleas, 3, 0)

        refresh_btn = QPushButton("Refresh Status")
        refresh_btn.setStyleSheet("padding: 10px; border: 1px solid #00fff6;")
        refresh_btn.clicked.connect(self.refresh_stats)
        layout.addWidget(refresh_btn)

        timer = QTimer(self)
        timer.timeout.connect(self.refresh_stats)
        timer.start(30000)

        self.refresh_stats()

    def refresh_stats(self):
        data = self.manager.get_overall_health()

        self.health_circle.set_health(data["health"])
        self.health_text.setText(f"System Health: {data['health']}")

        self.db_status.setText(f"Database: {'ONLINE' if data['db_ok'] else 'OFFLINE'}")
        latency = f"{data['latency']:.1f} ms" if data["latency"] else "N/A"
        self.db_latency.setText(f"Latency: {latency}")

        us = data["user_stats"]
        self.total_users.setText(f"Total Users: {us['total_users']}")
        self.locked_users.setText(f"Locked Users: {us['locked_users']}")
        self.active_users.setText(f"Active Users: {us['active_users']}")

        ss = data["signup_stats"]
        self.pending_signups.setText(f"Pending Signups: {ss['pending_signups']}")

        ps = data["plea_stats"]
        self.pending_pleas.setText(f"Pending Pleas: {ps['pending_pleas']}")
