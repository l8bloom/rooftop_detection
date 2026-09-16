from fastapi.testclient import TestClient

from fastapi_langgraph_demo.main import app


def test_readiness() -> None:
    response = TestClient(app).get("/ready")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"status": "ready"}
