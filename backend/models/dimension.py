"""Dimension domain model — Finance DNA's core artifact.

Justified by: docs/04-FINANCE-DNA.md, specifically:
  - §2  (What Makes a Valid Financial Dimension? — five qualification criteria)
  - §3  (Types of Financial Dimensions — ValueStructure × TemporalBehavior)
  - §5C (The six official Dimension Categories)
  - §6  (Individual Dimensions — the Aggregation Rule field)

Finance DNA owns Dimension objects permanently. No other module may mutate one.
Per ED-005: Atlas references Dimensions as one endpoint's attributes; it never
rewrites them.

The score field is typed as a union matching the three ValueStructures:
  - CONTINUOUS  → float   (bounded scalar)
  - CATEGORICAL → str     (one label from a fixed set)
  - BINARY      → bool    (present / absent)

The aggregation_rule field records how this Dimension combines across Assets
into a Portfolio DNA — defined per dimension in Finance DNA §6, not inferred
from ValueStructure alone, because the correct rule was designed-in during
qualification, not derived mechanically afterward.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.models.enums import (
    ApproximationLevel,
    DimensionCategory,
    EvidenceSource,
    TemporalBehavior,
    ValueStructure,
)


@dataclass(frozen=True)
class Dimension:
    """A single qualified Financial Dimension of one Asset.

    Every field is either directly named in Finance DNA §2–6, or derives
    from a requirement stated there. Nothing here was invented during coding.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    name: str
    """Canonical name matching an entry in Finance DNA §6
    (e.g. 'Capital Intensity', 'R&D Intensity')."""

    asset_id: str
    """ID of the Asset this Dimension describes. Dimension belongs to exactly
    one Asset; Finance DNA §2 criterion 3 (Composable) means many Dimension
    instances of the same name combine across Assets into Portfolio DNA."""

    # ------------------------------------------------------------------
    # Type system — Finance DNA §3
    # ------------------------------------------------------------------

    value_structure: ValueStructure
    """Axis 1: the shape of the value (CONTINUOUS / CATEGORICAL / BINARY)."""

    temporal_behavior: TemporalBehavior
    """Axis 2: how the value changes over time (STATIC / TIME_VARYING)."""

    # ------------------------------------------------------------------
    # Value — typed to match ValueStructure
    # ------------------------------------------------------------------

    score: float | str | bool
    """The dimension's value for this Asset at as_of.
      CONTINUOUS  → float in a defined, bounded range
      CATEGORICAL → str label from the dimension's fixed label set
      BINARY      → bool (True = present, False = absent)
    The correct Python type must match value_structure; Finance DNA §3
    defines which aggregation rule applies to each structure type.
    """

    # ------------------------------------------------------------------
    # Qualification metadata — Finance DNA §2 (criteria 4 and 5)
    # ------------------------------------------------------------------

    confidence: float
    """Certainty in this score, 0.0–1.0.
    Maps to the Confidence Layer defined in 02-FOUNDATIONAL-CONCEPTS.md."""

    evidence: tuple[str, ...]
    """One or more verifiable, inspectable facts supporting this score.
    Finance DNA §2, criterion 5: every value must be evidence-traceable."""

    evidence_source: EvidenceSource
    """The kind of evidence: DISCLOSED / PUBLIC_RECORD / DERIVED.
    Derived dimensions (e.g. Interest Rate Sensitivity) inherit this
    classification from their upstream inputs per Finance DNA §6."""

    # ------------------------------------------------------------------
    # Organisational metadata — Finance DNA §5C
    # ------------------------------------------------------------------

    category: DimensionCategory
    """One of the six official categories from Finance DNA §5C."""

    aggregation_rule: str
    """How this Dimension aggregates into Portfolio DNA.
    Matches the Aggregation Rule column Finance DNA §6 specifies per
    dimension: 'weighted_average' | 'distribution' | 'weighted_proportion'.
    Stored explicitly here rather than derived from ValueStructure alone,
    because the rule is a design decision, not a mechanical inference."""

    # ------------------------------------------------------------------
    # Temporal tracking — Finance DNA §3 (TemporalBehavior)
    # ------------------------------------------------------------------

    as_of: str
    """ISO-8601 date string (YYYY-MM-DD) for when this score was computed.
    TIME_VARYING dimensions must always carry this field; using a stale
    value as current silently violates Finance DNA §1's economic-identity
    standard. STATIC dimensions carry it too, for auditability."""

    primitive: bool = field(default=True)
    """True if this Dimension is directly observed from disclosed data.
    False (Derived) if it is computed from other qualified Dimensions
    (e.g. Technology Obsolescence Risk depends on R&D Intensity and
    Patent / IP Intensity). See Finance DNA §6 and Candidate Board."""

    approximation_level: ApproximationLevel = field(default=ApproximationLevel.C)
    """Quality of the data source used to derive this score.
    Justified by: docs/04-FINANCE-DNA-v0.2.md (Approximation Level Framework).

    V0.1 dimensions default to Level C (sector approximation) — retroactive
    classification that changes no score values, only adds transparency.
    V0.2 dimensions set Level B (industry approximation) explicitly.
    Level A (company-specific data) requires automated filing ingestion (V0.4).

    UNKNOWN means no reliable approximation exists — score should be None
    and dimension excluded from aggregation. Never store 0.0 for UNKNOWN.
    """
