# 12 — Evidence Domain Model

**Version:** 0.3
**Status:** Active — Design Frozen
**Depends on:** `docs/11-EVIDENCE-ARCHITECTURE.md`
**Implements:** V0.3 Milestone 13 blueprint

---

## Purpose

This document is the frozen blueprint for every object in the Evidence Layer.

`docs/11-EVIDENCE-ARCHITECTURE.md` answered the philosophical questions:
what is evidence, what sources are trusted, what remains manual.

This document answers the engineering questions:
what are the exact objects, what are their fields, what are their invariants,
and how do they relate to each other.

**Every implementation decision in `backend/evidence/` traces back to this document.
If code contradicts this document, the code is wrong.**

---

## Section 1 — Object hierarchy

The ownership tree is frozen. Every object knows exactly what owns it
and what it owns.

```
Source
  │  (one Source has many Documents)
  ▼
Document
  │  (one Document has many Sections)
  ▼
Section
  │  (one Section has many Paragraphs)
  ▼
Paragraph
  │  (one Paragraph has many Excerpts)
  ▼
Excerpt
  │  (one Excerpt is cited by many Evidence)
  ▼
Evidence
  │  (many Evidence form one EvidenceBundle)
  ▼
EvidenceBundle
  │  (one EvidenceBundle belongs to one RelationshipCandidate)
  ▼
RelationshipCandidate
```

**Ownership rules:**
- Nothing is orphaned. Every object except Source belongs to exactly one parent.
- Deletion propagates downward conceptually. In practice nothing is deleted —
  everything is marked invalid or superseded.
- Relationships do not propagate upward. Evidence does not know what
  RelationshipCandidate uses it. Only the Candidate knows its Evidence.

---

## Section 2 — Every object

### Source

**Purpose:**
A registered trusted information source type. Defines where Hyperion
is allowed to learn from. The Source is the root of trust.

**Owner:** Source Registry — maintained by humans. Not created by parsers.

**Immutable:** Yes. Source definitions are configuration, not data.

**Lifetime:** Permanent. A Source type is never deleted from the registry.

**Primary key:** Short, stable, human-readable ID. Not a UUID.
Examples: `sec-edgar-10k`, `sec-edgar-10q`, `federal-reserve-publications`

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | Yes | Stable slug. Never changes. |
| `name` | `str` | Yes | Human-readable name |
| `tier` | `SourceTier` | Yes | 1, 2, 3, or 4 |
| `document_type` | `DocumentType` | Yes | Annual filing, quarterly, press release, etc. |
| `update_frequency` | `str` | Yes | "ANNUAL", "QUARTERLY", "EVENT_DRIVEN" |
| `url_pattern` | `str \| None` | No | URL template for automated retrieval |
| `trust_note` | `str` | Yes | One-sentence rationale for this source's trust level |

**Invariants:**
- `id` must be unique across the Source Registry
- `id` must be lowercase, hyphens only, no spaces
- `tier` must be 1, 2, 3, or 4
- `trust_note` must be non-empty

**Example:**
```python
Source(
    id="sec-edgar-10k",
    name="SEC EDGAR Form 10-K Annual Report",
    tier=SourceTier.ONE,
    document_type=DocumentType.ANNUAL_FILING,
    update_frequency="ANNUAL",
    url_pattern="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-K",
    trust_note="Audited annual filings required by SEC. Highest regulatory standard.",
)
```

---

### Document

**Purpose:**
A single filing or publication downloaded from a trusted Source.
One 10-K, one Fed publication, one press release.

**Owner:** Parser — created when a document is downloaded and processed.

**Immutable:** Yes. A document's content never changes after ingestion.
Amended filings (10-K/A) are new Documents.

**Lifetime:** Permanent. Documents are never deleted.

**Primary key:** UUID generated at download time.

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | Yes | UUID |
| `source_id` | `str` | Yes | FK to Source |
| `company_id` | `str \| None` | No | FK to Asset ID in Atlas |
| `title` | `str` | Yes | Full document title |
| `fiscal_year` | `str \| None` | No | e.g., "2025" |
| `published_at` | `str` | Yes | ISO-8601 date of publication |
| `retrieved_at` | `str` | Yes | ISO-8601 datetime when downloaded |
| `url` | `str \| None` | No | Source URL |
| `page_count` | `int \| None` | No | Total pages |
| `superseded_by` | `str \| None` | No | Document ID of newer version |

