# ED-005 — Data Ownership

**Status:** Decided
**Date:** 28 June 2026

## Decision
This ADR introduces nothing new. It exists to carry `07-SYSTEM-ARCHITECTURE.md` Section 3's "Never" column and Section 6's four invariants into the codebase as something enforced by the type system, not just written down.

| Module | Owns | May never be mutated by |
|---|---|---|
| Finance DNA | Dimensions | Atlas, Janus, Titan |
| Atlas | Relationships, the graph | Finance DNA, Janus, Titan |
| Janus | The Reasoning Artifact | Titan (may evaluate, may not edit) |
| Titan | The qualification decision | Output layer (presentation only) |

## Rationale
Code review catches ownership violations after they're written. Immutable types prevent them from running at all — the same standard the conceptual documents already held themselves to (e.g., Atlas Section 2's "canonical, not duplicated" criterion).

## Alternatives Considered
- **Convention + code review only** — relies on every reviewer remembering every boundary, every time. Rejected as a weaker guarantee than the language can actually provide.

## Final Choice
Each artifact type in `backend/models/` (ED-003) is implemented as a frozen/immutable type. A module attempting to mutate an artifact it doesn't own fails at the type-checking or runtime level, not just at review.
