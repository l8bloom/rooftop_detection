"""One-node LangGraph graph that builds a greeting from a name."""

from typing import NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph


class GreetingState(TypedDict):
    name: str
    message: NotRequired[str]


def greet(state: GreetingState) -> dict[str, str]:
    return {"message": f"Hello, {state['name']}!"}


def build_greeting_graph() -> CompiledStateGraph:
    graph = StateGraph(GreetingState)
    graph.add_node("greet", greet)
    graph.add_edge(START, "greet")
    graph.add_edge("greet", END)
    return graph.compile()


greeting_graph: CompiledStateGraph = build_greeting_graph()
