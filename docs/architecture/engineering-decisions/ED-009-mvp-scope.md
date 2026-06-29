# ED-009 — MVP Scope (Version 0.1)

**Status:** Decided
**Date:** 28 June 2026

## Decision
Version 0.1 proves the full pipeline once, end to end, for a small, fixed set of companies. It does not prove any single stage broadly.

```
Portfolio (Apple, NVIDIA, Microsoft — fixed list)
   │
   ▼
Recognize Companies          (simple resolution, no fuzzy matching)
   │
   ▼
Build Finance DNA            (small hand-qualified subset — e.g. Capital
   │                          Intensity, Commodity Input Exposure — enough
   │                          to support one real Reasoning Path, not all 28)
   ▼
Create Atlas Graph           (manually seeded: Apple → depends_on → TSMC
   │                          → located_in → Taiwan → affected_by →
   │                          Geopolitical Risk)
   ▼
Traverse One Reasoning Path  (Janus V0 — fully deterministic, no model)
   │
   ▼
Reveal One Blind Spot        (Titan V0 — deterministic qualification
   │                          against 03-BLIND-SPOT-FRAMEWORK.md §7)
   ▼
Visualize It                 (one rendered Reasoning Chain — not a dashboard)
```

## Explicitly excluded from V0.1
Chat, LLM integration, news, predictions, portfolio optimization, alerts, multi-portfolio support, user accounts, any UI beyond rendering one Reasoning Chain.

## Rationale
Every excluded item fails Vision's own test — "does this reveal a Blind Spot?" — applied now to the build instead of the product. A "broader but shallower" V0.1 that touches more companies or dimensions without completing the full pipeline would prove less than this narrow, complete version does.

## Alternatives Considered
- **Broad-but-shallow MVP** (more companies/dimensions, incomplete pipeline) — rejected; proving the full pipeline once is worth more right now than proving any one stage broadly.

## Final Choice
The seven-step pipeline above is the literal Definition of Done for Phase 3. Nothing is "almost done" until every step in this chain executes against real data.
