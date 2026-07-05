"""Portfolio domain model.

Justified by: docs/02-FOUNDATIONAL-CONCEPTS.md (concept #3 — Portfolio).

A Portfolio is an ordered collection of Assets held by an investor at a point
in time. It is the unit a real investor actually holds and worries about, and
the primary input to the Ingestion layer (07-SYSTEM-ARCHITECTURE.md §4, hop 1).

Immutability: frozen=True. weights and assets are tuples (not lists) to prevent
mutation after construction. The two tuples are parallel: assets[i] is held at
weights[i]. This invariant is checked at construction time.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.models.asset import Asset


@dataclass(frozen=True)
class Portfolio:
    """An ordered, weighted collection of Assets.

    weights must be non-negative and sum to 1.0 (within floating-point
    tolerance). This is enforced by __post_init__, which is the only logic
    permitted in a domain model — it validates the invariant the type itself
    expresses, not business logic that belongs elsewhere.
    """

    name: str
    """Portfolio name or identifier."""

    assets: tuple[Asset, ...]
    """Ordered Asset holdings. Parallel to weights."""

    weights: tuple[float, ...]
    """Portfolio weights, parallel to assets. Must sum to 1.0 (±1e-6)."""

    def __post_init__(self) -> None:
        if len(self.assets) != len(self.weights):
            raise ValueError(
                f"assets ({len(self.assets)}) and weights ({len(self.weights)}) "
                "must have equal length."
            )
        if self.assets and not abs(sum(self.weights) - 1.0) < 1e-6:
            raise ValueError(f"Portfolio weights must sum to 1.0; got {sum(self.weights):.6f}.")
        if any(w < 0.0 for w in self.weights):
            raise ValueError("Portfolio weights must be non-negative.")
