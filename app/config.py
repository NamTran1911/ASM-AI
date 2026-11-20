import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Order Management AI System"
    ENVIRONMENT: str = "development"
    
    # Database URL: ho tro Supabase Postgres (Supavisor port 6543) hoac SQLite
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./orders.db")
    
    # Bao mat API
    API_KEY: str = os.getenv("API_KEY", "")
    REQUIRE_API_KEY: bool = os.getenv("REQUIRE_API_KEY", "false").lower() in ("true", "1", "yes")

    # Cau hinh LLM: Ho tro ca Google AI Studio va OpenAI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.5-flash-lite")
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai/"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

# Xu ly prefix postgres:// thanh postgresql:// cho SQLAlchemy
if settings.DATABASE_URL.startswith("postgres://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres://", "postgresql://", 1)
