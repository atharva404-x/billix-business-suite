import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.main import app
from app.middleware.security import SecurityHeadersMiddleware, RequestSizeLimitMiddleware
from app.middleware.rate_limit import RateLimitMiddleware


@pytest.fixture(autouse=True)
def cleanup_dependency_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def test_security_headers_present():
    """Test OWASP security headers present on responses."""
    client = TestClient(app)
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "Content-Security-Policy" in response.headers


def test_cors_preflight_headers():
    """Test CORS preflight OPTIONS request."""
    client = TestClient(app)
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET"
        }
    )
    
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_request_size_limit_middleware():
    """Test payload size limit middleware returns 413 for oversized requests."""
    test_app = FastAPI()
    test_app.add_middleware(RequestSizeLimitMiddleware, max_bytes=100)

    @test_app.post("/upload")
    async def upload_endpoint(data: dict):
        return {"status": "ok"}

    client = TestClient(test_app)
    
    # Under limit
    ok_resp = client.post(
        "/upload",
        json={"name": "test"},
        headers={"Content-Length": "15"}
    )
    assert ok_resp.status_code == 200

    # Over limit
    over_resp = client.post(
        "/upload",
        json={"data": "x" * 200},
        headers={"Content-Length": "250"}
    )
    assert over_resp.status_code == 413
    assert over_resp.json()["detail"] == "Payload Too Large"


def test_rate_limit_middleware():
    """Test rate limit middleware returns 429 when threshold exceeded."""
    test_app = FastAPI()
    test_app.add_middleware(RateLimitMiddleware, requests_per_minute=3)

    @test_app.get("/api/data")
    async def get_data():
        return {"data": "ok"}

    client = TestClient(test_app)
    
    # 3 requests within limit
    for _ in range(3):
        res = client.get("/api/data")
        assert res.status_code == 200

    # 4th request exceeds limit
    blocked_res = client.get("/api/data")
    assert blocked_res.status_code == 429
    assert blocked_res.json()["detail"] == "Too Many Requests"
    assert blocked_res.headers["Retry-After"] == "60"


def test_gzip_compression():
    """Test response compression for payloads exceeding threshold."""
    test_app = FastAPI()
    test_app.add_middleware(GZipMiddleware, minimum_size=100)

    @test_app.get("/large-data")
    async def large_data():
        return {"items": ["item_" + str(i) for i in range(200)]}

    client = TestClient(test_app)
    response = client.get("/large-data", headers={"Accept-Encoding": "gzip"})
    
    assert response.status_code == 200
    assert response.headers.get("content-encoding") == "gzip"
