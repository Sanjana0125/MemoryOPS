import os
from pathlib import Path
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "incidentiq.db"

def get_cors_origins() -> list[str]:
    cors_env = os.getenv("CORS_ORIGINS")
    if cors_env:
        return [origin.strip() for origin in cors_env.split(",") if origin.strip()]
    return [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

class Settings(BaseModel):
    PROJECT_NAME: str = "IncidentIQ API"
    VERSION: str = "0.1.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
    CORS_ORIGINS: list[str] = Field(default_factory=get_cors_origins)
    HINDSIGHT_API_URL: str = os.getenv("HINDSIGHT_API_URL", "http://localhost:8888")
    HINDSIGHT_API_KEY: str | None = os.getenv("HINDSIGHT_API_KEY", None)
    HINDSIGHT_BANK_ID: str = os.getenv("HINDSIGHT_BANK_ID", "incidentiq")
    GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY", None)
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

settings = Settings()