**Invariants:**
- `source_id` must reference a valid Source
- `published_at` must precede `retrieved_at`
- A Document with `superseded_by` set cannot be referenced by new Evidence

**Example:**
```python
Document(
    id="d7f3a1b2-4c8e-4f2a-b9d1-1e5c3f7a9b2d",
    source_id="sec-edgar-10k",
    company_id="apple-inc",
    title="Apple Inc. Form 10-K Annual Report FY2025",
    fiscal_year="2025",
    published_at="2025-11-01",
    retrieved_at="2025-11-15T09:23:41Z",
    url="https://www.sec.gov/Archives/edgar/data/320193/...",
    page_count=88,
    superseded_by=None,
)
```

---

### Section

**Purpose:**
A named subdivision of a Document. "Item 1A. Risk Factors", "MD&A", etc.

**Owner:** Parser.

**Immutable:** Yes.

**Lifetime:** Tied to its Document.

**Primary key:** UUID.

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | Yes | UUID |
| `document_id` | `str` | Yes | FK to Document |
| `title` | `str` | Yes | Section heading text |
| `index` | `int` | Yes | Position within Document (0-based) |
| `section_type` | `SectionType` | Yes | RISK_FACTORS, MD_AND_A, BUSINESS, NOTES, OTHER |

**Invariants:**
- `index` must be unique within a Document
- `title` must be non-empty

---

### Paragraph

**Purpose:**
The smallest independently addressable unit of document text.
The atom of the Evidence Layer.

**Owner:** Parser.

**Immutable:** Yes.

**Lifetime:** Tied to its Section.

**Primary key:** UUID.

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | Yes | UUID |
| `section_id` | `str` | Yes | FK to Section |
| `document_id` | `str` | Yes | Denormalized FK for fast lookup |
| `index` | `int` | Yes | Position within Section (0-based) |
| `text` | `str` | Yes | Full verbatim text |
| `paragraph_type` | `ParagraphType` | Yes | NARRATIVE, TABLE, HEADING, FOOTNOTE, CAPTION |
| `page` | `int \| None` | No | Page number in original document |
| `word_count` | `int` | Yes | Computed at creation |

**Why `paragraph_type` matters:**
LLMs behave differently on tables vs narrative. Stored at parse time —
costs nothing. Inferring it later is expensive.

**Invariants:**
- `index` must be unique within a Section
- `text` must be non-empty
- `word_count` must equal `len(text.split())`
- `document_id` must match the Document reachable via Section

**Example:**
```python
Paragraph(
    id="p3e8f2a1-9b4c-4d7e-a1f3-2c5d8e1b4f7a",
    section_id="s9a2c4d1-7e3f-4b8a-c2d5-6f1e8a3b7c4d",
    document_id="d7f3a1b2-4c8e-4f2a-b9d1-1e5c3f7a9b2d",
    index=214,
    text="We are dependent on TSMC as a sole-source supplier for Apple Silicon processors.",
    paragraph_type=ParagraphType.NARRATIVE,
    page=27,
    word_count=15,
)
```

---

### Excerpt

**Purpose:**
A specific character span within a Paragraph. The exact text that
supports a claim.

**Key design decision: Hyperion stores character offsets, not raw text.**
The raw text is always reconstructable from `Paragraph.text[char_start:char_end]`.
No text is duplicated. Excerpts are precise and verifiable.

**Owner:** Relationship Extractor or human reviewer.

**Immutable:** Yes.

**Lifetime:** Tied to its Paragraph.

**Primary key:** UUID.

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | Yes | UUID |
| `paragraph_id` | `str` | Yes | FK to Paragraph |
| `document_id` | `str` | Yes | Denormalized FK |
| `char_start` | `int` | Yes | Start offset in Paragraph.text (inclusive) |
| `char_end` | `int` | Yes | End offset in Paragraph.text (exclusive) |
| `created_by` | `str` | Yes | "EXTRACTOR" or "REVIEWER" |

**Computed property (not stored):**
```python
@property
def text(self) -> str:
    return paragraph.text[self.char_start:self.char_end]
```

**Invariants:**
- `char_start` ≥ 0
- `char_end` > `char_start`
- `char_end` ≤ `len(Paragraph.text)` for referenced Paragraph
- `created_by` must be "EXTRACTOR" or "REVIEWER"

