"""Janus ranker — significance test and path selection.

Justified by: docs/06-JANUS.md §2 (What Makes a Valid Inference?) and
the frozen design Decision 3 (significance test).

Single responsibility: given candidate paths from traversal.py, apply the
significance test and return the highest-confidence-product path that passes.
No artifact construction. No traversal. Just filtering and selection.

V0.1 Significance Test (Decision 3 — frozen):
  A candidate path is significant if and only if ALL four conditions hold:
    1. len(path) >= 1                    (non-empty)
    2. len(path) <= MAX_DEPTH            (within depth limit)
    3. no repeated nodes along the path  (explicit cycle guard)
    4. confidence_product >= 0.5         (minimum evidential strength)

If multiple paths are significant, the one with the highest confidence
product is selected. This is deterministic for a given graph — the same
graph always produces the same ranking.
"""

from __future__ import annotations

from backend.janus.traversal import MAX_DEPTH, MIN_CONFIDENCE_PRODUCT
from backend.models import Relationship

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _confidence_product(path: tuple[Relationship, ...]) -> float:
    """Multiply all edge confidence values along the path.

    An empty path returns 0.0 (explicitly not significant).
    A single edge returns that edge's confidence.
    """
    if not path:
        return 0.0
    product = 1.0
    for rel in path:
        product *= rel.confidence
    return product


def _has_no_repeated_nodes(path: tuple[Relationship, ...]) -> bool:
    """Return True if no node id appears more than once along the path.

    Per Decision 4 (stopping rules) and per the general no-cycles
    requirement stated in Janus's design: paths like Apple → TSMC →
    Taiwan → TSMC are never significant, even if the cycle is short.

    Explicitly enforced here even though Atlas.find_paths() already
    prevents cycles via its BFS implementation — Janus should not rely
    on Atlas's implementation detail remaining unchanged forever.
    """
    node_ids: list[str] = [rel.source_id for rel in path]
    if path:
        node_ids.append(path[-1].target_id)
    return len(node_ids) == len(set(node_ids))


def _is_significant(path: tuple[Relationship, ...]) -> bool:
    """Apply all four significance criteria to one candidate path."""
    return (
        len(path) >= 1
        and len(path) <= MAX_DEPTH
        and _has_no_repeated_nodes(path)
        and _confidence_product(path) >= MIN_CONFIDENCE_PRODUCT
    )


# ---------------------------------------------------------------------------
# Public ranking function
# ---------------------------------------------------------------------------


def rank_paths(
    paths: tuple[tuple[Relationship, ...], ...],
) -> tuple[Relationship, ...] | None:
    """Apply the significance test and return the best path, or None.

    Per Decision 6 (return behavior): if no candidate path passes the
    significance test, return None. Janus does not produce a weak artifact
    for a borderline path — silence is preferable to an unsupported claim.

    If multiple paths are significant (e.g. Apple has both a commodity
    exposure path and a geopolitical exposure path), the one with the highest
    confidence product is selected. Deterministic for a given graph.
    """
    significant = [p for p in paths if _is_significant(p)]
    if not significant:
        return None
    return max(significant, key=_confidence_product)
