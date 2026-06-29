# ED-003 — Repository Structure

**Status:** Decided
**Date:** 28 June 2026

## Decision
The repository layout mirrors `07-SYSTEM-ARCHITECTURE.md` exactly — one folder per module, named identically to that module's name in the conceptual documents. No folder should exist that doesn't map to something already named in Sections 3 or 4 of that document.

```
hyperion/
├── docs/                          # 00-07 + research/ + architecture/
├── backend/
│   ├── ingestion/                 # Portfolio Ingestion Layer (07 §4, hop 1)
│   ├── finance_dna/                # Finance DNA (04)
│   ├── atlas/                      # Atlas (05)
│   ├── janus/                      # Janus (06)
│   ├── titan/                      # Titan (03 §7 / 07 §5)
│   ├── output/                     # Explainable Output Layer (07 §4, hop 6)
│   ├── models/                     # shared frozen artifact types: Dimension,
│   │                               # Relationship, ReasoningArtifact, BlindSpot
│   ├── api/
│   └── tests/
├── frontend/
├── datasets/
├── scripts/
└── README.md
```

## Rationale
Every top-level backend folder corresponds to exactly one row in `07-SYSTEM-ARCHITECTURE.md` Section 3, or one hop in Section 4. This is the literal embodiment of "no surprises" — anyone who has read the conceptual documents already knows where to find the code, before opening a single file.

## Alternatives Considered
- **Flat `src/` with files instead of folders** — faster to start, but doesn't give Python's import system anything to enforce; a boundary violation becomes a silent function call instead of an import error.
- **Structure by technical layer** (`models/`, `services/`, `controllers/`) — organizes by technical pattern rather than by responsibility. Rejected specifically because it would make it easy for Janus-shaped logic to live quietly inside a generic `services/` folder without anyone noticing a boundary had been crossed.

## Final Choice
One folder per conceptual module, named identically to its document. `models/` holds the shared, frozen artifact types every module's "Never" column (ED-005) depends on.
