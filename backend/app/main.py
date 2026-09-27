from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.config import settings
from app.database import get_db, check_database_health, engine, Base

# Create tables if any defined
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="IncidentIQ API - AI-powered incident response assistant for DevOps/SRE engineers",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    database: str
    version: str

@app.get("/api/v1/health", response_model=HealthResponse)
def health_check():
    db_ok = check_database_health()
    if not db_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unhealthy", "database": "disconnected", "version": settings.VERSION}
        )
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.VERSION,
    }

@app.get("/")
def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs"
    }
