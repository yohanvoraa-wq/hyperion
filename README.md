# Hyperion

**Every portfolio contains risks the investor never knowingly took on. Hyperion finds them.**

[![CI](https://github.com/yohanvoraa-wq/hyperion/actions/workflows/ci.yml/badge.svg)](https://github.com/yohanvoraa-wq/hyperion/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-740%20passing-brightgreen.svg)](#testing)
[![mypy](https://img.shields.io/badge/mypy-strict-blue.svg)](pyproject.toml)

---

## What Hyperion does

You hold Apple stock. You know Apple designs iPhones.

You may not know that Apple depends on TSMC as a sole-source supplier for its
most profitable chips, that TSMC concentrates over 90% of advanced manufacturing
in Taiwan, and that Taiwan carries persistent geopolitical risk.

That's a **Blind Spot** — a material exposure you hold without having decided to.

Hyperion finds these systematically, and shows its work:

```
Apple Inc.
  → DEPENDS_ON_SUPPLIES → Taiwan Semiconductor Manufacturing Company
  → LOCATED_IN          → Taiwan
  → AFFECTED_BY         → Taiwan Geopolitical Risk

Confidence: 0.8075

WHY THIS MATTERS
  Apple's semiconductor supply chain creates a geographic concentration
  the investor may not have explicitly accounted for.

EVIDENCE
  • Apple 10-K FY2024: TSMC identified as sole-source supplier
  • TSMC Annual Report: >90% of advanced node capacity in Taiwan

WHAT WOULD INVALIDATE THIS
  • Evidence that Apple has materially diversified chip manufacturing
  • TSMC establishing significant capacity outside Taiwan
```

Every conclusion is traceable. Every step cites a source. Nothing is generated
by a language model.

---

## Why this is different

Most financial AI tools produce fluent text that sounds authoritative. You cannot
verify how they reached their conclusion, and you cannot tell whether they made
it up.

Hyperion inverts this:

| | Typical LLM tool | Hyperion |
|---|---|---|
| **Reasoning** | Hidden in the model | Explicit graph traversal |
| **Same input twice** | Different answers | Identical answer, always |
| **Evidence** | Absent or invented | Cited to source documents |
| **Uncertainty** | Confident regardless | Confidence scores throughout |
| **When it doesn't know** | Generates something | Returns silence |

That last row matters most. When Hyperion has no qualifying reasoning path for
a company, it returns nothing. Microsoft, analyzed against V0.1 data, correctly
returned no Blind Spot rather than inventing one.

> *"Silence is preferable to weak explanations."* — [Constitution](docs/00-CONSTITUTION.md), Principle 6

---

## Quick start

**Requirements:** Python 3.12+ and [uv](https://docs.astral.sh/uv/)

```bash
git clone https://github.com/yohanvoraa-wq/hyperion.git
cd hyperion
uv sync
```

**See it reason:**

```bash
uv run python scripts/demo.py
```

**Verify every canonical case:**

```bash
uv run python scripts/run_benchmarks.py
```

**Inspect the knowledge base:**

```bash
uv run python scripts/knowledge_report.py
```

**Start the API:**

```bash
uv run python scripts/serve.py
# → http://localhost:8000/docs
```

---

## Using the API

```bash
curl -X POST http://localhost:8000/v1/analyze \
     -H "Content-Type: application/json" \
     -d '{"portfolio": ["Apple", "NVIDIA", "Nestle"], "as_of": "2024-12-31"}'
```

```json
{
  "metadata": {
    "hyperion_version": "0.1",
    "finance_dna_schema": "0.2",
    "processing_time_ms": 63
  },
  "blind_spots": [
    {
      "summary": {
        "company_id": "apple-inc",
        "company_name": "Apple Inc.",
        "confidence": 0.8075,
        "severity": "MEDIUM",
        "categories": ["dependency", "macroeconomic"]
      },
      "explanation": {
        "steps": [
          {
            "premise": "Apple Inc. → DEPENDS_ON_SUPPLIES → TSMC",
            "inference": "Apple has a supply chain dependency on TSMC.",
            "relationship_type": "depends_on_supplies",
            "source_id": "apple-inc",
            "target_id": "tsmc"
          }
        ]
      },
      "evidence": {
        "supporting_evidence": ["Apple 10-K: TSMC sole-source supplier"],
        "assumptions": ["Finance DNA uses sector-level approximations (V0.1)"],
        "falsifiability_conditions": ["Evidence of manufacturing diversification"]
      }
    }
  ],
  "no_findings": [],
  "errors": []
}
```

Every response includes `source_id`, `target_id`, and `relationship_type` for
every step — enough to render the reasoning chain as an interactive graph without
any additional API calls.

---

## How it works

Five modules. Five public functions. One direction of data flow.

```
    Portfolio  ["Apple", "NVIDIA", "Nestle"]
        │
        │  load_portfolio()
        ▼
    INGESTION ─────────── Resolves names, tickers, aliases → Asset objects
        │
        │  evaluate()
        ▼
    FINANCE DNA ───────── What kind of company is this?
        │                 15 dimensions: Capital Intensity, Supply Chain
        │                 Complexity, Currency Exposure, Energy Dependency,
        │                 Pricing Power, Customer Concentration...
        │  build()
        ▼
    ATLAS ─────────────── How is it connected to the world?
        │                 23 nodes, 26 relationships
        │                 Companies → Suppliers → Geographies → Macro Risks
        │  reason()
        ▼
    JANUS ─────────────── Which path matters?
        │                 BFS traversal, confidence ≥ 0.5, depth ≤ 4
        │                 Returns ReasoningArtifact or None
        │  qualify()
        ▼
    TITAN ─────────────── Does this reveal a genuine Blind Spot?
        │                 Four criteria: meaningful, non-obvious,
        │                 evidence-supported, changes understanding
        ▼
    BlindSpot            Explainable finding with falsifiability conditions
```

**Architectural rules that never change:**

1. Every module has exactly one public verb
2. Every artifact is immutable (`frozen=True` or `MappingProxyType`)
3. No module imports from a downstream module
4. The engine never imports from the API layer
5. IDs are permanent and never reused

See [`docs/ENGINE-STABILITY.md`](docs/ENGINE-STABILITY.md) for the formal
declaration of which modules are architecturally frozen.

---

## What Hyperion can currently reason about

Progress is measured by **reasoning patterns demonstrated**, not by node count.
Each pattern is validated by an executable benchmark that runs in CI.

| Pattern | Case | Chain | Confidence |
|---------|------|-------|-----------|
| ✅ Supply Chain Risk | `apple_taiwan` | Apple → TSMC → Taiwan → Geopolitical Risk | 0.8075 |
| ✅ Commodity Shock | `nestle_coffee` | Nestlé → Coffee → Brazil → Climate Risk | 0.7268 |
| ✅ Regulatory Risk | `nvidia_export_controls` | NVIDIA → China → Export Controls | 0.8100 |
| ✅ Interest Rate Sensitivity | `microsoft_interest_rate` | Microsoft → US → Fed Rate Policy | 0.6800 |
| ✅ Currency Exposure | `amazon_eu_currency` | Amazon → Europe → EUR/USD Risk | 0.7650 |
| 🔲 Geopolitical Risk | *planned* | — | — |
| 🔲 Customer Concentration | *planned* | — | — |
| 🔲 Supplier Concentration | *planned* | — | — |
| 🔲 Energy Dependency | *planned* | — | — |
| 🔲 Labour Exposure | *planned* | — | — |

**Coverage: 5 / 10 canonical patterns.**

Every benchmark is a JSON file specifying the expected company, confidence range,
and reasoning path. If a knowledge base change breaks Apple's 0.8075 confidence,
CI fails. See [`benchmarks/`](benchmarks/).

---

## Repository structure

```
hyperion/
├── backend/
│   ├── models/          Shared immutable domain objects
│   ├── ingestion/       Portfolio → Assets
│   ├── finance_dna/     Asset → FinanceDNA (15 dimensions)
│   ├── atlas/           Assets + DNA → KnowledgeGraph
│   ├── janus/           KnowledgeGraph → ReasoningArtifact
│   ├── titan/           ReasoningArtifact → BlindSpot
│   ├── evidence/        Evidence Layer (V0.3, in progress)
│   ├── api/             DTOs, schemas, FastAPI service
│   └── tests/           740 tests
├── benchmarks/
│   └── canonical_cases/ Executable reasoning benchmarks
├── datasets/
│   ├── assets.csv              7 companies
│   ├── atlas/                  Nodes and relationships
│   └── sources/                Trusted source registry
├── docs/                Architecture documents (00–12)
├── knowledge/           Knowledge registry
├── research/            Canonical reasoning patterns
└── scripts/
    ├── demo.py                 Terminal demonstration
    ├── serve.py                API server
    ├── run_benchmarks.py       Benchmark suite
    ├── lint_atlas.py           Knowledge graph integrity
    └── knowledge_report.py     Knowledge base dashboard
```

---

## Design philosophy

Hyperion was built document-first. Every architectural decision was frozen in
writing before any code was written, and every one of thirteen milestones was
implemented against a design that already existed.

| Document | What it decides |
|----------|----------------|
| [`00-CONSTITUTION.md`](docs/00-CONSTITUTION.md) | Ten principles governing every decision |
| [`03-BLIND-SPOT-FRAMEWORK.md`](docs/03-BLIND-SPOT-FRAMEWORK.md) | What qualifies as a Blind Spot |
| [`04-FINANCE-DNA.md`](docs/04-FINANCE-DNA.md) | How company identity is represented |
| [`05-ATLAS.md`](docs/05-ATLAS.md) | Knowledge graph ontology |
| [`06-JANUS.md`](docs/06-JANUS.md) | Reasoning model and traversal rules |
| [`09-PUBLIC-INTERFACE.md`](docs/09-PUBLIC-INTERFACE.md) | Frozen API contract |
| [`11-EVIDENCE-ARCHITECTURE.md`](docs/11-EVIDENCE-ARCHITECTURE.md) | Evidence provenance model |
| [`ENGINE-STABILITY.md`](docs/ENGINE-STABILITY.md) | Which modules are frozen |

The engine has not changed since v0.1.0-alpha. Every subsequent release added
knowledge or capability without modifying a single reasoning module.

---

## Testing

```bash
uv run pytest              # 740 tests
uv run mypy backend        # strict type checking, 0 issues
uv run ruff check backend/ # linting, 0 issues
```

The CI pipeline runs all four gates on every push: ruff, mypy `--strict`, pytest,
and the full benchmark suite.

---

## Roadmap

| Version | Focus | Status |
|---------|-------|--------|
| **v0.1.0-alpha** | Deterministic reasoning engine, API, CI | ✅ Released |
| **v0.2.0-alpha** | Knowledge expansion, 5/10 patterns, benchmarks | ✅ Released |
| **v0.3** | Evidence Layer — SEC filing ingestion with provenance | 🔨 In progress |
| v0.4 | Automated knowledge acquisition, LLM explanation layer | Planned |
| v0.5 | Interactive graph visualization | Planned |
| v1.0 | 10/10 patterns, thousands of companies | Planned |

The V0.3 Evidence Layer is what will let Hyperion learn from primary sources
rather than hand-curated data. The architecture is complete
([`docs/11-EVIDENCE-ARCHITECTURE.md`](docs/11-EVIDENCE-ARCHITECTURE.md)) and the
domain models, source registry, document model, and SEC parser are implemented.

Full plan: [`ROADMAP.md`](ROADMAP.md)

---

## Contributing

The most valuable contributions require no engine knowledge — adding a company
is one CSV row, adding a relationship is another. Every relationship must cite
verifiable evidence.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for how to add companies, relationships,
and Finance DNA dimensions.

---

## Current limitations

Stated plainly, because a system about hidden risks should not hide its own:

- **Finance DNA scores are industry-level approximations.** Company-specific
  scoring requires automated filing ingestion (V0.4).
- **The knowledge graph is hand-curated.** 7 companies, 23 nodes, 26
  relationships. The Evidence Layer will change this.
- **Janus returns one reasoning path per company.** Multi-path reasoning is
  planned for V0.4.
- **Five of ten canonical patterns are demonstrated.** The remaining five are
  specified but not yet implemented.

---

## License

MIT — see [`LICENSE`](LICENSE).

---

<div align="center">

**Hyperion is a reasoning system, not a chatbot.**

Every conclusion is traceable. Every step cites a source. Every claim can be falsified.

</div>
