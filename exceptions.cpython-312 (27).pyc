"""Finance DNA scoring rules — one evaluator function per dimension.

Justified by: docs/04-FINANCE-DNA.md §6 (Individual Dimensions) and
ED-004 (Engineering Principles, specifically: Deterministic before
probabilistic).

This file answers WHAT a dimension scores for a given Asset. It contains
nothing else — no category, no type system, no qualification rationale.
Those live in dimensions.py, which is the single source of truth for
dimension metadata (ED-004 principle 2: Never duplicate knowledge).

Structure of each evaluator
----------------------------
1. Validate required Asset fields → MissingAssetDataError if absent.
2. Look up score: (sector, industry) → float, with sector-only fallback.
3. Construct and return an immutable Dimension from the DimensionDefinition
   metadata imported from dimensions.py.

V0.1 data model
---------------
All V0.1 scores are sector-level approximations derived from the Asset's
sector and industry classification. No company-specific financial data
(PP&E, R&D spend, revenue by geography) is used yet — that arrives when
Ingestion is extended to load company financials.

Confidence: every V0.1 Dimension carries _V01_CONFIDENCE = 0.6.
This is explicitly a placeholder, not a computed value. The architectural
review (06-JANUS.md) reserved confidence computation for Janus; Finance DNA
§2 does not require confidence to be computed here. 0.6 signals
'sector-level approximation, treat with appropriate scepticism' to any
downstream module that inspects it.

evidence_source: EvidenceSource.DERIVED — scores are inferred from
sector/industry knowledge, not read directly from a company filing.
primitive: False — same reason.

See SCORING-RATIONALE.md for the human justification behind every number.
"""

from __future__ import annotations

from backend.finance_dna.dimensions import (
    CAPITAL_INTENSITY,
    COMMODITY_INPUT_EXPOSURE,
    GEOGRAPHIC_REVENUE_CONCENTRATION,
    INNOVATION_INTENSITY,
    REGULATORY_EXPOSURE,
    SUPPLY_CHAIN_COMPLEXITY,
)
from backend.finance_dna.exceptions import MissingAssetDataError
from backend.models import Asset, Dimension
from backend.models.enums import EvidenceSource

# ---------------------------------------------------------------------------
# V0.1 universal constants
# ---------------------------------------------------------------------------

_V01_CONFIDENCE: float = 0.6
"""Fixed placeholder confidence for all V0.1 sector-level scores.
Confidence computation belongs to Janus (06-JANUS.md §2). Finance DNA §2
requires evidence-traceability, not a computed confidence value at this stage.
This value signals 'sector approximation' to any reader of the Dimension."""

_EVIDENCE_NOTE: str = (
    "V0.1 sector-level approximation. "
    "See backend/finance_dna/SCORING-RATIONALE.md for justification."
)


def _evidence(asset: Asset, extra: str = "") -> tuple[str, ...]:
    """Build a standard V0.1 evidence tuple for a given Asset."""
    base = f"Sector: {asset.sector!r}, Industry: {asset.industry!r}. " + _EVIDENCE_NOTE
    if extra:
        return (base, extra)
    return (base,)


def _lookup(
    asset: Asset,
    scores: dict[tuple[str, str], float],
    fallback: dict[str, float],
    dimension_name: str,
) -> float:
    """Look up a score using (sector, industry) with explicit sector fallback.

    Uses `is None` checks rather than truthiness (`or`) so that a legitimate
    score of 0.0 is never silently replaced by the sector fallback. This is
    the correct pattern for any lookup that must handle the full float range.
    """
    if asset.sector is None:
        raise MissingAssetDataError(asset.id, "sector", dimension_name)
    key = (asset.sector, asset.industry or "")
    score = scores.get(key)
    if score is None:
        score = fallback.get(asset.sector)
    if score is None:
        raise MissingAssetDataError(asset.id, "sector (unrecognised)", dimension_name)
    return score


# ---------------------------------------------------------------------------
# Capital Intensity
# 04-FINANCE-DNA.md §6 — Cost & Capital Structure
# How much fixed capital the business requires relative to output.
# ---------------------------------------------------------------------------

_CAPITAL_INTENSITY_SCORES: dict[tuple[str, str], float] = {
    ("Technology", "Semiconductors"): 0.85,
    ("Technology", "Software"): 0.20,
    ("Technology", "Consumer Electronics"): 0.55,
    ("Technology", "Internet Services"): 0.35,
    ("Consumer Discretionary", "E-Commerce & Cloud Services"): 0.50,
    ("Consumer Staples", "Food & Beverages"): 0.60,
}
_CAPITAL_INTENSITY_FALLBACK: dict[str, float] = {
    "Technology": 0.45,
    "Consumer Discretionary": 0.45,
    "Consumer Staples": 0.58,
}


