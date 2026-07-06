"""FastAPI dependencies.

Justified by: FastAPI dependency injection pattern.

get_pipeline_service() is the only dependency for V0.1. It creates
PipelineService exactly once (cached via lru_cache) so the asset
registry is loaded at startup and not re-read on every request.

Future milestones may add authentication, rate limiting, or database
session dependencies here. This file is the right place for them.
"""

from __future__ import annotations

from functools import lru_cache

from backend.api.pipeline import PipelineService


@lru_cache(maxsize=1)
def get_pipeline_service() -> PipelineService:
    """Return the singleton PipelineService.

    lru_cache(maxsize=1) ensures the registry is loaded once at
    startup. The service is stateless across requests — the same
    instance handles all concurrent calls safely.

    In tests, override this via app.dependency_overrides if a
    custom service instance is needed.
    """
    return PipelineService()
