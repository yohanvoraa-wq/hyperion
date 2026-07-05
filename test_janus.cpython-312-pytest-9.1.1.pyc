"""FinanceDNA domain model — Finance DNA's cross-module artifact.

Justified by: docs/04-FINANCE-DNA.md (the module as a whole) and
docs/07-SYSTEM-ARCHITECTURE.md §5 (Finance DNA → Atlas hop).

FinanceDNA is the artifact Finance DNA produces and Atlas consumes.
It lives in backend/models/ for the same reason every cross-module
artifact does: Finance DNA produces it; Atlas reads it; neither should
know the other's internals.

Fields
------
version
    The Finance DNA schema version that produced this artifact.
    Atlas should record which version it consumed — FinanceDNA V0.1
    carries 6 dimensions; V1.0 may carry 28. Atlas cannot assume they
    are interchangeable without checking this field.

asset_id
    The Asset this DNA describes. Every Dimension inside must share
    this asset_id — enforced by __post_init__.

dimensions
    An ordered, immutable tuple of qualified Dimension objects.
    Ordering is stable within a version (registry insertion order).

evaluated_at
    ISO-8601 date of evaluation. Required because TIME_VARYING
    dimensions are only meaningful when their snapshot date is known.
    Finance DNA §3 — TemporalBehavior: 'using last year's value as if
    it still holds today would quietly violate the economic-identity
    standard.'
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.models.dimension import Dimension


@dataclass(frozen=True)
class FinanceDNA:
    """The complete Finance DNA representation of one Asset.

    Immutable by design (frozen=True). Once produced by Finance DNA's
    evaluator, no downstream module — Atlas, Janus, Titan — may alter
    the dimensions or their scores. ED-005 (Data Ownership): Finance DNA
    owns Dimensions permanently.
    """

    version: str
    """Finance DNA schema version (e.g. '0.1').
    Atlas records this when consuming a FinanceDNA artifact so that
    schema differences between versions are always explicit, never
    silently assumed away."""

    asset_id: str
    """ID of the Asset this Finance DNA describes.
    Must match Asset.id from backend/models/asset.py."""

    dimensions: tuple[Dimension, ...]
    """All qualified Dimension objects for this Asset, in registry order.
    Every Dimension.asset_id must equal this FinanceDNA.asset_id —
    enforced by __post_init__."""

    evaluated_at: str
    """ISO-8601 date string (YYYY-MM-DD) when this Finance DNA was
    evaluated. Injected by the evaluator; V0.1 tests inject a fixed
    date so that test output is byte-for-byte reproducible regardless
    of when the test suite runs."""

    def __post_init__(self) -> None:
        """Enforce invariants across the dimensions tuple."""
        # Every Dimension must belong to this Asset.
        mismatched = [d.name for d in self.dimensions if d.asset_id != self.asset_id]
        if mismatched:
            raise ValueError(
                f"FinanceDNA for '{self.asset_id}' contains Dimensions "
                f"with a different asset_id: {mismatched}. Every Dimension "
                "in a FinanceDNA artifact must belong to the same Asset."
            )

        # No dimension name may appear twice.
        # Capital Intensity appearing twice would mean Atlas receives two
        # conflicting scores for the same characteristic — neither is safe to use.
        seen: set[str] = set()
        for d in self.dimensions:
            if d.name in seen:
                raise ValueError(
                    f"Duplicate dimension name '{d.name}' in FinanceDNA "
                    f"for '{self.asset_id}'. Each dimension may appear once."
                )
            seen.add(d.name)
