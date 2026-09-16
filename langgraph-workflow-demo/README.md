# Standalone LangGraph workflow service

This directory contains a non-deployed FastAPI and LangGraph repository demo.
It runs independently from the existing application and requires Python 3.11 or
newer.

Run all commands from `langgraph-workflow-demo/`.

## Install and run

```sh
python -m pip install -e ".[dev]"
uvicorn langgraph_workflow_demo.main:app --reload
```

Check service health:

```sh
curl -s http://127.0.0.1:8000/health
```

The response is:

```json
{"status":"ok"}
```

Analyze text:

```sh
curl -s -X POST http://127.0.0.1:8000/workflows/analyze \
  -H 'Content-Type: application/json' \
  -d '{"text":" hello world "}'
```

The response is:

```json
{"normalized_text":"hello world","word_count":2,"steps":["trim_text","count_words"]}
```

## Verify

```sh
pytest
ruff check .
ruff format --check .
```
