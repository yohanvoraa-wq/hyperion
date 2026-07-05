# Atlas Module

**Justified by:** `docs/05-ATLAS.md`

---

## Purpose

Atlas builds the Financial Knowledge Graph — the canonical representation of relationships between Assets, Commodities, Geographies, Macro Factors, and other economic entities that Finance DNA cannot represent, because Finance DNA describes each Asset *in isolation*.

Atlas exists to answer: **How are things connected?**

Finance DNA answers: *What is this company?*
Atlas answers: *How is it connected to everything else?*
Janus answers: *What follows from those connections?*

---

## Inputs

- A sequence of `Asset` objects (from Ingestion)
- A mapping of `asset_id → FinanceDNA` (from Finance DNA, optional — assets without evaluated Finance DNA get `finance_dna=None` on their node)

---

## Outputs

A `KnowledgeGraph` object from `backend/models/knowledge_graph.py`, containing:
- `nodes` — every Asset node (with Finance DNA attached) and every context node
- `relationships` — every qualified edge, carrying evidence and confidence

---

## Public API

```python
from backend.atlas import build

graph = build(assets, finance_dnas)
graph = build(assets)              # finance_dna=None on all nodes
```

One entry point. No other public functions.

---

## Internal Structure

| File | Responsibility |
|---|---|
| `loader.py` | Reads `datasets/atlas/context_nodes.csv` and `seed_relationships.csv` |
| `builder.py` | `build(assets, finance_dnas) -> KnowledgeGraph` |
| `exceptions.py` | `AtlasError`, `DuplicateNodeError`, `OrphanedRelationshipError` |

---

## Responsibilities

- Create one `GraphNode` per Asset (with Finance DNA if available)
- Load context nodes from `datasets/atlas/context_nodes.csv`
- Load seed relationships from `datasets/atlas/seed_relationships.csv`
- Enforce Atlas §2 invariants at construction (via `KnowledgeGraph.__init__`)
- Return an immutable `KnowledgeGraph`

---

## Never

Atlas never:
- Mutates any `Asset` or `FinanceDNA` it receives
- Creates `Blind Spots`, `ReasoningArtifact`s, or `Dimension` objects
- Performs traversal as reasoning (that is Janus's job)
- Selects which paths matter (that is Janus's job)
- Makes network or API calls
- Uses probabilistic or ML-based relationship discovery (V0.1: hand-seeded data only)

---

## V0.1 Scope

The graph for V0.1 is hand-seeded from two CSV files in `datasets/atlas/`.
Future milestones will supplement or replace hand-seeded data with automated
relationship discovery from financial filings and external data sources.

The key V0.1 path the demo uses:

```
Apple → depends_on ↔ supplies → TSMC
                                   │
                              located_in
                                   │
                                Taiwan
                                   │
                             affected_by
                                   │
                       Taiwan Geopolitical Risk
```

This path is what enables the first Blind Spot in Milestone 8.
