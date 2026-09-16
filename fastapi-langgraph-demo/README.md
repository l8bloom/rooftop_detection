# fastapi-langgraph-demo

A minimal FastAPI service with an asynchronous `GET /health` endpoint and an asynchronous `POST /hello` endpoint. `/hello` runs a one-node LangGraph `StateGraph` that turns `{"name": "Ada"}` into `{"message": "Hello, Ada!"}`. The project is isolated from the rest of this repository and ships no Dockerfile.

Run every command from `fastapi-langgraph-demo/`.

## Install

```bash
python -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

## Test

```bash
python -m pytest
```

## Examples

Run these against the server started above. The line after each command is its output.

```bash
curl -s http://127.0.0.1:8000/health
{"status":"ok"}

curl -s -X POST http://127.0.0.1:8000/hello -H 'Content-Type: application/json' -d '{"name": "Ada"}'
{"message":"Hello, Ada!"}
```
