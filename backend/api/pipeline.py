"""PipelineService — the single orchestration layer.

Justified by: docs/09-PUBLIC-INTERFACE.md and Milestone 10 design.

Every external interface — REST API, CLI, future batch jobs — calls this
one class. Business logic stays in the engine. The handler orchestrates.

PipelineService:
  1. Pre-loads the asset registry at startup (not per request)
  2. Handles partial success: unknown identifiers go to errors[], not 4xx
  3. Runs the full pipeline: ingestion → finance DNA → atlas → janus → titan
  4. Maps engine output → AnalyzeResponseSchema via mapper + serializer

The FastAPI handler should have zero business logic. It validates the
request, calls service.analyze(), and returns the result. Nothing more.
"""

from __future__ import annotations

import time
from datetime import date

from backend.api.mapper import map_analyze_response
from backend.api.schemas import AnalyzeResponseSchema
from backend.api.serializers import serialize_response
from backend.atlas import build
from backend.finance_dna import evaluate
from backend.ingestion import load_asset_registry, load_portfolio
from backend.ingestion.exceptions import EmptyPortfolioError
from backend.ingestion.loader import AssetRegistry
from backend.janus import reason
from backend.models import BlindSpot, FinanceDNA
from backend.titan import qualify


def _partition(
    raw_identifiers: list[str],
    registry: AssetRegistry,
) -> tuple[list[str], list[str]]:
    """Split raw identifiers into (resolvable, unknown).

    Partial success semantics: unknown identifiers go into errors[],
    allowing the pipeline to run for the companies it can resolve.
    Per 09-PUBLIC-INTERFACE.md: a portfolio with one misspelled name
    should not fail entirely.
    """
    resolvable: list[str] = []
    unknown: list[str] = []
    for raw in raw_identifiers:
        if registry.find(raw) is not None:
            resolvable.append(raw)
        else:
            unknown.append(raw)
    return resolvable, unknown


class PipelineService:
    """Orchestrates the complete Hyperion pipeline for one analysis request.

    Pre-loads the asset registry at instantiation so that repeated
    requests do not re-read the CSV on every call. The registry is
    read-only after loading, so pre-loading is safe for concurrent use.

    All interfaces (FastAPI, CLI, future batch jobs) call analyze().
    This is the single public entry point to the full pipeline.
    """

    def __init__(self) -> None:
        self._registry = load_asset_registry()
        self._all_assets = list(self._registry.assets)

    def analyze(
        self,
        raw_identifiers: list[str],
        as_of: str | None = None,
    ) -> AnalyzeResponseSchema:
        """Run the full pipeline for a list of raw company identifiers.

        Parameters
        ----------
        raw_identifiers:
            Company names, tickers, or aliases — same resolution as
            the Ingestion layer. Case-insensitive.
        as_of:
            ISO-8601 date for Finance DNA evaluation. With a fixed as_of,
            the same request always produces the same response (minus
            metadata timing fields). Defaults to today's date.

        Returns
        -------
        AnalyzeResponseSchema
            JSON-serializable Pydantic schema ready for HTTP response.

        Raises
        ------
        EmptyPortfolioError
            When all provided identifiers are unknown (no resolvable
            companies remain after filtering). The handler converts this
            to HTTP 422.
        """
        start = time.monotonic()
        evaluation_date = as_of or date.today().isoformat()

        # --- Partial success: separate known from unknown ---
        resolvable, unknown_ids = _partition(raw_identifiers, self._registry)
        if not resolvable:
            raise EmptyPortfolioError()

        # --- Ingestion ---
        portfolio = load_portfolio(resolvable)

        # --- Finance DNA ---
        finance_dnas: dict[str, FinanceDNA] = {
            asset.id: evaluate(asset, as_of=evaluation_date)
            for asset in portfolio.assets
        }

        # --- Atlas ---
        graph = build(self._all_assets, finance_dnas)

        # --- Janus + Titan ---
        blind_spots: dict[str, BlindSpot | None] = {}
        for asset in portfolio.assets:
            artifact = reason(asset.id, graph)
            blind_spots[asset.id] = qualify(artifact) if artifact is not None else None

        # --- Map + serialize ---
        elapsed_ms = int((time.monotonic() - start) * 1000)
        dto = map_analyze_response(
            portfolio=portfolio,
            blind_spots=blind_spots,
            unknown_identifiers=unknown_ids,
            graph=graph,
            processing_time_ms=elapsed_ms,
            as_of=evaluation_date,
        )
        return serialize_response(dto)
