import pytest
from fastapi.testclient import TestClient

from langgraph_workflow_demo.main import app
from langgraph_workflow_demo.workflow import workflow

client = TestClient(app)


def test_analyze_trims_text_counts_words_and_reports_steps() -> None:
    response = client.post("/workflows/analyze", json={"text": " hello world "})

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "normalized_text": "hello world",
        "word_count": 2,
        "steps": ["trim_text", "count_words"],
    }


@pytest.mark.parametrize("text", ["", "   \t\n"])
def test_analyze_rejects_empty_or_whitespace_only_text(text: str) -> None:
    response = client.post("/workflows/analyze", json={"text": text})

    assert response.status_code == 422


def test_analyze_rejects_missing_text() -> None:
    response = client.post("/workflows/analyze", json={})

    assert response.status_code == 422


def test_analyze_rejects_non_string_text() -> None:
    response = client.post("/workflows/analyze", json={"text": 123})

    assert response.status_code == 422


def test_compiled_workflow_is_deterministic() -> None:
    initial_state = {"text": " repeatable words ", "word_count": 0, "steps": []}
    expected = {
        "text": "repeatable words",
        "word_count": 2,
        "steps": ["trim_text", "count_words"],
    }

    assert workflow.invoke(initial_state) == expected
    assert workflow.invoke(initial_state) == expected
