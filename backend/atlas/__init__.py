"""Atlas module — public interface.

Justified by: docs/05-ATLAS.md and
docs/07-SYSTEM-ARCHITECTURE.md §3 (Atlas owns Relationships).

Single responsibility: convert Assets and FinanceDNA artifacts into a
canonical, immutable KnowledgeGraph.

Public API
----------
build(assets, finance_dnas, *, context_nodes_path, relationships_path)
    -> KnowledgeGraph
    The only entry point. Builds the graph from seed data + Assets.

AtlasError, DuplicateNodeError, OrphanedRelationshipError
    Exception types for structured error handling.

Boundary contract (07-SYSTEM-ARCHITECTURE.md §6):
    This module imports from backend.models only.
    It never imports from finance_dna, janus, titan, or ingestion.
    It never creates Dimensions, ReasoningArtifacts, or BlindSpots.
    The KnowledgeGraph it produces is immutable after construction.
"""

from backend.atlas.builder import build
from backend.atlas.exceptions import (
    AtlasError,
    DuplicateNodeError,
    OrphanedRelationshipError,
)

__all__ = [
    "build",
    "AtlasError",
    "DuplicateNodeError",
    "OrphanedRelationshipError",
]