**Example:**
```python
Excerpt(
    id="e1f4b7c2-8d3a-4e9f-b2c5-7a1d4e8f2b5c",
    paragraph_id="p3e8f2a1-9b4c-4d7e-a1f3-2c5d8e1b4f7a",
    document_id="d7f3a1b2-4c8e-4f2a-b9d1-1e5c3f7a9b2d",
    char_start=0,
    char_end=80,
    created_by="EXTRACTOR",
)
# text property returns:
# "We are dependent on TSMC as a sole-source supplier for Apple Silicon processors."
```

---

### Evidence

**Purpose:**
A verified claim derived from a specific Excerpt. Links source text
to the assertion that a relationship exists at a given confidence.

**Owner:** Extractor creates. Reviewer marks verified.

**Immutable:** Yes. Core fields set at creation and never change.
Status changes use `valid_until` and `superseded_by`.

**Lifetime:** Permanent. Never deleted.

**Primary key:** UUID. Never reused.

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | Yes | UUID — permanent |
| `excerpt_id` | `str` | Yes | FK to Excerpt |
| `document_id` | `str` | Yes | Denormalized FK |
| `source_id` | `str` | Yes | FK to Source |
| `evidence_type` | `EvidenceType` | Yes | DIRECT or DERIVED |
| `confidence` | `float` | Yes | [0.0, 1.0] |
| `retrieved_at` | `str` | Yes | ISO-8601 datetime of extraction |
| `valid_from` | `str` | Yes | ISO-8601 date (document publication) |
| `valid_until` | `str \| None` | No | ISO-8601 date when superseded |
| `superseded_by` | `str \| None` | No | Evidence ID of superseding record |
| `reviewer_id` | `str \| None` | No | Reviewer identifier |
| `reviewed_at` | `str \| None` | No | ISO-8601 datetime of review |

**Invariants:**
- `confidence` ∈ [0.0, 1.0]
- `valid_until`, if set, must be after `valid_from`
- If `superseded_by` is set, `valid_until` must also be set
- If `reviewed_at` is set, `reviewer_id` must also be set
- Once set, `id` and `excerpt_id` cannot change

**Example:**
```python
Evidence(
    id="ev7c2d4f1-3a8b-4e5c-9f1d-2b6a8e3c5f9d",
    excerpt_id="e1f4b7c2-8d3a-4e9f-b2c5-7a1d4e8f2b5c",
    document_id="d7f3a1b2-4c8e-4f2a-b9d1-1e5c3f7a9b2d",
    source_id="sec-edgar-10k",
    evidence_type=EvidenceType.DIRECT,
    confidence=0.96,
    retrieved_at="2025-11-15T09:23:41Z",
    valid_from="2025-11-01",
    valid_until=None,
    superseded_by=None,
    reviewer_id="yohan",
    reviewed_at="2025-11-16T14:30:00Z",
)
```

---

### EvidenceBundle

**Purpose:**
A collection of Evidence records supporting a RelationshipCandidate.
Tracks whether proposal and approval thresholds are met.

**Owner:** System — assembled by Extractor.

**Immutable:** Yes.

**Lifetime:** Tied to its RelationshipCandidate.

**Primary key:** UUID.

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | Yes | UUID |
| `evidence_ids` | `tuple[str, ...]` | Yes | Ordered tuple of Evidence IDs |
| `proposal_threshold_met` | `bool` | Yes | ≥1 Evidence with confidence ≥ 0.5 |
| `approval_threshold_met` | `bool` | Yes | Meets Atlas acceptance criteria |
| `min_confidence` | `float` | Yes | Minimum across all Evidence |
| `max_confidence` | `float` | Yes | Maximum across all Evidence |

**Thresholds:**
- Proposal: At least 1 Evidence with confidence ≥ 0.5
- Approval: At least 1 Tier 1 Direct Evidence OR 2 independent Tier 2+ Evidence

**Invariants:**
- `evidence_ids` non-empty, no duplicates
- `min_confidence` and `max_confidence` computed from actual Evidence
- If `approval_threshold_met`, then `proposal_threshold_met` must also be True

---

### RelationshipCandidate

**Purpose:**
A proposed Atlas relationship with supporting evidence, awaiting review.
NOT a Relationship. Becomes one only after human approval.

**Owner:** Extractor creates. Reviewer transitions status.

**Immutable:** Core proposal fields immutable. Status transitions follow lifecycle.

**Lifetime:** Permanent. All statuses preserved.

