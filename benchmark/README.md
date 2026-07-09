# Canonical Reasoning Benchmarks

This directory contains the canonical reasoning cases that define what Hyperion must be able to reason about. Every case is simultaneously a regression test, a product specification, a research example, and a success criterion.

---

## Knowledge Coverage

This table is the primary metric for Version 0.2 progress. Not nodes added. Not dimensions added. Pattern coverage.

| Pattern | Case | State | Company | Confidence |
|---------|------|-------|---------|------------|
| Supply Chain Risk | `apple_taiwan` | ✅ Implemented | Apple | 0.8075 |
| Commodity Shock | `nestle_coffee` | ✅ Implemented | Nestlé | 0.7268 |
| Regulatory Risk | `nvidia_export_controls` | ✅ Implemented | NVIDIA | 0.8100 |
| Geopolitical Risk | — | 🔲 Planned | — | — |
| Currency Exposure | — | 🔲 Planned | — | — |
| Interest Rate Sensitivity | — | 🔲 Planned | — | — |
| Customer Concentration | — | 🔲 Planned | — | — |
| Supplier Concentration | — | 🔲 Planned | — | — |
| Energy Dependency | — | 🔲 Planned | — | — |
| Labour Exposure | — | 🔲 Planned | — | — |

**Current coverage: 3 / 10 patterns demonstrated.**

Version 0.2 target: 5 / 10 patterns. Run `uv run python scripts/run_benchmarks.py` to verify.

---

## Case States

| State | Symbol | Meaning | Passing criterion |
|-------|--------|---------|-------------------|
| Implemented | ✅ | Engine produces expected output today | Exact confidence range + path structure |
| Partial | 🟡 | Company exists, some blind spot found, not the target path | Any blind spot found for the company |
| Planned | 🔲 | Company or required nodes don't exist yet | None — defines what to build |

---

## Knowledge Domain Coverage

How well each financial risk domain is represented in the current Atlas.

```
Supply Chain   ██████████░░░░░░  60%  (apple_taiwan + TSMC/Taiwan nodes)
Commodity      ████████░░░░░░░░  50%  (nestle_coffee + coffee/brazil nodes)
Regulation     ██████░░░░░░░░░░  38%  (nvidia_export_controls + export ban node)
Geopolitical   ████░░░░░░░░░░░░  25%  (Taiwan risk exists, China risk added)
Currency       ██░░░░░░░░░░░░░░  13%  (no dedicated case yet)
Energy         █░░░░░░░░░░░░░░░   6%  (dimension exists, no Atlas case)
Labour         █░░░░░░░░░░░░░░░   6%  (dimension exists, no Atlas case)
Interest Rate  █░░░░░░░░░░░░░░░   6%  (us-fed-rate node added, no case)
Customer       ░░░░░░░░░░░░░░░░   0%  (dimension exists, no Atlas nodes)
Supplier       ░░░░░░░░░░░░░░░░   0%  (dimension exists, no Atlas nodes)
```

---

## Directory structure

```
benchmarks/
├── README.md              — this file (coverage table, domain coverage)
├── schema.md              — field definitions and validation rules
└── canonical_cases/
    ├── apple_taiwan.json          — Implemented  (Supply Chain Risk)
    ├── nvidia_export_controls.json — Implemented  (Regulatory Risk)
    └── nestle_coffee.json         — Implemented  (Commodity Shock)
```

---

## How to use these cases

**Run the benchmark suite:**
```bash
uv run python scripts/run_benchmarks.py
```

**As regression tests** — verify a specific case still passes after an Atlas change:
```bash
curl -X POST http://localhost:8000/v1/analyze \
     -H "Content-Type: application/json" \
     -d '{"portfolio": ["Apple"], "as_of": "2024-12-31"}'
```

Verify: `blind_spots[0].summary.confidence` is within `[0.80, 0.82]`.

**As a planning tool** — before adding any Finance DNA dimension or Atlas node, open the relevant case file and check `required_knowledge`. If the addition doesn't appear there, ask: which case does this serve?

---

## How to add a new case

1. Choose a pattern from `research/canonical-reasoning-patterns.md`
2. Choose a real company where the pattern applies clearly
3. Find verifiable public evidence (10-K filing, analyst report, regulatory filing)
4. Write the `expected` section first — define the output before asking what knowledge is needed
5. Write `required_knowledge` — this becomes your Atlas and Finance DNA shopping list
6. Set state to `Planned` (almost certainly, for a new case)
7. Save as `benchmarks/canonical_cases/{pattern}_{company}.json`
8. Update the Knowledge Coverage table in this README

**A case without evidence is a hypothesis, not a benchmark.**

---

## Planned cases for Version 0.2 completion

| Planned case | Pattern | Target company | Key Atlas nodes needed |
|-------------|---------|---------------|----------------------|
| `apple_china_revenue` | Currency Exposure | Apple | cny-usd-risk |
| `alphabet_eu_regulation` | Geopolitical Risk | Alphabet | eu-digital-regulation |
| `amazon_energy` | Energy Dependency | Amazon | electricity, grid-instability |
| `qualcomm_apple_concentration` | Customer Concentration | Qualcomm | apple-revenue-dependency |
| `microsoft_interest_rate` | Interest Rate Sensitivity | Microsoft | us-fed-rate |
