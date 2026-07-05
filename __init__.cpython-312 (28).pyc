"""Dimension definitions — the single source of truth for dimension metadata.

Justified by: docs/04-FINANCE-DNA.md §2 (qualification criteria), §3 (type
system), §5C (dimension categories), and §6 (individual dimension entries).

This file answers WHAT each dimension is, not WHAT it scores. Scoring tables
live exclusively in rules.py. Keeping them separate enforces ED-004 principle 2
(Never duplicate knowledge): the name, category, value structure, temporal
behavior, and aggregation rule for Capital Intensity exist in exactly one place —
here — and rules.py imports them rather than redeclaring them.

DimensionDefinition is an internal Finance DNA type. It is NOT a cross-module
artifact — Atlas consumes Dimension objects from backend/models/, not
DimensionDefinition objects. DimensionDefinition is the passport that defines
a dimension; Dimension is the passport stamp that records one Asset's score.

The six V0.1 dimensions are the subset from Finance DNA §6 sufficient to
demonstrate every category of dimension (business structure, cost & capital,
macroeconomic sensitivity, innovation, revenue, governance) without creating
months of work before Atlas can consume the output. They are locked for V0.1
per the architectural review — no additions without an updated section in §6.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.models.enums import DimensionCategory, TemporalBehavior, ValueStructure


@dataclass(frozen=True)
class DimensionDefinition:
    """Metadata describing a Financial Dimension — no values, no scores.

    Every field maps directly to a property Finance DNA §2 requires a
    qualified dimension to have. qualification_rationale records the
    argument for why this dimension passed §2's five criteria, so that
    argument doesn't need to be reconstructed six months later when
    someone asks why it's in the registry.
    """

    name: str
    """Canonical name matching Finance DNA §6 (e.g. 'Capital Intensity').
    Must exactly match the name field used in Dimension objects produced
    by the corresponding evaluator in rules.py."""

    category: DimensionCategory
    """One of the six official categories from Finance DNA §5C."""

    value_structure: ValueStructure
    """CONTINUOUS, CATEGORICAL, or BINARY — from Finance DNA §3, Axis 1."""

    temporal_behavior: TemporalBehavior
    """STATIC or TIME_VARYING — from Finance DNA §3, Axis 2."""

    aggregation_rule: str
    """How this dimension aggregates into Portfolio DNA.
    'weighted_average' | 'distribution' | 'weighted_proportion'.
    Must match the Aggregation Rule column in Finance DNA §6."""

    qualification_rationale: str
    """Why this dimension passed Finance DNA §2's five qualification criteria.
    This is engineering documentation, not a user-facing string. Its job is
    to make the acceptance decision traceable to a human reading rules.py
    six months after the fact."""


# ---------------------------------------------------------------------------
# The six locked V0.1 dimensions.
# Source: docs/04-FINANCE-DNA.md §6 (Individual Dimensions).
# Adding a dimension requires a corresponding §6 entry AND a new evaluator
# in rules.py AND a new entry in registry.py. No partial additions.
# ---------------------------------------------------------------------------

CAPITAL_INTENSITY: DimensionDefinition = DimensionDefinition(
    name="Capital Intensity",
    category=DimensionCategory.COST_AND_CAPITAL_STRUCTURE,
    value_structure=ValueStructure.CONTINUOUS,
    temporal_behavior=TemporalBehavior.STATIC,
    aggregation_rule="weighted_average",
    qualification_rationale=(
        "Passes all five Finance DNA §2 criteria. Reflects economic identity "
        "(fixed-asset reliance is structural, not sentiment-driven). Comparable "
        "across sectors (PP&E / Revenue computes identically for software and "
        "steel). Composable as weighted average. Directly influences Interest "
        "Rate Sensitivity and Operating Leverage. V0.1: sector-level "
        "approximation pending company-specific PP&E / Revenue data."
    ),
)

COMMODITY_INPUT_EXPOSURE: DimensionDefinition = DimensionDefinition(
    name="Commodity Input Exposure",
    category=DimensionCategory.MACROECONOMIC_AND_REGULATORY_SENSITIVITY,
    value_structure=ValueStructure.CONTINUOUS,
    temporal_behavior=TemporalBehavior.TIME_VARYING,
    aggregation_rule="weighted_average",
    qualification_rationale=(
        "Passes all five Finance DNA §2 criteria. Commodity reliance is an "
        "economic identity property (it describes the cost structure, not the "
        "share price). Comparable across sectors. Composable as weighted "
        "average. Directly drives Inflation Sensitivity. V0.1: sector-level "
        "approximation; disclosed hedging notes provide company-specific data "
        "in future versions."
    ),
)

SUPPLY_CHAIN_COMPLEXITY: DimensionDefinition = DimensionDefinition(
    name="Supply Chain Complexity",
    category=DimensionCategory.BUSINESS_STRUCTURE,
    value_structure=ValueStructure.CONTINUOUS,
    temporal_behavior=TemporalBehavior.STATIC,
    aggregation_rule="weighted_average",
    qualification_rationale=(
        "Passes all five Finance DNA §2 criteria. Multi-tier global supply "
        "chain involvement is a structural property of a business model. "
        "Comparable across sectors. Composable. Directly drives Dependency "
        "relationships in Atlas (a highly complex supply chain implies more "
        "Atlas edges). V0.1: sector-level approximation."
    ),
)

INNOVATION_INTENSITY: DimensionDefinition = DimensionDefinition(
    name="Innovation Intensity",
    category=DimensionCategory.INNOVATION_AND_TECHNOLOGY,
    value_structure=ValueStructure.CONTINUOUS,
    temporal_behavior=TemporalBehavior.TIME_VARYING,
    aggregation_rule="weighted_average",
    qualification_rationale=(
        "Passes all five Finance DNA §2 criteria. R&D-to-revenue ratio is a "
        "structural property of the business model, not a valuation signal. "
        "Comparable across sectors (R&D / Revenue is dimensionless). Composable. "
        "Drives Technology Obsolescence Risk (a Derived dimension). Directly "
        "disclosed in financial filings. V0.1: sector-level approximation "
        "pending per-company R&D / Revenue data."
    ),
)

REGULATORY_EXPOSURE: DimensionDefinition = DimensionDefinition(
    name="Regulatory Exposure",
    category=DimensionCategory.MACROECONOMIC_AND_REGULATORY_SENSITIVITY,
    value_structure=ValueStructure.CONTINUOUS,
    temporal_behavior=TemporalBehavior.TIME_VARYING,
    aggregation_rule="weighted_average",
    qualification_rationale=(
        "Passes all five Finance DNA §2 criteria. Regulatory oversight degree "
        "is structural and does not move with market sentiment. Comparable "
        "across sectors. Composable. Drives Regulatory Dependency relationships "
        "in Atlas. Disclosed in risk factor sections and regulatory body "
        "public records. V0.1: sector-level approximation."
    ),
)

GEOGRAPHIC_REVENUE_CONCENTRATION: DimensionDefinition = DimensionDefinition(
    name="Geographic Revenue Concentration",
    category=DimensionCategory.REVENUE_STRUCTURE,
    value_structure=ValueStructure.CONTINUOUS,
    temporal_behavior=TemporalBehavior.TIME_VARYING,
    aggregation_rule="weighted_average",
    qualification_rationale=(
        "Passes all five Finance DNA §2 criteria. Revenue concentration by "
        "geography is an economic identity property (structural, not "
        "sentiment). Comparable across sectors. Composable. Primary input "
        "to Currency Exposure (a Derived dimension). Disclosed via segment "
        "reporting. V0.1: sector-level approximation pending actual geographic "
        "revenue breakdowns from filings."
    ),
)

# Registry of all V0.1 definitions — ordered; order determines evaluation order.
ALL_DEFINITIONS: tuple[DimensionDefinition, ...] = (
    CAPITAL_INTENSITY,
    COMMODITY_INPUT_EXPOSURE,
    SUPPLY_CHAIN_COMPLEXITY,
    INNOVATION_INTENSITY,
    REGULATORY_EXPOSURE,
    GEOGRAPHIC_REVENUE_CONCENTRATION,
)
