from pathlib import Path
import json
import os
from core.config import AppConfig
from core.gui_generator import UIThemeAnalyzer
from core.gui_generator import (
    TEMPLATE_GUI_MAIN,
    TEMPLATE_MAIN_WINDOW_WITH_HISTORY,
    TEMPLATE_MAIN_WINDOW_NO_HISTORY,
    TEMPLATE_INSTRUCTOR_WINDOW,
    TEMPLATE_WORKPLACE_WINDOW,
    TEMPLATE_THERAPY_WINDOW,
    TEMPLATE_RESEARCH_WINDOW,
    TEMPLATE_CREATIVE_WINDOW
)

from core.models import log_generated_app
from core.ai_data_store import AIDataStore
from core.offline_ai_store import OfflineProjectStore

TEMPLATE_MAIN = """import sys
from agent import Agent

def main():
    agent = Agent()
    print("AI Ready. Type 'exit' to quit.")

    while True:
        user = input("You: ")
        if user.lower() in ["exit", "quit"]:
            break

        reply = agent.chat(user)
        print("AI:", reply)

if __name__ == "__main__":
    main()
import os
import sys
from pathlib import Path

class Agent:
    def __init__(self):
        config_path = None
        
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            config_path = Path(sys._MEIPASS) / "config.json"
        
        if not config_path or not config_path.exists():
            config_path = Path("config.json")
        
        if not config_path.exists():
            config_path = Path(__file__).parent / "config.json"
        
        if not config_path.exists():
            config_path = Path.cwd() / "config.json"
        
        if not config_path.exists():
            raise FileNotFoundError(f"config.json not found")
        
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        self.client = Groq(api_key=cfg["api_key"])
        self.model = cfg["default_model"]
        self.ai_name = cfg.get("ai_name", "AI Assistant")
        self.ai_id = cfg.get("ai_id", self.ai_name.lower().replace(" ", "_"))
        self.current_person_id = None
        self.current_person_name = None
        self.current_user_id = 1

        self.history = [
            {"role": "system", "content": cfg["system_prompt"]}
        ]
        
        try:
            from core.ai_memory import AIMemory
            self.memory = AIMemory(self.ai_name)
        except:
            self.memory = None
        
        try:
            from core.ai_data_store import AIDataStore
            self.data_store = AIDataStore
            self._load_user_data()
        except:
            self.data_store = None

    def set_person(self, person_id: str, person_name: str):
        self.current_person_id = person_id
        self.current_person_name = person_name
        
        if self.memory:
            context = self.memory.get_context_for_person(person_id)
            if context:
                self.history[0]["content"] += f"\\n\\n[Person Context]\\n{context}"

    def set_user_id(self, user_id: int):
        self.current_user_id = user_id
        self._load_user_data()

    def _load_user_data(self):
        if not self.data_store:
            return
        
        try:
            data = self.data_store.retrieve_ai_data(self.ai_id, self.current_user_id)
            if data and data.get("preferences"):
                prefs_text = json.dumps(data["preferences"], indent=2)
                if "[User Preferences]" not in self.history[0]["content"]:
                    self.history[0]["content"] += f"\\n\\n[User Preferences]\\n{prefs_text}"
        except:
            pass

    def chat(self, message: str) -> str:
        self.history.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history
        )

        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})
        
        if self.data_store:
            try:
                self.data_store.append_ai_interaction(
                    self.ai_id,
                    self.current_user_id,
                    {
                        "user_message": message,
                        "ai_response": reply
                    }
                )
            except:
                pass
        
        if self.memory and self.current_person_id:
            self.memory.update_interaction(
                self.current_person_id,
                self.current_person_name,
                {
                    "question": message,
                    "answer": reply,
                    "topic": message[:50]  # Brief topic
                }
            )
        
        return reply

class ProjectGenerator:
    @staticmethod
    def generate_project(path: Path, description: str, api_key: str, model: str, user_id: int = 1):
        if not path.exists():
            path.mkdir(parents=True)

        ui_config = UIThemeAnalyzer.analyze(description)

        system_prompt = f"""
You are a custom AI assistant.

Purpose: {description}

Rules:
- Be helpful, clear, and structured.
- Explain reasoning when useful.
- Stay focused on the user's request.
        "instructor": TEMPLATE_INSTRUCTOR_WINDOW,
        "workplace": TEMPLATE_WORKPLACE_WINDOW,
        "therapy": TEMPLATE_THERAPY_WINDOW,
        "research": TEMPLATE_RESEARCH_WINDOW,
        "creative": TEMPLATE_CREATIVE_WINDOW,
    }
    
    if ui_type in templates:
        return templates[ui_type]
    elif ui_type == "generic_chat":
        return TEMPLATE_MAIN_WINDOW_WITH_HISTORY
    else:
        return TEMPLATE_MAIN_WINDOW_WITH_HISTORY
