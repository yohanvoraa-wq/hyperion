# 11 — Evidence Architecture

**Version:** 0.3
**Status:** Active — Design Frozen
**Milestone:** 12 — Evidence Architecture (Design)

---

## Purpose

This document defines the evidence layer that sits beneath Hyperion's knowledge graph. It answers every architectural question before implementation begins, exactly as the Constitution answered questions about reasoning before the engine was built.

Every V0.3 implementation decision traces back to this document. If an implementation choice contradicts something written here, the implementation is wrong — not the document.

---

## The three-layer architecture

Hyperion has three distinct layers with different responsibilities, different change rates, and different quality bars.

```
Evidence Layer    — "I read this."
       ↓
Knowledge Layer   — "I believe this."
       ↓
Reasoning Layer   — "Therefore..."
```

**Reasoning Layer** (Janus, Titan) — frozen since V0.1. Consumes knowledge. Never consumes evidence directly.

**Knowledge Layer** (Atlas) — expanding since V0.2. Stores relationships. Cites evidence by ID. Never stores raw text.

**Evidence Layer** (new in V0.3) — knows where knowledge came from. Stores provenance. Never reasons. Never stores relationships.

These layers must never collapse into each other. A parser belongs in the Evidence Layer. A relationship belongs in the Knowledge Layer. The Reasoning Layer remains unchanged by V0.3 entirely.

---

## What is evidence?

Evidence is a verifiable, sourced pointer to a specific location in a specific document that supports or refutes the existence, direction, confidence, or temporal status of an Atlas relationship.

Evidence is **not**:
- A summary of what a document says
- An LLM-generated statement
- A general claim about an industry
- An analyst opinion without a primary source
- A relationship itself

Evidence is a citation. "Apple 10-K FY2025, Item 1, page 27: TSMC identified as sole-source supplier for Apple Silicon processors." That sentence, plus metadata about where it came from, when it was retrieved, and how confident we are in the extraction — that is evidence.

---

## Two types of evidence

### Direct Evidence

Explicitly stated in the source document. The document says exactly this, using these words.

Example: "Apple 10-K FY2025, Risk Factors: We are dependent on TSMC as a sole-source supplier for Apple Silicon chips."

Confidence modifier: **1.0** (no penalty for directness)

### Derived Evidence

Inferred from context, calculation, or combination of statements. The document does not use this exact phrase, but the evidence can be derived from explicit statements.

Example: "TSMC Annual Report 2025, Operations: Our manufacturing facilities in Taiwan represent 94% of installed capacity" → derived relationship: TSMC is geographically concentrated in Taiwan.

Confidence modifier: **0.85** (15% penalty for derivation)

This mirrors the Approximation Level framework from Finance DNA. The type of evidence is always stored alongside the evidence itself.

---

## Trusted source hierarchy

Not all sources are equal. Hyperion uses a four-tier source registry.

### Tier 1 — Regulatory Filings (highest trust)

- SEC EDGAR 10-K (Annual Report)
- SEC EDGAR 10-Q (Quarterly Report)
- SEC EDGAR 8-K (Current Report — material events)
- ESMA filings (European equivalent)
- Companies House annual reports (UK)
- TSE disclosures (Japan)

Confidence modifier: **1.0**
Human review required: Yes (V0.3). Automated in V0.4 (once pipeline is validated).

### Tier 2 — Government and Regulatory Publications

- Federal Reserve publications
- European Central Bank publications
- BIS (Bank for International Settlements) reports
- OECD data publications
- US Department of Commerce trade data
- Government statistical agencies

Confidence modifier: **0.90**
Human review required: Yes (always)

### Tier 3 — Company-Published Materials

- Investor presentations
- Earnings call transcripts
- Press releases
- Company sustainability reports

Confidence modifier: **0.80**
Human review required: Yes (always)
Note: Company-published materials are promotional. Treat with appropriate skepticism.

### Tier 4 — Secondary Research

- Industry analyst reports (Goldman Sachs, Morgan Stanley, Gartner, IDC)
- Academic research papers
- Trade publications (Bloomberg, Reuters, Financial Times)

Confidence modifier: **0.70**
Human review required: Yes (always)
Note: Secondary sources must cite a primary source. If they do not, they do not qualify.

### Rejected sources

- Social media
- Wikipedia
- Blogs, opinion pieces
- Anonymous sources
- AI-generated content
- Any source that cannot be independently verified

---

## Can evidence expire?

