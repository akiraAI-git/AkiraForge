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
import json
import os
from pathlib import Path
from groq import Groq

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
                    "answer": reply
                }
            )
        
        return reply
"""

from pathlib import Path
import json
import os

class UIThemeAnalyzer:
    @staticmethod
    def analyze(description: str) -> dict:
        """Analyze description to determine UI theme"""
        keywords_to_theme = {
            "creative": ["creative", "art", "design", "music"],
            "therapy": ["therapy", "mental", "health", "wellness"],
            "research": ["research", "study", "analyze", "academic"],
            "workplace": ["work", "business", "professional", "team"],
            "instructor": ["teach", "learn", "student", "course"]
        }
        
        description_lower = description.lower()
        for theme, keywords in keywords_to_theme.items():
            if any(keyword in description_lower for keyword in keywords):
                return {"type": theme}
        
        return {"type": "generic_chat"}

class OfflineAIStore:
    @staticmethod
    def store_message(ai_id: str, user_id: int, message: dict) -> bool:
        """Store message locally"""
        try:
            store_dir = Path.home() / ".akiraforge" / "ai_store" / ai_id
            store_dir.mkdir(parents=True, exist_ok=True)
            
            messages_file = store_dir / "messages.json"
            messages = []
            
            if messages_file.exists():
                with open(messages_file) as f:
                    messages = json.load(f)
            
            messages.append({
                "user_id": user_id,
                "message": message,
                "timestamp": str(Path.cwd())
            })
            
            with open(messages_file, 'w') as f:
                json.dump(messages, f, indent=2)
            
            return True
        except Exception as e:
            print(f"[OfflineAIStore] Error storing message: {e}")
            return False

class ProjectGenerator:
    @staticmethod
    def generate_project(path: Path, description: str, api_key: str, model: str, user_id: int = 1):
        """Generate a new AI project"""
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
- Maintain context across conversations.
- Be honest about limitations.
"""

        # Create project metadata
        project_config = {
            "name": path.name,
            "description": description,
            "api_key": api_key,
            "model": model,
            "ui_type": ui_config.get("type", "generic_chat"),
            "system_prompt": system_prompt,
            "user_id": user_id,
            "created_at": str(Path.cwd())
        }

        # Save project configuration
        config_file = path / "config.json"
        with open(config_file, 'w') as f:
            json.dump(project_config, f, indent=2)

        # Create empty messages log
        messages_file = path / "messages.json"
        with open(messages_file, 'w') as f:
            json.dump([], f)

        return {
            "path": str(path),
            "config": project_config,
            "status": "created"
        }

    @staticmethod
    def load_project(path: Path) -> dict:
        """Load an existing project"""
        try:
            config_file = path / "config.json"
            if not config_file.exists():
                return None
            
            with open(config_file) as f:
                return json.load(f)
        except Exception as e:
            print(f"[ProjectGenerator] Error loading project: {e}")
            return None

    @staticmethod
    def delete_project(path: Path) -> bool:
        """Delete a project"""
        try:
            import shutil
            if path.exists():
                shutil.rmtree(path)
            return True
        except Exception as e:
            print(f"[ProjectGenerator] Error deleting project: {e}")
            return False
