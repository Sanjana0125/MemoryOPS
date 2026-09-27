from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.hindsight_service import HindsightService

client = TestClient(app)

def test_hindsight_service_retain():
    mock_client = MagicMock()
    mock_client.retain.return_value = {"status": "ok", "id": "mem-123"}

    service = HindsightService(base_url="http://localhost:8888", bank_id="testbank")
    service._client = mock_client

    res = service.retain_incident(
        incident_id="INC-101",
        service="Payment API",
        error="Database connection timeout",
        symptoms="High Gateway Timeout rate",
        severity="high",
        root_cause="Connection pool exhaustion",
        resolution="Increased connection pool size",
        outcome="Resolved"
    )

    assert res["success"] is True
    assert res["incident_id"] == "INC-101"
    mock_client.retain.assert_called_once()
    kwargs = mock_client.retain.call_args.kwargs
    assert kwargs["bank_id"] == "testbank"
    assert "INC-101" in kwargs["content"]

def test_hindsight_service_recall():
    mock_client = MagicMock()
    mock_client.recall.return_value = {"memories": [{"content": "INC-101 details"}]}

    service = HindsightService(base_url="http://localhost:8888", bank_id="testbank")
    service._client = mock_client

    res = service.recall_memories(query="Database timeout")
    assert res["success"] is True
    assert res["results"] == {"memories": [{"content": "INC-101 details"}]}
    mock_client.recall.assert_called_once_with(
        bank_id="testbank",
        query="Database timeout",
        budget="mid",
        max_tokens=4096,
        tags=None
    )

def test_hindsight_service_reflect():
    mock_client = MagicMock()
    mock_client.reflect.return_value = {"reflection": "Common pattern is connection pool exhaustion."}

    service = HindsightService(base_url="http://localhost:8888", bank_id="testbank")
    service._client = mock_client

    res = service.reflect_patterns(query="What causes database timeouts?")
    assert res["success"] is True
    assert res["results"] == {"reflection": "Common pattern is connection pool exhaustion."}

def test_recall_api_endpoint():
    with patch("app.routers.incidents.hindsight_service.recall_memories") as mock_recall:
        mock_recall.return_value = {
            "success": True,
            "query": "Database connection timeout",
            "results": {"memories": [{"id": "INC-101"}]}
        }

        response = client.post("/api/v1/incidents/recall", json={
            "query": "Database connection timeout",
            "service": "Payment API"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["results"]["memories"][0]["id"] == "INC-101"

def test_reflect_api_endpoint():
    with patch("app.routers.incidents.hindsight_service.reflect_patterns") as mock_reflect:
        mock_reflect.return_value = {
            "success": True,
            "query": "Database connection patterns",
            "results": {"pattern": "Pool exhaustion under load"}
        }

        response = client.post("/api/v1/incidents/reflect", json={
            "query": "Database connection patterns"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["results"]["pattern"] == "Pool exhaustion under load"