Yes. Evidence has a validity period. When a new annual report supersedes the previous one, the old evidence does not disappear — it is marked superseded.

**How expiry works:**

Every evidence record has:
- `retrieved_at` — when Hyperion read this
- `valid_from` — when the source document was published
- `valid_until` — when the source was superseded (None = still valid)

When a new 10-K is ingested, the parser checks whether existing evidence from the previous 10-K is contradicted or superseded. If so, it marks the old evidence as superseded and creates a new evidence record.

The relationship does not automatically change. The new evidence enters the candidate queue for human review.

**Evidence never disappears.** The history of what Hyperion believed and why is permanently preserved. This is what makes the knowledge graph auditable.

---

## Can two sources disagree?

Yes. This is called a **contradiction** and it is expected, especially across source tiers.

**What happens when sources disagree:**

A new evidence candidate that contradicts an existing accepted relationship is flagged automatically with `CONTRADICTS_EXISTING` status. It enters the review queue as a priority item. A human reviewer must resolve it.

Resolution options:
1. **Accept new evidence** — supersedes the old, relationship confidence updates
2. **Reject new evidence** — old relationship preserved, new evidence marked REJECTED with reason
3. **Create parallel evidence** — both are valid for different time periods or geographies

**Contradiction is not failure.** Contradiction is information. A relationship where two Tier 1 sources disagree is a signal that the underlying fact is uncertain — and the confidence value should reflect that uncertainty.

---

## Evidence versioning

Every Atlas relationship tracks its confidence history. Confidence is not a static number — it is a time series.

```
apple-inc → DEPENDS_ON_SUPPLIES → tsmc

2024-12-31  confidence: 0.95  source: Apple 10-K FY2024
2025-12-31  confidence: 0.88  source: Apple 10-K FY2025 (Arizona fab operational, partial diversification)
2026-12-31  confidence: 0.75  source: Apple 10-K FY2026 (TSMC Arizona at 20% of Apple Silicon volume)
```

This history is never deleted. Reasoning runs against the current confidence. Evidence history is preserved for audit.

**Version invariant:** The confidence at any historical point can be reconstructed from the evidence history. If the evidence history is consistent with the confidence history, the knowledge graph is internally consistent.

---

## When is a relationship accepted into Atlas?

**Minimum requirements for acceptance:**

| Condition | Requirement |
|-----------|-------------|
| Minimum sources | At least 1 Tier 1 source OR at least 2 independent Tier 2+ sources |
| Evidence type | At least one Direct evidence record (Derived alone is insufficient) |
| Contradiction | No unresolved contradictions |
| Human review | One human reviewer must explicitly approve |
| Duplicate check | No existing equivalent relationship already in Atlas |

**What "independent" means:** Two sources from the same document family (e.g., two sections of the same 10-K) do not count as independent. Two sources from different companies, different publications, or different filing periods count as independent.

**No automated Atlas writes.** Ever. In V0.3. This constraint is permanent unless explicitly revisited in a future architecture document.

---

## How does evidence affect confidence?

The relationship confidence in Atlas is computed from its evidence:

```
base_confidence = evidence_tier_modifier × evidence_type_modifier × source_agreement_modifier
```

Where:

- `evidence_tier_modifier` = source tier confidence (1.0, 0.90, 0.80, 0.70)
- `evidence_type_modifier` = Direct (1.0) or Derived (0.85)
- `source_agreement_modifier` = 1.0 if all sources agree, 0.85 if sources partially agree, 0.70 if sources disagree

**Multiple sources:** When multiple evidence records support the same relationship, the base confidence is computed from the highest-tier source and adjusted upward for corroboration:

```
final_confidence = base_confidence + (0.03 × number_of_corroborating_sources)
capped at 0.99
```

No relationship can have confidence 1.0 unless it is a definitional truth (e.g., TSMC BELONGS_TO semiconductor-industry). Empirical relationships are always uncertain.

---

## What happens to existing V0.2 relationships?

The 26 hand-seeded relationships in V0.2 Atlas have evidence fields in the CSV, but no formal Evidence objects. They are classified as **Legacy Relationships**.

**Legacy Relationship rules:**
- They remain in Atlas unchanged
- They are not automatically upgraded to Evidence objects
- When the Evidence Layer exists, legacy relationships can be retroactively upgraded by creating an Evidence object and linking it
- Until then, their evidence field is treated as a plain text citation (Level C approximation — same as V0.1 Finance DNA)
- The `v0.1.0-alpha` and `v0.2.0-alpha` release tags permanently document when these relationships were created without formal evidence

