from fastapi import FastAPI
from pydantic import BaseModel, StrictStr

from fastapi_langgraph_demo.workflow import workflow


class WorkflowRequest(BaseModel):
    text: StrictStr


class WorkflowResponse(BaseModel):
    result: str


app = FastAPI()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def readiness() -> dict[str, str]:
    return {"status": "ready"}


@app.post("/workflow", response_model=WorkflowResponse)
def run_workflow(request: WorkflowRequest) -> WorkflowResponse:
    transformed_state = workflow.invoke({"text": request.text})
    return WorkflowResponse(result=transformed_state["text"])
