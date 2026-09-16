"""FastAPI application with a health endpoint and a LangGraph greeting endpoint."""

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.graph import greeting_graph


class HelloRequest(BaseModel):
    name: str = Field(min_length=1)


class HelloResponse(BaseModel):
    message: str


app: FastAPI = FastAPI(title="fastapi-langgraph-demo")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/hello")
async def hello(body: HelloRequest) -> HelloResponse:
    result = await greeting_graph.ainvoke({"name": body.name})
    return HelloResponse(message=result["message"])
