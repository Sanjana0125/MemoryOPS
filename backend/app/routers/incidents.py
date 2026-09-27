import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Incident
from app.schemas import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResolve,
    IncidentResponse,
    MemoryRecallQuery,
    MemoryReflectQuery,
    IncidentAnalysisRequest,
    IncidentAnalysisResponse,
    IncidentInvestigationResponse,
)
from app.hindsight_service import hindsight_service
from app.ai_service import ai_incident_service

router = APIRouter(prefix="/api/v1/incidents", tags=["Incidents"])
legacy_router = APIRouter(prefix="/api/incidents", tags=["Incidents (Legacy Route)"])

def perform_investigation_workflow(incident: Incident) -> IncidentInvestigationResponse:
    # 1. Hindsight RECALL
    recall_query = f"Service: {incident.service} | Error: {incident.error} | Symptoms: {incident.symptoms}"
    recalled = hindsight_service.recall_memories(query=recall_query)

    similar_incidents: List[Dict[str, Any]] = []
    previous_root_causes: List[str] = []
    previous_resolutions: List[str] = []

    if recalled.get("success") and recalled.get("results"):
        results = recalled["results"]
        items = []
        if isinstance(results, dict):
            items = results.get("results", []) or results.get("memories", [])
        elif isinstance(results, list):
            items = results
        elif hasattr(results, "results"):
            items = getattr(results, "results") or []

        for item in items:
            item_dict = item if isinstance(item, dict) else (item.__dict__ if hasattr(item, "__dict__") else {"text": str(item)})
            similar_incidents.append(item_dict)

            text_str = str(item_dict)
            if "Root Cause:" in text_str:
                rc_part = text_str.split("Root Cause:")[1]
                rc = rc_part.split("\\n")[0].split("\n")[0].split("Resolution:")[0].strip(" '\"}\\",)
                if rc and rc not in previous_root_causes:
                    previous_root_causes.append(rc)
            if "Resolution:" in text_str:
                res_part = text_str.split("Resolution:")[1]
                res = res_part.split("\\n")[0].split("\n")[0].strip(" '\"}\\",)
                if res and res not in previous_resolutions:
                    previous_resolutions.append(res)

    # 2. Groq Analysis
    ai_res = ai_incident_service.analyze_incident(
        service=incident.service,
        error=incident.error,
        symptoms=incident.symptoms,
        severity=incident.severity,
    )

    recommended_action = ai_res.get("recommended_action", "Investigate service logs and system metrics.")
    explanation = ai_res.get("reasoning", "Analysis based on current symptoms and historical incident recall.")

    ai_analysis_summary = {
        "probable_root_cause": ai_res.get("probable_root_cause"),
        "confidence": ai_res.get("confidence"),
        "reasoning": ai_res.get("reasoning"),
        "supporting_historical_incidents": ai_res.get("supporting_historical_incidents", []),
    }

    return IncidentInvestigationResponse(
        current_incident=IncidentResponse.model_validate(incident),
        similar_historical_incidents=similar_incidents,
        previous_root_causes=previous_root_causes,
        previous_resolutions=previous_resolutions,
        ai_analysis=ai_analysis_summary,
        recommended_action=recommended_action,
        explanation=explanation,
    )

