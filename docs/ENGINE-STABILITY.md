# Engine Stability Declaration

**Version:** 0.1
**Status:** Active
**Effective:** v0.1.0-alpha

---

## Frozen Modules

The following modules are considered architecturally stable as of v0.1.0-alpha.

| Module | Location | Public API | Status |
|--------|----------|------------|--------|
| Shared Models | `backend/models/` | All exported types | **Frozen** |
| Ingestion | `backend/ingestion/` | `load_portfolio()` | **Frozen** |
| Finance DNA | `backend/finance_dna/` | `evaluate()` | **Frozen** |
| Atlas | `backend/atlas/` | `build()` | **Frozen** |
| Janus | `backend/janus/` | `reason()` | **Frozen** |
| Titan | `backend/titan/` | `qualify()` | **Frozen** |
| Public Contract | `backend/api/dto.py`, `schemas.py` | `AnalyzeResponseSchema` | **Frozen** |

---

## What "Frozen" Means

**Frozen** means the public API — the function signatures, the artifact shapes, and the architectural boundaries — will not change without a documented breaking change and a version increment.

Frozen does **not** mean the module is done growing. It means:

- The public entry point (`evaluate`, `build`, `reason`, `qualify`) will not change signature
- The artifacts it produces (`FinanceDNA`, `KnowledgeGraph`, `ReasoningArtifact`, `BlindSpot`) will not lose fields
- The module boundary (what it imports, what it never imports) is permanent
- Bug fixes are always permitted
- New dimensions, new relationships, and new context nodes are always permitted — they extend knowledge, not architecture

---

## What Can Change

**Knowledge** — adding Finance DNA dimensions, Atlas nodes, and Atlas relationships is explicitly encouraged. This is how Hyperion grows. It does not require changing any frozen module.

**API response fields** — new *optional* fields may be added to the response schema. Existing fields never change meaning within the same API version. See `docs/09-PUBLIC-INTERFACE.md`.

**Interfaces** — `backend/api/app.py`, `routes.py`, `pipeline.py`, `scripts/demo.py`, `scripts/serve.py` — these are delivery mechanisms and may evolve freely.

---

## Proposing a Change to a Frozen Module

Changes to frozen modules require:

1. A clear statement of the bug or genuine architectural problem being solved
2. Evidence that the problem cannot be solved by extending knowledge rather than changing the engine
3. A proposed change that preserves backward compatibility, or a documented breaking change with version increment

The burden of proof is on the proposal. Hyperion's architectural discipline is the source of its reliability. Proposals that would "make things more flexible" without a concrete use case are rejected by default.

---

## Why This Matters

Every module in Hyperion has one public verb:

```
load_portfolio() → Portfolio
evaluate()       → FinanceDNA
build()          → KnowledgeGraph
reason()         → ReasoningArtifact | None
qualify()        → BlindSpot | None
```

These five verbs compose into the complete pipeline. Changing any of them changes the composition. The stability of the pipeline is the foundation on which all future knowledge expansion, interfaces, and automation are built.

*The engine is the operating system. You don't redesign the operating system to run more applications. You run more applications.*
