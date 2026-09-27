from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class IncidentBase(BaseModel):
    service: str = Field(..., min_length=1, description="Service name affected by the incident")
    error: str = Field(..., min_length=1, description="Primary error message or exception")
    symptoms: str = Field(..., min_length=1, description="Observable symptoms or impact")
    severity: str = Field(default="medium", description="Severity level (e.g., low, medium, high, critical)")
    root_cause: Optional[str] = Field(default=None, description="Root cause of the incident")
    resolution: Optional[str] = Field(default=None, description="Steps taken to resolve the incident")
    outcome: str = Field(default="Open", description="Current status/outcome (e.g., Open, Investigating, Resolved)")

class IncidentCreate(IncidentBase):
    id: Optional[str] = Field(default=None, description="Optional custom ID, e.g. INC-101. Auto-generated if omitted.")

class IncidentUpdate(BaseModel):
    service: Optional[str] = Field(default=None, min_length=1)
    error: Optional[str] = Field(default=None, min_length=1)
    symptoms: Optional[str] = Field(default=None, min_length=1)
    severity: Optional[str] = None
    root_cause: Optional[str] = None
    resolution: Optional[str] = None
    outcome: Optional[str] = None

class IncidentResolve(BaseModel):
    root_cause: Optional[str] = Field(default=None, description="Root cause identified during resolution")
    resolution: str = Field(..., min_length=1, description="Resolution steps taken")
    outcome: str = Field(default="Resolved", description="Outcome status upon resolution")

class IncidentResponse(IncidentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
