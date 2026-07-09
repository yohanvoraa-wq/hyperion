# Canonical Reasoning Benchmarks

This directory contains the canonical reasoning cases that define what Hyperion must be able to reason about. Every case is simultaneously a regression test, a product specification, a research example, and a success criterion.

---

## Knowledge Coverage

This table is the primary metric for Version 0.2 progress. Not nodes added. Not dimensions added. Pattern coverage.

| Pattern | Case | State | Company |
|---------|------|-------|---------|
| Supply Chain Risk | `apple_taiwan` | ✅ A | Apple |
| Geopolitical Risk | `nvidia_export_controls` | 🟡 B | NVIDIA |
| Commodity Shock | `nestle_coffee` | ❌ C | Nestlé |
| Currency Exposure | — | ❌ C | — |
| Regulatory Risk | — | ❌ C | — |
| Interest Rate Sensitivity | — | ❌ C | — |
| Customer Concentration | — | ❌ C | — |
| Supplier Concentration | — | ❌ C | — |
| Energy Dependency | — | ❌ C | — |
| Labour Exposure | — | ❌ C | — |

**Current coverage: 1 / 10 patterns fully demonstrated.**

Version 0.2 target: 5 / 10 patterns with at least one State A case each.

---

## States

| State | Meaning | Passing criterion |
|-------|---------|-------------------|
| ✅ A — Implemented | Engine produces expected output today | Exact confidence range + exact reasoning path |
| 🟡 B — Partial | Company exists, some path found, not the target path | Any blind spot found for the company |
| ❌ C — Target | Company or required nodes don't exist yet | None — defines what to build |

---

## Directory structure

```
benchmarks/
├── README.md              — this file
├── schema.md              — field definitions and validation rules
└── canonical_cases/
    ├── apple_taiwan.json          — State A  (Supply Chain Risk)
    ├── nvidia_export_controls.json — State B  (Regulatory Risk / Geopolitical Risk)
    └── nestle_coffee.json         — State C  (Commodity Shock)
```

---

## How to use these cases

**As regression tests:**

Run the API against a State A case and verify the output matches:

```bash
curl -X POST http://localhost:8000/v1/analyze \
     -H "Content-Type: application/json" \
     -d '{"portfolio": ["Apple"], "as_of": "2024-12-31"}'
```

Then verify:
- `blind_spots[0].summary.company_id == "apple-inc"`
- `blind_spots[0].summary.confidence` is within `[0.80, 0.82]`
- `blind_spots[0].explanation.steps` matches the `reasoning_path` exactly

**As a planning tool:**

Before adding any Finance DNA dimension or Atlas node, open the relevant case file and check the `required_knowledge` section. If the addition doesn't appear there, ask: which case does this serve? If the answer is none, the addition may not belong in Version 0.2.

**As a progress tracker:**

Update the Knowledge Coverage table above each time a case moves from C → B or B → A. The table is the honest answer to "how far along is Version 0.2?"

---

## How to add a new case

1. Choose a pattern from `research/canonical-reasoning-patterns.md`
2. Choose a real company where the pattern applies clearly
3. Find verifiable public evidence (10-K filing, analyst report, regulatory filing)
4. Write the `expected` section first — define the output before asking what knowledge is needed
5. Write `required_knowledge` — this becomes your Atlas and Finance DNA shopping list
6. Set the state honestly (almost certainly C for a new case)
7. Save as `benchmarks/canonical_cases/{pattern}_{company}.json`
8. Update the Knowledge Coverage table in this README

**A case without evidence is a hypothesis, not a benchmark.**

---

## Relationship to the roadmap

```
Benchmark (State C)
      ↓
Finance DNA Expansion (add required dimensions)
      ↓
Atlas Expansion (add required nodes and relationships)
      ↓
Benchmark (State B → State A)
      ↓
Next pattern
```

Every Finance DNA dimension added in Version 0.2 should move at least one case from C toward B. Every Atlas node added should move at least one case from B toward A. If an addition moves no case forward, it belongs in a later version.

---

## Version 0.2 target cases

These cases will be added during Version 0.2 knowledge expansion:

| Planned case | Pattern | Target company |
|-------------|---------|---------------|
| `apple_china_revenue` | Currency Exposure | Apple |
| `alphabet_eu_regulation` | Regulatory Risk | Alphabet |
| `amazon_energy` | Energy Dependency | Amazon |
| `qualcomm_apple_concentration` | Customer Concentration | Qualcomm |
| `microsoft_interest_rate` | Interest Rate Sensitivity | Microsoft |

Each planned case has a corresponding entry in `research/canonical-reasoning-patterns.md` describing the required Finance DNA dimensions and Atlas node types.
