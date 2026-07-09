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

# ---------------------------------------------------------------------------
# V0.2 scoring principles (frozen — docs/04-FINANCE-DNA-v0.2.md)
# Conservative over optimistic. Unknown over fabricated.
# Deterministic over statistical. Publicly explainable over empirically fitted.
# Benchmark-driven over coverage-driven.
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# The nine V0.2 dimensions.
# Source: docs/04-FINANCE-DNA-v0.2.md
# Approximation Level: B (Industry) for all nine.
# Every dimension below earned its place by serving at least one canonical
# reasoning pattern in research/canonical-reasoning-patterns.md.
# ---------------------------------------------------------------------------

# --- Market Structure -------------------------------------------------------

PRICING_POWER: DimensionDefinition = DimensionDefinition(
    name="Pricing Power",
    category=DimensionCategory.MARKET_STRUCTURE,
    value_structure=ValueStructure.CONTINUOUS,
    temporal_behavior=TemporalBehavior.STATIC,
    aggregation_rule="weighted_average",
    qualification_rationale=(
        "Passes all five Finance DNA §2 criteria. Pricing power is an economic "
        "identity property of the business model — it describes structural "
        "demand elasticity, not sentiment or share price. Comparable across "
        "sectors (high-moat vs commodity businesses differ materially). "
        "Composable as weighted average. Directly modulates the severity of "
        "Commodity Shock, Energy Dependency, and Labour Exposure blind spots: "
        "a company with HIGH pricing power can pass cost shocks to customers; "
        "LOW pricing power absorbs them in margin. V0.2: Level B industry "
        "approximation. Level A requires realised price increase vs volume "
        "impact from earnings call analysis."
    ),
)

CUSTOMER_CONCENTRATION: DimensionDefinition = DimensionDefinition(
    name="Customer Concentration",
    category=DimensionCategory.MARKET_STRUCTURE,
    value_structure=ValueStructure.CONTINUOUS,
    temporal_behavior=TemporalBehavior.TIME_VARYING,
    aggregation_rule="weighted_average",
    qualification_rationale=(
        "Passes all five Finance DNA §2 criteria. Revenue dependence on a small "
        "customer set is a structural property of the business model (B2B "
        "specialists vs mass-market consumer companies differ materially and "
        "persistently). Comparable across sectors. Composable. Directly drives "
        "the Customer Concentration canonical reasoning pattern: a single "
        "customer reducing orders is a binary demand shock, not a gradual "
        "market shift. V0.2: Level B. Level A requires 10-K customer "
        "concentration disclosures (required when >10% from a single customer)."
    ),
)

SUPPLIER_CONCENTRATION: DimensionDefinition = DimensionDefinition(
    name="Supplier Concentration",
    category=DimensionCategory.MARKET_STRUCTURE,
    value_structure=ValueStructure.CONTINUOUS,
    temporal_behavior=TemporalBehavior.STATIC,
    aggregation_rule="weighted_average",
    qualification_rationale=(
        "Passes all five Finance DNA §2 criteria. Extends Supply Chain "
        "Complexity with a directional fragility measure: complexity measures "
        "breadth (how many tiers, how many geographies); concentration measures "
        "fragility (how many alternatives exist if the primary supplier fails). "
        "A company with a complex supply chain may have many diversified "
        "suppliers (LOW concentration) or one critical single-source dependency "
        "(HIGH concentration). Both properties matter for different patterns. "
        "Directly drives the Supplier Concentration reasoning pattern. V0.2: "
        "Level B. Level A requires supplier risk factor disclosures from 10-K."
    ),
)

# --- Financial Structure ----------------------------------------------------

REVENUE_DIVERSIFICATION: DimensionDefinition = DimensionDefinition(
    name="Revenue Diversification",
    category=DimensionCategory.FINANCIAL_STRUCTURE,
    value_structure=ValueStructure.CONTINUOUS,
    temporal_behavior=TemporalBehavior.TIME_VARYING,
    aggregation_rule="weighted_average",
    qualification_rationale=(
        "Passes all five Finance DNA §2 criteria. Revenue distribution across "
        "products, geographies, and customers is a structural property of the "
        "business model. Acts as a confidence modulator across all patterns: "
        "a company with LOW revenue diversification has less ability to absorb "
        "a blind spot in any single area (the shock affects a larger proportion "
        "of total revenue). Comparable across sectors. Composable. V0.2: "
        "Level B. Level A requires segment revenue percentages from annual "
        "reports (Herfindahl-Hirschman Index of revenue concentration)."
    ),
)

DEBT_SENSITIVITY: DimensionDefinition = DimensionDefinition(
    name="Debt Sensitivity",
    category=DimensionCategory.FINANCIAL_STRUCTURE,
    value_structure=ValueStructure.CONTINUOUS,
    temporal_behavior=TemporalBehavior.TIME_VARYING,
    aggregation_rule="weighted_average",
    qualification_rationale=(
        "Passes all five Finance DNA §2 criteria. Non-redundant with Capital "
        "Intensity: Capital Intensity measures fixed asset requirements (how "
        "much capital is needed); Debt Sensitivity measures financing cost "
        "exposure (how sensitive the P&L is to interest rate changes on "
        "that capital). A cash-rich semiconductor company (HIGH Capital "
        "Intensity, LOW Debt Sensitivity) differs fundamentally from a "
        "leveraged REIT (HIGH Capital Intensity, HIGH Debt Sensitivity). "
        "Directly drives the Interest Rate Sensitivity reasoning pattern. "
        "V0.2: Level B/C depending on industry. Level A requires net "
        "debt/EBITDA and interest coverage ratio from balance sheet."
    ),
)

