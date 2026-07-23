import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.core.database import get_db_session
from app.core.metrics import metrics_collector
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware


@pytest.fixture(autouse=True)
def cleanup_dependency_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def test_health_endpoint():
    """Test public /health endpoint."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Billix"


def test_readiness_endpoint(db_session: AsyncSession):
    """Test public /ready endpoint with database check."""
    app.dependency_overrides[get_db_session] = lambda: db_session
    client = TestClient(app)
    
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"


def test_metrics_endpoint():
    """Test public /metrics endpoint."""
    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "uptime_seconds" in data
    assert "total_requests" in data
    assert "status_codes" in data
    assert "latency_ms" in data


def test_request_id_and_correlation_id_propagation():
    """Test X-Request-ID and X-Correlation-ID header generation and propagation."""
    client = TestClient(app)
    
    # Test auto-generated IDs
    response = client.get("/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert "X-Correlation-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0

    # Test custom passed IDs propagation
    custom_req_id = "test-req-12345"
    custom_corr_id = "test-corr-67890"
    
    response = client.get(
        "/health",
        headers={
            "X-Request-ID": custom_req_id,
            "X-Correlation-ID": custom_corr_id
        }
    )
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == custom_req_id
    assert response.headers["X-Correlation-ID"] == custom_corr_id


def test_error_handler_middleware_captures_exceptions():
    """Test ErrorHandlerMiddleware catches uncaught exceptions and returns standard 500 JSON."""
    test_app = FastAPI()
    test_app.add_middleware(ErrorHandlerMiddleware)
    test_app.add_middleware(RequestIDMiddleware)

    @test_app.get("/error-route")
    async def crash():
        raise RuntimeError("Simulated internal error")

    client = TestClient(test_app)
    response = client.get("/error-route", headers={"X-Request-ID": "err-req-999"})
    
    assert response.status_code == 500
    data = response.json()
    assert "request_id" in data
    assert data["request_id"] == "err-req-999"
    assert "correlation_id" in data
    assert response.headers["X-Request-ID"] == "err-req-999"
