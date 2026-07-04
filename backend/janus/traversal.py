"""Janus traversal — candidate path discovery.

Justified by: docs/06-JANUS.md §3 (Types of Reasoning: Deductive) and
the frozen design Decision 2 (candidate path definition) and
Decision 4 (stopping rules).

Single responsibility: take an asset_id and a KnowledgeGraph, return all
paths that qualify as candidates for reasoning. No ranking. No artifacts.
Just traversal.

V0.1 Stopping Rules (Decision 4 — frozen):
  Maximum depth    = 4
  Simple paths     = no repeated nodes (enforced by Atlas.find_paths BFS;
                     Janus makes it explicit here as well)
  Valid endpoints  = MACRO_FACTOR or ECONOMIC_EVENT nodes only
  Invalid terminal = Geography, Industry, Commodity, Regulation, Asset
  No repeated nodes (explicit guard, even though Atlas already prevents
                     cycles in BFS — Janus should not rely on Atlas forever)
"""

from __future__ import annotations

from backend.models import KnowledgeGraph, Relationship
from backend.models.enums import ContextNodeType

# ---------------------------------------------------------------------------
# Frozen V0 constants — Decision 3 and Decision 4
# ---------------------------------------------------------------------------

MAX_DEPTH: int = 4
"""Maximum number of relationship hops in any candidate path.
Paths longer than this are not considered for reasoning, regardless of
their confidence product. Prevents runaway chains like Apple → TSMC →
Taiwan → China → Semiconductor Market → Global Trade.
"""

MIN_CONFIDENCE_PRODUCT: float = 0.5
"""Minimum product of all edge confidences along a path for it to qualify
as significant. A path with confidence product below this threshold does not
produce a ReasoningArtifact — Janus returns None instead. Per Decision 6:
silence is preferable to a weak explanation.
"""

_QUALIFYING_ENDPOINT_TYPES: frozenset[ContextNodeType] = frozenset(
    {
        ContextNodeType.MACRO_FACTOR,
        ContextNodeType.ECONOMIC_EVENT,
    }
)
"""The only node types that may terminate a V0 Reasoning Path.
A path ending at Geography, Industry, Commodity, or any other type
is not yet a reasoning conclusion — it is merely a structural fact.
Reasoning requires arriving at something that represents a risk or event.
"""


# ---------------------------------------------------------------------------
# Candidate path discovery
# ---------------------------------------------------------------------------


def get_candidate_paths(
    asset_id: str,
    graph: KnowledgeGraph,
) -> tuple[tuple[Relationship, ...], ...]:
    """Return all non-empty paths from asset_id that end at a qualifying node.

    Uses KnowledgeGraph.find_paths() for each qualifying endpoint node,
    collecting all paths across all qualifying targets. Per Decision 2:
    a candidate path is any simple path returned by find_paths() that
    starts at the Asset node.

    Filters:
      - Empty paths (same-node result from find_paths) are excluded.
      - Paths ending at non-qualifying node types are never requested.

    No ranking, no significance filtering, no artifact construction here.
    Those belong to ranker.py and reasoner.py respectively.
    """
    qualifying_target_ids = [
        n.id for n in graph.nodes if n.node_class in _QUALIFYING_ENDPOINT_TYPES
    ]

    all_paths: list[tuple[Relationship, ...]] = []
    for target_id in qualifying_target_ids:
        paths = graph.find_paths(asset_id, target_id, max_depth=MAX_DEPTH)
        all_paths.extend(p for p in paths if p)  # exclude empty paths

    return tuple(all_paths)
