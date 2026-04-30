from core.config import ConfigManager
from core.multi_llm_router import get_llm_router
from PySide6.QtCore import QObject, Signal

class StreamingAgent(QObject):

    token_received = Signal(str)
    response_finished = Signal()

    def __init__(self):
        super().__init__()
        cfg = ConfigManager.load_config()

        self.router = get_llm_router()
        self.model = cfg.default_model

        self.history = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]

    def send_message(self, message: str):
        try:
            self.history.append({"role": "user", "content": message})

            response = self.router.chat_completion(
                model=self.model,
                messages=self.history
            )

            self.history.append({"role": "assistant", "content": response})
            self.token_received.emit(response)
            self.response_finished.emit()
        except Exception as e:
            error_msg = f"[ERROR] Failed to communicate with LLM: {str(e)}"
            self.token_received.emit(error_msg)
            self.response_finished.emit()
