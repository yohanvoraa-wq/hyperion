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

---

## Version 0.3 — Evidence Layer

*Teaching Hyperion how to learn.*

V0.1 built the reasoning engine. V0.2 taught it finance. V0.3 teaches it how to acquire and verify knowledge on its own — with humans in the loop at every write.

**Architecture:** `docs/11-EVIDENCE-ARCHITECTURE.md`

**The three-layer architecture:**
```
Evidence Layer    — "I read this."
       ↓
Knowledge Layer   — "I believe this."
       ↓
Reasoning Layer   — "Therefore..."
```

The Reasoning Layer does not change in V0.3.

### Milestone 12 — Evidence Architecture ✓

Design document. Freezes all architectural decisions before implementation.
Philosophy: evidence before knowledge. Humans approve. Systems propose.

### Milestone 13 — Evidence Domain Model

`backend/evidence/` — the frozen objects.

```
Evidence, EvidenceType, EvidenceBundle
Source, SourceTier, SourceRegistry
Document, Section, Paragraph
RelationshipCandidate, CandidateStatus
EvidenceConfidence
```

No parser. No ingestion. Only immutable models and tests.
Same discipline as Milestone 2 (Shared Models) in V0.1.

### Milestone 14 — Source Registry

Before reading documents, Hyperion knows where evidence is allowed to come from.

```
SEC EDGAR 10-K/10-Q/8-K   Tier 1
Government publications    Tier 2
Company presentations      Tier 3
Industry research          Tier 4
```

Every source has: trust level, document type, update frequency, version.
Atlas doesn't care. Evidence doesn't care. Only the registry knows.

### Milestone 15 — Document Model

Universal representation of parsed documents.

```
Document → Sections → Paragraphs → Citations
```

Every parser eventually produces this. Whether the source is SEC EDGAR today
or ESMA tomorrow or OECD next year — everything normalises to Document objects.

### Milestone 16 — SEC EDGAR Parser

One source. Done well.

```
Download 10-K from EDGAR
       ↓
Extract text
       ↓
Normalise encoding
       ↓
Segment paragraphs
       ↓
Identify sections (Risk Factors, MD&A, Supplier disclosures)
       ↓
Document object
```

No Atlas writes. No relationship extraction. Only Document objects.

### Milestone 17 — Relationship Extractor

AI appears here. Only here.

```
Paragraph → LLM → Candidate relationships with evidence attached
```

Prompt discipline:
- Extract only explicit statements. Do not infer.
- Attach paragraph ID and raw text to every candidate.
- Return structured JSON. No narrative.

Output: `RelationshipCandidate` objects in the candidate queue.
Nothing written to Atlas.

### Milestone 18 — Knowledge Review Pipeline

The human approval workflow. Exactly like GitHub Pull Requests for Atlas.

```
RelationshipCandidate
       ↓
Automated checks (duplicate, contradiction, minimum evidence)
       ↓
Review queue
       ↓
Human reviewer: approve / reject / defer
       ↓
Atlas (if approved, with Evidence ID)
```

The final write is the only manual step that cannot be automated in V0.3.

### Milestone 19 — Evidence Benchmarks

Benchmark cases gain an evidence section.

```json
{
  "expected": {
    "reasoning_path": [...],
    "evidence": {
      "apple-inc → tsmc": {
        "source_tier": 1,
        "evidence_type": "DIRECT",
        "min_confidence": 0.90
      }
    }
  }
}
```

Benchmarks now test provenance, not just reasoning.
The apple_taiwan golden example must cite a 10-K by the end of V0.3.

### Milestone 20 — v0.3.0-alpha Release

```
Evidence Layer operational
SEC EDGAR pipeline validated
Three relationships upgraded from legacy to evidence-backed
Benchmark suite passing (all V0.2 cases preserved)
Evidence architecture documented
```

---

## Version 0.4 — Intelligence Layer

*Hyperion learns to explain itself.*

- Automated Atlas growth from evidence pipeline (human review still required for edge cases)
- LLM explanation layer: explains reasoning chains using only attached evidence
- Multi-path Janus: surfaces more than one blind spot per company
- Evidence-first confidence: all confidence values derived from Evidence objects
- `apple_china_revenue` benchmark becomes Implemented

---

## Version 0.5 — Interface Layer

- Interactive graph visualisation
- Portfolio dashboard
- Reasoning explorer
- CLI improvements

---

## Version 1.0

- Thousands of companies
- Tens of thousands of relationships
- All confidence values at Level A (company-specific filing data)
- Complete benchmark suite (10/10 patterns)
- Stable public API
- Open-source community
