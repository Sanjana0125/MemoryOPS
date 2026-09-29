import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "MemoryOps API"
    assert data["status"] == "running"

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "version" in data

def test_cors_preflight_and_analyze_headers():
    """Verify CORS preflight OPTIONS and POST response headers for deployed Render frontend origin."""
    render_origin = "https://memoryops-frontend.onrender.com"

    # 1. Preflight OPTIONS request
    preflight_resp = client.options(
        "/api/v1/incidents/INC-142/analyze",
        headers={
            "Origin": render_origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        }
    )
    assert preflight_resp.status_code == 200
    assert preflight_resp.headers.get("access-control-allow-origin") == render_origin
    assert "POST" in preflight_resp.headers.get("access-control-allow-methods", "")

    # 2. Actual POST request
    post_resp = client.post(
        "/api/v1/incidents/INC-142/analyze",
        headers={"Origin": render_origin}
    )
    assert post_resp.status_code == 200
    assert post_resp.headers.get("access-control-allow-origin") == render_origin
