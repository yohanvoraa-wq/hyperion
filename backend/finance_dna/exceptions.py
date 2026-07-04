"""Finance DNA evaluation exceptions.

Justified by: docs/04-FINANCE-DNA.md §2 (qualification criteria, specifically
criterion 5 — evidence-traceability) and docs/07-SYSTEM-ARCHITECTURE.md §5
(Finance DNA → Atlas hop: Finance DNA must produce valid Dimensions or fail
explicitly, never silently produce garbage).

Three exception types cover the three distinct failure modes:
  MissingAssetDataError  — Asset lacks data the evaluator requires
  UnknownDimensionError  — A dimension name was requested that the registry
                           does not contain (future-proofing for selective
                           evaluation if that is ever introduced)
  EvaluationError        — Base class; catch-all for unexpected failures

These are kept narrow deliberately. V0.1 evaluators only need sector and
industry — if either is absent, MissingAssetDataError is the right signal.
"""


class EvaluationError(Exception):
    """Base class for all Finance DNA evaluation errors."""


class MissingAssetDataError(EvaluationError):
    """Raised when an Asset lacks data required to evaluate a dimension.

    V0.1 evaluators derive scores from sector and industry. If sector is
    None the evaluator cannot proceed — this exception carries enough
    context for the caller to log a useful message without inspecting the
    raw Asset or guessing what went wrong.
    """

    def __init__(self, asset_id: str, missing_field: str, dimension_name: str) -> None:
        self.asset_id = asset_id
        self.missing_field = missing_field
        self.dimension_name = dimension_name
        super().__init__(
            f"Cannot evaluate '{dimension_name}' for asset '{asset_id}': "
            f"required field '{missing_field}' is None. "
            "Ensure the Asset was resolved with a complete sector classification."
        )


class UnknownDimensionError(EvaluationError):
    """Raised when a requested dimension name is not in the registry.

    Not raised by V0.1's evaluate() (which evaluates all registered
    dimensions). Reserved for future use if selective evaluation is
    introduced and a caller requests a name that does not exist.
    """

    def __init__(self, dimension_name: str) -> None:
        self.dimension_name = dimension_name
        super().__init__(
            f"No registered evaluator found for dimension '{dimension_name}'. "
            "Check backend/finance_dna/registry.py for the current dimension list."
        )
