from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
import pytest
from hindsight_client_api.exceptions import ApiException
from app.main import app
from app.hindsight_service import HindsightService

client = TestClient(app)

@pytest.mark.anyio
async def test_hindsight_service_aretain():
    mock_client = AsyncMock()
    mock_client.aretain.return_value = {"status": "ok", "id": "mem-123"}

    service = HindsightService(base_url="http://localhost:8888", bank_id="testbank")
    service._client = mock_client

    res = await service.aretain_incident(
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
    mock_client.aretain.assert_called_once()
    kwargs = mock_client.aretain.call_args.kwargs
    assert kwargs["bank_id"] == "testbank"
    assert "INC-101" in kwargs["content"]

@pytest.mark.anyio
async def test_hindsight_service_arecall():
    mock_client = AsyncMock()
    mock_client.arecall.return_value = {"memories": [{"content": "INC-101 details"}]}

    service = HindsightService(base_url="http://localhost:8888", bank_id="testbank")
    service._client = mock_client

    res = await service.arecall_memories(query="Database timeout")
    assert res["success"] is True
    assert res["results"] == {"memories": [{"content": "INC-101 details"}]}
    mock_client.arecall.assert_called_once_with(
        bank_id="testbank",
        query="Database timeout",
        budget="mid",
        max_tokens=4096,
        tags=None
    )

@pytest.mark.anyio
async def test_hindsight_service_areflect():
    mock_client = AsyncMock()
    mock_client.areflect.return_value = {"reflection": "Common pattern is connection pool exhaustion."}

    service = HindsightService(base_url="http://localhost:8888", bank_id="testbank")
    service._client = mock_client

    res = await service.areflect_patterns(query="What causes database timeouts?")
    assert res["success"] is True
    assert res["results"] == {"reflection": "Common pattern is connection pool exhaustion."}

@pytest.mark.anyio
async def test_hindsight_service_http_402_insufficient_credits():
    mock_client = AsyncMock()
    mock_exception = ApiException(status=402, reason="Payment Required", body='{"detail": "Insufficient credits"}')
    mock_client.arecall.side_effect = mock_exception

    service = HindsightService(base_url="http://localhost:8888", bank_id="testbank")
    service._client = mock_client

    res = await service.arecall_memories(query="Database timeout")
    assert res["success"] is False
    assert res["status_code"] == 402
    assert "insufficient credits" in res["error"].lower()

def test_recall_api_endpoint():
    with patch("app.routers.incidents.hindsight_service.arecall_memories") as mock_recall:
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
    with patch("app.routers.incidents.hindsight_service.areflect_patterns") as mock_reflect:
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
