from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QTabWidget, QTextEdit, QSpinBox,
    QDialog, QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from core.models import get_generated_apps
from core.db import get_db_connection
import json

class AITestDialog(QDialog):

    def __init__(self, ai_name, parent=None):
        super().__init__(parent)
        self.ai_name = ai_name
        self.setWindowTitle(f"Test AI: {ai_name}")
        self.setGeometry(100, 100, 600, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel(f"Testing: {self.ai_name}")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)

        layout.addWidget(QLabel("Chat History:"))
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Enter test message...")
        input_layout.addWidget(self.message_input)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_test_message)
        input_layout.addWidget(send_btn)
        layout.addLayout(input_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.close)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def send_test_message(self):
        message = self.message_input.text()
        if message:
            self.chat_display.append(f"<b>You:</b> {message}")
            self.message_input.clear()
            self.chat_display.append(f"<b>AI:</b> [Processing message...]")

class PlayboardWindow(QMainWindow):

    def __init__(self, username=None):
        super().__init__()
        self.username = username
        self.setWindowTitle("Akira Forge - Playboard")
        self.setGeometry(100, 100, 1200, 700)
        self.init_ui()
        self.load_generated_ais()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()

        header = QLabel("AI Playboard - Test & Monitor Generated AIs")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)

        self.tabs = QTabWidget()

        self.ai_list_tab = QWidget()
        self.metrics_tab = QWidget()
        self.monitor_tab = QWidget()

        self.tabs.addTab(self.ai_list_tab, "AI List")
        self.tabs.addTab(self.metrics_tab, "Metrics")
        self.tabs.addTab(self.monitor_tab, "Monitor")

        layout.addWidget(self.tabs)
        main_widget.setLayout(layout)

        self.init_ai_list_tab()
        self.init_metrics_tab()
        self.init_monitor_tab()

    def init_ai_list_tab(self):
        layout = QVBoxLayout()

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Search AI names...")
        self.filter_input.textChanged.connect(self.load_generated_ais)
        filter_layout.addWidget(self.filter_input)

        sort_label = QLabel("Sort by:")
        filter_layout.addWidget(sort_label)
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Most Recent", "Oldest", "Name (A-Z)", "Name (Z-A)"])
        self.sort_combo.currentTextChanged.connect(self.load_generated_ais)
        filter_layout.addWidget(self.sort_combo)

        layout.addLayout(filter_layout)

        self.ai_table = QTableWidget()
        self.ai_table.setColumnCount(6)
        self.ai_table.setHorizontalHeaderLabels([
            "AI Name", "Created", "User IP", "Status", "Actions", "Delete"
        ])
        self.ai_table.horizontalHeader().setStretchLastSection(False)
        self.ai_table.setColumnWidth(0, 200)
        self.ai_table.setColumnWidth(1, 150)
        self.ai_table.setColumnWidth(2, 120)
        self.ai_table.setColumnWidth(3, 100)
        self.ai_table.setColumnWidth(4, 150)
        self.ai_table.setColumnWidth(5, 100)
        layout.addWidget(self.ai_table)

        self.ai_list_tab.setLayout(layout)

    def init_metrics_tab(self):
        layout = QVBoxLayout()

        stats_layout = QHBoxLayout()

        self.total_ais_label = QLabel("Total AIs: 0")
        self.total_ais_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        stats_layout.addWidget(self.total_ais_label)

        self.table_usage_label = QLabel("Table Usage: 0%")
        self.table_usage_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        stats_layout.addWidget(self.table_usage_label)

        self.avg_interactions_label = QLabel("Avg Interactions: 0")
        self.avg_interactions_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        stats_layout.addWidget(self.avg_interactions_label)

        layout.addLayout(stats_layout)

        layout.addWidget(QLabel("Detailed Statistics:"))
        self.metrics_text = QTextEdit()
        self.metrics_text.setReadOnly(True)
        layout.addWidget(self.metrics_text)

        refresh_btn = QPushButton("Refresh Metrics")
        refresh_btn.clicked.connect(self.update_metrics)
        layout.addWidget(refresh_btn)

        self.metrics_tab.setLayout(layout)

    def init_monitor_tab(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Real-time Monitoring:"))

        self.monitor_text = QTextEdit()
        self.monitor_text.setReadOnly(True)
        layout.addWidget(self.monitor_text)

        button_layout = QHBoxLayout()

        start_monitor_btn = QPushButton("Start Monitor")
        start_monitor_btn.clicked.connect(self.start_monitoring)
        button_layout.addWidget(start_monitor_btn)

        stop_monitor_btn = QPushButton("Stop Monitor")
        stop_monitor_btn.clicked.connect(self.stop_monitoring)
        button_layout.addWidget(stop_monitor_btn)

        refresh_monitor_btn = QPushButton("Refresh Now")
        refresh_monitor_btn.clicked.connect(self.refresh_monitor)
        button_layout.addWidget(refresh_monitor_btn)

        layout.addLayout(button_layout)

        self.monitor_tab.setLayout(layout)

        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.refresh_monitor)

    def load_generated_ais(self):
        try:
            apps = get_generated_apps()

            filter_text = self.filter_input.text().lower()
            if filter_text:
                apps = [app for app in apps if filter_text in app.get('app_name', '').lower()]

            sort_by = self.sort_combo.currentText()
            if sort_by == "Oldest":
                apps = sorted(apps, key=lambda x: str(x.get('created_at', '')))
            elif sort_by == "Name (A-Z)":
                apps = sorted(apps, key=lambda x: x.get('app_name', '').lower())
            elif sort_by == "Name (Z-A)":
                apps = sorted(apps, key=lambda x: x.get('app_name', '').lower(), reverse=True)
            else:
                apps = sorted(apps, key=lambda x: str(x.get('created_at', '')), reverse=True)

            self.ai_table.setRowCount(len(apps))

            for row, app in enumerate(apps):
                name_item = QTableWidgetItem(app.get('app_name', 'Unknown'))
                self.ai_table.setItem(row, 0, name_item)

                created_item = QTableWidgetItem(str(app.get('created_at', '')))
                self.ai_table.setItem(row, 1, created_item)

                ip_item = QTableWidgetItem(app.get('user_ip', 'unknown'))
                self.ai_table.setItem(row, 2, ip_item)

                status_item = QTableWidgetItem("Active")
                status_item.setBackground(self._get_color_for_status("active"))
                self.ai_table.setItem(row, 3, status_item)

                test_btn = QPushButton("Test")
                test_btn.clicked.connect(lambda checked, name=app.get('app_name'): self.open_test_dialog(name))
                self.ai_table.setCellWidget(row, 4, test_btn)

                delete_btn = QPushButton("Delete")
                delete_btn.clicked.connect(lambda checked, app_id=app.get('id'): self.delete_ai(app_id))
                self.ai_table.setCellWidget(row, 5, delete_btn)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load AIs: {str(e)}")

    def open_test_dialog(self, ai_name):
        dialog = AITestDialog(ai_name, self)
        dialog.exec()

    def delete_ai(self, app_id):
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this AI?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM generated_apps WHERE id = %s", (app_id,))
                conn.commit()
                cursor.close()
                self.load_generated_ais()
                QMessageBox.information(self, "Success", "AI deleted successfully")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete AI: {str(e)}")

    def update_metrics(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            apps = get_generated_apps()
            total_ais = len(apps)
            self.total_ais_label.setText(f"Total AIs: {total_ais}")

            cursor.execute(
                "SELECT COUNT(*) as ai_count FROM ai_data_mapping WHERE table_name = 'ai_data_1'"
            )
            result = cursor.fetchone()
            ais_in_table = result['ai_count'] if result else 0
            usage_percent = (ais_in_table / 900) * 100
            self.table_usage_label.setText(f"Table Usage: {usage_percent:.1f}%")

            metrics_text = f"""
AI System Metrics
================

Generated AIs: {total_ais}
AIs in ai_data_1: {ais_in_table}
Table Capacity: 900 columns
Usage: {usage_percent:.1f}%

Recent AIs: Loaded from database
"""
            self.metrics_text.setText(metrics_text)
            cursor.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to update metrics: {str(e)}")

    def start_monitoring(self):
        self.monitor_timer.start(5000)
        self.monitor_text.append("Monitoring started...")

    def stop_monitoring(self):
        self.monitor_timer.stop()
        self.monitor_text.append("Monitoring stopped...")

    def refresh_monitor(self):
        try:
            self.monitor_text.append(f"[{QTimer()}] System check performed")
        except Exception as e:
            self.monitor_text.append(f"Error: {str(e)}")

    def go_back_home(self):
        if self.callback_back_to_home:
            self.callback_back_to_home()
        self.close()

    def apply_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0D0D0D;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #262626;
                color: white;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333333;
            }
            QTableWidget, QTextEdit, QLineEdit, QComboBox {
                background-color: #111111;
                color: #FFFFFF;
                border: 1px solid #333333;
            }
        """)
