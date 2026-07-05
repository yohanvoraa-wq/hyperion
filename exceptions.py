# Titan Module

**Justified by:** `docs/03-BLIND-SPOT-FRAMEWORK.md`

---

## Purpose

Titan evaluates a `ReasoningArtifact` against the Blind Spot qualification framework and produces a `BlindSpot` artifact only if every qualification criterion is satisfied.

Finance DNA answers: *What is this company?*
Atlas answers: *How is it connected?*
Janus answers: *Which path matters?*
Titan answers: *Does this reasoning reveal a Blind Spot?*

---

## Five Frozen Design Decisions (V0.1)

**Decision 1 — Public API:**
```python
qualify(reasoning_artifact: ReasoningArtifact) -> BlindSpot | None
```

**Decision 2 — Qualification Criteria:** Directly from `03-BLIND-SPOT-FRAMEWORK.md §7`. No additions. Four criteria:
1. **Meaningful** — changes how the investor thinks about risk
2. **Non-obvious** — most investors would be surprised
3. **Evidence-supported** — traces to an inspectable Reasoning Chain
4. **Changes understanding** — investor's mental model becomes more accurate

**Decision 3 — Failure behavior:** Any criterion fails → `None`. No partial BlindSpot.

**Decision 4 — Confidence:** Inherited from `ReasoningArtifact.confidence`. Never recalculated.

**Decision 5 — No modification:** Titan reads the `ReasoningArtifact`. Never edits it.

---

## Public API

```python
from backend.titan import qualify

blind_spot = qualify(reasoning_artifact)  # BlindSpot or None
```

One entry point. No other public functions.

---

## V0.1 Criterion Implementations

| Criterion | §7 Text | V0.1 Rule |
|---|---|---|
| Meaningful | Changes how investor thinks about risk | `len(steps) >= 1 AND confidence >= 0.5` |
| Non-obvious | Most investors would be surprised | `len(steps) >= 2` (indirect chain) |
| Evidence-supported | Traces to inspectable Reasoning Chain | `supporting_evidence non-empty` |
| Changes understanding | Mental model becomes more accurate | `falsifiability_conditions non-empty` |

---

## Never

Titan never:
- Modifies the `ReasoningArtifact` it receives
- Recalculates or adjusts confidence values
- Creates `Dimension`, `GraphNode`, or `Relationship` objects
- Qualifies partial findings (all four criteria must pass)
- Makes network or API calls
- Uses probabilistic or ML-based qualification (V0.1: fully deterministic)
