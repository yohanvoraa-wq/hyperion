# ED-004 — Engineering Principles

**Status:** Decided
**Date:** 28 June 2026

## Decision
Five engineering principles — the code-level equivalent of the Constitution. Each one exists to enforce something already established conceptually, not to introduce a new philosophy for code.

1. **One module, one responsibility.** Enforced by ED-003's folder structure plus an import rule: a module may import another module's public, frozen artifact type, never its internals.
2. **Never duplicate knowledge.** A fact lives in exactly one module — Atlas's canonical-representation principle (`05-ATLAS.md` §1), generalized to the whole codebase.
3. **Explainability before optimization.** No optimization is permitted in Atlas, Janus, or Titan if it removes the ability to reconstruct a Reasoning Chain after the fact.
4. **Deterministic before probabilistic.** Every module ships a deterministic implementation that passes its qualification tests before any AI/ML component is introduced. This is the direct justification for Janus V0 and Titan V0 having no model at all.
5. **Composition over inheritance.** Module boundaries are easier to police with explicit, composed dependencies than with inheritance hierarchies, which can blur responsibility across a shared base class without anyone intending it.

## Rationale
A generic style guide protects formatting, not architecture. Hyperion's actual risk — established across 00 through 07 — is module boundaries quietly eroding, not inconsistent code style.

## Alternatives Considered
- **Style guide only (PEP8 / Google style), no module-specific principles** — necessary but insufficient; doesn't address the boundary-erosion risk `07-SYSTEM-ARCHITECTURE.md` §1 named directly.

## Final Choice
The five principles above, referenced from every module's README, checked in code review against the specific boundary each principle protects.
