# Janus Module

**Justified by:** `docs/06-JANUS.md`

---

## Purpose

Janus transforms a KnowledgeGraph into an explainable ReasoningArtifact by selecting the single most significant reasoning path.

Finance DNA answers: *What is this company?*
Atlas answers: *How is it connected?*
Janus answers: *What follows from those connections?*

---

## Six Frozen Design Decisions (V0.1)

**Decision 1 — Public API:**
```python
reason(asset_id: str, graph: KnowledgeGraph) -> ReasoningArtifact | None
```

**Decision 2 — Candidate path:** any simple path from `KnowledgeGraph.find_paths()` starting at the Asset node. Not a new type.

**Decision 3 — Significance test:** path qualifies if it ends at `MACRO_FACTOR` or `ECONOMIC_EVENT` AND `confidence_product >= 0.5` AND `depth <= 4` AND no repeated nodes.

**Decision 4 — Stopping rules:** max depth 4, simple paths only, never terminate at Geography, must terminate at risk/event node, no repeated nodes.

**Decision 5 — Assumptions (fixed constants):**
- "Finance DNA dimensions are sector-level approximations (V0.1)."
- "Atlas relationships are hand-seeded for Version 0.1."

**Decision 6 — Return behavior:** significant path → `ReasoningArtifact`. Otherwise → `None`. Silence is preferable to a weak explanation.

---

## Public API

```python
from backend.janus import reason

artifact = reason("apple-inc", graph)  # ReasoningArtifact or None
```

One entry point. No other public functions.

---

## Internal Structure

| File | Responsibility |
|---|---|
| `traversal.py` | `get_candidate_paths(asset_id, graph)` — finds all paths to qualifying endpoints |
| `ranker.py` | `rank_paths(paths)` — applies significance test, returns best path |
| `reasoner.py` | `build_reasoning_artifact(asset_id, path, graph)` — produces the complete artifact |
| `exceptions.py` | `JanusError`, `NoReasoningPathError` |

---

## Responsibilities

- Traverse from the asset node to qualifying risk endpoints
- Score candidate paths by confidence product
- Convert the best path to a `ReasoningArtifact`
- Answer all five Janus §5 explainability questions in every artifact

---

## Never

Janus never:
- Modifies the `KnowledgeGraph` it receives
- Creates `GraphNode` or `Relationship` objects
- Scores companies or modifies `FinanceDNA`
- Qualifies `BlindSpot` objects (that is Titan's job)
- Makes network or API calls
- Uses probabilistic or ML-based reasoning (V0.1: fully deterministic)
- Produces an artifact when no significant path exists (returns `None`)

---

## V0.1 Demo Path

The V0.1 demonstration Janus produces:

```
Apple Inc.
  → DEPENDS_ON_SUPPLIES → Taiwan Semiconductor Manufacturing Company
  → LOCATED_IN → Taiwan
  → AFFECTED_BY → Taiwan Geopolitical Risk
```

Confidence: 0.95 × 1.0 × 0.85 = 0.8075
