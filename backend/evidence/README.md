# backend/evidence/

The Evidence Layer — the foundation of Version 0.3.

---

## Purpose

This module defines the frozen vocabulary for the Evidence Layer.

Every object in this module answers one question:
**Where did Hyperion learn this?**

Without this module, Hyperion can say:
> "Apple depends on TSMC."

With this module, Hyperion can say:
> "Apple depends on TSMC — Apple 10-K FY2025, Item 1A, paragraph 214,
> confidence 0.96, verified 2025-11-16, reviewer: yohan."

---

## Responsibilities

This module does exactly one thing:
**Define the immutable data structures for evidence provenance.**

---

## Object hierarchy

```
Source
  ↓  (one Source has many Documents)
Document
  ↓  (one Document has many Sections)
Section
  ↓  (one Section has many Paragraphs)
Paragraph
  ↓  (one Paragraph has many Excerpts)
Excerpt
  ↓  (one Excerpt is cited by many Evidence)
Evidence
  ↓  (many Evidence form one EvidenceBundle)
EvidenceBundle
  ↓  (one EvidenceBundle belongs to one RelationshipCandidate)
RelationshipCandidate
```

---

## Public API

```python
from backend.evidence import (
    # Models
    Source, Document, Section, Paragraph, Excerpt,
    Evidence, EvidenceBundle, RelationshipCandidate,

    # Enums
    SourceTier, DocumentType, SectionType,
    ParagraphType, EvidenceType, CandidateStatus,

    # Lifecycle
    VALID_TRANSITIONS, TERMINAL_STATUSES,

    # Exceptions
    EvidenceError, InvalidEvidenceError,
    InvalidCandidateError, DocumentIntegrityError,
)
```

---

## Key design decisions

**Excerpts store character offsets, not raw text.**
`Excerpt.resolve_text(paragraph_text)` reconstructs the text on demand.
No duplication. No risk of excerpt drifting from its source.

**ParagraphType is stored at parse time.**
LLMs apply different extraction strategies to TABLE vs NARRATIVE content.
Storing the type costs nothing. Inferring it later is expensive.

**SUPERSEDED ≠ EXPIRED.**
SUPERSEDED: better evidence replaced this — relationship still holds.
EXPIRED: the relationship itself no longer holds.

**Evidence is never deleted.**
`valid_until` marks supersession. `superseded_by` points to the replacement.
The history is permanent and auditable.

**No automated Atlas writes.**
`RelationshipCandidate` is a proposal. It becomes an Atlas relationship
only after human approval in the Knowledge Review Pipeline (Milestone 18).

---

## Invariants

See `docs/12-EVIDENCE-DOMAIN-MODEL.md` Section 3 for all 20 invariants.

The most critical:

1. `Evidence.confidence` ∈ [0.0, 1.0]
2. `superseded_by` requires `valid_until`
3. `reviewed_at` requires `reviewer_id`
4. PENDING candidates have no reviewer fields
5. APPROVED candidates have all three review fields
6. REJECTED candidates have rejection_reason
7. SUPERSEDED and EXPIRED are both terminal — no further transitions

---

## What this module never does

- Reads files from disk
- Makes network requests
- Writes to Atlas
- Imports from `backend.atlas`, `backend.janus`, `backend.titan`,
  `backend.finance_dna`, or `backend.api`
- Contains business logic about what relationships mean
- Makes decisions about what is true or false

Only allowed imports: `backend.evidence.*` and Python standard library.

---

## Files

| File | Contents |
|------|----------|
| `enums.py` | All enumerations: SourceTier, DocumentType, SectionType, ParagraphType, EvidenceType, CandidateStatus |
| `models.py` | All frozen dataclasses: Source through RelationshipCandidate |
| `exceptions.py` | Exception hierarchy: EvidenceError, InvalidEvidenceError, InvalidCandidateError, DocumentIntegrityError |
| `__init__.py` | Public interface — exports all public types |

---

## Tests

`backend/tests/test_evidence.py` — 95 assertions across 6 groups:

1. Construction — all models build with valid data
2. Immutability — all models reject mutation
3. Validation — invalid inputs raise correct exceptions
4. Invariants — architectural truths tested explicitly
5. Lifecycle — status transitions validated
6. Enums and determinism — hashability, comparability, coverage
