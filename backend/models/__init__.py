"""Shared domain models — the common language of the Hyperion codebase.

Every other backend module imports from here, never from individual
model files directly. This gives the models package a clean, stable
public API: if an internal file is renamed or refactored, nothing
outside backend/models/ breaks.

Import order follows the dependency direction:
  enums (no dependencies)
  -> asset, portfolio (depend on enums)
  -> dimension (depends on enums)
  -> relationship (depends on enums)
  -> reasoning_artifact (depends on enums)
  -> blindspot (depends on enums + reasoning_artifact)
  -> finance_dna (depends on dimension)

Per ED-005 (Data Ownership): all types exported here are frozen
dataclasses. A module that does not own an artifact type may read
instances of it; it may never mutate them.
"""

from backend.models.asset import Asset
from backend.models.blindspot import BlindSpot
from backend.models.dimension import Dimension
from backend.models.enums import (
    AssetType,
    BlindSpotCategory,
    Cardinality,
    ContextNodeType,
    DimensionCategory,
    Directionality,
    EvidenceSource,
    ReasoningMode,
    RelationshipTemporality,
    RelationshipType,
    TemporalBehavior,
    ValueStructure,
)
from backend.models.finance_dna import FinanceDNA
from backend.models.portfolio import Portfolio
from backend.models.reasoning_artifact import ReasoningArtifact, ReasoningStep
from backend.models.relationship import Relationship

__all__ = [
    # Core artifacts -- one per module boundary
    "Asset",
    "Portfolio",
    "Dimension",
    "Relationship",
    "ReasoningStep",
    "ReasoningArtifact",
    "BlindSpot",
    "FinanceDNA",
    # Enumerations
    "AssetType",
    "ContextNodeType",
    "DimensionCategory",
    "ValueStructure",
    "TemporalBehavior",
    "RelationshipType",
    "Directionality",
    "RelationshipTemporality",
    "Cardinality",
    "EvidenceSource",
    "BlindSpotCategory",
    "ReasoningMode",
]
