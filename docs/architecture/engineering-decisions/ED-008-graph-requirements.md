# ED-008 — Graph Representation Requirements

**Status:** Decided (properties only — no library chosen)
**Date:** 28 June 2026

## Decision
Before any graph library is chosen, the representation must satisfy five properties. This ADR names the test; ED-010 (Session 2, Technology Choices) names what passes it.

1. **Directed** — `05-ATLAS.md` §5 makes Directionality (Directed / Bidirectional / Symmetric) a first-class relationship characteristic. The representation must support directed edges natively, not simulate them.
2. **Explainable** — every edge must carry its own Evidence Source and Confidence (`05-ATLAS.md` §5) as edge-level metadata, not just a label.
3. **Traversable** — must support path-finding suitable for Reasoning Path construction (`05-ATLAS.md` §7) without requiring the whole graph in memory — not a stress concern at MVP scale, but a requirement the choice shouldn't foreclose.
4. **Versionable** — a relationship's Temporality (Persistent / Temporal / Event-driven) must not delete history. An Event-driven edge that's no longer active stays inspectable, not erased.
5. **Serializable** — exportable to a portable format. The graph is the literal artifact `05-ATLAS.md`'s header names — Knowledge Graph Ontology — and must be inspectable outside whatever runtime is querying it.

## Rationale
Naming a library before naming these properties risks choosing something popular but structurally wrong for what Atlas actually requires — the same mistake the documentation phase avoided by qualifying dimensions before naming them (`04-FINANCE-DNA.md` §2).

## Alternatives Considered
Not yet evaluated. Naming candidates (e.g., a Python graph library vs. a graph database) is explicitly out of scope for this ADR and belongs to Session 2.

## Final Choice
Not yet made. This ADR is complete once these five properties are agreed; the choice itself is ED-010.