**Primary key:** UUID.

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `str` | Yes | UUID |
| `source_id` | `str` | Yes | Proposed source node ID |
| `target_id` | `str` | Yes | Proposed target node ID |
| `relationship_type` | `str` | Yes | Atlas relationship type |
| `evidence_bundle_id` | `str` | Yes | FK to EvidenceBundle |
| `proposed_confidence` | `float` | Yes | Confidence if approved |
| `status` | `CandidateStatus` | Yes | See lifecycle |
| `proposed_at` | `str` | Yes | ISO-8601 datetime |
| `reviewed_at` | `str \| None` | No | ISO-8601 datetime |
| `reviewer_id` | `str \| None` | No | Reviewer identifier |
| `rejection_reason` | `str \| None` | No | Required when REJECTED |
| `approved_relationship_id` | `str \| None` | No | Atlas ID when APPROVED |

**Status definitions:**

| Status | Meaning |
|--------|---------|
| PENDING | Awaiting review |
| APPROVED | Written to Atlas |
| REJECTED | Not added — archived |
| DEFERRED | Returned to queue |
| SUPERSEDED | Better candidate replaced this one |
| EXPIRED | Relationship itself no longer holds |

**SUPERSEDED vs EXPIRED:**
SUPERSEDED = better evidence replaced the candidate. Relationship still holds.
EXPIRED = the underlying fact is no longer true.

**Invariants:**
- `source_id` ≠ `target_id`
- `proposed_confidence` ≤ `EvidenceBundle.max_confidence`
- APPROVED must have `reviewer_id`, `reviewed_at`, `approved_relationship_id`
- REJECTED must have `reviewer_id`, `reviewed_at`, `rejection_reason`
- PENDING must have `reviewer_id = None`, `reviewed_at = None`

---

## Section 3 — Object invariants

### Confidence invariants

```
1.  All confidence values ∈ [0.0, 1.0]. No exceptions.

2.  DERIVED confidence ≤ DIRECT confidence for the same claim.

3.  RelationshipCandidate.proposed_confidence ≤
    EvidenceBundle.max_confidence.

4.  No relationship enters Atlas with confidence from Evidence
    not in its EvidenceBundle.
```

### Ownership invariants

```
5.  Every Document belongs to exactly one Source.
6.  Every Section belongs to exactly one Document.
7.  Every Paragraph belongs to exactly one Section.
8.  Every Excerpt belongs to exactly one Paragraph.
9.  Every Evidence references exactly one Excerpt.
10. Every EvidenceBundle references at least one Evidence.
11. Every RelationshipCandidate references exactly one EvidenceBundle.
```

### Lifecycle invariants

```
12. Evidence is never modified after creation.
13. Evidence with valid_until set cannot be referenced by new Candidates.
14. PENDING candidates must have reviewer_id = None.
15. APPROVED candidates must have reviewer_id, reviewed_at, approved_relationship_id.
16. REJECTED candidates must have reviewer_id, reviewed_at, rejection_reason.
17. SUPERSEDED ≠ EXPIRED. Different statuses, different meanings.
```

### Reference integrity invariants

```
18. Every FK reference must point to an existing object.
19. Denormalized document_id fields must match the traversal chain.
20. UUIDs are generated once and never changed.
```

---

## Section 4 — Lifecycle diagrams

### Evidence lifecycle

```
            EXTRACTOR creates
                   │
                   ▼
               CREATED
           (valid_until=None)
                   │
         ┌─────────┴──────────┐
         │                    │
   newer filing         fact no longer
   supersedes           holds
         │                    │
         ▼                    ▼
    SUPERSEDED            EXPIRED
 (valid_until set,    (valid_until set,
  superseded_by set)   superseded_by=None)
```

Evidence is never deleted.

### RelationshipCandidate lifecycle

```
        EXTRACTOR creates
               │
               ▼
           PENDING
               │
    ┌──────────┼──────────┐
    │          │          │
APPROVED   REJECTED   DEFERRED
(→ Atlas)  (archived) (→ queue)
    │                     │
    │               PENDING (again)
    │
┌───┴───┐
│       │
SUPERSEDED  EXPIRED
```

**Valid transitions:**
PENDING → APPROVED, REJECTED, DEFERRED
DEFERRED → PENDING
APPROVED → SUPERSEDED, EXPIRED

**Terminal states (no further transitions):**
REJECTED, EXPIRED, SUPERSEDED

### Full pipeline

