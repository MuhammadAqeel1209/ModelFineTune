from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.routes import get_openrouter_service
from app.main import app
from app.services.openrouter import OpenRouterError


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_invalid_empty_message() -> None:
    with TestClient(app) as client:
        response = client.post("/api/chat", json={"messages": [{"role": "user", "content": "  "}]})
    assert response.status_code == 422


def test_successful_chat_response() -> None:
    service = type("MockService", (), {})()
    service.create_completion = AsyncMock(return_value="Hello from the mock provider")
    app.dependency_overrides[get_openrouter_service] = lambda: service
    try:
        with TestClient(app) as client:
            response = client.post("/api/chat", json={"messages": [{"role": "user", "content": "Hi"}]})
        assert response.status_code == 200
        assert response.json()["message"] == {"role": "assistant", "content": "Hello from the mock provider"}
    finally:
        app.dependency_overrides.clear()


def test_provider_failure_is_hidden_behind_safe_error() -> None:
    service = type("MockService", (), {})()
    service.create_completion = AsyncMock(side_effect=OpenRouterError("Provider unavailable"))
    app.dependency_overrides[get_openrouter_service] = lambda: service
    try:
        with TestClient(app) as client:
            response = client.post("/api/chat", json={"messages": [{"role": "user", "content": "Hi"}]})
        assert response.status_code == 502
        assert response.json()["detail"] == "Provider unavailable"
    finally:
        app.dependency_overrides.clear()
