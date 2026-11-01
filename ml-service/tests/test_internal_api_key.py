from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ml_routes_require_configured_internal_key(monkeypatch):
    monkeypatch.setenv("INTERNAL_API_KEY", "test-shared-key")

    missing_key = client.get("/api/ml/stats/numeric")
    invalid_key = client.get(
        "/api/ml/stats/numeric",
        headers={"X-Internal-Key": "wrong-key"},
    )
    valid_key = client.get(
        "/api/ml/stats/numeric",
        headers={"X-Internal-Key": "test-shared-key"},
    )

    assert missing_key.status_code == 401
    assert invalid_key.status_code == 401
    assert valid_key.status_code == 405


def test_ml_routes_remain_usable_when_internal_key_is_unset(monkeypatch):
    monkeypatch.delenv("INTERNAL_API_KEY", raising=False)

    response = client.get("/api/ml/stats/numeric")

    assert response.status_code == 405


def test_cors_allows_backend_origin_only():
    allowed = client.options(
        "/api/ml/stats/numeric",
        headers={
            "Origin": "http://localhost:8080",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "x-internal-key",
        },
    )
    rejected = client.options(
        "/api/ml/stats/numeric",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:8080"
    assert "access-control-allow-origin" not in rejected.headers
