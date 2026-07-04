# Finance DNA Module

**Justified by:** `docs/04-FINANCE-DNA.md`

---

## Purpose

Finance DNA is a deterministic transformation engine that converts an `Asset` into a structured representation of financially meaningful characteristics.

It is the answer to the question Finance DNA §1 asks: *How can publicly traded companies be represented in a way that preserves the characteristics necessary for financial reasoning?*

---

## Inputs

An `Asset` object from `backend/models/asset.py`.

Finance DNA never sees raw strings. It never calls Ingestion. It receives only what Ingestion has already resolved into a typed, immutable `Asset`.

---

## Outputs

A `FinanceDNA` object from `backend/models/finance_dna.py`, containing:
- `version` — the schema version that produced this artifact
- `asset_id` — the Asset this DNA describes
- `dimensions` — a tuple of immutable `Dimension` objects, one per registered dimension
- `evaluated_at` — ISO-8601 date of evaluation

---

## Public API

```python
from backend.finance_dna import evaluate

finance_dna = evaluate(asset)
finance_dna = evaluate(asset, as_of="2024-12-31")  # inject date for reproducibility
```

One entry point. No other public functions.

---

## Internal Structure

| File | Responsibility |
|---|---|
| `dimensions.py` | Dimension metadata — what each dimension IS (category, type, rationale) |
| `rules.py` | Scoring logic — sector/industry lookup tables, one function per dimension |
| `registry.py` | Pairs each definition with its evaluator; defines evaluation order |
| `evaluator.py` | The single public `evaluate()` function |
| `exceptions.py` | `EvaluationError`, `MissingAssetDataError`, `UnknownDimensionError` |

---

## Responsibilities

- Evaluate each dimension independently (no dimension reads another's score)
- Return immutable `Dimension` objects
- Assign `asset_id` on every `Dimension` matching the input `Asset.id`
- Produce deterministic output for the same input and same `as_of` date

---

## Never

Finance DNA never:
- Mutates the `Asset` it receives
- Makes network or API calls
- Reads from any database
- Uses probabilistic or ML-based scoring
- Produces `Relationship`, `ReasoningArtifact`, or `BlindSpot` objects
- Sets `confidence` values with real computation (V0.1 uses a fixed placeholder — see `rules.py`)
- **Performs inference.** Finance DNA produces scores, not conclusions. Interpreting what a score means for a Portfolio, or combining scores into a reasoned finding, belongs to Janus. Reading this module's output and treating it as reasoning would be a misuse of the architecture.

---

## V0.1 Scope

Six dimensions, evaluated from `Asset.sector` and `Asset.industry` only:

1. Capital Intensity
2. Commodity Input Exposure
3. Supply Chain Complexity
4. Innovation Intensity
5. Regulatory Exposure
6. Geographic Revenue Concentration

All V0.1 scores are **sector-level approximations**. Company-specific data (disclosed PP&E, R&D spend, revenue by geography) arrives in a later milestone. See `SCORING-RATIONALE.md` for the justification behind each lookup table.
