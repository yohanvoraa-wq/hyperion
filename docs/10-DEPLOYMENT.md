# 10 — Deployment

**Version:** 0.1
**Status:** Active
**Applies to:** Hyperion v0.1.0-alpha

---

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (package manager)

Verify:
```bash
python --version   # 3.12 or higher
uv --version       # any recent version
```

---

## Setup

Clone the repository and install dependencies:

```bash
git clone <repo-url>
cd hyperion
uv sync
```

`uv sync` reads `pyproject.toml`, resolves the lockfile, and installs all
dependencies into a local `.venv`. No manual `pip install` needed.
No system-wide packages are touched.

---

## Running the Demo

The fastest way to see Hyperion reason:

```bash
uv run python scripts/demo.py
```

Expected output:

```
==================================================
  Hyperion v0.1  (Finance DNA schema 0.1)
  Financial Reasoning Demonstration
==================================================

  Portfolio
    •  Apple
    •  NVIDIA
    •  Microsoft

--------------------------------------------------
  Building Knowledge Graph...
    ✓  15 nodes
    ✓  11 relationships

  Running Janus...
    ✓  Apple Inc.
    ✓  NVIDIA Corporation
    -  No significant reasoning path found for Microsoft Corporation.

  Running Titan...
    ✓  Apple Inc. — Blind Spot qualified
    ✓  NVIDIA Corporation — Blind Spot qualified

  Blind Spot #1
  Company: Apple Inc.
  Confidence: 0.8075
  ...
==================================================
```

The demo portfolio is hardcoded in `scripts/demo.py`. Edit `DEMO_PORTFOLIO`
to analyze different companies — any name, ticker, or alias from
`datasets/assets.csv`.

---

## Running the API Server

Start the development server:

```bash
uv run python scripts/serve.py
```

The server starts at `http://localhost:8000` with auto-reload enabled.

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/v1/health` | Liveness probe |
| `POST` | `/v1/analyze` | Analyze a portfolio |
| `GET` | `/docs` | Swagger UI (interactive) |
| `GET` | `/redoc` | ReDoc documentation |

---

## Making Requests

**Health check:**
```bash
curl http://localhost:8000/v1/health
```
```json
{"status": "ok", "version": "0.1"}
```

**Analyze a portfolio:**
```bash
curl -X POST http://localhost:8000/v1/analyze \
     -H "Content-Type: application/json" \
     -d '{"portfolio": ["Apple", "NVIDIA", "Microsoft"]}'
```

**With a fixed date** (for reproducible results):
```bash
curl -X POST http://localhost:8000/v1/analyze \
     -H "Content-Type: application/json" \
     -d '{"portfolio": ["Apple", "NVIDIA"], "as_of": "2024-12-31"}'
```

The same request with the same `as_of` always returns the same response
(excluding `metadata.processing_time_ms`, `metadata.request_id`, and
`metadata.processed_at`, which vary per invocation by design).

**Using the Swagger UI:**

Open `http://localhost:8000/docs` in a browser. Click `POST /v1/analyze`
→ Try it out → fill in the request body → Execute. The full response
renders inline with syntax highlighting.

---

## Running the Tests

All 407 tests:
```bash
uv run pytest
```

Specific milestone:
```bash
uv run pytest backend/tests/test_pipeline.py   # end-to-end pipeline
uv run pytest backend/tests/test_api_routes.py # HTTP routes
uv run pytest backend/tests/test_finance_dna.py
```

With verbose output:
```bash
uv run pytest -v
```

---

## Code Quality

Lint check:
```bash
uv run ruff check backend/
```

Type check:
```bash
uv run mypy backend
```

Both must pass clean before any commit. The project uses `mypy --strict`
and ruff with the configuration in `pyproject.toml`.

---

## Configuration

All V0.1 configuration is in source files, not environment variables:

| What | Where | Default |
|------|-------|---------|
| Asset registry | `datasets/assets.csv` | 7 companies |
| Atlas seed nodes | `datasets/atlas/context_nodes.csv` | 8 context nodes |
| Atlas seed edges | `datasets/atlas/seed_relationships.csv` | 11 relationships |
| Finance DNA scoring | `backend/finance_dna/rules.py` | Sector-level tables |
| Significance threshold | `backend/janus/traversal.py` | `MIN_CONFIDENCE_PRODUCT = 0.5` |
| Max reasoning depth | `backend/janus/traversal.py` | `MAX_DEPTH = 4` |
| Server host/port | `scripts/serve.py` | `127.0.0.1:8000` |

To add a company: append a row to `datasets/assets.csv`. No code changes required.

To add a relationship: append a row to `datasets/atlas/seed_relationships.csv`.
Both endpoints must already exist as nodes (in `assets.csv` or `context_nodes.csv`).

---

## Production Invocation

For a production deployment (not covered in V0.1), bypass `scripts/serve.py`
and invoke uvicorn directly:

```bash
uvicorn backend.api.app:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --no-access-log
```

Remove `--reload` (development only). Add a reverse proxy (nginx, Caddy)
in front for TLS termination. Docker and orchestration are out of scope
for V0.1.

---

## V0.1 Known Limitations

- Finance DNA uses sector-level scoring approximations, not company-specific disclosures
- Atlas relationships are hand-seeded, not automatically discovered from filings
- Single reasoning pattern: Asset → Dependency → Geography → Macro Risk
- No authentication, rate limiting, or persistence layer
- 7 companies in the asset registry (extend via `datasets/assets.csv`)
