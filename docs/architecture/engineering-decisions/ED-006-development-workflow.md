# ED-006 — Development Workflow

**Status:** Decided
**Date:** 28 June 2026

## Decision
```
Idea → Specification → Prototype → Implementation → Tests → Review → Merge
```
"Specification" here means a short note or a one-paragraph addition to the relevant module's README before code is written — not a full conceptual document. The discipline being preserved is *think before writing*, not the weight of the original Markdown phase.

## Rationale
This mirrors the documentation phase's own workflow rather than inventing a new one for code. The risk named in `07-SYSTEM-ARCHITECTURE.md` §1 — boundaries eroding under deadline pressure — is exactly what a workflow with no specification step would make easier.

## Alternatives Considered
- **Trunk-based development, no specification step** — appropriate for a mature team with established conventions; premature here, while module boundaries are still being translated into code for the first time.
- **Full Scrum/sprint process** — unnecessary overhead at MVP scale and team size.

## Final Choice
The seven-step workflow above — lightweight enough not to slow a small team, structured enough to prevent the exact boundary erosion the architecture phase was built to avoid.