CURRENCY_EXPOSURE: DimensionDefinition = DimensionDefinition(
    name="Currency Exposure",
    category=DimensionCategory.FINANCIAL_STRUCTURE,
    value_structure=ValueStructure.CONTINUOUS,
    temporal_behavior=TemporalBehavior.TIME_VARYING,
    aggregation_rule="weighted_average",
    qualification_rationale=(
        "Passes all five Finance DNA §2 criteria. Extends Geographic Revenue "
        "Concentration with the financial mechanics: geography tells us WHERE "
        "revenue comes from; Currency Exposure tells us WHAT the financial "
        "impact is when exchange rates move. A purely domestic company with "
        "some international suppliers has LOW currency exposure even if "
        "Geographic Revenue Concentration is moderate. Directly drives the "
        "Currency Exposure canonical reasoning pattern. V0.2: Level B. "
        "Level A requires geographic revenue breakdown and hedging program "
        "disclosures from annual reports (management FX sensitivity guidance)."
    ),
)

# --- Operational Structure --------------------------------------------------

ENERGY_DEPENDENCY: DimensionDefinition = DimensionDefinition(
    name="Energy Dependency",
    category=DimensionCategory.OPERATIONAL_STRUCTURE,
    value_structure=ValueStructure.CONTINUOUS,
    temporal_behavior=TemporalBehavior.STATIC,
    aggregation_rule="weighted_average",
    qualification_rationale=(
        "Passes all five Finance DNA §2 criteria. Non-redundant with Commodity "
        "Input Exposure: Commodity Input Exposure focuses on raw material "
        "inputs (silicon wafers, agricultural commodities, metals); Energy "
        "Dependency focuses on energy specifically, which has distinct price "
        "dynamics, policy risk (carbon taxes, renewable mandates), and "
        "reliability risk (grid instability) that raw material commodity "
        "exposure does not capture. Semiconductor fabs and data centres "
        "have very different commodity exposure from energy dependency "
        "— both are high in semiconductors. Directly drives the Energy "
        "Dependency reasoning pattern. V0.2: Level B — energy intensity is "
        "one of the best-documented industry characteristics (IEA, EPA data)."
    ),
)

LABOUR_INTENSITY: DimensionDefinition = DimensionDefinition(
    name="Labour Intensity",
    category=DimensionCategory.OPERATIONAL_STRUCTURE,
    value_structure=ValueStructure.CONTINUOUS,
    temporal_behavior=TemporalBehavior.STATIC,
    aggregation_rule="weighted_average",
    qualification_rationale=(
        "Passes all five Finance DNA §2 criteria. Labour is a primary cost "
        "in some industries and negligible in others — this is a structural "
        "property of the business model, not a market signal. A software "
        "company and a contract manufacturer can have similar revenues but "
        "radically different labour intensity. High labour intensity creates "
        "exposure to wage inflation, minimum wage legislation, unionisation, "
        "geographic workforce concentration, and labour disruption. Directly "
        "drives the Labour Exposure reasoning pattern. V0.2: Level B. "
        "Level A requires headcount, labour cost as % of revenue, and union "
        "coverage rates from annual reports and regulatory filings."
    ),
)

REGULATORY_COMPLIANCE_COST: DimensionDefinition = DimensionDefinition(
    name="Regulatory Compliance Cost",
    category=DimensionCategory.OPERATIONAL_STRUCTURE,
    value_structure=ValueStructure.CONTINUOUS,
    temporal_behavior=TemporalBehavior.TIME_VARYING,
    aggregation_rule="weighted_average",
    qualification_rationale=(
        "Passes all five Finance DNA §2 criteria. Extends Regulatory Exposure "
        "(which measures how exposed a company is to regulatory risk) with the "
        "cost and operational burden dimension. Two companies can have identical "
        "regulatory exposure but very different compliance costs: a pharmaceutical "
        "company bears FDA approval costs that structurally constrain speed to "
        "market; a software company bears GDPR compliance costs that are "
        "meaningful but not dominant. Compliance cost is an economic identity "
        "property (it describes the cost structure). Directly drives the "
        "Regulatory Risk reasoning pattern with greater precision than Regulatory "
        "Exposure alone. V0.2: Level B. Annual reassessment recommended because "
        "digital regulation (EU AI Act, DMA) is expanding rapidly."
    ),
)


# ---------------------------------------------------------------------------
# Complete 15-dimension registry — V0.1 (6) + V0.2 (9).
# Order determines evaluation order in the REGISTRY (registry.py).
# V0.1 dimensions precede V0.2 dimensions for backward compatibility:
# existing code that uses FinanceDNA.dimensions positionally is unaffected.
# ---------------------------------------------------------------------------

ALL_DEFINITIONS: tuple[DimensionDefinition, ...] = (
    # V0.1 — six locked dimensions
    CAPITAL_INTENSITY,
    COMMODITY_INPUT_EXPOSURE,
    SUPPLY_CHAIN_COMPLEXITY,
    INNOVATION_INTENSITY,
    REGULATORY_EXPOSURE,
    GEOGRAPHIC_REVENUE_CONCENTRATION,
    # V0.2 — nine new dimensions (Level B)
    PRICING_POWER,
    CUSTOMER_CONCENTRATION,
    SUPPLIER_CONCENTRATION,
    REVENUE_DIVERSIFICATION,
    DEBT_SENSITIVITY,
    CURRENCY_EXPOSURE,
    ENERGY_DEPENDENCY,
    LABOUR_INTENSITY,
    REGULATORY_COMPLIANCE_COST,
)
