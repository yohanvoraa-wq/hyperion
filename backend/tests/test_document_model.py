"""Tests for backend/evidence/document.py — Milestone 15.

Six test groups covering builder construction, auto-generation,
traversal, invariants, immutability, and error cases.

Target: 65 assertions.

Stop list:
    NO file I/O
    NO SEC API
    NO PDF parsing
    NO Evidence creation
    NO Atlas imports
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from backend.evidence import (
    DocumentBuilder,
    ParagraphType,
    ParsedDocument,
    SectionType,
)
from backend.evidence.document import _new_id
from backend.evidence.exceptions import DocumentIntegrityError
from backend.evidence.models import Document, Section

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

DOC_ID = "d7f3a1b2-4c8e-4f2a-b9d1-1e5c3f7a9b2d"
SOURCE_ID = "sec-edgar-10k"

RISK_TEXT = (
    "We are dependent on TSMC as a sole-source supplier for Apple Silicon processors. "
    "Any disruption to TSMC's operations in Taiwan could materially affect our ability "
    "to produce our most profitable product lines."
)
BUSINESS_TEXT = (
    "Apple designs, manufactures and markets smartphones, personal computers, "
    "tablets, wearables and accessories."
)
TABLE_TEXT = "TSMC | Taiwan | 0.95 | sole-source"


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
    )


@pytest.fixture()
def simple_parsed(document: Document) -> ParsedDocument:
    """One section, two paragraphs."""
    builder = DocumentBuilder(document)
    s1 = builder.add_section(
        title="Item 1A. Risk Factors",
        section_type=SectionType.RISK_FACTORS,
    )
    builder.add_paragraph(
        section_id=s1.id,
        text=RISK_TEXT,
        paragraph_type=ParagraphType.NARRATIVE,
        page=27,
    )
    builder.add_paragraph(
        section_id=s1.id,
        text=TABLE_TEXT,
        paragraph_type=ParagraphType.TABLE,
        page=28,
    )
    return builder.build()


@pytest.fixture()
def multi_section_parsed(document: Document) -> ParsedDocument:
    """Two sections with paragraphs each."""
    builder = DocumentBuilder(document)
    s1 = builder.add_section(
        title="Item 1. Business",
        section_type=SectionType.BUSINESS,
    )
    s2 = builder.add_section(
        title="Item 1A. Risk Factors",
        section_type=SectionType.RISK_FACTORS,
    )
    builder.add_paragraph(
        section_id=s1.id,
        text=BUSINESS_TEXT,
        paragraph_type=ParagraphType.NARRATIVE,
        page=5,
    )
    builder.add_paragraph(
        section_id=s2.id,
        text=RISK_TEXT,
        paragraph_type=ParagraphType.NARRATIVE,
        page=27,
    )
    builder.add_paragraph(
        section_id=s2.id,
        text=TABLE_TEXT,
        paragraph_type=ParagraphType.TABLE,
        page=28,
    )
    return builder.build()


# ===========================================================================
# Group 1 — Builder basics
# ===========================================================================


class TestBuilderBasics:
    """DocumentBuilder constructs correct counts and metadata."""

    def test_empty_builder_has_no_sections(self, document: Document) -> None:
        builder = DocumentBuilder(document)
        assert builder.section_count == 0

    def test_empty_builder_has_no_paragraphs(self, document: Document) -> None:
        builder = DocumentBuilder(document)
        assert builder.paragraph_count == 0

    def test_builder_document_property(self, document: Document) -> None:
        builder = DocumentBuilder(document)
        assert builder.document is document

    def test_add_section_increments_count(self, document: Document) -> None:
        builder = DocumentBuilder(document)
        builder.add_section(title="Sec A", section_type=SectionType.BUSINESS)
        assert builder.section_count == 1
        builder.add_section(title="Sec B", section_type=SectionType.RISK_FACTORS)
        assert builder.section_count == 2

    def test_add_paragraph_increments_count(self, document: Document) -> None:
        builder = DocumentBuilder(document)
        s = builder.add_section(title="Test", section_type=SectionType.OTHER)
        builder.add_paragraph(
            section_id=s.id, text="Text one.", paragraph_type=ParagraphType.NARRATIVE
        )
        assert builder.paragraph_count == 1
        builder.add_paragraph(
            section_id=s.id, text="Text two.", paragraph_type=ParagraphType.NARRATIVE
        )
        assert builder.paragraph_count == 2

    def test_build_returns_parsed_document(self, document: Document) -> None:
        builder = DocumentBuilder(document)
        result = builder.build()
        assert isinstance(result, ParsedDocument)

    def test_build_can_be_called_multiple_times(self, document: Document) -> None:
        builder = DocumentBuilder(document)
        s = builder.add_section(title="A", section_type=SectionType.BUSINESS)
        builder.add_paragraph(
            section_id=s.id, text="First build.", paragraph_type=ParagraphType.NARRATIVE
        )
        first = builder.build()

        # Second build after more additions — first is unaffected
        builder.add_paragraph(
            section_id=s.id, text="Added later.", paragraph_type=ParagraphType.NARRATIVE
        )
        second = builder.build()

        assert first.total_paragraphs == 1
        assert second.total_paragraphs == 2


# ===========================================================================
# Group 2 — Auto-generation
# ===========================================================================


class TestAutoGeneration:
    """Builder auto-generates IDs and indices correctly."""

    def test_section_index_starts_at_zero(self, document: Document) -> None:
        builder = DocumentBuilder(document)
        s = builder.add_section(title="First", section_type=SectionType.BUSINESS)
        assert s.index == 0

    def test_section_indices_are_sequential(self, document: Document) -> None:
        builder = DocumentBuilder(document)
        s1 = builder.add_section(title="A", section_type=SectionType.BUSINESS)
        s2 = builder.add_section(title="B", section_type=SectionType.RISK_FACTORS)
        s3 = builder.add_section(title="C", section_type=SectionType.MD_AND_A)
        assert s1.index == 0
        assert s2.index == 1
        assert s3.index == 2

    def test_paragraph_index_starts_at_zero_per_section(
        self, document: Document
    ) -> None:
        builder = DocumentBuilder(document)
        s = builder.add_section(title="Test", section_type=SectionType.OTHER)
        p = builder.add_paragraph(
            section_id=s.id, text="First para.", paragraph_type=ParagraphType.NARRATIVE
        )
        assert p.index == 0

    def test_paragraph_indices_sequential_within_section(
        self, document: Document
    ) -> None:
        builder = DocumentBuilder(document)
        s = builder.add_section(title="Test", section_type=SectionType.OTHER)
        p1 = builder.add_paragraph(
            section_id=s.id, text="Para one.", paragraph_type=ParagraphType.NARRATIVE
        )
        p2 = builder.add_paragraph(
            section_id=s.id, text="Para two.", paragraph_type=ParagraphType.NARRATIVE
        )
        p3 = builder.add_paragraph(
            section_id=s.id, text="Para three.", paragraph_type=ParagraphType.NARRATIVE
        )
        assert p1.index == 0
        assert p2.index == 1
        assert p3.index == 2

    def test_paragraph_indices_reset_per_section(self, document: Document) -> None:
        builder = DocumentBuilder(document)
        s1 = builder.add_section(title="A", section_type=SectionType.BUSINESS)
        s2 = builder.add_section(title="B", section_type=SectionType.RISK_FACTORS)
        builder.add_paragraph(
            section_id=s1.id, text="S1 P1.", paragraph_type=ParagraphType.NARRATIVE
        )
        builder.add_paragraph(
            section_id=s1.id, text="S1 P2.", paragraph_type=ParagraphType.NARRATIVE
        )
        p1_s2 = builder.add_paragraph(
            section_id=s2.id, text="S2 P1.", paragraph_type=ParagraphType.NARRATIVE
        )
        # First paragraph in section 2 has index 0, not 2
        assert p1_s2.index == 0

    def test_auto_generated_section_id_is_uuid(self, document: Document) -> None:
        builder = DocumentBuilder(document)
        s = builder.add_section(title="Test", section_type=SectionType.OTHER)
        # UUID4 is 36 chars with hyphens
        assert len(s.id) == 36
        assert s.id.count("-") == 4

    def test_explicit_section_id_is_preserved(self, document: Document) -> None:
        builder = DocumentBuilder(document)
        custom_id = "my-custom-section-id"
        s = builder.add_section(
            title="Test",
            section_type=SectionType.OTHER,
            section_id=custom_id,
        )
        assert s.id == custom_id

    def test_word_count_auto_computed(self, document: Document) -> None:
        builder = DocumentBuilder(document)
        s = builder.add_section(title="Test", section_type=SectionType.OTHER)
        text = "Apple TSMC Taiwan supply chain risk."
        p = builder.add_paragraph(
            section_id=s.id, text=text, paragraph_type=ParagraphType.NARRATIVE
        )
        assert p.word_count == len(text.split())

    def test_document_id_propagated_to_sections(self, document: Document) -> None:
        builder = DocumentBuilder(document)
        s = builder.add_section(title="Test", section_type=SectionType.OTHER)
        assert s.document_id == document.id

    def test_document_id_propagated_to_paragraphs(self, document: Document) -> None:
        builder = DocumentBuilder(document)
        s = builder.add_section(title="Test", section_type=SectionType.OTHER)
        p = builder.add_paragraph(
            section_id=s.id, text="Some text.", paragraph_type=ParagraphType.NARRATIVE
        )
        assert p.document_id == document.id


# ===========================================================================
# Group 3 — ParsedDocument traversal
# ===========================================================================


class TestParsedDocumentTraversal:
    """Traversal methods return correct results."""

    def test_section_count(self, simple_parsed: ParsedDocument) -> None:
        assert simple_parsed.section_count == 1

    def test_total_paragraphs(self, simple_parsed: ParsedDocument) -> None:
        assert simple_parsed.total_paragraphs == 2

    def test_total_paragraphs_multi_section(
        self, multi_section_parsed: ParsedDocument
    ) -> None:
        assert multi_section_parsed.total_paragraphs == 3

    def test_total_word_count(self, simple_parsed: ParsedDocument) -> None:
        expected = len(RISK_TEXT.split()) + len(TABLE_TEXT.split())
        assert simple_parsed.total_word_count == expected

    def test_all_paragraphs_returns_in_order(
        self, multi_section_parsed: ParsedDocument
    ) -> None:
        paragraphs = multi_section_parsed.all_paragraphs()
        assert len(paragraphs) == 3
        # Section 0 (Business) paragraph first, section 1 (Risk Factors) after
        assert paragraphs[0].text == BUSINESS_TEXT
        assert paragraphs[1].text == RISK_TEXT
        assert paragraphs[2].text == TABLE_TEXT

    def test_get_paragraphs_returns_section_subset(
        self, multi_section_parsed: ParsedDocument
    ) -> None:
        risk_section = next(
            s for s in multi_section_parsed.sections
            if s.section_type == SectionType.RISK_FACTORS
        )
        paragraphs = multi_section_parsed.get_paragraphs(risk_section.id)
        assert len(paragraphs) == 2

    def test_get_paragraphs_unknown_section_returns_empty(
        self, simple_parsed: ParsedDocument
    ) -> None:
        result = simple_parsed.get_paragraphs("nonexistent-section-id")
        assert result == ()

    def test_find_paragraph_by_id(self, simple_parsed: ParsedDocument) -> None:
        all_ps = simple_parsed.all_paragraphs()
        target = all_ps[0]
        found = simple_parsed.find_paragraph(target.id)
        assert found is not None
        assert found.id == target.id

    def test_find_paragraph_unknown_returns_none(
        self, simple_parsed: ParsedDocument
    ) -> None:
        result = simple_parsed.find_paragraph("nonexistent-paragraph-id")
        assert result is None

    def test_find_section_by_id(self, multi_section_parsed: ParsedDocument) -> None:
        first_section = multi_section_parsed.sections[0]
        found = multi_section_parsed.find_section(first_section.id)
        assert found is not None
        assert found.id == first_section.id

    def test_find_section_unknown_returns_none(
        self, simple_parsed: ParsedDocument
    ) -> None:
        result = simple_parsed.find_section("nonexistent-section-id")
        assert result is None

    def test_empty_document_has_zero_paragraphs(self, document: Document) -> None:
        builder = DocumentBuilder(document)
        parsed = builder.build()
        assert parsed.total_paragraphs == 0
        assert parsed.total_word_count == 0
        assert parsed.section_count == 0
        assert parsed.all_paragraphs() == ()


# ===========================================================================
# Group 4 — ParsedDocument invariants
# ===========================================================================


class TestParsedDocumentInvariants:
    """Cross-object consistency invariants are enforced."""

    def test_all_sections_share_document_id(
        self, multi_section_parsed: ParsedDocument
    ) -> None:
        doc_id = multi_section_parsed.document.id
        for section in multi_section_parsed.sections:
            assert section.document_id == doc_id

    def test_all_paragraphs_share_document_id(
        self, multi_section_parsed: ParsedDocument
    ) -> None:
        doc_id = multi_section_parsed.document.id
        for paragraph in multi_section_parsed.all_paragraphs():
            assert paragraph.document_id == doc_id

    def test_section_indices_are_sequential(
        self, multi_section_parsed: ParsedDocument
    ) -> None:
        indices = sorted(s.index for s in multi_section_parsed.sections)
        assert indices == list(range(len(indices)))

    def test_paragraph_indices_sequential_within_section(
        self, multi_section_parsed: ParsedDocument
    ) -> None:
        for section in multi_section_parsed.sections:
            paragraphs = multi_section_parsed.get_paragraphs(section.id)
            indices = [p.index for p in paragraphs]
            assert indices == list(range(len(indices)))

    def test_mismatched_document_id_in_section_raises(
        self, document: Document
    ) -> None:
        wrong_section = Section(
            id="sec-wrong",
            document_id="completely-different-doc-id",
            title="Mismatched",
            index=0,
            section_type=SectionType.OTHER,
        )
        from types import MappingProxyType
        with pytest.raises(DocumentIntegrityError, match="document_id"):
            ParsedDocument(
                document=document,
                sections=(wrong_section,),
                paragraphs_by_section=MappingProxyType({}),
            )

    def test_non_sequential_section_indices_raises(
        self, document: Document
    ) -> None:
        s1 = Section(
            id="s1", document_id=DOC_ID, title="A", index=0,
            section_type=SectionType.OTHER,
        )
        s2 = Section(
            id="s2", document_id=DOC_ID, title="B", index=5,  # gap!
            section_type=SectionType.OTHER,
        )
        from types import MappingProxyType
        with pytest.raises(DocumentIntegrityError, match="sequential"):
            ParsedDocument(
                document=document,
                sections=(s1, s2),
                paragraphs_by_section=MappingProxyType({}),
            )

    def test_unknown_section_key_in_paragraphs_raises(
        self, document: Document
    ) -> None:
        from types import MappingProxyType
        with pytest.raises(DocumentIntegrityError, match="unknown section_id"):
            ParsedDocument(
                document=document,
                sections=(),
                paragraphs_by_section=MappingProxyType(
                    {"ghost-section": ()}
                ),
            )


# ===========================================================================
# Group 5 — Builder error cases
# ===========================================================================


class TestBuilderErrors:
    """Builder raises correct exceptions for invalid operations."""

    def test_paragraph_to_unknown_section_raises(
        self, document: Document
    ) -> None:
        builder = DocumentBuilder(document)
        with pytest.raises(DocumentIntegrityError, match="Unknown section_id"):
            builder.add_paragraph(
                section_id="ghost-section",
                text="Test text.",
                paragraph_type=ParagraphType.NARRATIVE,
            )

    def test_duplicate_section_id_raises(self, document: Document) -> None:
        builder = DocumentBuilder(document)
        builder.add_section(
            title="First",
            section_type=SectionType.OTHER,
            section_id="dup-id",
        )
        with pytest.raises(DocumentIntegrityError, match="Duplicate section ID"):
            builder.add_section(
                title="Second",
                section_type=SectionType.OTHER,
                section_id="dup-id",
            )

    def test_duplicate_paragraph_id_raises(self, document: Document) -> None:
        builder = DocumentBuilder(document)
        s = builder.add_section(title="Test", section_type=SectionType.OTHER)
        builder.add_paragraph(
            section_id=s.id,
            text="First.",
            paragraph_type=ParagraphType.NARRATIVE,
            paragraph_id="dup-para-id",
        )
        with pytest.raises(DocumentIntegrityError, match="Duplicate paragraph ID"):
            builder.add_paragraph(
                section_id=s.id,
                text="Second.",
                paragraph_type=ParagraphType.NARRATIVE,
                paragraph_id="dup-para-id",
            )


# ===========================================================================
# Group 6 — Immutability
# ===========================================================================


class TestImmutability:
    """ParsedDocument and its contents are fully immutable."""

    def test_parsed_document_is_frozen(
        self, simple_parsed: ParsedDocument
    ) -> None:
        with pytest.raises(FrozenInstanceError):
            simple_parsed.document = None  # type: ignore[misc,assignment]

    def test_sections_tuple_is_immutable(
        self, simple_parsed: ParsedDocument
    ) -> None:
        # tuples are always immutable
        assert isinstance(simple_parsed.sections, tuple)

    def test_paragraphs_by_section_is_mapping_proxy(
        self, simple_parsed: ParsedDocument
    ) -> None:
        from types import MappingProxyType
        assert isinstance(simple_parsed.paragraphs_by_section, MappingProxyType)

    def test_paragraphs_by_section_rejects_writes(
        self, simple_parsed: ParsedDocument
    ) -> None:
        with pytest.raises(TypeError):
            simple_parsed.paragraphs_by_section["new-key"] = ()  # type: ignore[index]

    def test_section_objects_are_frozen(
        self, simple_parsed: ParsedDocument
    ) -> None:
        with pytest.raises(FrozenInstanceError):
            simple_parsed.sections[0].title = "Hacked"  # type: ignore[misc]

    def test_paragraph_objects_are_frozen(
        self, simple_parsed: ParsedDocument
    ) -> None:
        paragraphs = simple_parsed.all_paragraphs()
        with pytest.raises(FrozenInstanceError):
            paragraphs[0].text = "Hacked"  # type: ignore[misc]

    def test_new_id_generates_unique_values(self) -> None:
        ids = {_new_id() for _ in range(100)}
        assert len(ids) == 100
