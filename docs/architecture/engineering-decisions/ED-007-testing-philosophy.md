# ED-007 — Testing Philosophy

**Status:** Decided
**Date:** 28 June 2026

## Decision
Four test categories — chosen because a reasoning system fails differently than a CRUD application, and coverage percentage doesn't catch the failures that actually matter here.

1. **Unit tests per module** — confirm a module's qualification logic behaves correctly in isolation (e.g., Finance DNA's five dimension criteria correctly accept/reject known cases).
2. **Integration tests across module boundaries** — confirm an artifact crossing a hop in `07-SYSTEM-ARCHITECTURE.md` §4–5 is well-formed on both sides (e.g., a Dimension Finance DNA produces is directly usable by Atlas, unmodified).
3. **Snapshot tests for Reasoning Chains** — a fixed input graph must always produce the same Reasoning Chain. A snapshot diff catches a chain silently changing when unrelated code changes — the direct enforcement of Janus's Reproducibility criterion (`06-JANUS.md` §2).
4. **Golden tests for Explainability** — a fixed set of conclusions where the full five-question answer (Why / Supported by what / How confident / What assumptions / What would change this) is hand-verified once, then checked to never silently degrade.

## Rationale
A system can have 100% line coverage and still produce an inconsistent Reasoning Chain. These four categories test the properties Hyperion actually promises, not just that the code executes.

## Alternatives Considered
- **Coverage-percentage targets as the primary metric** — measures the wrong thing for this system.
- **Property-based testing as the primary strategy** — a strong candidate for Finance DNA's qualification criteria specifically, once those criteria are trusted as formal properties rather than still being validated against real qualification decisions. Noted under Future Extensions, not adopted for V0.1.

## Final Choice
The four categories above, applied per module starting at Milestone 2 (Finance DNA).
