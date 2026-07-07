# Hyperion Roadmap

---

## Version 0.1 — Engine ✅

*Complete. Architecturally frozen.*

The deterministic financial reasoning pipeline: from a portfolio of company names to an explainable Blind Spot, with evidence, assumptions, and falsifiability conditions. Fully tested (407 tests), fully typed, with a REST API and deployment documentation.

```
Ingestion → Finance DNA → Atlas → Janus → Titan → BlindSpot
```

---

## Version 0.2 — Knowledge Representation

*Current focus.*

The engine works. The world it reasons over is small. Version 0.2 expands that world without changing how the engine reasons.

**Finance DNA: 6 → 15 dimensions**
Adding: Revenue Diversification, Customer Concentration, Pricing Power, Debt Sensitivity, Currency Exposure, Labor Intensity, IP Intensity, Regulatory Compliance Cost, Environmental Exposure.

**Atlas: 15 → 200+ nodes**
Adding: major geographies (20), commodities (15), currencies (10), macro factors (20+), more companies.

**10 canonical reasoning patterns**
Every Atlas and Finance DNA addition must serve one of the ten patterns defined in `research/canonical-reasoning-patterns.md`. No random growth.

---

## Version 0.3 — Knowledge Acquisition

*Automated knowledge building.*

Once the representation schema is stable, build importers that feed it automatically.

- SEC filing parser → Finance DNA dimensions
- Public relationship datasets → Atlas edges
- Macro data feeds → Context node updates
- News event detection → Economic Event nodes

---

## Version 0.4 — Visualization

*Making reasoning visible.*

Interactive graph explorer that renders the Atlas KnowledgeGraph and animates reasoning chains.

- Node → click → see Finance DNA dimensions
- Edge → click → see evidence and confidence
- Blind Spot → animated path from company to risk
- Development tool first, product feature second

---

## Version 1.0 — AI Explanation Layer

*LLMs augment reasoning. They do not replace it.*

The engine remains deterministic. LLMs provide natural-language explanation of Blind Spots, conversational Q&A over the knowledge graph, and portfolio-level narrative summaries.

The pipeline becomes:
```
Engine → Blind Spot → LLM Explanation → Human-readable insight
```

Reasoning happens before language. Language communicates what reasoning found.

---

## Five Pillars

Every contribution to Hyperion falls into one of five pillars:

| Pillar | Description | Version |
|--------|-------------|---------|
| **Engine** | Core reasoning pipeline | Frozen at v0.1 |
| **Knowledge** | Finance DNA dimensions, Atlas nodes and relationships | v0.2–v0.3 |
| **Interfaces** | API, CLI, visualization, frontend | v0.2+ |
| **Automation** | Data importers, graph builders | v0.3+ |
| **Developer Experience** | CI, documentation, tooling | Continuous |

When proposing a contribution, identify which pillar it strengthens. If the answer is none, it probably doesn't belong in Hyperion yet.

---

*This roadmap reflects intentional discipline: prove the engine first, expand the knowledge, then expose it through interfaces. Adding AI before the knowledge base is rich enough produces impressive-sounding explanations for a tiny slice of reality.*
