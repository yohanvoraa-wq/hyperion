#!/usr/bin/env python3
"""scripts/serve.py — Start the Hyperion API server.

Development:
    uv run python scripts/serve.py

Production (direct uvicorn):
    uvicorn backend.api.app:app --host 0.0.0.0 --port 8000 --workers 4

Once running, visit:
    http://localhost:8000/docs       — interactive API documentation
    http://localhost:8000/v1/health  — health check
    http://localhost:8000/v1/analyze — POST endpoint

Example curl:
    curl -X POST http://localhost:8000/v1/analyze \\
         -H "Content-Type: application/json" \\
         -d '{"portfolio": ["Apple", "NVIDIA", "Microsoft"]}'
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import uvicorn  # noqa: E402

if __name__ == "__main__":
    uvicorn.run(
        "backend.api.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
    )
