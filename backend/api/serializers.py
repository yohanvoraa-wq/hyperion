"""API serializers — DTO to Pydantic schema conversion.

Justified by: docs/09-PUBLIC-INTERFACE.md.

Serializers handle the translation from DTOs (typed Python dataclasses)
to Pydantic schemas (JSON-serializable). This is where special type
handling lives: datetime formatting, UUID strings, enum → lowercase
string, Decimal → float, etc.

In V0.1, most fields are already strings and floats, so the serializers
are mechanically simple. The structure exists for future use — when the
engine starts producing richer types, only this file changes.

Per Change 8 (design review): the DTO → Pydantic layer is explicit and
separate from both the mapper (engine → DTO) and the schemas (wire format).
The three files have distinct, non-overlapping responsibilities.
"""

from __future__ import annotations

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
from backend.api.schemas import (
    AnalyzeResponseSchema,
    BlindSpotSchema,
    BlindSpotSummarySchema,
    ErrorSchema,
    EvidenceSchema,
    ExplanationSchema,
    MetadataSchema,
    NoFindingSchema,
    ReasoningStepSchema,
)

# ---------------------------------------------------------------------------
# Individual serializers — bottom-up
# ---------------------------------------------------------------------------


def _serialize_metadata(dto: MetadataDTO) -> MetadataSchema:
    return MetadataSchema(
        hyperion_version=dto.hyperion_version,
        finance_dna_schema=dto.finance_dna_schema,
        processed_at=dto.processed_at,
        processing_time_ms=dto.processing_time_ms,
        request_id=dto.request_id,
    )


def _serialize_step(dto: ReasoningStepDTO) -> ReasoningStepSchema:
    return ReasoningStepSchema(
        premise=dto.premise,
        inference=dto.inference,
        confidence=dto.confidence,
        relationship_type=dto.relationship_type,
        source_id=dto.source_id,
        target_id=dto.target_id,
        source_label=dto.source_label,
        target_label=dto.target_label,
    )


def _serialize_summary(dto: BlindSpotSummaryDTO) -> BlindSpotSummarySchema:
    return BlindSpotSummarySchema(
        company_id=dto.company_id,
        company_name=dto.company_name,
        confidence=dto.confidence,
        severity=dto.severity,
        categories=list(dto.categories),  # tuple → list for JSON array
    )


def _serialize_explanation(dto: ExplanationDTO) -> ExplanationSchema:
    return ExplanationSchema(steps=[_serialize_step(s) for s in dto.steps])


def _serialize_evidence(dto: EvidenceDTO) -> EvidenceSchema:
    return EvidenceSchema(
        supporting_evidence=list(dto.supporting_evidence),
        assumptions=list(dto.assumptions),
        falsifiability_conditions=list(dto.falsifiability_conditions),
    )


def _serialize_blind_spot(dto: BlindSpotDTO) -> BlindSpotSchema:
    return BlindSpotSchema(
        summary=_serialize_summary(dto.summary),
        explanation=_serialize_explanation(dto.explanation),
        evidence=_serialize_evidence(dto.evidence),
    )


def _serialize_no_finding(dto: NoFindingDTO) -> NoFindingSchema:
    return NoFindingSchema(
        company_id=dto.company_id,
        company_name=dto.company_name,
        reason=dto.reason,
    )


def _serialize_error(dto: ErrorDTO) -> ErrorSchema:
    return ErrorSchema(identifier=dto.identifier, reason=dto.reason)


# ---------------------------------------------------------------------------
# Public serializer — the only entry point
# ---------------------------------------------------------------------------


def serialize_response(dto: AnalyzeResponseDTO) -> AnalyzeResponseSchema:
    """Convert a complete AnalyzeResponseDTO to a JSON-serializable Pydantic schema.

    This is the only public function in serializers.py. It is the final
    step before JSON output. The FastAPI handler (Milestone 10) will call
    this function and return its result; Pydantic handles the rest.

    All DTO → schema conversions happen here. Special type handling
    (datetime, UUID, enum → string, etc.) lives in the individual
    _serialize_* helpers above.
    """
    return AnalyzeResponseSchema(
        metadata=_serialize_metadata(dto.metadata),
        portfolio=list(dto.portfolio),
        blind_spots=[_serialize_blind_spot(bs) for bs in dto.blind_spots],
        no_findings=[_serialize_no_finding(nf) for nf in dto.no_findings],
        errors=[_serialize_error(e) for e in dto.errors],
    )
