"""Evidence Layer enumerations.

Justified by: docs/12-EVIDENCE-DOMAIN-MODEL.md (Enumerations section).

All enums for backend/evidence/ are defined here.
No string literals appear anywhere else in the evidence module.

Six enumerations covering source trust, document structure,
evidence type, and candidate lifecycle.

This module has zero dependencies on any other Hyperion module.
"""

from __future__ import annotations

from enum import IntEnum, StrEnum


class SourceTier(IntEnum):
    """Trust tier for a registered information source.

    Tier 1: Regulatory filings — highest trust (SEC EDGAR, ESMA)
    Tier 2: Government publications (Federal Reserve, OECD)
    Tier 3: Company-published materials (presentations, press releases)
    Tier 4: Secondary research (analyst reports, trade publications)

    Lower number = higher trust. Tier 1 outranks all others.
    Confidence modifiers: 1.0, 0.90, 0.80, 0.70 respectively.
    """

    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4


class DocumentType(StrEnum):
    """The type of a document, independent of its source.

    Determines parsing strategy and default confidence modifier.
    """

    ANNUAL_FILING = "ANNUAL_FILING"
    QUARTERLY_FILING = "QUARTERLY_FILING"
    CURRENT_REPORT = "CURRENT_REPORT"
    GOVERNMENT_REPORT = "GOVERNMENT_REPORT"
    PRESENTATION = "PRESENTATION"
    PRESS_RELEASE = "PRESS_RELEASE"
    RESEARCH_REPORT = "RESEARCH_REPORT"


class SectionType(StrEnum):
    """Named subdivision types within a Document.

    Relationship Extractor applies different extraction strategies
    per section type. Risk Factors are the highest-value section
    for supply chain, regulatory, and macro exposure claims.
    """

    RISK_FACTORS = "RISK_FACTORS"
    MD_AND_A = "MD_AND_A"
    BUSINESS = "BUSINESS"
    FINANCIALS = "FINANCIALS"
    NOTES = "NOTES"
    OTHER = "OTHER"


class ParagraphType(StrEnum):
    """The structural type of a paragraph within a section.

    LLMs behave differently on tables vs narrative text.
    Stored at parse time — costs nothing, inferring later is expensive.

    NARRATIVE: prose text
    TABLE: structured tabular data
    HEADING: section or subsection title
    FOOTNOTE: footnoted reference or disclaimer
    CAPTION: figure or table caption
    """

    NARRATIVE = "NARRATIVE"
    TABLE = "TABLE"
    HEADING = "HEADING"
    FOOTNOTE = "FOOTNOTE"
    CAPTION = "CAPTION"


class EvidenceType(StrEnum):
    """How the evidence was derived from its source text.

    DIRECT: explicitly stated in the source. "TSMC is sole-source supplier."
    Confidence modifier: 1.0 (no penalty).

    DERIVED: inferred from context or calculation.
    "TSMC reports 94% Taiwan capacity" → TSMC is geographically concentrated.
    Confidence modifier: 0.85 (15% penalty).

    DERIVED confidence must never exceed DIRECT confidence for the same claim.
    """

    DIRECT = "DIRECT"
    DERIVED = "DERIVED"


class CandidateStatus(StrEnum):
    """Lifecycle status of a RelationshipCandidate.

    Valid transitions:
        PENDING  → APPROVED, REJECTED, DEFERRED
        DEFERRED → PENDING
        APPROVED → SUPERSEDED, EXPIRED

    Terminal states (no further transitions):
        REJECTED, SUPERSEDED, EXPIRED

    SUPERSEDED vs EXPIRED:
        SUPERSEDED = better candidate replaced this one.
                     The underlying relationship still holds.
        EXPIRED    = the relationship itself no longer holds.
                     The fact was true but is no longer current.
    """

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"
    SUPERSEDED = "SUPERSEDED"
    EXPIRED = "EXPIRED"


# ---------------------------------------------------------------------------
# Valid status transitions — enforced by the Knowledge Review Pipeline
# (Milestone 18). Defined here as the single source of truth.
# ---------------------------------------------------------------------------

VALID_TRANSITIONS: dict[CandidateStatus, frozenset[CandidateStatus]] = {
    CandidateStatus.PENDING: frozenset({
        CandidateStatus.APPROVED,
        CandidateStatus.REJECTED,
        CandidateStatus.DEFERRED,
    }),
    CandidateStatus.DEFERRED: frozenset({
        CandidateStatus.PENDING,
    }),
    CandidateStatus.APPROVED: frozenset({
        CandidateStatus.SUPERSEDED,
        CandidateStatus.EXPIRED,
    }),
    CandidateStatus.REJECTED: frozenset(),    # terminal
    CandidateStatus.SUPERSEDED: frozenset(),  # terminal
    CandidateStatus.EXPIRED: frozenset(),     # terminal
}

TERMINAL_STATUSES: frozenset[CandidateStatus] = frozenset({
    CandidateStatus.REJECTED,
    CandidateStatus.SUPERSEDED,
    CandidateStatus.EXPIRED,
})
