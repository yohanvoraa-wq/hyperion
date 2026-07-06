"""HTTP error handlers.

Justified by: docs/09-PUBLIC-INTERFACE.md (Error Responses section).

Three categories of error, per the frozen contract:
  HTTP 422 — request was structurally valid but semantically wrong
              (empty portfolio, duplicate assets, etc.)
  HTTP 500 — the pipeline itself failed unexpectedly

Unknown companies are NOT errors at this layer — they are handled by
PipelineService as partial success and appear in errors[] in the response
body. HTTP 4xx is reserved for problems that prevent the pipeline from
running at all.

The generic Exception handler is a safety net. In production, the
exception should be logged with the request_id before returning 500.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.ingestion.exceptions import DuplicateAssetError, EmptyPortfolioError


def register_error_handlers(app: FastAPI) -> None:
    """Attach all Hyperion exception handlers to the FastAPI app."""

    @app.exception_handler(EmptyPortfolioError)
    async def handle_empty_portfolio(
        _request: Request, exc: EmptyPortfolioError
    ) -> JSONResponse:
        """Raised when all provided identifiers are unknown or none were given."""
        return JSONResponse(
            status_code=422,
            content={
                "error": "INVALID_REQUEST",
                "detail": str(exc),
            },
        )

    @app.exception_handler(DuplicateAssetError)
    async def handle_duplicate_asset(
        _request: Request, exc: DuplicateAssetError
    ) -> JSONResponse:
        """Raised when the same company appears twice under different identifiers."""
        return JSONResponse(
            status_code=422,
            content={
                "error": "INVALID_REQUEST",
                "detail": str(exc),
            },
        )

    @app.exception_handler(Exception)
    async def handle_generic(
        _request: Request, _exc: Exception
    ) -> JSONResponse:
        """Safety net for unexpected failures.

        In production: log the exception with request_id before returning.
        For V0.1: return a generic 500 without leaking stack traces.
        """
        return JSONResponse(
            status_code=500,
            content={
                "error": "PIPELINE_ERROR",
                "detail": "An internal error occurred. Check server logs.",
            },
        )
