from app.graph import greeting_graph


def test_greeting_graph_builds_message() -> None:
    result = greeting_graph.invoke({"name": "Ada"})
    assert result["message"] == "Hello, Ada!"
