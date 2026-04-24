import json
from pathlib import Path
from dataclasses import dataclass, asdict

CONFIG_PATH = Path("config.json")

@dataclass
class AppConfig:
    api_key: str = ""
    default_model: str = "llama-3.1-8b-instant"
    project_directory: str = str(Path.home() / "Documents" / "MyAIs")

class ConfigManager:
    @staticmethod
    def ensure_config():
        if not CONFIG_PATH.exists():
            ConfigManager.save_config(AppConfig())

    @staticmethod
    def load_config() -> AppConfig:
        if not CONFIG_PATH.exists():
            ConfigManager.ensure_config()
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return AppConfig(**data)

    @staticmethod
    def save_config(config: AppConfig):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(asdict(config), f, indent=2)
