"""Titan module — public interface.

Justified by: docs/03-BLIND-SPOT-FRAMEWORK.md and
docs/07-SYSTEM-ARCHITECTURE.md §3 (Titan owns Qualification).

Titan evaluates a ReasoningArtifact against the Blind Spot qualification
framework and produces a BlindSpot artifact only if every criterion is satisfied.

Public API
----------
qualify(reasoning_artifact) -> BlindSpot | None
    The only entry point. Returns a BlindSpot if all four criteria from
    Blind Spot Framework §7 are satisfied; None otherwise.

TitanError, QualificationError
    Exception types for structured error handling.

Boundary contract (07-SYSTEM-ARCHITECTURE.md §6):
    This module imports from backend.models only.
    It never imports from finance_dna, atlas, janus, or ingestion.
    It never modifies the ReasoningArtifact it receives.
    It never recalculates confidence (Decision 4: inherited from Janus).
    It never creates Dimensions, Relationships, or GraphNodes.
    Titan owns the qualification decision. Nothing downstream may
    change that decision or the reasoning chain behind it.
"""

from backend.titan.exceptions import QualificationError, TitanError
from backend.titan.qualifier import qualify

__all__ = [
    "qualify",
    "TitanError",
    "QualificationError",
]
