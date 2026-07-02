"""Relationship domain model — Atlas's core artifact.

Justified by: docs/05-ATLAS.md, specifically:
  - §2  (What Makes a Valid Relationship? — five qualification criteria)
  - §4  (Relationship types and their domain/range)
  - §5  (Five relationship characteristics: Directionality, Temporality,
          Cardinality, EvidenceSource, Confidence)
  - §1  (Founding principle: one canonical representation per fact)

Atlas owns Relationship objects permanently. Per ED-005 and 07-SYSTEM-ARCHITECTURE.md
§6: Atlas never creates Blind Spots; Janus never creates Relationships. A module
that needs to traverse a Relationship may read it; it may never mutate or
re-create it under a different name.

The source_id / target_id fields reference node identifiers — Asset.id for
Asset nodes, or a canonical string identifier for context nodes (Commodity,
Geography, MacroFactor, etc.) that do not themselves have a Finance DNA profile.
This keeps Relationship self-contained without importing Asset directly, which
would create a dependency that runs the wrong direction in the module boundary
(Atlas referencing Finance DNA's internals rather than models/).
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.models.enums import (
    Cardinality,
    Directionality,
    EvidenceSource,
    RelationshipTemporality,
    RelationshipType,
)


@dataclass(frozen=True)
class Relationship:
    """A single qualified edge in the Atlas knowledge graph.

    Every field maps directly to an Atlas §4–§5 property. Nothing was
    invented during coding; the table in Atlas §5 is the specification
    for the characteristic fields below.
    """

    # ------------------------------------------------------------------
    # Edge identity
    # ------------------------------------------------------------------

    source_id: str
    """Canonical identifier of the edge's source node.
    For Asset nodes: Asset.id. For context nodes: a canonical slug
    (e.g. 'tsmc', 'taiwan', 'geopolitical-risk-taiwan')."""

    target_id: str
    """Canonical identifier of the edge's target node (same convention)."""

    relationship_type: RelationshipType
    """One of the nine types from Atlas §4. DEPENDS_ON_SUPPLIES is stored
    once; the Directionality characteristic records which end is which."""

    # ------------------------------------------------------------------
    # Five characteristics — Atlas §5
    # ------------------------------------------------------------------

    directionality: Directionality
    """DIRECTED, BIDIRECTIONAL, or SYMMETRIC.
    DEPENDS_ON_SUPPLIES is BIDIRECTIONAL: one canonical edge read as
    'depends_on' from source and 'supplies' from target. This resolves
    the Section 4 open question about depends_on/supplies duplication."""

    temporality: RelationshipTemporality
    """PERSISTENT, TEMPORAL (bounded term), or EVENT_DRIVEN."""

    cardinality: Cardinality
    """ONE_TO_ONE, ONE_TO_MANY, or MANY_TO_MANY."""

    evidence_source: EvidenceSource
    """DISCLOSED, PUBLIC_RECORD, or DERIVED.
    Per Atlas §5: a Derived relationship's confidence depends on the
    confidence of its source relationships."""

    confidence: float
    """Certainty in this relationship, 0.0–1.0.
    Maps to the Confidence Layer in 02-FOUNDATIONAL-CONCEPTS.md.
    Per Atlas §5: 'Determined per instance' for all relationship types."""

    # ------------------------------------------------------------------
    # Evidence — Atlas §2 (criterion 4: evidence-traceability)
    # ------------------------------------------------------------------

    evidence: tuple[str, ...]
    """One or more verifiable facts that this edge cleared Atlas §2's
    evidence-traceability criterion against. Every relationship that
    exists in the graph passed that criterion before it was added;
    this field preserves the record of how."""

    # ------------------------------------------------------------------
    # Temporal bounds — Atlas §5 (RelationshipTemporality)
    # ------------------------------------------------------------------

    valid_from: str | None = None
    """ISO-8601 date string. Required for TEMPORAL relationships.
    None for PERSISTENT and EVENT_DRIVEN edges."""

    valid_until: str | None = None
    """ISO-8601 date string marking when a TEMPORAL relationship ends.
    None if the relationship is PERSISTENT or not yet superseded.
    Per Atlas §8 open question: TEMPORAL relationships approaching or past
    this date should not be silently treated as active."""
