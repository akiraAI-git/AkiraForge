import os
from typing import Optional, Dict, Any, List
from enum import Enum

class LLMProvider(Enum):
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    META = "meta"
    LOCAL = "local"

class LLMConfig:
    GROQ_MODELS = [
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile",
        "mixtral-8x7b-32768",
        "gemma-7b-it"
    ]
    
    OPENAI_MODELS = [
        "gpt-4",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "gpt-4o"
    ]
    
    ANTHROPIC_MODELS = [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-2.1"
    ]
    
    GOOGLE_MODELS = [
        "gemini-2.0-flash",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "palm-2"
    ]
    
    META_MODELS = [
        "llama-3-70b",
        "llama-3-8b",
        "llama-2-70b",
        "llama-2-13b"
    ]
    
    LOCAL_MODELS = [
        "llama2",
        "mistral",
        "neural-chat",
        "dolphin-mixtral"
    ]

class MultiLLMRouter:
    def __init__(self):
        self.groq_client = None
        self.openai_client = None
        self.anthropic_client = None
        self.google_client = None
        self.meta_client = None
        self.local_url = os.getenv("LOCAL_LLM_URL", "http://localhost:11434")
        
        self._init_clients()
    
    def _init_clients(self):
        try:
            if os.getenv("GROQ_API_KEY"):
                from groq import Groq
                self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        except Exception as e:
            print(f"[LLM] Groq initialization failed: {e}")
        
        try:
            if os.getenv("OPENAI_API_KEY"):
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        except Exception as e:
            print(f"[LLM] OpenAI initialization failed: {e}")
        
        try:
            if os.getenv("ANTHROPIC_API_KEY"):
                import anthropic
                self.anthropic_client = anthropic.Anthropic(
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )
        except Exception as e:
            print(f"[LLM] Anthropic initialization failed: {e}")
        
        try:
            if os.getenv("GOOGLE_API_KEY"):
                import google.generativeai as genai
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                self.google_client = genai
        except Exception as e:
            print(f"[LLM] Google initialization failed: {e}")
        
        try:
            if os.getenv("META_API_KEY"):
                from openai import OpenAI
                self.meta_client = OpenAI(
                    api_key=os.getenv("META_API_KEY"),
                    base_url="https://api.llama-api.com"
                )
        except Exception as e:
            print(f"[LLM] Meta initialization failed: {e}")
    
    def detect_provider(self, model: str) -> LLMProvider:
        model_lower = model.lower()
        
        for groq_model in LLMConfig.GROQ_MODELS:
            if groq_model.lower() in model_lower or model_lower in groq_model.lower():
                return LLMProvider.GROQ
        
        for openai_model in LLMConfig.OPENAI_MODELS:
            if openai_model.lower() in model_lower or model_lower in openai_model.lower():
                return LLMProvider.OPENAI
        
        for anthropic_model in LLMConfig.ANTHROPIC_MODELS:
            if anthropic_model.lower() in model_lower or model_lower in anthropic_model.lower():
                return LLMProvider.ANTHROPIC
        
        for google_model in LLMConfig.GOOGLE_MODELS:
            if google_model.lower() in model_lower or model_lower in google_model.lower():
                return LLMProvider.GOOGLE
        
        for meta_model in LLMConfig.META_MODELS:
            if meta_model.lower() in model_lower or model_lower in meta_model.lower():
                return LLMProvider.META
        
        for local_model in LLMConfig.LOCAL_MODELS:
            if local_model.lower() in model_lower or model_lower in local_model.lower():
                return LLMProvider.LOCAL
        
        return LLMProvider.GROQ
    
    def chat_completion(self, model: str, messages: List[Dict], **kwargs) -> str:
        provider = self.detect_provider(model)
        
        if provider == LLMProvider.GROQ:
            return self._groq_chat(model, messages, **kwargs)
        elif provider == LLMProvider.OPENAI:
            return self._openai_chat(model, messages, **kwargs)
        elif provider == LLMProvider.ANTHROPIC:
            return self._anthropic_chat(model, messages, **kwargs)
        elif provider == LLMProvider.GOOGLE:
            return self._google_chat(model, messages, **kwargs)
        elif provider == LLMProvider.META:
            return self._meta_chat(model, messages, **kwargs)
        elif provider == LLMProvider.LOCAL:
            return self._local_chat(model, messages, **kwargs)
        else:
            return self._groq_chat(model, messages, **kwargs)
    
    def _groq_chat(self, model: str, messages: List[Dict], **kwargs) -> str:
        if not self.groq_client:
            raise RuntimeError("Groq client not initialized. Set GROQ_API_KEY environment variable.")
        
        try:
            response = self.groq_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1024),
                **{k: v for k, v in kwargs.items() if k not in ["temperature", "max_tokens"]}
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[Groq] Error: {e}")
            raise
    
    def _openai_chat(self, model: str, messages: List[Dict], **kwargs) -> str:
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized. Set OPENAI_API_KEY environment variable.")
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1024),
                **{k: v for k, v in kwargs.items() if k not in ["temperature", "max_tokens"]}
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[OpenAI] Error: {e}")
            raise
    
    def _anthropic_chat(self, model: str, messages: List[Dict], **kwargs) -> str:
        if not self.anthropic_client:
            raise RuntimeError("Anthropic client not initialized. Set ANTHROPIC_API_KEY environment variable.")
        
        try:
            system_prompt = None
            filtered_messages = []
            
            for msg in messages:
                if msg.get("role") == "system":
                    system_prompt = msg.get("content")
                else:
                    filtered_messages.append(msg)
            
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=kwargs.get("max_tokens", 1024),
                system=system_prompt,
                messages=filtered_messages,
                temperature=kwargs.get("temperature", 0.7),
            )
            return response.content[0].text
        except Exception as e:
            print(f"[Anthropic] Error: {e}")
            raise
    
    def _google_chat(self, model: str, messages: List[Dict], **kwargs) -> str:
        if not self.google_client:
            raise RuntimeError("Google client not initialized. Set GOOGLE_API_KEY environment variable.")
        
        try:
            genai = self.google_client
            model_obj = genai.GenerativeModel(model)
            
            conversation_text = ""
            for msg in messages:
                role = "User" if msg.get("role") == "user" else "Assistant"
                conversation_text += f"{role}: {msg.get('content')}\n"
            
            response = model_obj.generate_content(
                conversation_text,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get("temperature", 0.7),
                    max_output_tokens=kwargs.get("max_tokens", 1024),
                )
            )
            return response.text
        except Exception as e:
            print(f"[Google] Error: {e}")
            raise
    
    def _meta_chat(self, model: str, messages: List[Dict], **kwargs) -> str:
        if not self.meta_client:
            raise RuntimeError("Meta client not initialized. Set META_API_KEY environment variable.")
        
        try:
            response = self.meta_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1024),
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[Meta] Error: {e}")
            raise
    
    def _local_chat(self, model: str, messages: List[Dict], **kwargs) -> str:
        try:
            import requests
            
            conversation_text = ""
            for msg in messages:
                conversation_text += msg.get("content", "") + " "
            
            response = requests.post(
                f"{self.local_url}/api/generate",
                json={
                    "model": model,
                    "prompt": conversation_text,
                    "stream": False,
                    "temperature": kwargs.get("temperature", 0.7),
                },
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                raise Exception(f"Local LLM error: {response.status_code}")
        except Exception as e:
            print(f"[Local LLM] Error: {e}")
            raise
    
    def get_available_providers(self) -> Dict[str, bool]:
        return {
            "groq": bool(self.groq_client),
            "openai": bool(self.openai_client),
            "anthropic": bool(self.anthropic_client),
            "google": bool(self.google_client),
            "meta": bool(self.meta_client),
            "local": True
        }
    
    def get_models_for_provider(self, provider: str) -> List[str]:
        provider_lower = provider.lower()
        
        if provider_lower == "groq":
            return LLMConfig.GROQ_MODELS
        elif provider_lower == "openai":
            return LLMConfig.OPENAI_MODELS
        elif provider_lower == "anthropic":
            return LLMConfig.ANTHROPIC_MODELS
        elif provider_lower == "google":
            return LLMConfig.GOOGLE_MODELS
        elif provider_lower == "meta":
            return LLMConfig.META_MODELS
        elif provider_lower == "local":
            return LLMConfig.LOCAL_MODELS
        else:
            return []

_router_instance = None

def get_llm_router() -> MultiLLMRouter:
    global _router_instance
    if _router_instance is None:
        _router_instance = MultiLLMRouter()
    return _router_instance
