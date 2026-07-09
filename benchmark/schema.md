# Canonical Reasoning Case Schema

**Version:** 1.0
**Status:** Frozen
**Purpose:** Defines the structure every canonical reasoning case must follow.

---

## Why this schema exists

A canonical reasoning case is simultaneously four things:

- **Regression test** — verifies the engine produces a specific output for a specific input
- **Product specification** — defines what Hyperion must be able to reason about
- **Research example** — documents a real financial reasoning pattern with evidence
- **Success criterion** — determines when a knowledge expansion is complete

One JSON file serves all four purposes. That is only possible if the schema is precise enough to be unambiguous and stable enough to act as a contract.

---

## Schema

```json
{
  "id": "string",
  "version": "string",
  "state": "A | B | C",
  "pattern": "string",
  "business_question": "string",
  "description": "string",

  "input": {
    "portfolio": ["string"],
    "as_of": "YYYY-MM-DD"
  },

  "expected": {
    "status": "BLIND_SPOT_FOUND | NO_FINDING | ERROR",
    "company": "string",
    "confidence": {
      "min": "float",
      "max": "float"
    },
    "reasoning_path": [
      {
        "relationship": "string",
        "source": "string",
        "target": "string"
      }
    ],
    "required_categories": ["string"]
  },

  "required_knowledge": {
    "finance_dna_dimensions": ["string"],
    "atlas_node_types": ["string"],
    "atlas_relationship_types": ["string"],
    "atlas_nodes_required": ["string"]
  },

  "future_expansion": ["string"],

  "evidence": ["string"],

  "notes": "string"
}
```

---

## Field definitions

### Top-level fields

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique stable identifier. Snake case. Never reused. Example: `apple_taiwan` |
| `version` | Yes | Schema version this case was written against. Currently `"1.0"` |
| `state` | Yes | Implementation state. See States section below |
| `pattern` | Yes | The canonical reasoning pattern this case demonstrates. Must match one of the ten patterns in `research/canonical-reasoning-patterns.md` |
| `business_question` | Yes | The plain-English question a portfolio manager would ask. One sentence |
| `description` | Yes | What this case demonstrates and why it matters |

### Input fields

| Field | Required | Description |
|-------|----------|-------------|
| `portfolio` | Yes | List of raw company identifiers, exactly as passed to `POST /v1/analyze` |
| `as_of` | Yes | Fixed evaluation date. Must be fixed so the case is deterministic |

### Expected fields

| Field | Required | Description |
|-------|----------|-------------|
| `status` | Yes | `BLIND_SPOT_FOUND` — engine must qualify a blind spot. `NO_FINDING` — engine must return silence. `ERROR` — engine must return an error |
| `company` | Yes (if BLIND_SPOT_FOUND) | The `company_id` of the asset for which a blind spot is expected |
| `confidence.min` | Yes (if BLIND_SPOT_FOUND) | Minimum acceptable confidence. Inclusive |
| `confidence.max` | Yes (if BLIND_SPOT_FOUND) | Maximum acceptable confidence. Inclusive |
| `reasoning_path` | Yes (if BLIND_SPOT_FOUND) | Ordered list of reasoning steps. Each step has `relationship`, `source`, and `target` matching Atlas node IDs |
| `required_categories` | Yes (if BLIND_SPOT_FOUND) | Blind spot categories that must be present in the response |

The confidence range exists because Finance DNA scoring may be refined over time. A 0.02 range accommodates minor recalibrations without breaking the regression test. Ranges wider than 0.05 suggest the case is underspecified.

### Required knowledge fields

These fields document what Atlas and Finance DNA must contain for this case to pass. They serve as the shopping list for Version 0.2 knowledge expansion.

| Field | Required | Description |
|-------|----------|-------------|
| `finance_dna_dimensions` | Yes | Dimension names required for this pattern to produce a meaningful score |
| `atlas_node_types` | Yes | Node class types (COMPANY, GEOGRAPHY, MACRO_FACTOR, etc.) that must exist |
| `atlas_relationship_types` | Yes | Relationship types that must exist in the reasoning path |
| `atlas_nodes_required` | Yes | Specific node IDs that must exist in Atlas |

### Other fields

| Field | Required | Description |
|-------|----------|-------------|
| `future_expansion` | No | Nodes, relationships, or patterns that would strengthen this case further |
| `evidence` | Yes | At least one verifiable public source supporting the reasoning chain |
| `notes` | No | Implementation notes, known limitations, or context for contributors |

---

## States

Every canonical case has a state that describes where the current engine stands relative to it.

### State A — Implemented

The current engine, with current Atlas and Finance DNA, produces the expected output. The case acts as a regression test. If it fails after a knowledge expansion, something was accidentally broken.

**Passing criterion:** Engine returns `BLIND_SPOT_FOUND` for the expected company with confidence in the specified range and a reasoning path matching every step.

### State B — Partially Implemented

The company exists in Atlas and Finance DNA can evaluate it, but the specific reasoning path does not exist yet. The engine may return a different blind spot for this company through a different path.

**Passing criterion:** Engine returns any `BLIND_SPOT_FOUND` for the expected company. The specific path does not need to match.

**When it becomes State A:** When the required Atlas nodes and relationships are added.

### State C — Target

The company may not exist in the registry, or the required Atlas nodes do not exist. The engine currently returns `NO_FINDING` or an error for this input.

**Passing criterion:** None today. This case defines what to build.

**When it becomes State B:** When the company is added to the registry and Finance DNA can evaluate it.

---

## Canonical patterns

Every case must reference one of these ten patterns:

1. Supply Chain Risk
2. Commodity Shock
3. Interest Rate Sensitivity
4. Currency Exposure
5. Regulatory Risk
6. Customer Concentration
7. Supplier Concentration
8. Energy Dependency
9. Labour Exposure
10. Geopolitical Risk

See `research/canonical-reasoning-patterns.md` for the full specification of each pattern.

---

## Adding a new case

1. Choose the pattern the case demonstrates
2. Write the `expected` section first — define what the engine must produce before asking what knowledge is needed
3. Write the `required_knowledge` section — this becomes your Atlas and Finance DNA shopping list
4. Set the state honestly — do not mark a case as State A unless the engine actually produces the expected output today
5. Add at least one evidence citation

A case without evidence is a hypothesis, not a benchmark.

---

## Validation

A case is considered passing when:

```
response.blind_spots[company_id].summary.confidence >= expected.confidence.min
response.blind_spots[company_id].summary.confidence <= expected.confidence.max
response.blind_spots[company_id].explanation.steps == expected.reasoning_path
response.blind_spots[company_id].summary.categories ⊇ expected.required_categories
```

All four conditions must hold simultaneously.
