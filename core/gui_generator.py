CONVERSATION_KEYWORDS = [
        "workplace", "business", "professional", "consultant", "tutor",
        "coach", "assistant", "advisor", "therapist", "counselor",
        "learning", "education", "help", "support", "guide"
    ]

    PLAYFUL_KEYWORDS = ["kid", "children", "kindergarten", "fun", "game", "play", "cartoon", "silly"]
    PROFESSIONAL_KEYWORDS = ["business", "workplace", "corporate", "finance", "legal", "medical", "professional"]
    CREATIVE_KEYWORDS = ["artist", "designer", "creative", "music", "art", "writer", "storyteller"]
    MINIMAL_KEYWORDS = ["simple", "minimal", "task", "quick", "fast", "efficient"]
    TECH_KEYWORDS = ["programmer", "developer", "tech", "code", "software", "engineer"]

    INSTRUCTOR_KEYWORDS = ["teach", "tutor", "instructor", "lesson", "lesson", "coach", "training", "course", "class"]
    WORKPLACE_KEYWORDS = ["workplace", "office", "team", "meeting", "project", "task", "deadline", "workflow"]
    THERAPY_KEYWORDS = ["therapy", "therapist", "counselor", "mental health", "wellness", "support", "coach"]
    RESEARCH_KEYWORDS = ["research", "analysis", "data", "scientist", "academic", "paper", "study"]
    CREATIVE_KEYWORDS_EXTENDED = ["writer", "storyteller", "novelist", "poet", "creative writing"]

    @staticmethod
    def analyze(description: str) -> dict:
        desc_lower = description.lower()

        ui_type = "generic_chat"

        if any(kw in desc_lower for kw in UIThemeAnalyzer.INSTRUCTOR_KEYWORDS):
            ui_type = "instructor"
        elif any(kw in desc_lower for kw in UIThemeAnalyzer.WORKPLACE_KEYWORDS):
            ui_type = "workplace"
        elif any(kw in desc_lower for kw in UIThemeAnalyzer.THERAPY_KEYWORDS):
            ui_type = "therapy"
        elif any(kw in desc_lower for kw in UIThemeAnalyzer.RESEARCH_KEYWORDS):
            ui_type = "research"
        elif any(kw in desc_lower for kw in UIThemeAnalyzer.CREATIVE_KEYWORDS_EXTENDED):
            ui_type = "creative"

        needs_history = any(keyword in desc_lower for keyword in UIThemeAnalyzer.CONVERSATION_KEYWORDS)

        if any(kw in desc_lower for kw in UIThemeAnalyzer.PLAYFUL_KEYWORDS):
            theme = "playful"
            colors = {"primary": "#FF6B9D", "secondary": "#FFA06B", "background": "#FFF8F0"}
            style = "joyful"
        elif any(kw in desc_lower for kw in UIThemeAnalyzer.PROFESSIONAL_KEYWORDS):
            theme = "professional"
            colors = {"primary": "#1E3A8A", "secondary": "#3B82F6", "background": "#F8FAFC"}
            style = "corporate"
        elif any(kw in desc_lower for kw in UIThemeAnalyzer.CREATIVE_KEYWORDS):
            theme = "creative"
            colors = {"primary": "#8B5CF6", "secondary": "#EC4899", "background": "#FAF5FF"}
            style = "artistic"
        elif any(kw in desc_lower for kw in UIThemeAnalyzer.TECH_KEYWORDS):
            theme = "tech"
            colors = {"primary": "#10B981", "secondary": "#06B6D4", "background": "#0F172A"}
            style = "minimal"
        elif any(kw in desc_lower for kw in UIThemeAnalyzer.MINIMAL_KEYWORDS):
            theme = "minimal"
            colors = {"primary": "#6366F1", "secondary": "#8B5CF6", "background": "#FFFFFF"}
            style = "clean"
        else:
            theme = "default"
            colors = {"primary": "#3B82F6", "secondary": "#06B6D4", "background": "#F9FAFB"}
            style = "balanced"

        def is_light(color):
            color = color.lstrip('#')
            r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
            return (r*299 + g*587 + b*114) / 1000 > 186

        background = colors.get("background", "#FFFFFF")
        text_color = "#1F2937" if is_light(background) else "#F9FAFB"
        if (is_light(background) and is_light(text_color)) or (not is_light(background) and not is_light(text_color)):
            colors = {"primary": "#3B82F6", "secondary": "#06B6D4", "background": "#18181B"}
            text_color = "#F9FAFB"

        colors["text"] = text_color

        return {
            "theme": theme,
            "colors": colors,
            "needs_history": needs_history,
            "style": style,
            "ui_type": ui_type,
            "description": description
        }

