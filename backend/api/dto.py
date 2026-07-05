"""API Data Transfer Objects — intermediate representation.

Justified by: docs/09-PUBLIC-INTERFACE.md.

DTOs sit between the engine (backend/models/) and the JSON-serializable
Pydantic schemas (schemas.py). They are:
  - Typed Python dataclasses (not Pydantic, not JSON-serializable)
  - Immutable (frozen=True)
  - Decoupled from both the engine's internal types and the wire format

The flow is:
    Engine Objects → mapper.py → DTOs → serializers.py → Pydantic schemas → JSON

DTOs exist so that:
  1. The engine never knows about the API layer
  2. The API schemas never import engine types
  3. A single mapper → serializer change handles engine refactors
     without touching either the engine or the wire format

No business logic lives here. DTOs are shapes, not processes.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetadataDTO:
    """Per-response metadata, present in every response."""

    hyperion_version: str
    finance_dna_schema: str
    processed_at: str  # ISO-8601 datetime string
    processing_time_ms: int
    request_id: str  # UUID string


@dataclass(frozen=True)
class ReasoningStepDTO:
    """One step in an explanation chain, with full traceability fields.

    Per 09-PUBLIC-INTERFACE.md: every step exposes relationship_type,
    source_id, and target_id so that UI consumers can render graph
    visualisations directly without parsing the premise string.
    """

    premise: str
    inference: str
    confidence: float

    # Traceability fields — Change 6 from the design review
    relationship_type: str  # lowercase (e.g. "depends_on_supplies")
    source_id: str  # permanent node id
    target_id: str  # permanent node id
    source_label: str  # human-readable
    target_label: str  # human-readable


@dataclass(frozen=True)
class BlindSpotSummaryDTO:
    """High-level summary of one Blind Spot."""

    company_id: str
    company_name: str
    confidence: float
    severity: str  # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    categories: tuple[str, ...]  # lowercase strings


@dataclass(frozen=True)
class ExplanationDTO:
    """The ordered reasoning chain that justifies a Blind Spot."""

    steps: tuple[ReasoningStepDTO, ...]


@dataclass(frozen=True)
class EvidenceDTO:
    """Everything needed to answer 'why should I believe this?'"""

    supporting_evidence: tuple[str, ...]
    assumptions: tuple[str, ...]
    falsifiability_conditions: tuple[str, ...]


@dataclass(frozen=True)
class BlindSpotDTO:
    """A fully qualified Blind Spot, grouped into three logical sections.

    Per Change 3 from the design review: grouping into summary /
    explanation / evidence makes the structure easier to evolve and
    easier for clients to parse selectively.
    """

    summary: BlindSpotSummaryDTO
    explanation: ExplanationDTO
    evidence: EvidenceDTO


@dataclass(frozen=True)
class NoFindingDTO:
    """A company that was resolved but produced no Blind Spot.

    'No finding' is not an error. The pipeline ran for this company,
    no significant reasoning path met the qualification criteria,
    and Hyperion is correctly silent. Per Decision 6 (Janus) and
    Decision 3 (Titan): silence is preferable to a weak explanation.
    """

    company_id: str
    company_name: str
    reason: str  # "NO_QUALIFYING_REASONING_PATH"


@dataclass(frozen=True)
class ErrorDTO:
    """An identifier that could not be resolved at all.

    Errors go in errors[], not HTTP 4xx, so that a portfolio with
    one misspelled company name does not fail entirely.
    Per 09-PUBLIC-INTERFACE.md: partial success semantics.
    """

    identifier: str  # original identifier as submitted
    reason: str  # "UNKNOWN_COMPANY"


@dataclass(frozen=True)
class AnalyzeResponseDTO:
    """The complete response for one /v1/analyze request."""

    metadata: MetadataDTO
    portfolio: tuple[str, ...]  # resolved company names in order
    blind_spots: tuple[BlindSpotDTO, ...]
    no_findings: tuple[NoFindingDTO, ...]
    errors: tuple[ErrorDTO, ...]
