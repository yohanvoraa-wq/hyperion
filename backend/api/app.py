"""FastAPI application factory.

Justified by: Milestone 10 design.

create_app() is the single place where the FastAPI app is assembled.
Using a factory function (rather than a module-level app = FastAPI())
keeps the app testable — tests can call create_app() or import app
directly. The uvicorn entrypoint (scripts/serve.py) uses app.

The app:
  - Registers the two V0.1 routes (POST /v1/analyze, GET /v1/health)
  - Registers the Hyperion exception handlers
  - Sets OpenAPI metadata for future Milestone 10 documentation
"""

from __future__ import annotations

from fastapi import FastAPI

from backend.api.errors import register_error_handlers
from backend.api.routes import router


def create_app() -> FastAPI:
    """Build and return the configured FastAPI application."""
    application = FastAPI(
        title="Hyperion Financial Reasoning API",
        version="0.1",
        description=(
            "Deterministic financial reasoning engine. "
            "Converts a portfolio of company names into explainable Blind Spots — "
            "hidden exposures the investor did not knowingly take on."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
    )
    application.include_router(router)
    register_error_handlers(application)
    return application


app: FastAPI = create_app()
