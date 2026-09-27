import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.ai_service import AIIncidentService

client = TestClient(app)

def test_ai_service_analyze_incident_success():
    mock_groq_client = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = json.dumps({
        "probable_root_cause": "Database connection pool exhaustion",
        "recommended_action": "Increase max_connections parameter from 20 to 100",
        "confidence": "high",
        "reasoning": "INC-101 historical incident showed identical Gateway Timeout symptoms and was resolved by expanding the pool.",
        "supporting_historical_incidents": ["INC-101: Payment API database connection timeout"]
    })
    mock_completion.choices = [mock_choice]
    mock_groq_client.chat.completions.create.return_value = mock_completion

    service = AIIncidentService(api_key="gsk_fake_key")
    service._client = mock_groq_client

    with patch("app.ai_service.hindsight_service.recall_memories") as mock_recall:
        mock_recall.return_value = {
            "success": True,
            "results": {"memories": [{"id": "INC-101"}]}
        }

        res = service.analyze_incident(
            service="Payment API",
            error="Connection timeout",
            symptoms="HTTP 504 Gateway Timeout"
        )

        assert res["success"] is True
        assert res["probable_root_cause"] == "Database connection pool exhaustion"
        assert res["confidence"] == "high"
        assert "INC-101" in res["supporting_historical_incidents"][0]

def test_ai_service_missing_api_key_fallback():
    service = AIIncidentService(api_key=None)

    with patch("app.ai_service.hindsight_service.recall_memories") as mock_recall:
        mock_recall.return_value = {"success": True, "results": []}

        res = service.analyze_incident(
            service="Payment API",
            error="Connection timeout",
            symptoms="504 Gateway Timeout"
        )

        assert res["success"] is False
        assert res["confidence"] == "low"
        assert "not configured" in res["error_detail"].lower()

def test_ai_service_json_parse_error_fallback():
    mock_groq_client = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "INVALID_JSON_RESPONSE"
    mock_completion.choices = [mock_choice]
    mock_groq_client.chat.completions.create.return_value = mock_completion

    service = AIIncidentService(api_key="gsk_fake_key")
    service._client = mock_groq_client

    with patch("app.ai_service.hindsight_service.recall_memories") as mock_recall:
        mock_recall.return_value = {"success": True, "results": []}

        res = service.analyze_incident(
            service="Payment API",
            error="Connection timeout",
            symptoms="504 Gateway Timeout"
        )

        assert res["success"] is False
        assert res["confidence"] == "low"
        assert "failed to parse" in res["error_detail"].lower()

def test_analyze_new_incident_api_endpoint():
    with patch("app.routers.incidents.ai_incident_service.analyze_incident") as mock_analyze:
        mock_analyze.return_value = {
            "success": True,
            "service": "Checkout Service",
            "error": "Payment gateway down",
            "probable_root_cause": "Third party payment provider gateway offline",
            "recommended_action": "Switch payment provider fallback flag to Braintree",
            "confidence": "high",
            "reasoning": "Retrieved past incident showed similar third party API outage.",
            "supporting_historical_incidents": ["INC-101: Payment API database connection timeout"]
        }

        response = client.post("/api/v1/incidents/analyze", json={
            "service": "Checkout Service",
            "error": "Payment gateway down",
            "symptoms": "Spike in 502 Bad Gateway responses during checkout"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["probable_root_cause"] == "Third party payment provider gateway offline"

def test_analyze_existing_incident_api_endpoint():
    with patch("app.routers.incidents.hindsight_service.recall_memories") as mock_recall, \
         patch("app.routers.incidents.ai_incident_service.analyze_incident") as mock_analyze:

        mock_recall.return_value = {"success": True, "results": []}
        mock_analyze.return_value = {
            "success": True,
            "service": "Payment API",
            "error": "Database connection timeout",
            "probable_root_cause": "Database connection pool exhaustion",
            "recommended_action": "Increase connection pool size",
            "confidence": "high",
            "reasoning": "Historical evidence match.",
            "supporting_historical_incidents": ["INC-101: Payment API database connection timeout"]
        }

        response = client.post("/api/v1/incidents/INC-101/analyze")
        assert response.status_code == 200
        data = response.json()
        assert data["current_incident"]["id"] == "INC-101"
        assert data["recommended_action"] == "Increase connection pool size"
