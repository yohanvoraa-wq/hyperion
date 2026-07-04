"""Finance DNA module — public interface.

Justified by: docs/04-FINANCE-DNA.md and
docs/07-SYSTEM-ARCHITECTURE.md §3 (Finance DNA owns Identity).

Single responsibility: convert an Asset into a FinanceDNA artifact.

Public API
----------
evaluate(asset, *, as_of=None) -> FinanceDNA
    The only entry point. Evaluates all registered dimensions.

FINANCE_DNA_VERSION
    Current schema version string.

EvaluationError, MissingAssetDataError, UnknownDimensionError
    Exception types for structured error handling.

Boundary contract (07-SYSTEM-ARCHITECTURE.md §6):
    This module imports from backend.models only.
    It never imports from atlas, janus, titan, or ingestion.
    It never mutates the Asset it receives.
    The FinanceDNA it produces is an immutable frozen dataclass.
"""

from backend.finance_dna.evaluator import FINANCE_DNA_VERSION, evaluate
from backend.finance_dna.exceptions import (
    EvaluationError,
    MissingAssetDataError,
    UnknownDimensionError,
)

__all__ = [
    "evaluate",
    "FINANCE_DNA_VERSION",
    "EvaluationError",
    "MissingAssetDataError",
    "UnknownDimensionError",
]
