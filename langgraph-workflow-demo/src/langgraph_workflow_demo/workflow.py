from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

StepName = Literal["trim_text", "count_words"]


class WorkflowState(TypedDict):
    text: str
    word_count: int
    steps: list[StepName]


def trim_text(state: WorkflowState) -> WorkflowState:
    return {
        "text": state["text"].strip(),
        "word_count": state["word_count"],
        "steps": [*state["steps"], "trim_text"],
    }


def count_words(state: WorkflowState) -> WorkflowState:
    return {
        "text": state["text"],
        "word_count": len(state["text"].split()),
        "steps": [*state["steps"], "count_words"],
    }


def build_workflow() -> CompiledStateGraph:
    builder = StateGraph(WorkflowState)
    builder.add_node("trim_text", trim_text)
    builder.add_node("count_words", count_words)
    builder.add_edge(START, "trim_text")
    builder.add_edge("trim_text", "count_words")
    builder.add_edge("count_words", END)
    return builder.compile()


workflow = build_workflow()
