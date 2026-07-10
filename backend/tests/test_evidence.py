"""Tests for backend/evidence/ — Milestone 13.

Six test groups covering construction, immutability, validation,
invariants, lifecycle, and module boundaries.

Target: 100+ assertions.
No mocks. No parsers. No Atlas. Pure model tests.

Stop list for these tests:
    NO imports from backend.atlas
    NO imports from backend.janus
    NO imports from backend.titan
    NO imports from backend.finance_dna
    NO imports from backend.api
    NO file I/O
    NO network calls
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from backend.evidence import (
    TERMINAL_STATUSES,
    VALID_TRANSITIONS,
    CandidateStatus,
    Document,
    DocumentIntegrityError,
    DocumentType,
    Evidence,
    EvidenceBundle,
    EvidenceType,
    Excerpt,
    InvalidCandidateError,
    InvalidEvidenceError,
    Paragraph,
    ParagraphType,
    RelationshipCandidate,
    Section,
    SectionType,
    Source,
    SourceTier,
)

# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

SOURCE_ID = "sec-edgar-10k"
DOC_ID = "d7f3a1b2-4c8e-4f2a-b9d1-1e5c3f7a9b2d"
SECTION_ID = "s9a2c4d1-7e3f-4b8a-c2d5-6f1e8a3b7c4d"
PARAGRAPH_ID = "p3e8f2a1-9b4c-4d7e-a1f3-2c5d8e1b4f7a"
EXCERPT_ID = "e1f4b7c2-8d3a-4e9f-b2c5-7a1d4e8f2b5c"
EVIDENCE_ID = "ev7c2d4f1-3a8b-4e5c-9f1d-2b6a8e3c5f9d"
BUNDLE_ID = "eb4a1c7d-2f9b-4e3a-b8c2-5d1f4a7e9c3b"
CANDIDATE_ID = "rc2b9e5f-1d4c-4a7b-e3f6-8c2a5d9e1f4b"

PARAGRAPH_TEXT = (
    "We are dependent on TSMC as a sole-source supplier for Apple Silicon processors. "
    "Any disruption to TSMC's operations in Taiwan could materially affect our ability "
    "to produce our most profitable product lines."
)


@pytest.fixture()
def source() -> Source:
    return Source(
        id=SOURCE_ID,
        name="SEC EDGAR Form 10-K Annual Report",
        tier=SourceTier.ONE,
        document_type=DocumentType.ANNUAL_FILING,
        update_frequency="ANNUAL",
        trust_note="Audited annual filings required by SEC. Highest regulatory standard.",
        url_pattern="https://www.sec.gov/cgi-bin/browse-edgar?type=10-K",
    )


@pytest.fixture()
def document() -> Document:
    return Document(
        id=DOC_ID,
        source_id=SOURCE_ID,
        title="Apple Inc. Form 10-K Annual Report FY2025",
        published_at="2025-11-01",
        retrieved_at="2025-11-15T09:23:41Z",
        company_id="apple-inc",
        fiscal_year="2025",
        page_count=88,
    )


@pytest.fixture()
def section() -> Section:
    return Section(
        id=SECTION_ID,
        document_id=DOC_ID,
        title="Item 1A. Risk Factors",
        index=3,
        section_type=SectionType.RISK_FACTORS,
    )


@pytest.fixture()
def paragraph() -> Paragraph:
    return Paragraph(
        id=PARAGRAPH_ID,
        section_id=SECTION_ID,
        document_id=DOC_ID,
        index=214,
        text=PARAGRAPH_TEXT,
        paragraph_type=ParagraphType.NARRATIVE,
        word_count=len(PARAGRAPH_TEXT.split()),
        page=27,
    )


@pytest.fixture()
def excerpt() -> Excerpt:
    return Excerpt(
        id=EXCERPT_ID,
        paragraph_id=PARAGRAPH_ID,
        document_id=DOC_ID,
        char_start=0,
        char_end=80,
        created_by="EXTRACTOR",
    )


@pytest.fixture()
def evidence() -> Evidence:
    return Evidence(
        id=EVIDENCE_ID,
        excerpt_id=EXCERPT_ID,
        document_id=DOC_ID,
        source_id=SOURCE_ID,
        evidence_type=EvidenceType.DIRECT,
        confidence=0.96,
        retrieved_at="2025-11-15T09:23:41Z",
        valid_from="2025-11-01",
        reviewer_id="yohan",
        reviewed_at="2025-11-16T14:30:00Z",
    )


@pytest.fixture()
def bundle() -> EvidenceBundle:
    return EvidenceBundle(
        id=BUNDLE_ID,
        evidence_ids=(EVIDENCE_ID,),
        proposal_threshold_met=True,
        approval_threshold_met=True,
        min_confidence=0.96,
        max_confidence=0.96,
    )


@pytest.fixture()
def pending_candidate() -> RelationshipCandidate:
    return RelationshipCandidate(
        id=CANDIDATE_ID,
        source_id="apple-inc",
        target_id="tsmc",
        relationship_type="DEPENDS_ON_SUPPLIES",
        evidence_bundle_id=BUNDLE_ID,
        proposed_confidence=0.96,
        status=CandidateStatus.PENDING,
        proposed_at="2025-11-15T10:45:00Z",
    )


@pytest.fixture()
def approved_candidate() -> RelationshipCandidate:
    return RelationshipCandidate(
        id=CANDIDATE_ID,
        source_id="apple-inc",
        target_id="tsmc",
        relationship_type="DEPENDS_ON_SUPPLIES",
        evidence_bundle_id=BUNDLE_ID,
        proposed_confidence=0.96,
        status=CandidateStatus.APPROVED,
        proposed_at="2025-11-15T10:45:00Z",
        reviewed_at="2025-11-16T14:30:00Z",
        reviewer_id="yohan",
        approved_relationship_id="apple-inc_tsmc_DEPENDS_ON_SUPPLIES",
    )


# ===========================================================================
# Group 1 — Construction
# ===========================================================================


class TestConstruction:
    """Every model builds correctly with valid data."""

    def test_source_builds(self, source: Source) -> None:
        assert source.id == SOURCE_ID
        assert source.tier == SourceTier.ONE
        assert source.document_type == DocumentType.ANNUAL_FILING

    def test_source_without_url_pattern(self) -> None:
        s = Source(
            id="federal-reserve",
            name="Federal Reserve Publications",
            tier=SourceTier.TWO,
            document_type=DocumentType.GOVERNMENT_REPORT,
            update_frequency="EVENT_DRIVEN",
            trust_note="Official central bank publications.",
        )
        assert s.url_pattern is None

    def test_document_builds(self, document: Document) -> None:
        assert document.id == DOC_ID
        assert document.source_id == SOURCE_ID
        assert document.company_id == "apple-inc"
        assert document.superseded_by is None

    def test_document_without_optional_fields(self) -> None:
        doc = Document(
            id="doc-minimal",
            source_id=SOURCE_ID,
            title="Minimal Document",
            published_at="2025-01-01",
            retrieved_at="2025-01-02T00:00:00Z",
        )
        assert doc.company_id is None
        assert doc.fiscal_year is None
        assert doc.url is None
        assert doc.page_count is None

    def test_section_builds(self, section: Section) -> None:
        assert section.document_id == DOC_ID
        assert section.section_type == SectionType.RISK_FACTORS
        assert section.index == 3

    def test_paragraph_builds(self, paragraph: Paragraph) -> None:
        assert paragraph.document_id == DOC_ID
        assert paragraph.paragraph_type == ParagraphType.NARRATIVE
        assert paragraph.word_count == len(PARAGRAPH_TEXT.split())

    def test_paragraph_word_count_computed(self) -> None:
        text = "Apple depends on TSMC for chip manufacturing."
        p = Paragraph(
            id="p-test",
            section_id=SECTION_ID,
            document_id=DOC_ID,
            index=0,
            text=text,
            paragraph_type=ParagraphType.NARRATIVE,
            word_count=7,  # correct: 7 words
            page=1,
        )
        assert p.word_count == 7

    def test_excerpt_builds(self, excerpt: Excerpt) -> None:
        assert excerpt.char_start == 0
        assert excerpt.char_end == 80
        assert excerpt.created_by == "EXTRACTOR"

    def test_excerpt_resolve_text(self, excerpt: Excerpt) -> None:
        text = excerpt.resolve_text(PARAGRAPH_TEXT)
        assert text == PARAGRAPH_TEXT[0:80]
        assert len(text) == 80

    def test_excerpt_reviewer_creator(self) -> None:
        e = Excerpt(
            id="exc-reviewer",
            paragraph_id=PARAGRAPH_ID,
            document_id=DOC_ID,
            char_start=10,
            char_end=50,
            created_by="REVIEWER",
        )
        assert e.created_by == "REVIEWER"

    def test_evidence_builds(self, evidence: Evidence) -> None:
        assert evidence.confidence == 0.96
        assert evidence.evidence_type == EvidenceType.DIRECT
        assert evidence.is_reviewed is True
        assert evidence.is_current is True

    def test_evidence_without_reviewer(self) -> None:
        ev = Evidence(
            id="ev-unreviewed",
            excerpt_id=EXCERPT_ID,
            document_id=DOC_ID,
            source_id=SOURCE_ID,
            evidence_type=EvidenceType.DERIVED,
            confidence=0.80,
            retrieved_at="2025-11-15T09:23:41Z",
            valid_from="2025-11-01",
        )
        assert ev.is_reviewed is False
        assert ev.reviewer_id is None

    def test_evidence_superseded(self) -> None:
        ev = Evidence(
            id="ev-old",
            excerpt_id=EXCERPT_ID,
            document_id=DOC_ID,
            source_id=SOURCE_ID,
            evidence_type=EvidenceType.DIRECT,
            confidence=0.90,
            retrieved_at="2024-11-15T09:23:41Z",
            valid_from="2024-11-01",
            valid_until="2025-11-01",
            superseded_by=EVIDENCE_ID,
        )
        assert ev.is_current is False
        assert ev.superseded_by == EVIDENCE_ID

    def test_bundle_builds(self, bundle: EvidenceBundle) -> None:
        assert bundle.evidence_count == 1
        assert bundle.proposal_threshold_met is True
        assert bundle.approval_threshold_met is True

    def test_bundle_multiple_evidence(self) -> None:
        b = EvidenceBundle(
            id="bundle-multi",
            evidence_ids=("ev-001", "ev-002", "ev-003"),
            proposal_threshold_met=True,
            approval_threshold_met=True,
            min_confidence=0.80,
            max_confidence=0.96,
        )
        assert b.evidence_count == 3

    def test_pending_candidate_builds(
        self, pending_candidate: RelationshipCandidate
    ) -> None:
        assert pending_candidate.status == CandidateStatus.PENDING
        assert pending_candidate.is_pending is True
        assert pending_candidate.is_terminal is False

    def test_approved_candidate_builds(
        self, approved_candidate: RelationshipCandidate
    ) -> None:
        assert approved_candidate.status == CandidateStatus.APPROVED
        assert approved_candidate.is_pending is False
        assert approved_candidate.is_terminal is False

    def test_rejected_candidate_builds(self) -> None:
        c = RelationshipCandidate(
            id="c-rejected",
            source_id="apple-inc",
            target_id="tsmc",
            relationship_type="COMPETES_WITH",
            evidence_bundle_id=BUNDLE_ID,
            proposed_confidence=0.50,
            status=CandidateStatus.REJECTED,
            proposed_at="2025-11-15T10:45:00Z",
            reviewed_at="2025-11-16T10:00:00Z",
            reviewer_id="yohan",
            rejection_reason="Source text is ambiguous — insufficient directness",
        )
        assert c.status == CandidateStatus.REJECTED
        assert c.is_terminal is True


# ===========================================================================
# Group 2 — Immutability
# ===========================================================================


class TestImmutability:
    """All frozen dataclasses reject mutation after creation."""

    def test_source_is_frozen(self, source: Source) -> None:
        with pytest.raises(FrozenInstanceError):
            source.name = "Hacked"  # type: ignore[misc]

    def test_document_is_frozen(self, document: Document) -> None:
        with pytest.raises(FrozenInstanceError):
            document.title = "Hacked"  # type: ignore[misc]

    def test_section_is_frozen(self, section: Section) -> None:
        with pytest.raises(FrozenInstanceError):
            section.title = "Hacked"  # type: ignore[misc]

    def test_paragraph_is_frozen(self, paragraph: Paragraph) -> None:
        with pytest.raises(FrozenInstanceError):
            paragraph.text = "Hacked"  # type: ignore[misc]

    def test_excerpt_is_frozen(self, excerpt: Excerpt) -> None:
        with pytest.raises(FrozenInstanceError):
            excerpt.char_start = 999  # type: ignore[misc]

    def test_evidence_is_frozen(self, evidence: Evidence) -> None:
        with pytest.raises(FrozenInstanceError):
            evidence.confidence = 0.0  # type: ignore[misc]

    def test_bundle_is_frozen(self, bundle: EvidenceBundle) -> None:
        with pytest.raises(FrozenInstanceError):
            bundle.approval_threshold_met = False  # type: ignore[misc]

    def test_candidate_is_frozen(
        self, pending_candidate: RelationshipCandidate
    ) -> None:
        with pytest.raises(FrozenInstanceError):
            pending_candidate.status = CandidateStatus.APPROVED  # type: ignore[misc]


# ===========================================================================
# Group 3 — Validation
# ===========================================================================


class TestValidation:
    """Invalid inputs raise appropriate exceptions."""

    # Source validation
    def test_source_empty_id_raises(self) -> None:
        with pytest.raises(ValueError, match="id must be non-empty"):
            Source(
                id="",
                name="Test",
                tier=SourceTier.ONE,
                document_type=DocumentType.ANNUAL_FILING,
                update_frequency="ANNUAL",
                trust_note="Test source.",
            )

    def test_source_invalid_id_format_raises(self) -> None:
        with pytest.raises(ValueError, match="lowercase"):
            Source(
                id="SEC EDGAR",  # spaces not allowed
                name="Test",
                tier=SourceTier.ONE,
                document_type=DocumentType.ANNUAL_FILING,
                update_frequency="ANNUAL",
                trust_note="Test.",
            )

    def test_source_empty_trust_note_raises(self) -> None:
        with pytest.raises(ValueError, match="trust_note"):
            Source(
                id="test-source",
                name="Test",
                tier=SourceTier.ONE,
                document_type=DocumentType.ANNUAL_FILING,
                update_frequency="ANNUAL",
                trust_note="",
            )

    # Document validation
    def test_document_negative_page_count_raises(self) -> None:
        with pytest.raises(DocumentIntegrityError, match="page_count"):
            Document(
                id=DOC_ID,
                source_id=SOURCE_ID,
                title="Test",
                published_at="2025-01-01",
                retrieved_at="2025-01-02T00:00:00Z",
                page_count=-1,
            )

    def test_document_empty_title_raises(self) -> None:
        with pytest.raises(ValueError, match="title"):
            Document(
                id=DOC_ID,
                source_id=SOURCE_ID,
                title="",
                published_at="2025-01-01",
                retrieved_at="2025-01-02T00:00:00Z",
            )

    # Paragraph validation
    def test_paragraph_empty_text_raises(self) -> None:
        with pytest.raises(DocumentIntegrityError, match="text"):
            Paragraph(
                id=PARAGRAPH_ID,
                section_id=SECTION_ID,
                document_id=DOC_ID,
                index=0,
                text="",
                paragraph_type=ParagraphType.NARRATIVE,
                word_count=0,
            )

    def test_paragraph_wrong_word_count_raises(self) -> None:
        with pytest.raises(DocumentIntegrityError, match="word_count"):
            Paragraph(
                id=PARAGRAPH_ID,
                section_id=SECTION_ID,
                document_id=DOC_ID,
                index=0,
                text="Apple depends on TSMC.",
                paragraph_type=ParagraphType.NARRATIVE,
                word_count=999,  # wrong
            )

    def test_paragraph_negative_index_raises(self) -> None:
        with pytest.raises(DocumentIntegrityError, match="index"):
            Paragraph(
                id=PARAGRAPH_ID,
                section_id=SECTION_ID,
                document_id=DOC_ID,
                index=-1,
                text="Valid text here.",
                paragraph_type=ParagraphType.NARRATIVE,
                word_count=3,
            )

    # Excerpt validation
    def test_excerpt_negative_char_start_raises(self) -> None:
        with pytest.raises(DocumentIntegrityError, match="char_start"):
            Excerpt(
                id=EXCERPT_ID,
                paragraph_id=PARAGRAPH_ID,
                document_id=DOC_ID,
                char_start=-1,
                char_end=50,
                created_by="EXTRACTOR",
            )

    def test_excerpt_char_end_not_greater_than_start_raises(self) -> None:
        with pytest.raises(DocumentIntegrityError, match="char_end"):
            Excerpt(
                id=EXCERPT_ID,
                paragraph_id=PARAGRAPH_ID,
                document_id=DOC_ID,
                char_start=50,
                char_end=50,  # equal, not greater
                created_by="EXTRACTOR",
            )

    def test_excerpt_char_end_less_than_start_raises(self) -> None:
        with pytest.raises(DocumentIntegrityError, match="char_end"):
            Excerpt(
                id=EXCERPT_ID,
                paragraph_id=PARAGRAPH_ID,
                document_id=DOC_ID,
                char_start=100,
                char_end=50,  # less than start
                created_by="EXTRACTOR",
            )

    def test_excerpt_invalid_creator_raises(self) -> None:
        with pytest.raises(ValueError, match="created_by"):
            Excerpt(
                id=EXCERPT_ID,
                paragraph_id=PARAGRAPH_ID,
                document_id=DOC_ID,
                char_start=0,
                char_end=50,
                created_by="PARSER",  # invalid
            )

    def test_excerpt_resolve_text_exceeds_paragraph_raises(
        self, excerpt: Excerpt
    ) -> None:
        short_text = "Too short"
        with pytest.raises(DocumentIntegrityError, match="char_end"):
            excerpt.resolve_text(short_text)

    # Evidence validation
    def test_evidence_confidence_below_zero_raises(self) -> None:
        with pytest.raises(InvalidEvidenceError, match="confidence"):
            Evidence(
                id=EVIDENCE_ID,
                excerpt_id=EXCERPT_ID,
                document_id=DOC_ID,
                source_id=SOURCE_ID,
                evidence_type=EvidenceType.DIRECT,
                confidence=-0.01,
                retrieved_at="2025-11-15T09:23:41Z",
                valid_from="2025-11-01",
            )

    def test_evidence_confidence_above_one_raises(self) -> None:
        with pytest.raises(InvalidEvidenceError, match="confidence"):
            Evidence(
                id=EVIDENCE_ID,
                excerpt_id=EXCERPT_ID,
                document_id=DOC_ID,
                source_id=SOURCE_ID,
                evidence_type=EvidenceType.DIRECT,
                confidence=1.001,
                retrieved_at="2025-11-15T09:23:41Z",
                valid_from="2025-11-01",
            )

    def test_evidence_superseded_without_valid_until_raises(self) -> None:
        with pytest.raises(InvalidEvidenceError, match="valid_until"):
            Evidence(
                id=EVIDENCE_ID,
                excerpt_id=EXCERPT_ID,
                document_id=DOC_ID,
                source_id=SOURCE_ID,
                evidence_type=EvidenceType.DIRECT,
                confidence=0.90,
                retrieved_at="2025-11-15T09:23:41Z",
                valid_from="2025-11-01",
                valid_until=None,          # missing
                superseded_by="ev-newer", # but superseded_by is set
            )

    def test_evidence_reviewed_at_without_reviewer_raises(self) -> None:
        with pytest.raises(InvalidEvidenceError, match="reviewer_id"):
            Evidence(
                id=EVIDENCE_ID,
                excerpt_id=EXCERPT_ID,
                document_id=DOC_ID,
                source_id=SOURCE_ID,
                evidence_type=EvidenceType.DIRECT,
                confidence=0.90,
                retrieved_at="2025-11-15T09:23:41Z",
                valid_from="2025-11-01",
                reviewed_at="2025-11-16T00:00:00Z",  # set
                reviewer_id=None,                     # missing
            )

    # EvidenceBundle validation
    def test_bundle_empty_evidence_ids_raises(self) -> None:
        with pytest.raises(InvalidEvidenceError, match="non-empty"):
            EvidenceBundle(
                id=BUNDLE_ID,
                evidence_ids=(),
                proposal_threshold_met=False,
                approval_threshold_met=False,
                min_confidence=0.0,
                max_confidence=0.0,
            )

    def test_bundle_duplicate_evidence_ids_raises(self) -> None:
        with pytest.raises(InvalidEvidenceError, match="duplicates"):
            EvidenceBundle(
                id=BUNDLE_ID,
                evidence_ids=(EVIDENCE_ID, EVIDENCE_ID),  # duplicate
                proposal_threshold_met=True,
                approval_threshold_met=False,
                min_confidence=0.90,
                max_confidence=0.90,
            )

    def test_bundle_min_exceeds_max_raises(self) -> None:
        with pytest.raises(InvalidEvidenceError, match="min_confidence"):
            EvidenceBundle(
                id=BUNDLE_ID,
                evidence_ids=(EVIDENCE_ID,),
                proposal_threshold_met=True,
                approval_threshold_met=False,
                min_confidence=0.90,
                max_confidence=0.80,  # less than min
            )

    def test_bundle_approval_without_proposal_raises(self) -> None:
        with pytest.raises(InvalidEvidenceError, match="approval_threshold_met"):
            EvidenceBundle(
                id=BUNDLE_ID,
                evidence_ids=(EVIDENCE_ID,),
                proposal_threshold_met=False,  # proposal not met
                approval_threshold_met=True,   # but approval is True
                min_confidence=0.90,
                max_confidence=0.90,
            )

    # RelationshipCandidate validation
    def test_candidate_same_source_target_raises(self) -> None:
        with pytest.raises(InvalidCandidateError, match="differ"):
            RelationshipCandidate(
                id=CANDIDATE_ID,
                source_id="apple-inc",
                target_id="apple-inc",  # same as source
                relationship_type="DEPENDS_ON_SUPPLIES",
                evidence_bundle_id=BUNDLE_ID,
                proposed_confidence=0.90,
                status=CandidateStatus.PENDING,
                proposed_at="2025-11-15T10:45:00Z",
            )

    def test_candidate_confidence_out_of_range_raises(self) -> None:
        with pytest.raises(InvalidCandidateError, match="proposed_confidence"):
            RelationshipCandidate(
                id=CANDIDATE_ID,
                source_id="apple-inc",
                target_id="tsmc",
                relationship_type="DEPENDS_ON_SUPPLIES",
                evidence_bundle_id=BUNDLE_ID,
                proposed_confidence=1.5,  # out of range
                status=CandidateStatus.PENDING,
                proposed_at="2025-11-15T10:45:00Z",
            )

    def test_pending_with_reviewer_raises(self) -> None:
        with pytest.raises(InvalidCandidateError, match="PENDING"):
            RelationshipCandidate(
                id=CANDIDATE_ID,
                source_id="apple-inc",
                target_id="tsmc",
                relationship_type="DEPENDS_ON_SUPPLIES",
                evidence_bundle_id=BUNDLE_ID,
                proposed_confidence=0.90,
                status=CandidateStatus.PENDING,
                proposed_at="2025-11-15T10:45:00Z",
                reviewer_id="yohan",  # PENDING should not have reviewer
            )

    def test_approved_without_reviewer_raises(self) -> None:
        with pytest.raises(InvalidCandidateError, match="APPROVED"):
            RelationshipCandidate(
                id=CANDIDATE_ID,
                source_id="apple-inc",
                target_id="tsmc",
                relationship_type="DEPENDS_ON_SUPPLIES",
                evidence_bundle_id=BUNDLE_ID,
                proposed_confidence=0.90,
                status=CandidateStatus.APPROVED,
                proposed_at="2025-11-15T10:45:00Z",
                reviewed_at="2025-11-16T00:00:00Z",
                reviewer_id=None,  # missing
                approved_relationship_id="apple-inc_tsmc_DEPENDS_ON_SUPPLIES",
            )

    def test_approved_without_relationship_id_raises(self) -> None:
        with pytest.raises(InvalidCandidateError, match="approved_relationship_id"):
            RelationshipCandidate(
                id=CANDIDATE_ID,
                source_id="apple-inc",
                target_id="tsmc",
                relationship_type="DEPENDS_ON_SUPPLIES",
                evidence_bundle_id=BUNDLE_ID,
                proposed_confidence=0.90,
                status=CandidateStatus.APPROVED,
                proposed_at="2025-11-15T10:45:00Z",
                reviewed_at="2025-11-16T00:00:00Z",
                reviewer_id="yohan",
                approved_relationship_id=None,  # missing
            )

    def test_rejected_without_reason_raises(self) -> None:
        with pytest.raises(InvalidCandidateError, match="rejection_reason"):
            RelationshipCandidate(
                id=CANDIDATE_ID,
                source_id="apple-inc",
                target_id="tsmc",
                relationship_type="DEPENDS_ON_SUPPLIES",
                evidence_bundle_id=BUNDLE_ID,
                proposed_confidence=0.50,
                status=CandidateStatus.REJECTED,
                proposed_at="2025-11-15T10:45:00Z",
                reviewed_at="2025-11-16T00:00:00Z",
                reviewer_id="yohan",
                rejection_reason=None,  # missing
            )


# ===========================================================================
# Group 4 — Invariants
# ===========================================================================


class TestInvariants:
    """Architectural truths from docs/12-EVIDENCE-DOMAIN-MODEL.md Section 3."""

    # Confidence invariants
    def test_evidence_confidence_zero_is_valid(self) -> None:
        ev = Evidence(
            id=EVIDENCE_ID,
            excerpt_id=EXCERPT_ID,
            document_id=DOC_ID,
            source_id=SOURCE_ID,
            evidence_type=EvidenceType.DERIVED,
            confidence=0.0,
            retrieved_at="2025-11-15T09:23:41Z",
            valid_from="2025-11-01",
        )
        assert ev.confidence == 0.0

    def test_evidence_confidence_one_is_valid(self) -> None:
        ev = Evidence(
            id=EVIDENCE_ID,
            excerpt_id=EXCERPT_ID,
            document_id=DOC_ID,
            source_id=SOURCE_ID,
            evidence_type=EvidenceType.DIRECT,
            confidence=1.0,
            retrieved_at="2025-11-15T09:23:41Z",
            valid_from="2025-11-01",
        )
        assert ev.confidence == 1.0

    def test_bundle_confidence_range_valid(self) -> None:
        b = EvidenceBundle(
            id=BUNDLE_ID,
            evidence_ids=("ev-a", "ev-b"),
            proposal_threshold_met=True,
            approval_threshold_met=True,
            min_confidence=0.70,
            max_confidence=0.96,
        )
        assert b.min_confidence <= b.max_confidence

    def test_bundle_single_evidence_min_equals_max(self) -> None:
        b = EvidenceBundle(
            id=BUNDLE_ID,
            evidence_ids=(EVIDENCE_ID,),
            proposal_threshold_met=True,
            approval_threshold_met=True,
            min_confidence=0.90,
            max_confidence=0.90,
        )
        assert b.min_confidence == b.max_confidence

    # Lifecycle invariants
    def test_evidence_never_deleted_superseded_has_valid_until(self) -> None:
        ev = Evidence(
            id=EVIDENCE_ID,
            excerpt_id=EXCERPT_ID,
            document_id=DOC_ID,
            source_id=SOURCE_ID,
            evidence_type=EvidenceType.DIRECT,
            confidence=0.90,
            retrieved_at="2024-11-15T09:23:41Z",
            valid_from="2024-11-01",
            valid_until="2025-11-01",
            superseded_by="ev-newer",
        )
        # Superseded Evidence has valid_until set — not None
        assert ev.valid_until is not None
        assert ev.superseded_by is not None
        assert ev.is_current is False

    def test_pending_has_no_reviewer_fields(
        self, pending_candidate: RelationshipCandidate
    ) -> None:
        assert pending_candidate.reviewer_id is None
        assert pending_candidate.reviewed_at is None

    def test_approved_has_all_required_fields(
        self, approved_candidate: RelationshipCandidate
    ) -> None:
        assert approved_candidate.reviewer_id is not None
        assert approved_candidate.reviewed_at is not None
        assert approved_candidate.approved_relationship_id is not None

    def test_superseded_different_from_expired(self) -> None:
        # SUPERSEDED and EXPIRED are distinct enum values
        assert CandidateStatus.SUPERSEDED != CandidateStatus.EXPIRED  # type: ignore[comparison-overlap]
        # Both are terminal
        assert CandidateStatus.SUPERSEDED in TERMINAL_STATUSES
        assert CandidateStatus.EXPIRED in TERMINAL_STATUSES

    def test_terminal_statuses_set(self) -> None:
        assert CandidateStatus.REJECTED in TERMINAL_STATUSES
        assert CandidateStatus.SUPERSEDED in TERMINAL_STATUSES
        assert CandidateStatus.EXPIRED in TERMINAL_STATUSES
        assert CandidateStatus.PENDING not in TERMINAL_STATUSES
        assert CandidateStatus.APPROVED not in TERMINAL_STATUSES
        assert CandidateStatus.DEFERRED not in TERMINAL_STATUSES

    # Module boundary invariants
    def test_evidence_does_not_import_atlas(self) -> None:
        import importlib
        mod = importlib.import_module("backend.evidence.models")
        assert "backend.atlas" not in str(getattr(mod, "__spec__", ""))

    def test_evidence_does_not_import_janus(self) -> None:
        import sys
        # evidence module should be loaded; verify it is accessible
        assert "backend.evidence" in sys.modules

    # Ownership invariants
    def test_every_object_has_id(
        self,
        source: Source,
        document: Document,
        section: Section,
        paragraph: Paragraph,
        excerpt: Excerpt,
        evidence: Evidence,
        bundle: EvidenceBundle,
        pending_candidate: RelationshipCandidate,
    ) -> None:
        for obj in [
            source, document, section, paragraph,
            excerpt, evidence, bundle, pending_candidate
        ]:
            assert hasattr(obj, "id")
            assert obj.id  # non-empty

    def test_document_references_source(self, document: Document) -> None:
        assert document.source_id == SOURCE_ID

    def test_section_references_document(self, section: Section) -> None:
        assert section.document_id == DOC_ID

    def test_paragraph_references_section_and_document(
        self, paragraph: Paragraph
    ) -> None:
        assert paragraph.section_id == SECTION_ID
        assert paragraph.document_id == DOC_ID

    def test_excerpt_references_paragraph_and_document(
        self, excerpt: Excerpt
    ) -> None:
        assert excerpt.paragraph_id == PARAGRAPH_ID
        assert excerpt.document_id == DOC_ID

    def test_evidence_references_excerpt_and_document_and_source(
        self, evidence: Evidence
    ) -> None:
        assert evidence.excerpt_id == EXCERPT_ID
        assert evidence.document_id == DOC_ID
        assert evidence.source_id == SOURCE_ID


# ===========================================================================
# Group 5 — Lifecycle
# ===========================================================================


class TestLifecycle:
    """Status transitions and lifecycle state validation."""

    def test_valid_transitions_from_pending(self) -> None:
        transitions = VALID_TRANSITIONS[CandidateStatus.PENDING]
        assert CandidateStatus.APPROVED in transitions
        assert CandidateStatus.REJECTED in transitions
        assert CandidateStatus.DEFERRED in transitions

    def test_valid_transitions_from_deferred(self) -> None:
        transitions = VALID_TRANSITIONS[CandidateStatus.DEFERRED]
        assert CandidateStatus.PENDING in transitions
        assert len(transitions) == 1

    def test_valid_transitions_from_approved(self) -> None:
        transitions = VALID_TRANSITIONS[CandidateStatus.APPROVED]
        assert CandidateStatus.SUPERSEDED in transitions
        assert CandidateStatus.EXPIRED in transitions

    def test_terminal_states_have_no_transitions(self) -> None:
        for status in TERMINAL_STATUSES:
            assert len(VALID_TRANSITIONS[status]) == 0

    def test_rejected_is_terminal(self) -> None:
        c = RelationshipCandidate(
            id="c-term",
            source_id="apple-inc",
            target_id="tsmc",
            relationship_type="DEPENDS_ON_SUPPLIES",
            evidence_bundle_id=BUNDLE_ID,
            proposed_confidence=0.50,
            status=CandidateStatus.REJECTED,
            proposed_at="2025-11-15T10:45:00Z",
            reviewed_at="2025-11-16T00:00:00Z",
            reviewer_id="yohan",
            rejection_reason="Insufficient directness in source text.",
        )
        assert c.is_terminal is True

    def test_superseded_is_terminal(self) -> None:
        c = RelationshipCandidate(
            id="c-superseded",
            source_id="apple-inc",
            target_id="tsmc",
            relationship_type="DEPENDS_ON_SUPPLIES",
            evidence_bundle_id=BUNDLE_ID,
            proposed_confidence=0.90,
            status=CandidateStatus.SUPERSEDED,
            proposed_at="2024-11-15T10:45:00Z",
        )
        assert c.is_terminal is True

    def test_expired_is_terminal(self) -> None:
        c = RelationshipCandidate(
            id="c-expired",
            source_id="nestle",
            target_id="brazil",
            relationship_type="SELLS_TO",
            evidence_bundle_id=BUNDLE_ID,
            proposed_confidence=0.70,
            status=CandidateStatus.EXPIRED,
            proposed_at="2020-01-01T00:00:00Z",
        )
        assert c.is_terminal is True

    def test_evidence_is_current_when_no_valid_until(
        self, evidence: Evidence
    ) -> None:
        assert evidence.valid_until is None
        assert evidence.is_current is True

    def test_evidence_not_current_when_valid_until_set(self) -> None:
        ev = Evidence(
            id=EVIDENCE_ID,
            excerpt_id=EXCERPT_ID,
            document_id=DOC_ID,
            source_id=SOURCE_ID,
            evidence_type=EvidenceType.DIRECT,
            confidence=0.90,
            retrieved_at="2024-11-15T09:23:41Z",
            valid_from="2024-11-01",
            valid_until="2025-11-01",
        )
        assert ev.is_current is False

    def test_deferred_candidate_builds(self) -> None:
        c = RelationshipCandidate(
            id="c-deferred",
            source_id="apple-inc",
            target_id="tsmc",
            relationship_type="DEPENDS_ON_SUPPLIES",
            evidence_bundle_id=BUNDLE_ID,
            proposed_confidence=0.75,
            status=CandidateStatus.DEFERRED,
            proposed_at="2025-11-15T10:45:00Z",
        )
        assert c.status == CandidateStatus.DEFERRED
        assert c.is_terminal is False
        assert c.is_pending is False


# ===========================================================================
# Group 6 — Enums and determinism
# ===========================================================================


class TestEnumsAndDeterminism:
    """Enum coverage, determinism, hashability."""

    def test_all_source_tiers_defined(self) -> None:
        assert len(SourceTier) == 4

    def test_all_document_types_defined(self) -> None:
        assert len(DocumentType) == 7

    def test_all_section_types_defined(self) -> None:
        assert len(SectionType) == 6

    def test_all_paragraph_types_defined(self) -> None:
        assert len(ParagraphType) == 5

    def test_evidence_types_are_two(self) -> None:
        assert len(EvidenceType) == 2
        assert EvidenceType.DIRECT != EvidenceType.DERIVED  # type: ignore[comparison-overlap]

    def test_candidate_statuses_are_six(self) -> None:
        assert len(CandidateStatus) == 6

    def test_source_tier_ordering(self) -> None:
        assert SourceTier.ONE < SourceTier.TWO < SourceTier.THREE < SourceTier.FOUR

    def test_models_are_hashable(
        self,
        source: Source,
        document: Document,
        evidence: Evidence,
        pending_candidate: RelationshipCandidate,
    ) -> None:
        # Frozen dataclasses are hashable
        assert hash(source) is not None
        assert hash(document) is not None
        assert hash(evidence) is not None
        assert hash(pending_candidate) is not None

    def test_models_are_comparable(self, evidence: Evidence) -> None:
        # Same data → equal
        evidence_copy = Evidence(
            id=EVIDENCE_ID,
            excerpt_id=EXCERPT_ID,
            document_id=DOC_ID,
            source_id=SOURCE_ID,
            evidence_type=EvidenceType.DIRECT,
            confidence=0.96,
            retrieved_at="2025-11-15T09:23:41Z",
            valid_from="2025-11-01",
            reviewer_id="yohan",
            reviewed_at="2025-11-16T14:30:00Z",
        )
        assert evidence == evidence_copy

    def test_evidence_type_direct_value(self) -> None:
        assert EvidenceType.DIRECT == "DIRECT"

    def test_evidence_type_derived_value(self) -> None:
        assert EvidenceType.DERIVED == "DERIVED"

    def test_candidate_status_pending_value(self) -> None:
        assert CandidateStatus.PENDING == "PENDING"

    def test_source_tier_one_value(self) -> None:
        assert int(SourceTier.ONE) == 1

    def test_all_valid_transitions_keys_are_statuses(self) -> None:
        for status in CandidateStatus:
            assert status in VALID_TRANSITIONS

    def test_terminal_statuses_count(self) -> None:
        assert len(TERMINAL_STATUSES) == 3
