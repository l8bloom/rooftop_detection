from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, StrictStr, field_validator

from langgraph_workflow_demo.workflow import workflow


class AnalyzeRequest(BaseModel):
    text: StrictStr

    @field_validator("text")
    @classmethod
    def reject_empty_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be empty")
        return value


class AnalyzeResponse(BaseModel):
    normalized_text: str
    word_count: int
    steps: tuple[Literal["trim_text"], Literal["count_words"]]


app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/workflows/analyze", response_model=AnalyzeResponse)
def analyze_workflow(request: AnalyzeRequest) -> AnalyzeResponse:
    result = workflow.invoke({"text": request.text, "word_count": 0, "steps": []})
    return AnalyzeResponse(
        normalized_text=result["text"],
        word_count=result["word_count"],
        steps=result["steps"],
    )
