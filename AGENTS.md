# Repository Guidelines

## Project Structure & Module Organization
The FastAPI service lives in `app/`, with `app/main.py` as the entrypoint, `app/service.py` holding the congestion detection logic, and `app/schemas.py` defining Pydantic models. Tests are in `tests/` (`test_api.py`, `test_service.py`). Reference docs are in `docs/` (`docs/API.md`, `docs/DESIGN.md`). Runtime dependencies are pinned in `requirements.txt`.

## Build, Test, and Development Commands
- `pip install -r requirements.txt`: install Python dependencies.
- `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`: run the API locally with auto-reload.
- `pytest`: execute the test suite.

## Coding Style & Naming Conventions
Use 4-space indentation, type hints where practical, and keep modules small and focused. Follow Python naming conventions: `snake_case` for functions/variables, `CapWords` for classes, and `UPPER_SNAKE_CASE` for constants. No formatter or linter is configured, so match existing style in `app/` and keep imports grouped and ordered.

## Testing Guidelines
Tests use `pytest` with files named `test_*.py` and functions prefixed with `test_`. API tests use FastAPI’s `TestClient`; service tests focus on clustering and congestion levels. There is no coverage gate, but changes to algorithms or response shapes should include corresponding tests.

## Commit & Pull Request Guidelines
Recent commits use short, imperative, sentence-case messages (e.g., “Add …”, “Fix …”, “Ensure …”). Keep commit subjects concise and scoped to one change. For pull requests, include a clear description, note relevant tests run (e.g., `pytest`), and add request/response examples when API behavior changes.

## Configuration Notes
Congestion thresholds are configurable in `app/service.py` via the `CongestionService` constructor. If you change defaults, update `README.md` and tests to keep behavior consistent.
