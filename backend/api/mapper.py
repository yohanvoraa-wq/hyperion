"""API mapper — the anti-corruption firewall.

Justified by: docs/09-PUBLIC-INTERFACE.md (The Anti-Corruption Rule).

This is THE ONLY FILE in backend/api/ that may import from the engine
(backend/models/, backend/atlas/, backend/janus/, backend/titan/, etc.).
No other API file crosses this boundary. Ever.

Per Change 7 (design review):
    API → mapper → engine
    NOT: API → Janus / API → Titan / API → Atlas

If the engine changes (new fields, renamed types, restructured modules),
only this file changes. The DTOs, schemas, and serializers are insulated.

The mapper's job:
  1. Accept engine objects
  2. Extract everything the API contract needs
  3. Return DTOs (dto.py) — pure Python, not Pydantic, not JSON

The serializer (serializers.py) handles DTO → Pydantic schema.
The mapper never produces Pydantic objects.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from backend.api.dto import (
    AnalyzeResponseDTO,
    BlindSpotDTO,
    BlindSpotSummaryDTO,
    ErrorDTO,
    EvidenceDTO,
    ExplanationDTO,
    MetadataDTO,
    NoFindingDTO,
    ReasoningStepDTO,
)

# Engine imports — ONLY allowed in this file within backend/api/
from backend.finance_dna import FINANCE_DNA_VERSION
from backend.models import BlindSpot, KnowledgeGraph, Portfolio, ReasoningStep

_HYPERION_VERSION: str = "0.1"

# ---------------------------------------------------------------------------
# Severity computation — V0.1 placeholder
# ---------------------------------------------------------------------------

_SEVERITY_V01: str = "MEDIUM"
"""V0.1: severity is frozen at MEDIUM for all qualified Blind Spots.
Severity and confidence are independent axes. Future versions will compute
severity from the Finance DNA dimensions and path characteristics.
Per 09-PUBLIC-INTERFACE.md: field is frozen now; computation evolves later."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _find_node_id_by_label(label: str, graph: KnowledgeGraph) -> str:
    """Look up a node's canonical id from its human-readable label.

    Returns the label itself if no node is found — graceful degradation
    that preserves the information while signalling a lookup miss. In V0.1
    this should never occur since every label in the reasoning chain comes
    from a node that exists in the graph.
    """
    for node in graph.nodes:
        if node.label == label:
            return node.id
    return label  # fallback: use label as id — signals a lookup miss


def _map_step(step: ReasoningStep, graph: KnowledgeGraph) -> ReasoningStepDTO:
    """Convert one engine ReasoningStep to a ReasoningStepDTO with traceability.

    The premise string has the format:
        "Source Label → RELATIONSHIP_TYPE → Target Label"

    This format is defined by backend/janus/reasoner.py and is stable for V0.1.
    The traceability fields (source_id, target_id, relationship_type) are
    extracted here so that API consumers never need to parse the premise string.
    """
    parts = step.premise.split(" → ")
    if len(parts) == 3:
        source_label = parts[0].strip()
        relationship_type = parts[1].strip().lower()
        target_label = parts[2].strip()
    else:
        # Unexpected format — preserve what we have, signal the miss
        source_label = step.premise
        relationship_type = "unknown"
        target_label = "unknown"

    return ReasoningStepDTO(
        premise=step.premise,
        inference=step.inference,
        confidence=step.confidence,
        relationship_type=relationship_type,
        source_id=_find_node_id_by_label(source_label, graph),
        target_id=_find_node_id_by_label(target_label, graph),
        source_label=source_label,
        target_label=target_label,
    )


