from fastapi.testclient import TestClient

from fastapi_langgraph_demo.main import app
from fastapi_langgraph_demo.workflow import workflow

client = TestClient(app)


def test_workflow_trims_whitespace_before_uppercasing() -> None:
    response = client.post("/workflow", json={"text": " hello "})

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"result": "HELLO"}


def test_workflow_uppercases_mixed_case_text() -> None:
    response = client.post("/workflow", json={"text": "MiXeD"})

    assert response.status_code == 200
    assert response.json() == {"result": "MIXED"}


def test_workflow_rejects_missing_text() -> None:
    response = client.post("/workflow", json={})

    assert response.status_code == 422


def test_workflow_rejects_non_string_text() -> None:
    response = client.post("/workflow", json={"text": 123})

    assert response.status_code == 422


def test_compiled_workflow_is_deterministic() -> None:
    initial_state = {"text": " repeatable "}

    assert workflow.invoke(initial_state) == {"text": "REPEATABLE"}
    assert workflow.invoke(initial_state) == {"text": "REPEATABLE"}
