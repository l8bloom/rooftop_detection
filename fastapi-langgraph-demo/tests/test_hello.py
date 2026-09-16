import inspect

from fastapi.testclient import TestClient

from app.main import app, hello

client = TestClient(app)


def test_hello_returns_greeting() -> None:
    response = client.post("/hello", json={"name": "Ada"})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Ada!"}


def test_hello_rejects_missing_name() -> None:
    response = client.post("/hello", json={})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "name"]


def test_hello_rejects_empty_name() -> None:
    response = client.post("/hello", json={"name": ""})
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "name"]


def test_hello_handler_is_coroutine() -> None:
    assert inspect.iscoroutinefunction(hello)
