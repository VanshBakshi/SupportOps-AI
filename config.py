from functools import lru_cache
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    app_name: str = "SupportOps AI"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-development"
    database_url: str = "sqlite:///./supportops.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    llm_provider: str = "none"
    openai_api_key: str = ""
    gemini_api_key: str = ""
    model_directory: str = str(ROOT / "ai" / "models")
    model_confidence_threshold: float = 0.70

    model_config = SettingsConfigDict(env_file=ROOT / "backend" / ".env", extra="ignore", case_sensitive=False)

    @field_validator("llm_provider")
    @classmethod
    def valid_provider(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in {"none", "openai", "gemini"}:
            raise ValueError("llm_provider must be none, openai, or gemini")
        return v

    @property
    def cors_list(self):
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
