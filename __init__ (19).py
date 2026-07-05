"""Janus module — public interface.

Justified by: docs/06-JANUS.md and the six frozen design decisions.

Janus transforms a KnowledgeGraph into an explainable ReasoningArtifact
by selecting the single most significant reasoning path.

Public API
----------
reason(asset_id, graph) -> ReasoningArtifact | None
    The only entry point. Returns an artifact if a significant path
    exists, None otherwise. Per Decision 6: silence is preferable to
    a weak explanation.

FINANCE_DNA_VERSION is not repeated here — Janus is version-independent.

JanusError, NoReasoningPathError
    Exception types for structured error handling.

Boundary contract (07-SYSTEM-ARCHITECTURE.md §6):
    This module imports from backend.models only.
    It never imports from finance_dna, atlas, titan, or ingestion.
    It never modifies the KnowledgeGraph it receives.
    It never scores companies or qualifies Blind Spots.
    It only reasons.
"""

from backend.janus.exceptions import JanusError, NoReasoningPathError
from backend.janus.ranker import rank_paths
from backend.janus.reasoner import build_reasoning_artifact
from backend.janus.traversal import get_candidate_paths
from backend.models import KnowledgeGraph, ReasoningArtifact


def reason(
    asset_id: str,
    graph: KnowledgeGraph,
) -> ReasoningArtifact | None:
    """Transform an asset's graph neighbourhood into an explainable ReasoningArtifact.

    This is the only public function in the Janus module.
    It is the answer to the single responsibility Janus owns:
    'Janus transforms a KnowledgeGraph into an explainable ReasoningArtifact
    by selecting the single most significant reasoning path.'

    Parameters
    ----------
    asset_id:
        The id of the Asset node to reason about. Must match a node id
        in the KnowledgeGraph. If the asset is not in the graph, returns
        None (same as no significant path found).
    graph:
        The KnowledgeGraph produced by Atlas. Janus reads this graph;
        it never modifies it.

    Returns
    -------
    ReasoningArtifact
        A complete, immutable artifact answering all five Janus §5
        explainability questions. Only returned when a significant
        path exists (confidence_product >= 0.5, depth <= 4,
        ends at MACRO_FACTOR or ECONOMIC_EVENT, no repeated nodes).
    None
        When no significant path exists. Per Decision 6: Janus does
        not produce a weak artifact. Silence is preferable.
    """
    candidates = get_candidate_paths(asset_id, graph)
    best_path = rank_paths(candidates)
    if best_path is None:
        return None
    return build_reasoning_artifact(asset_id, best_path, graph)


__all__ = [
    "reason",
    "JanusError",
    "NoReasoningPathError",
]
