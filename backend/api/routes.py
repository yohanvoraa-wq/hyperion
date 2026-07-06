"""API routes — POST /v1/analyze and GET /v1/health.

Justified by: docs/09-PUBLIC-INTERFACE.md.

Two endpoints. Nothing more for V0.1.

Every handler here is intentionally thin:
  - Receive the request (Pydantic validates automatically)
  - Call the service
  - Return the result

No engine imports. No reasoning logic. No graph construction.
The handler does not know how Janus works. It does not know how
Atlas builds the graph. It orchestrates — nothing more.

This is the proof that the architecture worked: the endpoint is small
because all the thinking was done in the engine.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.api.dependencies import get_pipeline_service
from backend.api.pipeline import PipelineService
from backend.api.schemas import AnalyzeRequestSchema, AnalyzeResponseSchema

router = APIRouter()


@router.post(
    "/v1/analyze",
    response_model=AnalyzeResponseSchema,
    summary="Analyze a portfolio for Blind Spots",
    description=(
        "Run the full Hyperion pipeline on a list of company identifiers. "
        "Returns qualified Blind Spots, no-findings, and any resolution errors. "
        "With a fixed as_of date, the same request always returns the same response."
    ),
)
def analyze(
    request: AnalyzeRequestSchema,
    service: PipelineService = Depends(get_pipeline_service),  # noqa: B008
) -> AnalyzeResponseSchema:
    """POST /v1/analyze — the only Hyperion endpoint for V0.1."""
    return service.analyze(list(request.portfolio), request.as_of)


@router.get(
    "/v1/health",
    summary="Health check",
    description="Returns service status and version. Use for load balancer health checks.",
)
def health() -> dict[str, str]:
    """GET /v1/health — lightweight liveness probe."""
    return {"status": "ok", "version": "0.1"}
