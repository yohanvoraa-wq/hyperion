"""API Pydantic schemas — the frozen public contract.

Justified by: docs/09-PUBLIC-INTERFACE.md.

These are the Pydantic V2 models that define the exact JSON shape
Hyperion exposes to the world. Every field name, every type, every
nesting level is a versioned commitment. Changing these schemas
requires incrementing the API version.

The schemas mirror the DTOs (dto.py) but are:
  - JSON-serializable via Pydantic
  - Validated on input (AnalyzeRequestSchema)
  - Suitable for OpenAPI schema generation (Milestone 10)

No engine types are imported here. No mapper logic lives here.
These schemas describe shapes, not processes.

Per Change 1 (design review): no engine terminology is exposed.
'reasoning_chain' → 'explanation.steps'. Janus may change or disappear;
the wire format does not.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------


class AnalyzeRequestSchema(BaseModel):
    """The body of POST /v1/analyze.

    portfolio: list of company identifiers — names, tickers, or aliases.
    as_of: ISO-8601 date for reproducible results. Defaults to today.
    """

    model_config = ConfigDict(frozen=True)

    portfolio: list[str] = Field(
        min_length=1,
        description=(
            "List of company identifiers (names, tickers, or aliases). "
            "Case-insensitive. At least one required."
        ),
    )
    as_of: str | None = Field(
        default=None,
        description=(
            "ISO-8601 date (YYYY-MM-DD) for the Finance DNA evaluation. "
            "With a fixed as_of, the same request always returns the same response. "
            "Defaults to today."
        ),
    )


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------


class MetadataSchema(BaseModel):
    """Per-response metadata. Present in every response."""

    model_config = ConfigDict(frozen=True)

    hyperion_version: str = Field(description="Hyperion engine version.")
    finance_dna_schema: str = Field(
        description="Finance DNA schema version used for this analysis."
    )
    processed_at: str = Field(description="ISO-8601 datetime when the analysis was executed.")
    processing_time_ms: int = Field(
        description="Wall-clock time for the full pipeline in milliseconds."
    )
    request_id: str = Field(
        description="UUID uniquely identifying this request. Use for tracing and debugging."
    )


# ---------------------------------------------------------------------------
# Blind Spot — three logical sections
# ---------------------------------------------------------------------------


class ReasoningStepSchema(BaseModel):
    """One step in an explanation chain.

    Per Change 6 (design review): includes traceability fields
    (relationship_type, source_id, target_id, labels) so that UI
    consumers can render graph visualisations without parsing premise strings.
    """

    model_config = ConfigDict(frozen=True)

    premise: str = Field(description="The factual starting point of this step.")
    inference: str = Field(description="What follows from the premise.")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in this individual step.")

    # Traceability fields
    relationship_type: str = Field(
        description="Lowercase Atlas relationship type (e.g. 'depends_on_supplies')."
    )
    source_id: str = Field(description="Permanent source node identifier.")
    target_id: str = Field(description="Permanent target node identifier.")
    source_label: str = Field(description="Human-readable source name.")
    target_label: str = Field(description="Human-readable target name.")


class ExplanationSchema(BaseModel):
    """The ordered reasoning chain.

    Per Change 1 (design review): named 'explanation' not 'reasoning_chain'.
    Engine terminology stays internal; the wire format is consumer-facing.
    """

    model_config = ConfigDict(frozen=True)

    steps: list[ReasoningStepSchema]


class EvidenceSchema(BaseModel):
    """Evidence, assumptions, and falsifiability — answers 'why believe this?'"""

    model_config = ConfigDict(frozen=True)

    supporting_evidence: list[str]
    assumptions: list[str]
    falsifiability_conditions: list[str]


class BlindSpotSummarySchema(BaseModel):
    """High-level summary of one Blind Spot."""

    model_config = ConfigDict(frozen=True)

    company_id: str = Field(
        description=(
            "Permanent, immutable identifier. "
            "Per 09-PUBLIC-INTERFACE.md: IDs are never renamed or reused."
        )
    )
    company_name: str = Field(description="Human-readable display name.")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in this Blind Spot (product of reasoning step confidences).",
    )
    severity: str = Field(
        description=(
            "Impact severity: LOW / MEDIUM / HIGH / CRITICAL. "
            "Independent of confidence. V0.1: always MEDIUM (placeholder)."
        )
    )
    categories: list[str] = Field(
        description=(
            "Lowercase Blind Spot taxonomy categories (e.g. ['dependency', 'macroeconomic'])."
        )
    )


class BlindSpotSchema(BaseModel):
    """A fully qualified Blind Spot, grouped into three logical sections.

    Per Change 3 (design review): summary / explanation / evidence grouping
    makes the schema easier to evolve and allows clients to consume
    selectively without processing the full response.
    """

    model_config = ConfigDict(frozen=True)

    summary: BlindSpotSummarySchema
    explanation: ExplanationSchema
    evidence: EvidenceSchema


# ---------------------------------------------------------------------------
# No finding and errors
# ---------------------------------------------------------------------------


class NoFindingSchema(BaseModel):
    """A company that was resolved but produced no Blind Spot.

    Not an error — the pipeline ran correctly. Janus and Titan correctly
    returned silence because no significant path met the qualification criteria.
    """

    model_config = ConfigDict(frozen=True)

    company_id: str
    company_name: str
    reason: str = Field(
        description=(
            "'NO_QUALIFYING_REASONING_PATH' — no path from this asset "
            "to a risk endpoint met the significance criteria."
        )
    )


class ErrorSchema(BaseModel):
    """An identifier that could not be resolved.

    Errors are in errors[], not HTTP 4xx, for partial success semantics.
    """

    model_config = ConfigDict(frozen=True)

    identifier: str = Field(description="The original identifier as submitted.")
    reason: str = Field(description="'UNKNOWN_COMPANY' — not found in the registry.")


# ---------------------------------------------------------------------------
# Root response
# ---------------------------------------------------------------------------


class AnalyzeResponseSchema(BaseModel):
    """The complete response for one /v1/analyze request."""

    model_config = ConfigDict(frozen=True)

    metadata: MetadataSchema
    portfolio: list[str] = Field(description="Resolved company names, in the order submitted.")
    blind_spots: list[BlindSpotSchema]
    no_findings: list[NoFindingSchema]
    errors: list[ErrorSchema]
