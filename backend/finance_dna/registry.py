"""Finance DNA dimension registry.

Justified by: docs/04-FINANCE-DNA.md §5 (Dimension Categories) and the
architectural review (registry registers definitions, not bare strings).

The registry answers exactly one question: which dimensions are active in
this version of Finance DNA, and what evaluator produces each one?

Adding a new dimension in a future milestone is exactly one step here:
add a RegisteredDimension to REGISTRY. Nothing else changes in this file.
The evaluation order is the insertion order of REGISTRY.

RegisteredDimension pairs a DimensionDefinition (the metadata, from
dimensions.py) with its EvaluatorFn (the scoring logic, from rules.py).
This pairing ensures the registry integrity test (Group 5 in the test suite)
can verify that every registered evaluator produces a Dimension whose name
matches its definition's name — catching category-swap bugs where, for
example, someone accidentally wires Capital Intensity's definition to
Commodity Exposure's evaluator.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from backend.finance_dna.dimensions import (
    CAPITAL_INTENSITY,
    COMMODITY_INPUT_EXPOSURE,
    GEOGRAPHIC_REVENUE_CONCENTRATION,
    INNOVATION_INTENSITY,
    REGULATORY_EXPOSURE,
    SUPPLY_CHAIN_COMPLEXITY,
    DimensionDefinition,
)
from backend.finance_dna.rules import (
    evaluate_capital_intensity,
    evaluate_commodity_input_exposure,
    evaluate_geographic_revenue_concentration,
    evaluate_innovation_intensity,
    evaluate_regulatory_exposure,
    evaluate_supply_chain_complexity,
)
from backend.models import Asset, Dimension

# ---------------------------------------------------------------------------
# Evaluator function type
# (Asset, as_of: str) -> Dimension
# ---------------------------------------------------------------------------

type EvaluatorFn = Callable[[Asset, str], Dimension]


@dataclass
class RegisteredDimension:
    """A DimensionDefinition paired with its evaluator function.

    Internal to Finance DNA — not a cross-module artifact.
    Atlas consumes Dimension objects; it never sees RegisteredDimension.

    The pairing exists so that registry integrity tests can confirm
    that every evaluator produces a Dimension whose name matches the
    registered definition. Without this pairing, a wiring mistake
    (wrong evaluator attached to wrong definition) would only be caught
    at runtime when the wrong Dimension name appeared in a FinanceDNA.
    """

    definition: DimensionDefinition
    evaluator: EvaluatorFn


# ---------------------------------------------------------------------------
# The V0.1 registry — six locked dimensions in evaluation order.
# Source: docs/04-FINANCE-DNA.md §6.
# ---------------------------------------------------------------------------

REGISTRY: tuple[RegisteredDimension, ...] = (
    RegisteredDimension(CAPITAL_INTENSITY, evaluate_capital_intensity),
    RegisteredDimension(COMMODITY_INPUT_EXPOSURE, evaluate_commodity_input_exposure),
    RegisteredDimension(SUPPLY_CHAIN_COMPLEXITY, evaluate_supply_chain_complexity),
    RegisteredDimension(INNOVATION_INTENSITY, evaluate_innovation_intensity),
    RegisteredDimension(REGULATORY_EXPOSURE, evaluate_regulatory_exposure),
    RegisteredDimension(
        GEOGRAPHIC_REVENUE_CONCENTRATION,
        evaluate_geographic_revenue_concentration,
    ),
)
