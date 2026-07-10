"""Evidence Layer domain models.

Justified by: docs/12-EVIDENCE-DOMAIN-MODEL.md.

Eight frozen dataclasses in dependency order:

    Source              — root of trust (Section Registry)
    Document            — a single filing
    Section             — named subdivision of a Document
    Paragraph           — smallest addressable text unit
    Excerpt             — character-offset span within a Paragraph
    Evidence            — verified claim with provenance
    EvidenceBundle      — Evidence collection for a Candidate
    RelationshipCandidate — proposed Atlas relationship

Every model is:
    - frozen (immutable after creation)
    - fully typed (mypy --strict)
    - zero business logic (validation only)
    - zero imports from Atlas, Janus, Titan, Finance DNA, or API

Invariants are enforced in __post_init__.
Cross-object invariants (FK consistency, confidence ordering)
are enforced by the service layer in Milestone 18.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.evidence.enums import (
    CandidateStatus,
    DocumentType,
    EvidenceType,
    ParagraphType,
    SectionType,
    SourceTier,
)
from backend.evidence.exceptions import (
    DocumentIntegrityError,
    InvalidCandidateError,
    InvalidEvidenceError,
)

# ---------------------------------------------------------------------------
# Source
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Source:
    """A registered trusted information source type.

    Source is the root of the Evidence hierarchy.
    Defined in the Source Registry — maintained by humans,
    not created by parsers.

    Justified by: docs/12-EVIDENCE-DOMAIN-MODEL.md §2 (Source).

    Invariants:
        id must be lowercase and contain only letters, digits, hyphens
        tier must be a valid SourceTier
        trust_note must be non-empty
    """

    id: str
    name: str
    tier: SourceTier
    document_type: DocumentType
    update_frequency: str
    trust_note: str
    url_pattern: str | None = field(default=None)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Source.id must be non-empty")
        if not all(c.islower() or c.isdigit() or c == "-" for c in self.id):
            raise ValueError(
                f"Source.id must be lowercase letters, digits, and hyphens only: {self.id!r}"
            )
        if not self.name:
            raise ValueError("Source.name must be non-empty")
        if not self.trust_note:
            raise ValueError("Source.trust_note must be non-empty")
        if not self.update_frequency:
            raise ValueError("Source.update_frequency must be non-empty")


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Document:
    """A single filing or publication downloaded from a trusted Source.

    Immutable after ingestion. Amended filings are separate Documents.
    Justified by: docs/12-EVIDENCE-DOMAIN-MODEL.md §2 (Document).

    Invariants:
        id must be non-empty (UUID)
        source_id must reference a valid Source (enforced by service layer)
        published_at must precede retrieved_at (format: ISO-8601)
        superseded Documents cannot be referenced by new Evidence
            (enforced by service layer)
    """

    id: str
    source_id: str
    title: str
    published_at: str
    retrieved_at: str
    company_id: str | None = field(default=None)
    fiscal_year: str | None = field(default=None)
    url: str | None = field(default=None)
    page_count: int | None = field(default=None)
    superseded_by: str | None = field(default=None)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Document.id must be non-empty")
        if not self.source_id:
            raise ValueError("Document.source_id must be non-empty")
        if not self.title:
            raise ValueError("Document.title must be non-empty")
        if not self.published_at:
            raise ValueError("Document.published_at must be non-empty")
        if not self.retrieved_at:
            raise ValueError("Document.retrieved_at must be non-empty")
        if self.page_count is not None and self.page_count < 1:
            raise DocumentIntegrityError(
                f"Document.page_count must be positive, got {self.page_count}"
            )


# ---------------------------------------------------------------------------
# Section
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Section:
    """A named subdivision of a Document.

    Examples: "Item 1A. Risk Factors", "Management's Discussion and Analysis"

    Justified by: docs/12-EVIDENCE-DOMAIN-MODEL.md §2 (Section).

    Invariants:
        index is unique within a Document (enforced by service layer)
        title must be non-empty
    """

    id: str
    document_id: str
    title: str
    index: int
    section_type: SectionType

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Section.id must be non-empty")
        if not self.document_id:
            raise ValueError("Section.document_id must be non-empty")
        if not self.title:
            raise ValueError("Section.title must be non-empty")
        if self.index < 0:
            raise DocumentIntegrityError(
                f"Section.index must be ≥ 0, got {self.index}"
            )


# ---------------------------------------------------------------------------
# Paragraph
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Paragraph:
    """The smallest independently addressable unit of document text.

    The atom of the Evidence Layer. Every Excerpt, Evidence, and
    RelationshipCandidate ultimately traces to specific Paragraph IDs.

    paragraph_type stored at parse time because LLMs apply different
    extraction strategies to TABLE vs NARRATIVE vs FOOTNOTE content.

    Justified by: docs/12-EVIDENCE-DOMAIN-MODEL.md §2 (Paragraph).

    Invariants:
        text must be non-empty
        word_count must equal len(text.split())
        index unique within Section (enforced by service layer)
        document_id must match Section's document_id (service layer)
    """

    id: str
    section_id: str
    document_id: str
    index: int
    text: str
    paragraph_type: ParagraphType
    word_count: int
    page: int | None = field(default=None)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Paragraph.id must be non-empty")
        if not self.section_id:
            raise ValueError("Paragraph.section_id must be non-empty")
        if not self.document_id:
            raise ValueError("Paragraph.document_id must be non-empty")
        if not self.text:
            raise DocumentIntegrityError("Paragraph.text must be non-empty")
        if self.index < 0:
            raise DocumentIntegrityError(
                f"Paragraph.index must be ≥ 0, got {self.index}"
            )
        expected_word_count = len(self.text.split())
        if self.word_count != expected_word_count:
            raise DocumentIntegrityError(
                f"Paragraph.word_count {self.word_count} does not match "
                f"len(text.split()) = {expected_word_count}"
            )
        if self.page is not None and self.page < 1:
            raise DocumentIntegrityError(
                f"Paragraph.page must be positive, got {self.page}"
            )


# ---------------------------------------------------------------------------
# Excerpt
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Excerpt:
    """A specific character span within a Paragraph.

    Stores character offsets, NOT raw text. The text is always
    reconstructable from Paragraph.text[char_start:char_end].
    No duplication. No risk of excerpt drifting from source.

    Justified by: docs/12-EVIDENCE-DOMAIN-MODEL.md §2 (Excerpt).

    Invariants:
        char_start ≥ 0
        char_end > char_start
        char_end ≤ len(Paragraph.text) for the referenced Paragraph
            (enforced by service layer — Paragraph not available here)
        created_by must be "EXTRACTOR" or "REVIEWER"

    Computed property (not stored):
        text = Paragraph.text[char_start:char_end]
    """

    id: str
    paragraph_id: str
    document_id: str
    char_start: int
    char_end: int
    created_by: str

    _VALID_CREATORS: frozenset[str] = field(
        default=frozenset({"EXTRACTOR", "REVIEWER"}),
        init=False,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Excerpt.id must be non-empty")
        if not self.paragraph_id:
            raise ValueError("Excerpt.paragraph_id must be non-empty")
        if not self.document_id:
            raise ValueError("Excerpt.document_id must be non-empty")
        if self.char_start < 0:
            raise DocumentIntegrityError(
                f"Excerpt.char_start must be ≥ 0, got {self.char_start}"
            )
        if self.char_end <= self.char_start:
            raise DocumentIntegrityError(
                f"Excerpt.char_end ({self.char_end}) must be > "
                f"char_start ({self.char_start})"
            )
        if self.created_by not in {"EXTRACTOR", "REVIEWER"}:
            raise ValueError(
                f"Excerpt.created_by must be 'EXTRACTOR' or 'REVIEWER', "
                f"got {self.created_by!r}"
            )

    def resolve_text(self, paragraph_text: str) -> str:
        """Reconstruct the excerpt text from the parent Paragraph text.

        The text is never stored in the Excerpt itself — this method
        reconstructs it on demand.

        Args:
            paragraph_text: The full text of the parent Paragraph.

        Returns:
            The verbatim excerpt text.

        Raises:
            DocumentIntegrityError: If char_end exceeds paragraph length.
        """
        if self.char_end > len(paragraph_text):
            raise DocumentIntegrityError(
                f"Excerpt.char_end ({self.char_end}) exceeds "
                f"paragraph text length ({len(paragraph_text)})"
            )
        return paragraph_text[self.char_start:self.char_end]


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Evidence:
    """A verified claim derived from a specific Excerpt.

    Links source text to the assertion that a relationship exists
    at a given confidence level. Permanent — never deleted.
    Status changes use valid_until and superseded_by fields.

    Justified by: docs/12-EVIDENCE-DOMAIN-MODEL.md §2 (Evidence).

    Invariants (model-level):
        confidence ∈ [0.0, 1.0]
        valid_until, if set, must follow valid_from (format checked only)
        superseded_by requires valid_until to be set
        reviewed_at requires reviewer_id to be set

    Cross-object invariants (service layer):
        DERIVED confidence ≤ DIRECT confidence for same claim
        excerpt_id must reference a valid Excerpt
        source_id must reference a valid Source
        superseded Documents cannot generate new Evidence
    """

    id: str
    excerpt_id: str
    document_id: str
    source_id: str
    evidence_type: EvidenceType
    confidence: float
    retrieved_at: str
    valid_from: str
    valid_until: str | None = field(default=None)
    superseded_by: str | None = field(default=None)
    reviewer_id: str | None = field(default=None)
    reviewed_at: str | None = field(default=None)

    def __post_init__(self) -> None:
        if not self.id:
            raise InvalidEvidenceError("Evidence.id must be non-empty")
        if not self.excerpt_id:
            raise InvalidEvidenceError("Evidence.excerpt_id must be non-empty")
        if not self.document_id:
            raise InvalidEvidenceError("Evidence.document_id must be non-empty")
        if not self.source_id:
            raise InvalidEvidenceError("Evidence.source_id must be non-empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise InvalidEvidenceError(
                f"Evidence.confidence must be in [0.0, 1.0], got {self.confidence}"
            )
        if not self.retrieved_at:
            raise InvalidEvidenceError("Evidence.retrieved_at must be non-empty")
        if not self.valid_from:
            raise InvalidEvidenceError("Evidence.valid_from must be non-empty")
        if self.superseded_by is not None and self.valid_until is None:
            raise InvalidEvidenceError(
                "Evidence.valid_until must be set when superseded_by is set"
            )
        if self.reviewed_at is not None and self.reviewer_id is None:
            raise InvalidEvidenceError(
                "Evidence.reviewer_id must be set when reviewed_at is set"
            )

    @property
    def is_current(self) -> bool:
        """True if this Evidence has not been superseded or expired."""
        return self.valid_until is None and self.superseded_by is None

    @property
    def is_reviewed(self) -> bool:
        """True if this Evidence has been reviewed by a human."""
        return self.reviewer_id is not None and self.reviewed_at is not None


# ---------------------------------------------------------------------------
# EvidenceBundle
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvidenceBundle:
    """A collection of Evidence records supporting a RelationshipCandidate.

    Tracks whether proposal and approval thresholds are met.
    The bundle's threshold flags are computed by the service layer
    and validated for consistency here.

    Thresholds (from docs/11-EVIDENCE-ARCHITECTURE.md):
        Proposal: ≥1 Evidence with confidence ≥ 0.5
        Approval:  ≥1 Tier 1 Direct Evidence OR ≥2 independent Tier 2+ Evidence

    Justified by: docs/12-EVIDENCE-DOMAIN-MODEL.md §2 (EvidenceBundle).

    Invariants:
        evidence_ids non-empty
        no duplicate evidence_ids
        min_confidence ≤ max_confidence
        both confidence values in [0.0, 1.0]
        approval_threshold_met → proposal_threshold_met
    """

    id: str
    evidence_ids: tuple[str, ...]
    proposal_threshold_met: bool
    approval_threshold_met: bool
    min_confidence: float
    max_confidence: float

    def __post_init__(self) -> None:
        if not self.id:
            raise InvalidEvidenceError("EvidenceBundle.id must be non-empty")
        if not self.evidence_ids:
            raise InvalidEvidenceError(
                "EvidenceBundle.evidence_ids must be non-empty"
            )
        if len(self.evidence_ids) != len(set(self.evidence_ids)):
            raise InvalidEvidenceError(
                "EvidenceBundle.evidence_ids must not contain duplicates"
            )
        if not 0.0 <= self.min_confidence <= 1.0:
            raise InvalidEvidenceError(
                f"EvidenceBundle.min_confidence must be in [0.0, 1.0], "
                f"got {self.min_confidence}"
            )
        if not 0.0 <= self.max_confidence <= 1.0:
            raise InvalidEvidenceError(
                f"EvidenceBundle.max_confidence must be in [0.0, 1.0], "
                f"got {self.max_confidence}"
            )
        if self.min_confidence > self.max_confidence:
            raise InvalidEvidenceError(
                f"EvidenceBundle.min_confidence ({self.min_confidence}) "
                f"must be ≤ max_confidence ({self.max_confidence})"
            )
        if self.approval_threshold_met and not self.proposal_threshold_met:
            raise InvalidEvidenceError(
                "EvidenceBundle: approval_threshold_met cannot be True "
                "when proposal_threshold_met is False"
            )

    @property
    def evidence_count(self) -> int:
        """Number of Evidence records in this bundle."""
        return len(self.evidence_ids)


# ---------------------------------------------------------------------------
# RelationshipCandidate
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RelationshipCandidate:
    """A proposed Atlas relationship with supporting evidence.

    NOT a Relationship. Becomes one only after human approval.
    Exists only in the Evidence Layer until APPROVED.

    The core proposal fields (source_id, target_id, relationship_type,
    evidence_bundle_id) are immutable. Status transitions follow the
    lifecycle defined in enums.VALID_TRANSITIONS.

    Status field consistency is enforced at construction time.
    Status transitions are enforced by the Knowledge Review Pipeline
    (Milestone 18), not by this model.

    Justified by: docs/12-EVIDENCE-DOMAIN-MODEL.md §2 (RelationshipCandidate).

    Model-level invariants:
        source_id ≠ target_id
        proposed_confidence ∈ [0.0, 1.0]
        PENDING: reviewer_id = None, reviewed_at = None
        APPROVED: reviewer_id set, reviewed_at set, approved_relationship_id set
        REJECTED: reviewer_id set, reviewed_at set, rejection_reason set
        DEFERRED: no reviewer required
        SUPERSEDED/EXPIRED: terminal — no further fields required

    Cross-object invariants (service layer):
        proposed_confidence ≤ EvidenceBundle.max_confidence
        evidence_bundle_id must reference a valid EvidenceBundle
        proposal_threshold_met must be True for PENDING to exist
    """

    id: str
    source_id: str
    target_id: str
    relationship_type: str
    evidence_bundle_id: str
    proposed_confidence: float
    status: CandidateStatus
    proposed_at: str
    reviewed_at: str | None = field(default=None)
    reviewer_id: str | None = field(default=None)
    rejection_reason: str | None = field(default=None)
    approved_relationship_id: str | None = field(default=None)

    def __post_init__(self) -> None:
        if not self.id:
            raise InvalidCandidateError("RelationshipCandidate.id must be non-empty")
        if not self.source_id:
            raise InvalidCandidateError("RelationshipCandidate.source_id must be non-empty")
        if not self.target_id:
            raise InvalidCandidateError("RelationshipCandidate.target_id must be non-empty")
        if self.source_id == self.target_id:
            raise InvalidCandidateError(
                f"source_id and target_id must differ, both are {self.source_id!r}"
            )
        if not self.relationship_type:
            raise InvalidCandidateError(
                "RelationshipCandidate.relationship_type must be non-empty"
            )
        if not self.evidence_bundle_id:
            raise InvalidCandidateError(
                "RelationshipCandidate.evidence_bundle_id must be non-empty"
            )
        if not 0.0 <= self.proposed_confidence <= 1.0:
            raise InvalidCandidateError(
                f"proposed_confidence must be in [0.0, 1.0], "
                f"got {self.proposed_confidence}"
            )
        if not self.proposed_at:
            raise InvalidCandidateError(
                "RelationshipCandidate.proposed_at must be non-empty"
            )
        self._validate_status_fields()

    def _validate_status_fields(self) -> None:
        """Enforce field consistency for each status."""
        status = self.status

        if status == CandidateStatus.PENDING:
            if self.reviewer_id is not None:
                raise InvalidCandidateError(
                    "PENDING candidate must not have reviewer_id set"
                )
            if self.reviewed_at is not None:
                raise InvalidCandidateError(
                    "PENDING candidate must not have reviewed_at set"
                )

        elif status == CandidateStatus.APPROVED:
            if self.reviewer_id is None:
                raise InvalidCandidateError(
                    "APPROVED candidate must have reviewer_id set"
                )
            if self.reviewed_at is None:
                raise InvalidCandidateError(
                    "APPROVED candidate must have reviewed_at set"
                )
            if self.approved_relationship_id is None:
                raise InvalidCandidateError(
                    "APPROVED candidate must have approved_relationship_id set"
                )

        elif status == CandidateStatus.REJECTED:
            if self.reviewer_id is None:
                raise InvalidCandidateError(
                    "REJECTED candidate must have reviewer_id set"
                )
            if self.reviewed_at is None:
                raise InvalidCandidateError(
                    "REJECTED candidate must have reviewed_at set"
                )
            if self.rejection_reason is None:
                raise InvalidCandidateError(
                    "REJECTED candidate must have rejection_reason set"
                )

    @property
    def is_terminal(self) -> bool:
        """True if this candidate is in a terminal state."""
        from backend.evidence.enums import TERMINAL_STATUSES
        return self.status in TERMINAL_STATUSES

    @property
    def is_pending(self) -> bool:
        """True if awaiting human review."""
        return self.status == CandidateStatus.PENDING
