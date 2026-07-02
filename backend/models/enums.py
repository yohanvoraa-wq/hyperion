"""Enumerations shared across all domain models.

Every enum here is the direct Python encoding of a concept already named in
the conceptual documents. Nothing is invented; the source section is cited
on each class.
"""

from enum import Enum, auto

# ---------------------------------------------------------------------------
# 04-FINANCE-DNA.md §3 — Types of Financial Dimensions
# ---------------------------------------------------------------------------


class ValueStructure(Enum):
    """The shape of the value a Financial Dimension holds at any moment."""

    CONTINUOUS = auto()  # bounded scalar; aggregates by weighted average
    CATEGORICAL = auto()  # fixed, mutually exclusive labels; aggregates as distribution
    BINARY = auto()  # present / absent; aggregates as weighted proportion


class TemporalBehavior(Enum):
    """How a Financial Dimension's value behaves as time passes."""

    STATIC = auto()  # stable until a structural event overwrites it
    TIME_VARYING = auto()  # expected to drift gradually; snapshot must be dated


# ---------------------------------------------------------------------------
# 04-FINANCE-DNA.md §5 — Dimension Categories
# ---------------------------------------------------------------------------


class DimensionCategory(Enum):
    """The six official categories from Finance DNA Section 5C."""

    BUSINESS_STRUCTURE = auto()
    REVENUE_STRUCTURE = auto()
    COST_AND_CAPITAL_STRUCTURE = auto()
    MACROECONOMIC_AND_REGULATORY_SENSITIVITY = auto()
    INNOVATION_AND_TECHNOLOGY = auto()
    GOVERNANCE_AND_CAPITAL_ALLOCATION = auto()


# ---------------------------------------------------------------------------
# 05-ATLAS.md §3 — Node types
# ---------------------------------------------------------------------------


class AssetType(Enum):
    """The Economic Actor node types from Atlas Section 3."""

    COMPANY = auto()  # publicly traded company — Version 1 scope (04 §4)
    SUPPLY_CHAIN_ENTITY = auto()  # non-Asset participant in a supply chain


class ContextNodeType(Enum):
    """Economic Context node types from Atlas Section 3."""

    COMMODITY = auto()
    GEOGRAPHY = auto()
    CURRENCY = auto()
    MACRO_FACTOR = auto()
    INDUSTRY = auto()
    REGULATION = auto()
    ECONOMIC_EVENT = auto()


# ---------------------------------------------------------------------------
# 05-ATLAS.md §4 — Relationship types
# ---------------------------------------------------------------------------


class RelationshipType(Enum):
    """The nine canonical relationship types from Atlas Section 4.

    depends_on / supplies are one Bidirectional relationship (Atlas §5),
    stored once and read in either direction — not two separate types.
    """

    DEPENDS_ON_SUPPLIES = auto()  # Bidirectional; Nestlé ↔ Coffee supplier
    COMPETES_WITH = auto()  # Symmetric
    SELLS_TO = auto()  # Directed; Temporal or Persistent per instance
    EXPORTS_TO = auto()  # Directed; Persistent
    LOCATED_IN = auto()  # Directed; Persistent
    EXPOSED_TO = auto()  # Directed; Persistent
    AFFECTED_BY = auto()  # Directed; Event-driven
    REGULATED_BY = auto()  # Directed; Persistent
    BELONGS_TO = auto()  # Directed; Persistent — added in Atlas §4 gap fix


# ---------------------------------------------------------------------------
# 05-ATLAS.md §5 — Relationship Characteristics
# ---------------------------------------------------------------------------


class Directionality(Enum):
    """From Atlas §5: Axis 1 of relationship characteristics."""

    DIRECTED = auto()  # meaning holds one way only
    BIDIRECTIONAL = auto()  # one fact, different label per direction
    SYMMETRIC = auto()  # same label, same meaning, either direction


class RelationshipTemporality(Enum):
    """From Atlas §5: Axis 2 of relationship characteristics.

    Named RelationshipTemporality (not Temporality) to avoid shadowing the
    concept of temporal behavior in Finance DNA dimensions.
    """

    PERSISTENT = auto()  # holds until a structural change overwrites it
    TEMPORAL = auto()  # holds for a known, bounded term
    EVENT_DRIVEN = auto()  # tied to a discrete occurrence


class Cardinality(Enum):
    """From Atlas §5."""

    ONE_TO_ONE = auto()
    ONE_TO_MANY = auto()
    MANY_TO_MANY = auto()


class EvidenceSource(Enum):
    """From Atlas §5 and Finance DNA §2 (evidence-traceability criterion)."""

    DISCLOSED = auto()  # directly stated in a filing or primary source
    PUBLIC_RECORD = auto()  # independently verifiable, not company-disclosed
    DERIVED = auto()  # inferred from a combination of qualified sources


# ---------------------------------------------------------------------------
# 03-BLIND-SPOT-FRAMEWORK.md §3 — Blind Spot Taxonomy
# ---------------------------------------------------------------------------


class BlindSpotCategory(Enum):
    """The six taxonomy categories from Blind Spot Framework Section 3.

    A BlindSpot may belong to more than one category simultaneously.
    The taxonomy exists to improve explanation, not force classification.
    """

    STRUCTURAL = auto()
    CONCENTRATION = auto()
    DEPENDENCY = auto()
    MACROECONOMIC = auto()
    TEMPORAL = auto()
    BEHAVIORAL = auto()


# ---------------------------------------------------------------------------
# 06-JANUS.md §3 — Reasoning Modes
# ---------------------------------------------------------------------------


class ReasoningMode(Enum):
    """The five reasoning modes from Janus Section 3.

    Not algorithms — the different shapes a justified conclusion can take.
    """

    DEDUCTIVE = auto()  # single forward traversal to a natural conclusion
    COMPARATIVE = auto()  # same pattern from two different starting nodes
    ANALOGICAL = auto()  # matching the shape of a path against a historical instance
    COUNTERFACTUAL = auto()  # same traversal with one edge hypothetically altered
    EXPLORATORY = auto()  # outward from one node across every available edge
