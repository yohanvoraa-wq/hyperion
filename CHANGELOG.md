# Changelog

All notable changes to Hyperion are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [v0.1.0-alpha] — 2026-06-28

First complete, deterministic, end-to-end demonstration of the Hyperion
financial reasoning pipeline. The Constitution has become software.

### Philosophy & Architecture

- **Constitution** (`docs/00-CONSTITUTION.md`) — 10 core principles
- **Vision** (`docs/01-VISION.md`) — Hyperion as a Financial Reasoning Platform
- **Foundational Concepts** (`docs/02-FOUNDATIONAL-CONCEPTS.md`) — 20 shared vocabulary definitions
- **Blind Spot Framework** (`docs/03-BLIND-SPOT-FRAMEWORK.md`) — taxonomy, qualification criteria, discovery process
- **Finance DNA** (`docs/04-FINANCE-DNA.md`) — identity representation model
- **Atlas** (`docs/05-ATLAS.md`) — knowledge graph ontology
- **Janus** (`docs/06-JANUS.md`) — reasoning model
- **System Architecture** (`docs/07-SYSTEM-ARCHITECTURE.md`) — module boundaries and data lifecycle
- **Engineering Decisions** (`docs/architecture/engineering-decisions/`) — ED-001 through ED-009

### Implementation

#### Shared Models (`backend/models/`)
- `Asset`, `Portfolio`, `Dimension`, `Relationship`
- `ReasoningStep`, `ReasoningArtifact`, `BlindSpot`
- `FinanceDNA`, `GraphNode`, `KnowledgeGraph`
- All models immutable (frozen dataclasses or immutable classes)

#### Ingestion Layer (`backend/ingestion/`)
- `load_portfolio(raw_identifiers) → Portfolio`
- Case-insensitive lookup by name, ticker, or alias
- Hand-seeded dataset: 7 companies (`datasets/assets.csv`)

#### Finance DNA (`backend/finance_dna/`)
- `evaluate(asset) → FinanceDNA`
- 6 qualified dimensions: Capital Intensity, Commodity Input Exposure,
  Supply Chain Complexity, Innovation Intensity, Regulatory Exposure,
  Geographic Revenue Concentration
- Fully deterministic; sector-level approximations for V0.1
- Scoring rationale documented in `SCORING-RATIONALE.md`

#### Atlas (`backend/atlas/`)
- `build(assets, finance_dnas) → KnowledgeGraph`
- 8 node types, 9 relationship types, 5 relationship characteristics
- V0.1 graph: 15 nodes, 11 hand-seeded relationships
- Full BFS traversal with path-finding (`KnowledgeGraph.find_paths`)

#### Janus (`backend/janus/`)
- `reason(asset_id, graph) → ReasoningArtifact | None`
- Single V0.1 reasoning pattern: Asset → Dependency → Geography → Macro Risk
- Significance test: confidence_product ≥ 0.5, depth ≤ 4, no cycles
- Every artifact answers all five Janus §5 explainability questions

#### Titan (`backend/titan/`)
- `qualify(reasoning_artifact) → BlindSpot | None`
- Four criteria from Blind Spot Framework §7 — no additions
- Fully deterministic; silence over weak explanations

### Demonstration (`scripts/demo.py`)

```
Portfolio: Apple, NVIDIA, Microsoft

✓ Apple     → 2 Blind Spots detected (Apple + NVIDIA)
✓ NVIDIA
-  Microsoft (no qualifying path — correct)
```

**Golden Example** (Apple):
```
Apple Inc.
→ DEPENDS_ON_SUPPLIES → Taiwan Semiconductor Manufacturing Company
→ LOCATED_IN → Taiwan
→ AFFECTED_BY → Taiwan Geopolitical Risk

Confidence: 0.8075
```

### Tests

- **328 passing tests** (0 failures, 0 mypy issues, 0 ruff issues)
- Unit tests per module (ED-007 category 1)
- Integration tests across boundaries (ED-007 category 2)
- **Pipeline integration tests** (`test_pipeline.py`) — full end-to-end, no mocks

### Known Limitations (V0.1)

- Finance DNA uses sector-level approximations, not company-specific disclosures
- Atlas relationships are hand-seeded, not automatically discovered
- Single reasoning pattern (Asset → Dependency → Geography → Macro Risk)
- No API, no frontend, no live financial data ingestion
- Confidence values are arithmetic products of hand-assigned edge weights

---

*Next: Repository polish (CI, Makefile, CONTRIBUTING), then FastAPI, then frontend.*
