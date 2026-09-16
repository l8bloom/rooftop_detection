from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph


class WorkflowState(TypedDict):
    text: str


def trim_text(state: WorkflowState) -> WorkflowState:
    return {"text": state["text"].strip()}


def uppercase_text(state: WorkflowState) -> WorkflowState:
    return {"text": state["text"].upper()}


def build_workflow() -> CompiledStateGraph:
    builder = StateGraph(WorkflowState)
    builder.add_node("trim_text", trim_text)
    builder.add_node("uppercase_text", uppercase_text)
    builder.add_edge(START, "trim_text")
    builder.add_edge("trim_text", "uppercase_text")
    builder.add_edge("uppercase_text", END)
    return builder.compile()


workflow = build_workflow()
