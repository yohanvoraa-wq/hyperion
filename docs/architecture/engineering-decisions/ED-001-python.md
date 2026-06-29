# ED-001 — Programming Language

**Status:** Decided
**Date:** 28 June 2026

## Decision
What language should Hyperion be implemented in?

## Rationale
Hyperion needs a mature graph ecosystem (Atlas), a mature data/AI ecosystem (Finance DNA's numeric qualification, Janus's eventual model integration), strong typing to encode module boundaries directly in the type system (a `Dimension`, a `Relationship`, a `ReasoningArtifact`, and a `BlindSpot` should be distinct, non-interchangeable types), and a credible path to a web API.

## Alternatives Considered
- **TypeScript / Node** — strong web tooling, materially weaker graph and data-science ecosystem.
- **Go** — excellent performance and concurrency, weak data-science/AI ecosystem; would slow Finance DNA and Janus more than it would help.
- **Rust** — excellent safety guarantees, but a steep learning curve and thin data-science ecosystem would slow MVP iteration without a corresponding benefit at this scale.

## Final Choice
**Python 3.12+.** Breadth of graph libraries, the AI/data ecosystem Janus will eventually need, FastAPI as a credible future API layer, and modern typing (generics, structural typing, frozen dataclasses) sufficient to enforce ED-005's ownership rules at the type level.