```
10-K Filing published on SEC EDGAR
        │
        ▼
Parser downloads → Document
        │
        ▼
Parser extracts → Sections → Paragraphs
        │
        ▼
Extractor reads relevant Paragraphs
        │
        ▼
Extractor creates Excerpts (char offsets)
        │
        ▼
Extractor creates Evidence records
        │
        ▼
Extractor assembles EvidenceBundle
        │
        ▼
Extractor creates RelationshipCandidate (PENDING)
        │
        ▼
Automated checks:
  duplicate? contradiction? threshold met?
        │
        ▼
Candidate Queue
        │
        ▼
Human Reviewer (reads Excerpt → Paragraph → Section → Document)
        │
   ┌────┴────┐
APPROVE   REJECT
   │
   ▼
Atlas update
```

---

## Section 5 — Legacy migration

Hyperion has 26 hand-seeded V0.2 relationships classified as Legacy.
They have evidence text in the CSV but no formal Evidence objects.

### Upgrade path

Legacy upgrade is NOT a new RelationshipCandidate flow.
The relationship already exists. The task is retroactive evidence attachment.

```
Legacy Atlas Relationship (26 exist)
        │
        ▼
Parser finds supporting text in 10-K
        │
        ▼
Extractor creates Excerpt + Evidence
        │
        ▼
Evidence linked to existing Atlas relationship
        │
        ▼
Relationship upgraded: Legacy → Evidence-backed
```

### Priority order

| Relationship | Evidence target | Priority |
|-------------|----------------|----------|
| apple-inc → tsmc | Apple 10-K: sole-source supplier | HIGH |
| tsmc → taiwan | TSMC Annual Report: >90% capacity | HIGH |
| nvidia → china | NVIDIA 10-K: 17% China revenue | HIGH |
| nestle → coffee | Nestlé Annual Report: largest input | MEDIUM |
| Remaining 22 | Various | LOW |

**V0.3 target:** Top 3 legacy relationships upgraded before v0.3.0-alpha.

---

## Enumerations

```python
class SourceTier(int, Enum):
    ONE   = 1
    TWO   = 2
    THREE = 3
    FOUR  = 4

class DocumentType(StrEnum):
    ANNUAL_FILING     = "ANNUAL_FILING"
    QUARTERLY_FILING  = "QUARTERLY_FILING"
    CURRENT_REPORT    = "CURRENT_REPORT"
    GOVERNMENT_REPORT = "GOVERNMENT_REPORT"
    PRESENTATION      = "PRESENTATION"
    PRESS_RELEASE     = "PRESS_RELEASE"
    RESEARCH_REPORT   = "RESEARCH_REPORT"

class SectionType(StrEnum):
    RISK_FACTORS = "RISK_FACTORS"
    MD_AND_A     = "MD_AND_A"
    BUSINESS     = "BUSINESS"
    FINANCIALS   = "FINANCIALS"
    NOTES        = "NOTES"
    OTHER        = "OTHER"

class ParagraphType(StrEnum):
    NARRATIVE = "NARRATIVE"
    TABLE     = "TABLE"
    HEADING   = "HEADING"
    FOOTNOTE  = "FOOTNOTE"
    CAPTION   = "CAPTION"

class EvidenceType(StrEnum):
    DIRECT  = "DIRECT"
    DERIVED = "DERIVED"

class CandidateStatus(StrEnum):
    PENDING    = "PENDING"
    APPROVED   = "APPROVED"
    REJECTED   = "REJECTED"
    DEFERRED   = "DEFERRED"
    SUPERSEDED = "SUPERSEDED"
    EXPIRED    = "EXPIRED"
```

---

## What `backend/evidence/` never does

- Reads files from disk
- Makes network requests
- Writes to Atlas
- Imports from `backend/atlas/`, `backend/janus/`, `backend/titan/`,
  `backend/finance_dna/`, or `backend/api/`
- Contains business logic about relationship meaning
- Makes decisions about what is true or false

Only shared imports allowed: `backend/models/` and Python standard library.

---

## Definition of done for Milestone 13

| Criterion | Verification |
|-----------|-------------|
| Object hierarchy frozen | This document committed |
| 7 objects implemented as frozen dataclasses | `backend/evidence/models.py` |
| All enums centralized | `backend/evidence/enums.py` |
| Exception hierarchy | `backend/evidence/exceptions.py` |
| 90–120 test assertions | `backend/tests/test_evidence.py` |
| All invariants tested explicitly | Test groups match Section 3 |
| mypy --strict passes | Clean |
| ruff passes | Clean |
| Existing benchmark suite green | 6/6 canonical cases pass |
| No existing engine module modified | git diff confirms |
| Public interface documented | `backend/evidence/README.md` |
