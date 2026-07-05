"""Finance DNA evaluator — the single public entry point.

Justified by: docs/04-FINANCE-DNA.md (the module as a whole) and
docs/07-SYSTEM-ARCHITECTURE.md §3 (Finance DNA owns Identity, produces
Dimensions, never creates Relationships).

One public function: evaluate(asset, *, as_of=None) -> FinanceDNA.

Design decisions
----------------
Single entry point: the architectural review confirmed Option A —
evaluate(asset) with no dimension-selection parameter. Nothing in the
current architecture needs selective evaluation. 'Earn abstractions,
don't prepare for them' (from the review).

as_of parameter: injected date for reproducibility. Tests pass a fixed
date ('2024-12-31') so that the output is byte-for-byte identical
regardless of when the test suite runs. Production calls omit as_of and
get today's date. This is the mechanism that satisfies the determinism
requirement (ED-004 principle 4) without making the evaluator impure.

Evaluation order: determined by REGISTRY insertion order (registry.py).
Stable within a version; this ensures FinanceDNA.dimensions[0] is always
Capital Intensity in V0.1.

The evaluator's only job is to call REGISTRY and assemble the results into
a FinanceDNA. It contains no scoring logic — that lives in rules.py.
"""

from __future__ import annotations

import datetime

from backend.finance_dna.registry import REGISTRY
from backend.models import Asset, FinanceDNA

FINANCE_DNA_VERSION: str = "0.1"
"""Current Finance DNA schema version.
Incremented when the registered dimension set changes materially
(additions, removals, or re-definitions that break backward compatibility).
Atlas consumers record this value alongside any FinanceDNA they store.
"""


def evaluate(asset: Asset, *, as_of: str | None = None) -> FinanceDNA:
    """Evaluate all registered Finance DNA dimensions for one Asset.

    This is the only public function in the Finance DNA module.
    It is the answer to the single responsibility this module owns:
    'Convert an Asset into a structured representation of financially
    meaningful characteristics.' (04-FINANCE-DNA.md)

    Parameters
    ----------
    asset:
        The resolved Asset to evaluate. Must have a non-None sector
        for V0.1 evaluators to succeed. Comes from backend.ingestion.
    as_of:
        ISO-8601 date string (YYYY-MM-DD). When provided, all Dimensions
        in the result carry this date as their as_of value.
        When None (default), today's date is used.
        Inject a fixed date in tests for deterministic output.

    Returns
    -------
    FinanceDNA
        Immutable artifact containing one Dimension per registered
        dimension, in registry order. Ready for Atlas to consume.

    Raises
    ------
    MissingAssetDataError
        If any registered evaluator requires a field the Asset lacks
        (typically sector=None).
    """
    evaluation_date = as_of or datetime.date.today().isoformat()

    dimensions = tuple(registered.evaluator(asset, evaluation_date) for registered in REGISTRY)

    return FinanceDNA(
        version=FINANCE_DNA_VERSION,
        asset_id=asset.id,
        dimensions=dimensions,
        evaluated_at=evaluation_date,
    )
