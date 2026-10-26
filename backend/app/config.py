from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./conversa.db"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    ai_response_timeout: float = 20.0
    frontend_origin: str = "http://localhost:5173"
    max_message_length: int = 2000
    context_message_limit: int = 10
    intent_confidence_threshold: float = 0.30
    memory_enabled: bool = True
    memory_retention_limit: int = 100
    contradiction_candidate_limit: int = 24
    contradiction_threshold: float = 0.72
    nli_model: str = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
    nli_timeout_seconds: float = 12.0
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
