import inspect

from fastapi.testclient import TestClient

from app.main import app, health

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_content_type_is_json() -> None:
    response = client.get("/health")
    assert response.headers["content-type"].startswith("application/json")


def test_health_rejects_post() -> None:
    response = client.post("/health")
    assert response.status_code == 405


def test_health_handler_is_coroutine() -> None:
    assert inspect.iscoroutinefunction(health)