TEMPLATE_GUI_MAIN = '''import sys
import os
from pathlib import Path

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    sys.path.insert(0, sys._MEIPASS)

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
TEMPLATE_WORKPLACE_WINDOW = '''from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTextEdit, QTabWidget, QTableWidget, QTableWidgetItem, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from agent import Agent
import json
import sys
from pathlib import Path

class MessageInput(QTextEdit):
    def __init__(self, send_callback):
        super().__init__()
        self.send_callback = send_callback
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.NoModifier:
            self.send_callback()
        else:
            super().keyPressEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        config_path = None
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            config_path = Path(sys._MEIPASS) / "config.json"
        if not config_path or not config_path.exists():
            config_path = Path("config.json")
        if not config_path.exists():
            config_path = Path.cwd() / "config.json"
        
        with open(config_path) as f:
            self.config = json.load(f)
        
        self.setWindowTitle(f" {self.config.get('ai_name', 'Workplace Assistant')}")
        self.setMinimumSize(1200, 750)
        self.agent = Agent()
        self.projects = {}
        
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        header_layout = QHBoxLayout()
        header = QLabel(f" {self.config.get('ai_name', 'Workplace')}")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        self.user_label = QLineEdit()
        self.user_label.setPlaceholderText("Your name...")
        self.user_label.setMaximumWidth(200)
        self.user_label.textChanged.connect(self.on_user_changed)
        header_layout.addWidget(self.user_label)
        
        layout.addLayout(header_layout)
        
        tabs = QTabWidget()
        
        projects_widget = QWidget()
        projects_layout = QVBoxLayout()
        self.project_table = QTableWidget()
        self.project_table.setColumnCount(3)
        self.project_table.setHorizontalHeaderLabels(["Project", "Status", "Progress"])
        projects_layout.addWidget(self.project_table)
        projects_widget.setLayout(projects_layout)
        tabs.addTab(projects_widget, " Projects")
        
        tasks_widget = QWidget()
        tasks_layout = QVBoxLayout()
        self.task_display = QTextEdit()
        self.task_display.setReadOnly(True)
        tasks_layout.addWidget(self.task_display)
        tasks_widget.setLayout(tasks_layout)
        tabs.addTab(tasks_widget, " Tasks")
        
        guidance_widget = QWidget()
        guidance_layout = QVBoxLayout()
        
        self.guidance_display = QTextEdit()
        self.guidance_display.setReadOnly(True)
        guidance_layout.addWidget(self.guidance_display)
        
         guidance_input_layout = QHBoxLayout()
         self.query_input = MessageInput(self.ask_for_guidance)
         self.query_input.setMaximumHeight(60)
         self.query_input.setPlaceholderText("Ask about a project or task... (Press Enter to send)")
         guidance_input_layout.addWidget(self.query_input)
        
        ask_btn = QPushButton("Get Guidance")
        ask_btn.clicked.connect(self.ask_for_guidance)
        guidance_input_layout.addWidget(ask_btn)
        
        guidance_layout.addLayout(guidance_input_layout)
        guidance_widget.setLayout(guidance_layout)
        tabs.addTab(guidance_widget, " Guidance")
        
        layout.addWidget(tabs)
    
    def ask_for_guidance(self):
        message = self.query_input.toPlainText().strip()
        if not message:
            return
        
        self.guidance_display.append(f"You: {message}")
        self.query_input.clear()
        
        try:
            response = self.agent.chat(message)
            self.guidance_display.append(f"Assistant: {response}\\n")
        except Exception as e:
            self.guidance_display.append(f"Error: {str(e)}")
    
    def on_user_changed(self, text):
        if hasattr(self.agent, 'set_person') and text.strip():
            self.agent.set_person(f"user_{text}", text)
    
     def apply_theme(self):
         colors = self.config.get("ui_colors", {})
         primary = colors.get("primary", "#1E3A8A")
         background = colors.get("background", "#F8FAFC")
         text_color = colors.get("text", "#1F2937")

         stylesheet = f"""
             QMainWindow {{ background-color: {background}; }}
             QTabWidget {{ background-color: {background}; color: {text_color}; }}
             QTabBar::tab {{ background-color: #E5E7EB; color: {text_color}; padding: 8px; }}
             QTabBar::tab:selected {{ background-color: {primary}; color: white; }}
             QPushButton {{ background-color: {primary}; color: white; border: none; 
                         border-radius: 4px; padding: 8px; font-weight: bold; }}
             QPushButton:hover {{ opacity: 0.8; }}
             QTextEdit {{ background-color: white; color: {text_color}; border: 1px solid #D1D5DB; border-radius: 4px; }}
             QLineEdit {{ background-color: white; color: {text_color}; border: 1px solid #D1D5DB; border-radius: 4px; padding: 4px; }}
             QLabel {{ color: {text_color}; }}
             QTableWidget {{ background-color: white; color: {text_color}; gridline-color: #D1D5DB; }}
             QTableWidget::item {{ padding: 4px; color: {text_color}; }}