def evaluate_capital_intensity(asset: Asset, as_of: str) -> Dimension:
    score = _lookup(
        asset,
        _CAPITAL_INTENSITY_SCORES,
        _CAPITAL_INTENSITY_FALLBACK,
        CAPITAL_INTENSITY.name,
    )
    return Dimension(
        name=CAPITAL_INTENSITY.name,
        asset_id=asset.id,
        value_structure=CAPITAL_INTENSITY.value_structure,
        temporal_behavior=CAPITAL_INTENSITY.temporal_behavior,
        score=score,
        confidence=_V01_CONFIDENCE,
        evidence=_evidence(asset),
        evidence_source=EvidenceSource.DERIVED,
        category=CAPITAL_INTENSITY.category,
        aggregation_rule=CAPITAL_INTENSITY.aggregation_rule,
        as_of=as_of,
        primitive=False,
    )


# ---------------------------------------------------------------------------
# Commodity Input Exposure
# 04-FINANCE-DNA.md §6 — Macroeconomic & Regulatory Sensitivity
# Degree to which costs are tied to commodity prices.
# ---------------------------------------------------------------------------

_COMMODITY_SCORES: dict[tuple[str, str], float] = {
    ("Technology", "Semiconductors"): 0.90,
    ("Technology", "Software"): 0.05,
    ("Technology", "Consumer Electronics"): 0.65,
    ("Technology", "Internet Services"): 0.15,
    ("Consumer Discretionary", "E-Commerce & Cloud Services"): 0.30,
    ("Consumer Staples", "Food & Beverages"): 0.85,
}
_COMMODITY_FALLBACK: dict[str, float] = {
    "Technology": 0.40,
    "Consumer Discretionary": 0.30,
    "Consumer Staples": 0.75,
}


def evaluate_commodity_input_exposure(asset: Asset, as_of: str) -> Dimension:
    score = _lookup(
        asset,
        _COMMODITY_SCORES,
        _COMMODITY_FALLBACK,
        COMMODITY_INPUT_EXPOSURE.name,
    )
    return Dimension(
        name=COMMODITY_INPUT_EXPOSURE.name,
        asset_id=asset.id,
        value_structure=COMMODITY_INPUT_EXPOSURE.value_structure,
        temporal_behavior=COMMODITY_INPUT_EXPOSURE.temporal_behavior,
        score=score,
        confidence=_V01_CONFIDENCE,
        evidence=_evidence(asset),
        evidence_source=EvidenceSource.DERIVED,
        category=COMMODITY_INPUT_EXPOSURE.category,
        aggregation_rule=COMMODITY_INPUT_EXPOSURE.aggregation_rule,
        as_of=as_of,
        primitive=False,
    )


# ---------------------------------------------------------------------------
# Supply Chain Complexity
# 04-FINANCE-DNA.md §6 — Business Structure
# Degree of multi-tier, global supply chain involvement.
# ---------------------------------------------------------------------------

_SUPPLY_CHAIN_SCORES: dict[tuple[str, str], float] = {
    ("Technology", "Semiconductors"): 0.95,
    ("Technology", "Software"): 0.10,
    ("Technology", "Consumer Electronics"): 0.85,
    ("Technology", "Internet Services"): 0.30,
    ("Consumer Discretionary", "E-Commerce & Cloud Services"): 0.70,
    ("Consumer Staples", "Food & Beverages"): 0.65,
}
_SUPPLY_CHAIN_FALLBACK: dict[str, float] = {
    "Technology": 0.50,
    "Consumer Discretionary": 0.65,
    "Consumer Staples": 0.60,
}


def evaluate_supply_chain_complexity(asset: Asset, as_of: str) -> Dimension:
    score = _lookup(
        asset,
        _SUPPLY_CHAIN_SCORES,
        _SUPPLY_CHAIN_FALLBACK,
        SUPPLY_CHAIN_COMPLEXITY.name,
    )
    return Dimension(
        name=SUPPLY_CHAIN_COMPLEXITY.name,
        asset_id=asset.id,
        value_structure=SUPPLY_CHAIN_COMPLEXITY.value_structure,
        temporal_behavior=SUPPLY_CHAIN_COMPLEXITY.temporal_behavior,
        score=score,
        confidence=_V01_CONFIDENCE,
        evidence=_evidence(asset),
        evidence_source=EvidenceSource.DERIVED,
        category=SUPPLY_CHAIN_COMPLEXITY.category,
        aggregation_rule=SUPPLY_CHAIN_COMPLEXITY.aggregation_rule,
        as_of=as_of,
        primitive=False,
    )


# ---------------------------------------------------------------------------
# Innovation Intensity
# 04-FINANCE-DNA.md §6 — Innovation & Technology (merges R&D Intensity)
# R&D spend relative to revenue; structural property of the business model.
# ---------------------------------------------------------------------------

