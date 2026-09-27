import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "incidentiq.db"

class Settings(BaseModel):
    PROJECT_NAME: str = "IncidentIQ API"
    VERSION: str = "0.1.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

settings = Settings()
