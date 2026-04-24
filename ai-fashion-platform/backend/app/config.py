"""Application settings — values can be overridden via environment variables
or a .env file (see .env.example)."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Fashion Intelligence Platform"
    version: str = "1.1.0"

    # Database
    database_url: str = "sqlite:///./ai_fashion.db"

    # Auth
    jwt_secret: str = "change-me-in-prod-please-use-a-long-random-string"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24  # 24h

    # AI
    confidence_threshold: float = 0.6

    # ---- LLM integration ---------------------------------------------------
    # Provider: "anthropic" | "openai" | "mock"
    # "mock" uses built-in deterministic generators (no API key needed).
    llm_provider: str = "mock"

    # Set one of these — only the one matching llm_provider is used.
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Model names — override per your account's access.
    # Defaults tuned for speed/cost since we fan out 4 parallel calls/request.
    anthropic_model: str = "claude-haiku-4-5-20251001"
    openai_model: str = "gpt-4o-mini"

    # LLM generation knobs
    llm_max_tokens: int = 1200
    llm_temperature: float = 0.7
    llm_timeout_seconds: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
