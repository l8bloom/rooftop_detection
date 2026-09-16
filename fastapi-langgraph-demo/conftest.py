"""Keep this project's tests out of a pytest run started from the repository root.

The root environment does not install this project's dependencies. When pytest
is started from ``fastapi-langgraph-demo/``, its own ``pyproject.toml`` becomes
the rootdir and the tests collect normally.
"""

from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent


def pytest_ignore_collect(collection_path: Path, config) -> bool:
    return config.rootpath.resolve() != PROJECT_DIR
