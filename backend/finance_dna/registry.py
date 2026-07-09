"""Finance DNA dimension registry — V0.2: 15 dimensions.

Justified by: docs/04-FINANCE-DNA.md §5, docs/04-FINANCE-DNA-v0.2.md.

V0.1 added 6 dimensions. V0.2 adds 9 more for a total of 15.
The only change from V0.1 is adding 9 RegisteredDimension entries.
The evaluator, the models, and the public evaluate() function are unchanged.
That is the proof the V0.1 architecture was correctly designed.

Evaluation order: V0.1 dimensions first, V0.2 dimensions after.
Existing code that uses FinanceDNA.dimensions positionally is unaffected.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from backend.finance_dna.dimensions import (
    CAPITAL_INTENSITY,
    COMMODITY_INPUT_EXPOSURE,
    CURRENCY_EXPOSURE,
    CUSTOMER_CONCENTRATION,
    DEBT_SENSITIVITY,
    ENERGY_DEPENDENCY,
    GEOGRAPHIC_REVENUE_CONCENTRATION,
    INNOVATION_INTENSITY,
    LABOUR_INTENSITY,
    PRICING_POWER,
    REGULATORY_COMPLIANCE_COST,
    REGULATORY_EXPOSURE,
    REVENUE_DIVERSIFICATION,
    SUPPLIER_CONCENTRATION,
    SUPPLY_CHAIN_COMPLEXITY,
    DimensionDefinition,
)
from backend.finance_dna.rules import (
    evaluate_capital_intensity,
    evaluate_commodity_input_exposure,
    evaluate_currency_exposure,
    evaluate_customer_concentration,
    evaluate_debt_sensitivity,
    evaluate_energy_dependency,
    evaluate_geographic_revenue_concentration,
    evaluate_innovation_intensity,
    evaluate_labour_intensity,
    evaluate_pricing_power,
    evaluate_regulatory_compliance_cost,
    evaluate_regulatory_exposure,
    evaluate_revenue_diversification,
    evaluate_supplier_concentration,
    evaluate_supply_chain_complexity,
)
from backend.models import Asset, Dimension

type EvaluatorFn = Callable[[Asset, str], Dimension]


@dataclass
class RegisteredDimension:
    """A DimensionDefinition paired with its evaluator function."""

    definition: DimensionDefinition
    evaluator: EvaluatorFn


# ---------------------------------------------------------------------------
# The V0.2 registry — 15 dimensions in evaluation order.
# V0.1 (6) precede V0.2 (9) for positional backward compatibility.
# ---------------------------------------------------------------------------

REGISTRY: tuple[RegisteredDimension, ...] = (
    # V0.1 — six locked dimensions
    RegisteredDimension(CAPITAL_INTENSITY, evaluate_capital_intensity),
    RegisteredDimension(COMMODITY_INPUT_EXPOSURE, evaluate_commodity_input_exposure),
    RegisteredDimension(SUPPLY_CHAIN_COMPLEXITY, evaluate_supply_chain_complexity),
    RegisteredDimension(INNOVATION_INTENSITY, evaluate_innovation_intensity),
    RegisteredDimension(REGULATORY_EXPOSURE, evaluate_regulatory_exposure),
    RegisteredDimension(
        GEOGRAPHIC_REVENUE_CONCENTRATION,
        evaluate_geographic_revenue_concentration,
    ),
    # V0.2 — nine new dimensions
    RegisteredDimension(PRICING_POWER, evaluate_pricing_power),
    RegisteredDimension(CUSTOMER_CONCENTRATION, evaluate_customer_concentration),
    RegisteredDimension(SUPPLIER_CONCENTRATION, evaluate_supplier_concentration),
    RegisteredDimension(REVENUE_DIVERSIFICATION, evaluate_revenue_diversification),
    RegisteredDimension(DEBT_SENSITIVITY, evaluate_debt_sensitivity),
    RegisteredDimension(CURRENCY_EXPOSURE, evaluate_currency_exposure),
    RegisteredDimension(ENERGY_DEPENDENCY, evaluate_energy_dependency),
    RegisteredDimension(LABOUR_INTENSITY, evaluate_labour_intensity),
    RegisteredDimension(REGULATORY_COMPLIANCE_COST, evaluate_regulatory_compliance_cost),
)
