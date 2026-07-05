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
  -> graph_node (depends on enums + finance_dna)
  -> knowledge_graph (depends on graph_node + relationship)

Per ED-005 (Data Ownership): all artifact types exported here are
immutable. A module that does not own an artifact may read it; never mutate.
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
from backend.models.graph_node import GraphNode
from backend.models.knowledge_graph import KnowledgeGraph
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
    "GraphNode",
    "KnowledgeGraph",
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