@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_incident(incident_in: IncidentCreate, db: Session = Depends(get_db)):
    incident_id = incident_in.id
    if incident_id:
        existing = db.query(Incident).filter(Incident.id == incident_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Incident with ID '{incident_id}' already exists."
            )
    else:
        incident_id = f"INC-{uuid.uuid4().hex[:6].upper()}"

    now = datetime.now(timezone.utc)
    incident = Incident(
        id=incident_id,
        service=incident_in.service,
        error=incident_in.error,
        symptoms=incident_in.symptoms,
        severity=incident_in.severity,
        root_cause=incident_in.root_cause,
        resolution=incident_in.resolution,
        outcome=incident_in.outcome,
        created_at=now,
        resolved_at=now if incident_in.outcome.lower() == "resolved" else None,
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    if incident.outcome.lower() == "resolved":
        hindsight_service.retain_incident(
            incident_id=incident.id,
            service=incident.service,
            error=incident.error,
            symptoms=incident.symptoms,
            severity=incident.severity,
            root_cause=incident.root_cause,
            resolution=incident.resolution,
            outcome=incident.outcome,
        )

    return incident

@router.get("", response_model=List[IncidentResponse])
def get_incidents(
    service: Optional[str] = Query(None, description="Filter by service name"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    outcome: Optional[str] = Query(None, description="Filter by outcome/status"),
    db: Session = Depends(get_db),
):
    query = db.query(Incident)
    if service:
        query = query.filter(Incident.service.ilike(f"%{service}%"))
    if severity:
        query = query.filter(Incident.severity.ilike(severity))
    if outcome:
        query = query.filter(Incident.outcome.ilike(outcome))

    return query.order_by(Incident.created_at.desc()).all()

@router.post("/recall")
def recall_similar_incidents(query_in: MemoryRecallQuery):
    search_parts = []
    if query_in.query:
        search_parts.append(query_in.query)
    if query_in.service:
        search_parts.append(f"Service: {query_in.service}")
    if query_in.error:
        search_parts.append(f"Error: {query_in.error}")
    if query_in.symptoms:
        search_parts.append(f"Symptoms: {query_in.symptoms}")

    full_query = " | ".join(search_parts) if search_parts else "historical incidents"

    result = hindsight_service.recall_memories(
        query=full_query,
        tags=query_in.tags,
    )
    return result

@router.post("/reflect")
def reflect_incident_patterns(query_in: MemoryReflectQuery):
    result = hindsight_service.reflect_patterns(
        query=query_in.query,
        context=query_in.context,
    )
    return result

@router.post("/analyze", response_model=IncidentAnalysisResponse)
def analyze_new_incident(analysis_in: IncidentAnalysisRequest):
    return ai_incident_service.analyze_incident(
        service=analysis_in.service,
        error=analysis_in.error,
        symptoms=analysis_in.symptoms,
        severity=analysis_in.severity,
        custom_query=analysis_in.custom_query,
    )

@router.post("/{incident_id}/analyze", response_model=IncidentInvestigationResponse)
@legacy_router.post("/{incident_id}/analyze", response_model=IncidentInvestigationResponse)
def analyze_existing_incident(incident_id: str, db: Session = Depends(get_db)):
    """
    POST /api/incidents/{incident_id}/analyze & POST /api/v1/incidents/{incident_id}/analyze
    Connects Incident -> Hindsight RECALL -> Groq -> Recommendations
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found."
        )

    return perform_investigation_workflow(incident)

@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found."
        )
    return incident

@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: str,
    incident_in: IncidentUpdate,
    db: Session = Depends(get_db),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found."
        )

    update_data = incident_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(incident, field, value)

    if "outcome" in update_data:
        if update_data["outcome"].lower() == "resolved" and not incident.resolved_at:
            incident.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(incident)

    if incident.outcome.lower() == "resolved":
        hindsight_service.retain_incident(
            incident_id=incident.id,
            service=incident.service,
            error=incident.error,
            symptoms=incident.symptoms,
            severity=incident.severity,
            root_cause=incident.root_cause,
            resolution=incident.resolution,
            outcome=incident.outcome,
        )

    return incident

@router.post("/{incident_id}/resolve", response_model=IncidentResponse)
@legacy_router.post("/{incident_id}/resolve", response_model=IncidentResponse)
def resolve_incident(
    incident_id: str,
    resolve_in: IncidentResolve,
    db: Session = Depends(get_db),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found."
        )

    if resolve_in.root_cause:
        incident.root_cause = resolve_in.root_cause
    incident.resolution = resolve_in.resolution
    incident.outcome = resolve_in.outcome
    incident.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(incident)

    hindsight_service.retain_incident(
        incident_id=incident.id,
        service=incident.service,
        error=incident.error,
        symptoms=incident.symptoms,
        severity=incident.severity,
        root_cause=incident.root_cause,
        resolution=incident.resolution,
        outcome=incident.outcome,
    )

    return incident