def _map_blind_spot(
    asset_id: str,
    blind_spot: BlindSpot,
    graph: KnowledgeGraph,
) -> BlindSpotDTO:
    """Convert one engine BlindSpot to a BlindSpotDTO.

    Groups fields into the three-section structure from the contract:
    summary / explanation / evidence. Titan's boolean criteria fields
    (is_meaningful, is_non_obvious, etc.) are internal — they do not
    cross the API boundary. The BlindSpot existing at all is the signal
    that all four criteria were met.

    asset_id is passed explicitly so company_id is always the stable
    internal identifier (e.g. 'apple-inc'), never the display label.
    Per 09-PUBLIC-INTERFACE.md: IDs are permanent and never reused.
    """
    artifact = blind_spot.supporting_reasoning

    # Resolve human-readable name from graph; fall back to asset_id if missing.
    asset_node = graph.find_node(asset_id)
    company_name = asset_node.label if asset_node is not None else asset_id

    summary = BlindSpotSummaryDTO(
        company_id=asset_id,
        company_name=company_name,
        confidence=blind_spot.confidence,
        severity=_SEVERITY_V01,
        categories=tuple(c.name.lower() for c in blind_spot.categories),
    )

    explanation = ExplanationDTO(
        steps=tuple(_map_step(step, graph) for step in artifact.reasoning_steps),
    )

    evidence = EvidenceDTO(
        supporting_evidence=artifact.supporting_evidence,
        assumptions=artifact.assumptions,
        falsifiability_conditions=artifact.falsifiability_conditions,
    )

    return BlindSpotDTO(
        summary=summary,
        explanation=explanation,
        evidence=evidence,
    )


# ---------------------------------------------------------------------------
# Public mapping function
# ---------------------------------------------------------------------------


def map_analyze_response(
    portfolio: Portfolio,
    blind_spots: dict[str, BlindSpot | None],
    unknown_identifiers: list[str],
    graph: KnowledgeGraph,
    processing_time_ms: int,
    as_of: str,
) -> AnalyzeResponseDTO:
    """Convert all engine outputs for one analysis request into an AnalyzeResponseDTO.

    This is the only public function in the mapper. It accepts every engine
    artifact produced by the pipeline and returns a single, complete DTO.

    Parameters
    ----------
    portfolio:
        The resolved Portfolio from Ingestion.
    blind_spots:
        Mapping of asset_id → BlindSpot | None from Titan.
        None means Janus or Titan produced no qualifying result.
    unknown_identifiers:
        Raw identifiers from the request that Ingestion could not resolve.
    graph:
        The KnowledgeGraph from Atlas. Used for node label → id lookup
        when constructing ReasoningStepDTOs.
    processing_time_ms:
        Wall-clock time for the full pipeline. Measured by the caller.
    as_of:
        The Finance DNA evaluation date used for this request.
    """
    now = datetime.now(tz=UTC).isoformat(timespec="seconds")

    metadata = MetadataDTO(
        hyperion_version=_HYPERION_VERSION,
        finance_dna_schema=FINANCE_DNA_VERSION,
        processed_at=now,
        processing_time_ms=processing_time_ms,
        request_id=str(uuid.uuid4()),
    )

    # Portfolio — use resolved display names
    resolved_names = tuple(asset.name for asset in portfolio.assets)

    # Blind spots — assets with qualified findings; preserve portfolio order
    blind_spot_dtos = tuple(
        _map_blind_spot(asset_id, bs, graph)
        for asset_id, bs in blind_spots.items()
        if bs is not None
    )

    # No findings — assets that resolved but produced no Blind Spot
    no_finding_dtos = tuple(
        NoFindingDTO(
            company_id=asset.id,
            company_name=asset.name,
            reason="NO_QUALIFYING_REASONING_PATH",
        )
        for asset in portfolio.assets
        if blind_spots.get(asset.id) is None
    )

    # Errors — identifiers that could not be resolved at all
    error_dtos = tuple(
        ErrorDTO(identifier=raw, reason="UNKNOWN_COMPANY") for raw in unknown_identifiers
    )

    return AnalyzeResponseDTO(
        metadata=metadata,
        portfolio=resolved_names,
        blind_spots=blind_spot_dtos,
        no_findings=no_finding_dtos,
        errors=error_dtos,
    )