Legacy relationships are not wrong. They are honest about their approximation level. The Evidence Layer will eventually replace them one by one as proper evidence is acquired.

---

## What remains manual in V0.3?

Everything that writes to Atlas remains manual.

**Automated in V0.3:**
- Document downloading from SEC EDGAR
- Text extraction and normalization
- Paragraph segmentation
- Section identification
- Candidate relationship extraction (AI-assisted)
- Contradiction detection
- Duplicate detection

**Manual in V0.3 (human required):**
- Final approval of every relationship candidate
- Resolution of contradictions
- Source trust level assignment for new source types
- Rejection of low-quality extractions
- Evidence confidence override

**This manual step is not a limitation — it is the quality guarantee.** Hyperion's relationships are trustworthy because a human verified each one against primary source evidence. That trustworthiness is the product.

Automation of the approval step is V0.4 work, and only for relationship types that have been validated at scale in V0.3.

---

## The candidate relationship lifecycle

```
Source Document
       ↓
Parser (V0.3 Milestone 16)
       ↓
Document Object
       ↓
Relationship Extractor (V0.3 Milestone 17)
       ↓
RelationshipCandidate (proposed, not in Atlas)
       ↓
Validation Checks
  - duplicate?
  - contradicts existing?
  - minimum evidence met?
       ↓
Candidate Queue
       ↓
Human Reviewer
  - approve → Atlas (with Evidence ID)
  - reject → archived with reason
  - defer → returned to queue
       ↓
Atlas (if approved)
```

No step in this pipeline writes to Atlas except the final human approval.

---

## Evidence objects — frozen fields

Every Evidence record contains exactly these fields. No V0.3 implementation may add or remove fields without a new architecture document.

```python
@dataclass(frozen=True)
class Evidence:
    id: str                          # Stable UUID — never reused
    source_id: str                   # FK to SourceRegistry
    document_id: str                 # FK to Document
    section: str                     # e.g., "Item 1A. Risk Factors"
    paragraph_index: int             # Position in document
    raw_text: str                    # Verbatim text from source
    evidence_type: EvidenceType      # DIRECT or DERIVED
    confidence: float                # [0.0, 1.0]
    retrieved_at: str                # ISO-8601 datetime
    valid_from: str                  # ISO-8601 date (document publication)
    valid_until: str | None          # ISO-8601 date (None = still valid)
    superseded_by: str | None        # Evidence ID of superseding record
    reviewer: str | None             # Who approved this evidence
    reviewed_at: str | None          # ISO-8601 datetime of review
```

---

## What V0.3 deliberately avoids

These are not forgotten. They are explicitly deferred.

- **Frontend** — out of scope
- **User authentication** — out of scope
- **Database persistence** — Atlas remains CSV-based in V0.3; database is V0.4+
- **Multi-user review** — single reviewer in V0.3
- **Automated Atlas writes** — never in V0.3
- **LLM explanation of blind spots** — V0.4
- **RAG, agents, chatbots** — V0.5+
- **News ingestion** — too noisy; Tier 1 sources only in V0.3
- **Real-time data feeds** — out of scope
- **Cloud deployment** — out of scope

---

## Success criteria for V0.3

V0.3 is complete when:

1. Every V0.3 module passes mypy --strict and the full test suite
2. At least one 10-K filing has been parsed end-to-end
3. At least three relationship candidates have been extracted, reviewed, and approved into Atlas
4. At least one existing V0.2 legacy relationship has been retroactively upgraded with formal evidence
5. The benchmark suite still passes (apple_taiwan at [0.80, 0.82])
6. The evidence model is fully documented in `SCORING-RATIONALE.md` equivalent for evidence

The last criterion is the most important. V0.3 should be as explainable as V0.2. Every evidence record should be as defensible as every Finance DNA score.

---

## Five architectural principles for V0.3

**1. Evidence before knowledge.** No relationship enters Atlas without evidence. No exception.

**2. Humans approve. Systems propose.** The pipeline surfaces candidates. People decide.

**3. Nothing disappears.** Evidence is versioned, not deleted. Relationships are superseded, not removed. The history is permanent.

**4. One source, done well.** SEC EDGAR first. No other sources until the EDGAR pipeline is validated and trusted.

**5. The Reasoning Layer is sacred.** Janus and Titan do not change. The Evidence Layer feeds the Knowledge Layer which feeds Reasoning. Evidence never touches Reasoning directly.