_INNOVATION_SCORES: dict[tuple[str, str], float] = {
    ("Technology", "Semiconductors"): 0.85,
    ("Technology", "Software"): 0.80,
    ("Technology", "Consumer Electronics"): 0.75,
    ("Technology", "Internet Services"): 0.85,
    ("Consumer Discretionary", "E-Commerce & Cloud Services"): 0.70,
    ("Consumer Staples", "Food & Beverages"): 0.20,
}
_INNOVATION_FALLBACK: dict[str, float] = {
    "Technology": 0.80,
    "Consumer Discretionary": 0.55,
    "Consumer Staples": 0.20,
}


def evaluate_innovation_intensity(asset: Asset, as_of: str) -> Dimension:
    score = _lookup(
        asset,
        _INNOVATION_SCORES,
        _INNOVATION_FALLBACK,
        INNOVATION_INTENSITY.name,
    )
    return Dimension(
        name=INNOVATION_INTENSITY.name,
        asset_id=asset.id,
        value_structure=INNOVATION_INTENSITY.value_structure,
        temporal_behavior=INNOVATION_INTENSITY.temporal_behavior,
        score=score,
        confidence=_V01_CONFIDENCE,
        evidence=_evidence(asset),
        evidence_source=EvidenceSource.DERIVED,
        category=INNOVATION_INTENSITY.category,
        aggregation_rule=INNOVATION_INTENSITY.aggregation_rule,
        as_of=as_of,
        primitive=False,
    )


# ---------------------------------------------------------------------------
# Regulatory Exposure
# 04-FINANCE-DNA.md §6 — Macroeconomic & Regulatory Sensitivity
# Degree of regulatory oversight affecting operations.
# ---------------------------------------------------------------------------

_REGULATORY_SCORES: dict[tuple[str, str], float] = {
    ("Technology", "Semiconductors"): 0.60,
    ("Technology", "Software"): 0.65,
    ("Technology", "Consumer Electronics"): 0.55,
    ("Technology", "Internet Services"): 0.80,
    ("Consumer Discretionary", "E-Commerce & Cloud Services"): 0.65,
    ("Consumer Staples", "Food & Beverages"): 0.70,
}
_REGULATORY_FALLBACK: dict[str, float] = {
    "Technology": 0.60,
    "Consumer Discretionary": 0.60,
    "Consumer Staples": 0.65,
}


def evaluate_regulatory_exposure(asset: Asset, as_of: str) -> Dimension:
    score = _lookup(
        asset,
        _REGULATORY_SCORES,
        _REGULATORY_FALLBACK,
        REGULATORY_EXPOSURE.name,
    )
    return Dimension(
        name=REGULATORY_EXPOSURE.name,
        asset_id=asset.id,
        value_structure=REGULATORY_EXPOSURE.value_structure,
        temporal_behavior=REGULATORY_EXPOSURE.temporal_behavior,
        score=score,
        confidence=_V01_CONFIDENCE,
        evidence=_evidence(asset),
        evidence_source=EvidenceSource.DERIVED,
        category=REGULATORY_EXPOSURE.category,
        aggregation_rule=REGULATORY_EXPOSURE.aggregation_rule,
        as_of=as_of,
        primitive=False,
    )


# ---------------------------------------------------------------------------
# Geographic Revenue Concentration
# 04-FINANCE-DNA.md §6 — Revenue Structure
# Lower score = more globally diversified revenue.
# ---------------------------------------------------------------------------

_GEO_SCORES: dict[tuple[str, str], float] = {
    ("Technology", "Semiconductors"): 0.60,
    ("Technology", "Software"): 0.35,
    ("Technology", "Consumer Electronics"): 0.45,
    ("Technology", "Internet Services"): 0.35,
    ("Consumer Discretionary", "E-Commerce & Cloud Services"): 0.55,
    ("Consumer Staples", "Food & Beverages"): 0.45,
}
_GEO_FALLBACK: dict[str, float] = {
    "Technology": 0.45,
    "Consumer Discretionary": 0.50,
    "Consumer Staples": 0.45,
}


def evaluate_geographic_revenue_concentration(asset: Asset, as_of: str) -> Dimension:
    score = _lookup(
        asset,
        _GEO_SCORES,
        _GEO_FALLBACK,
        GEOGRAPHIC_REVENUE_CONCENTRATION.name,
    )
    return Dimension(
        name=GEOGRAPHIC_REVENUE_CONCENTRATION.name,
        asset_id=asset.id,
        value_structure=GEOGRAPHIC_REVENUE_CONCENTRATION.value_structure,
        temporal_behavior=GEOGRAPHIC_REVENUE_CONCENTRATION.temporal_behavior,
        score=score,
        confidence=_V01_CONFIDENCE,
        evidence=_evidence(
            asset,
            "Note: V0.1 uses sector-level approximation. "
            "Actual geographic revenue breakdown requires segment filing data.",
        ),
        evidence_source=EvidenceSource.DERIVED,
        category=GEOGRAPHIC_REVENUE_CONCENTRATION.category,
        aggregation_rule=GEOGRAPHIC_REVENUE_CONCENTRATION.aggregation_rule,
        as_of=as_of,
        primitive=False,
    )
