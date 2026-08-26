from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="INCIDENTLENS_", env_file=".env", extra="ignore")

    environment: str = "development"
    llm_provider: str = "mock"
    allowed_origins: str = "http://localhost:3000"
    max_body_bytes: int = 16_384
    max_file_bytes: int = 262_144
    rate_limit_per_minute: int = 30
    database_url: str = "sqlite:///./incidentlens.db"
    demo_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[2] / "demo")
    evaluation_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[2] / "evaluation")
    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    @field_validator("llm_provider")
    @classmethod
    def valid_provider(cls, value: str) -> str:
        if value not in {"mock", "openai", "gemini"}:
            raise ValueError("llm_provider must be mock, openai, or gemini")
        return value

    @property
    def origins(self) -> list[str]:
        return [value.strip() for value in self.allowed_origins.split(",") if value.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
