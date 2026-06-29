# Hyperion

An explainable financial reasoning platform. See [`docs/01-VISION.md`](docs/01-VISION.md).

> Hyperion does not help investors make more decisions. Hyperion helps investors make better-informed decisions.

## Status

**Phase 3 — Implementation. Milestone 1 — Repository Bootstrap.**

This repository currently does nothing. It is ready to start doing something. No Finance DNA, no Atlas, no Janus, no Titan logic exists yet — only the structure they will live in.

## What this is

Hyperion is built from a fully specified conceptual architecture before any code was written. Read in order:

| Doc | Question it answers |
|---|---|
| `docs/00-CONSTITUTION.md` | Why does Hyperion exist? |
| `docs/01-VISION.md` | Where is Hyperion going? |
| `docs/02-FOUNDATIONAL-CONCEPTS.md` | What is Hyperion's vocabulary? |
| `docs/03-BLIND-SPOT-FRAMEWORK.md` | What is a Blind Spot, and what makes one worth surfacing? |
| `docs/04-FINANCE-DNA.md` | How is an Asset's identity represented? |
| `docs/05-ATLAS.md` | How are relationships between Assets represented? |
| `docs/06-JANUS.md` | How does Hyperion turn knowledge into a justified conclusion? |
| `docs/07-SYSTEM-ARCHITECTURE.md` | How do these modules wire together into a system? |
| `docs/architecture/engineering-decisions/` | Why was each engineering choice made? (ADRs ED-001–ED-009) |
| `docs/research/dimension-candidate-board.md` | How were Finance DNA's dimensions qualified? |

## The one engineering promise

**Never write code that isn't immediately justified by one of the documents above.**

If you find yourself writing a class and can't name which document introduced the concept it represents, stop. Either the code isn't needed yet, or a document needs to be updated first — not the other way around.

## Repository structure

```
backend/
├── ingestion/    # Portfolio Ingestion Layer        (07 §4, hop 1)
├── finance_dna/  # Identity Representation           (04)
├── atlas/        # Relationship Representation       (05)
├── janus/        # Reasoning                         (06)
├── titan/        # Blind Spot Qualification          (03 §7 / 07 §5)
├── output/       # Explainable Output Layer          (07 §4, hop 6)
├── models/       # Shared, immutable artifact types  (ED-005)
├── api/          # Empty for V0.1 — see ED-009
└── tests/
frontend/         # Empty for V0.1 — see ED-009
datasets/         # Small, fixed, hand-seeded V0.1 dataset
scripts/          # demo.py (not yet written) — the first executable goal
docs/             # Everything above
```

Every folder maps to exactly one row in `docs/07-SYSTEM-ARCHITECTURE.md` Section 3. No folder exists that doesn't.

## Engineering setup

This project uses `uv` (ED-002). Python 3.12+ (ED-001).

```bash
uv sync              # install dependencies
uv run ruff check .  # lint
uv run ruff format . # format
uv run mypy backend  # type-check
uv run pytest        # run tests (none yet)
```

## The first executable goal

Not API. Not frontend. Not authentication. A single command:

```bash
uv run python scripts/demo.py
```

…that prints one Reasoning Chain and one qualified Blind Spot for a fixed three-company portfolio (Apple, NVIDIA, Microsoft), built entirely deterministically — no model, no API call. Per ED-009, that's the literal Definition of Done for the next phase of work. `scripts/demo.py` does not exist yet.

## Milestone roadmap

```
Milestone 1 — Repository Bootstrap        ← you are here
Milestone 2 — Shared Models (backend/models)
Milestone 3 — Finance DNA V0 (4 dimensions, 1 company)
Milestone 4 — Atlas V0 (1 graph: Apple → TSMC → Taiwan → Geopolitical Risk)
Milestone 5 — Janus V0 (deterministic, no AI)
Milestone 6 — Titan V0 (deterministic, no AI)
Milestone 7 — Demo Pipeline (scripts/demo.py runs end to end)
```

Progress from here is measured by demonstrations, not commits or documents completed.
