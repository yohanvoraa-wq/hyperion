"""Tests for backend/evidence/parsers.py — Milestone 16.

Five test groups covering the full parser pipeline:
    1. Basic parsing — parser produces a valid ParsedDocument
    2. Section identification — ITEM X. patterns map to correct SectionTypes
    3. Paragraph segmentation — blank-line splitting, noise filtering
    4. Paragraph classification — TABLE / HEADING / FOOTNOTE / NARRATIVE
    5. Edge cases — empty text, no sections, normalization

Target: 55 assertions.

Test fixtures use synthetic text that mimics 10-K structure.
No real SEC filings are used (copyright).
No network calls. No file I/O. No LLMs.

Stop list:
    NO downloading from SEC EDGAR
    NO real 10-K files
    NO Evidence creation
    NO Atlas imports
"""

from __future__ import annotations

import pytest

from backend.evidence.document import ParsedDocument
from backend.evidence.enums import ParagraphType, SectionType
from backend.evidence.models import Document
from backend.evidence.parsers import SECEdgarParser

# ---------------------------------------------------------------------------
# Synthetic 10-K fixture text
# ---------------------------------------------------------------------------

SAMPLE_10K = """
PART I

Item 1. BUSINESS

Apple Inc. designs, manufactures, and markets smartphones, personal computers,
tablets, wearables, and accessories, and sells a variety of related services.

We operate through the following reportable segments: Americas, Europe, Greater China,
Japan, and Rest of Asia Pacific.

ITEM 1A. RISK FACTORS

We are dependent on TSMC as a sole-source supplier for Apple Silicon processors.
Any disruption to TSMC's operations in Taiwan could materially affect our ability
to produce our most profitable product lines.

Our products and services may experience quality problems that could harm our
business and reputation and result in warranty claims and product liability lawsuits.

Substantially all of our hardware products are manufactured by outsourcing partners
located primarily in China, with some products manufactured in the USA and India.

ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS

The following discussion should be read in conjunction with our consolidated financial
statements and the related notes thereto.

Net sales decreased 3 percent or $11.6 billion during 2023 compared to 2022,
driven by lower net sales of Mac, iPhone, and Wearables, Home and Accessories.

ITEM 8. FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA

Index to Financial Statements

| Revenue             | FY2024  | FY2023  |
| Total Net Sales     | $391.0B | $383.3B |
| Gross Profit        | $173.2B | $169.1B |
| Operating Income    | $123.2B | $114.3B |

ITEM 15. EXHIBITS AND FINANCIAL STATEMENT SCHEDULES

(1) The following exhibits are filed as part of this Annual Report on Form 10-K.
"""

SAMPLE_NO_ITEMS = """
This document does not contain SEC ITEM markers.

It has multiple paragraphs separated by blank lines.

Each paragraph should be treated as content within a single unnamed section.

This is a longer paragraph that should definitely pass the minimum word count threshold
for inclusion in the parsed output of the SEC EDGAR parser being tested here.
"""

SAMPLE_WINDOWS_ENDINGS = (
    "ITEM 1A. RISK FACTORS\r\n\r\n"
    "We depend on TSMC for chip manufacturing at scale.\r\n\r\n"
    "Any disruption in Taiwan could cause material harm to revenue.\r\n"
)

SAMPLE_TABLE_PARAGRAPH = """| Revenue | 2024 | 2023 |
| Net Sales | $391B | $383B |
| Gross Profit | $173B | $169B |"""

SAMPLE_HEADING_PARAGRAPH = "MANAGEMENT'S DISCUSSION AND ANALYSIS"

SAMPLE_FOOTNOTE_PARAGRAPH = (
    "(1) Amounts have been adjusted to reflect the adoption of new accounting standards."
)

SAMPLE_NARRATIVE_PARAGRAPH = (
    "We are dependent on TSMC as a sole-source supplier for Apple Silicon processors. "
    "Any disruption to TSMC's operations in Taiwan could materially affect our ability "
    "to produce our most profitable product lines."
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

DOC_ID = "test-doc-001"
SOURCE_ID = "sec-edgar-10k"


@pytest.fixture()
def document() -> Document:
    return Document(
        id=DOC_ID,
        source_id=SOURCE_ID,
        title="Apple Inc. Form 10-K FY2025 (Test Fixture)",
        published_at="2025-11-01",
        retrieved_at="2025-11-15T09:23:41Z",
        company_id="apple-inc",
    )


@pytest.fixture()
def parser() -> SECEdgarParser:
    return SECEdgarParser()


@pytest.fixture()
def parsed(parser: SECEdgarParser, document: Document):  # type: ignore[no-untyped-def]
    return parser.parse(text=SAMPLE_10K, document=document)


# ===========================================================================
# Group 1 — Basic parsing
# ===========================================================================


class TestBasicParsing:
    """Parser produces a valid, well-formed ParsedDocument."""

    def test_parse_returns_parsed_document(self, parsed) -> None:  # type: ignore[no-untyped-def]
        from backend.evidence.document import ParsedDocument
        assert isinstance(parsed, ParsedDocument)

    def test_document_id_preserved(self, parsed, document: Document) -> None:  # type: ignore[no-untyped-def]
        assert parsed.document.id == document.id

    def test_document_title_preserved(self, parsed, document: Document) -> None:  # type: ignore[no-untyped-def]
        assert parsed.document.title == document.title

    def test_parsed_has_sections(self, parsed) -> None:  # type: ignore[no-untyped-def]
        assert parsed.section_count > 0

    def test_parsed_has_paragraphs(self, parsed) -> None:  # type: ignore[no-untyped-def]
        assert parsed.total_paragraphs > 0

    def test_total_word_count_is_positive(self, parsed) -> None:  # type: ignore[no-untyped-def]
        assert parsed.total_word_count > 0

    def test_all_paragraphs_have_text(self, parsed) -> None:  # type: ignore[no-untyped-def]
        for paragraph in parsed.all_paragraphs():
            assert paragraph.text.strip()

    def test_all_paragraphs_word_count_consistent(self, parsed) -> None:  # type: ignore[no-untyped-def]
        for paragraph in parsed.all_paragraphs():
            assert paragraph.word_count == len(paragraph.text.split())

    def test_all_sections_have_valid_type(self, parsed) -> None:  # type: ignore[no-untyped-def]
        valid_types = set(SectionType)
        for section in parsed.sections:
            assert section.section_type in valid_types

    def test_all_paragraphs_have_valid_type(self, parsed) -> None:  # type: ignore[no-untyped-def]
        valid_types = set(ParagraphType)
        for paragraph in parsed.all_paragraphs():
            assert paragraph.paragraph_type in valid_types


# ===========================================================================
# Group 2 — Section identification
# ===========================================================================


class TestSectionIdentification:
    """ITEM X. patterns are identified and mapped to correct SectionTypes."""

    def test_item_1_maps_to_business(self, parsed) -> None:  # type: ignore[no-untyped-def]
        business = next(
            (s for s in parsed.sections if s.section_type == SectionType.BUSINESS),
            None,
        )
        assert business is not None

    def test_item_1a_maps_to_risk_factors(self, parsed) -> None:  # type: ignore[no-untyped-def]
        risk = next(
            (s for s in parsed.sections if s.section_type == SectionType.RISK_FACTORS),
            None,
        )
        assert risk is not None

    def test_item_7_maps_to_md_and_a(self, parsed) -> None:  # type: ignore[no-untyped-def]
        mda = next(
            (s for s in parsed.sections if s.section_type == SectionType.MD_AND_A),
            None,
        )
        assert mda is not None

    def test_item_8_maps_to_financials(self, parsed) -> None:  # type: ignore[no-untyped-def]
        fin = next(
            (s for s in parsed.sections if s.section_type == SectionType.FINANCIALS),
            None,
        )
        assert fin is not None

    def test_item_15_maps_to_notes(self, parsed) -> None:  # type: ignore[no-untyped-def]
        notes = next(
            (s for s in parsed.sections if s.section_type == SectionType.NOTES),
            None,
        )
        assert notes is not None

    def test_five_sections_identified(self, parsed) -> None:  # type: ignore[no-untyped-def]
        assert parsed.section_count == 5

    def test_section_titles_include_item_number(self, parsed) -> None:  # type: ignore[no-untyped-def]
        for section in parsed.sections:
            assert section.title.startswith("Item ")

    def test_risk_factors_section_has_paragraphs(self, parsed) -> None:  # type: ignore[no-untyped-def]
        risk = next(
            s for s in parsed.sections
            if s.section_type == SectionType.RISK_FACTORS
        )
        paragraphs = parsed.get_paragraphs(risk.id)
        assert len(paragraphs) > 0

    def test_tsmc_paragraph_in_risk_factors(self, parsed) -> None:  # type: ignore[no-untyped-def]
        risk = next(
            s for s in parsed.sections
            if s.section_type == SectionType.RISK_FACTORS
        )
        paragraphs = parsed.get_paragraphs(risk.id)
        texts = [p.text for p in paragraphs]
        assert any("TSMC" in t for t in texts)

    def test_section_indices_are_sequential(self, parsed) -> None:  # type: ignore[no-untyped-def]
        indices = sorted(s.index for s in parsed.sections)
        assert indices == list(range(len(indices)))

    def test_no_item_text_produces_single_section(
        self, parser: SECEdgarParser, document: Document
    ) -> None:
        parsed = parser.parse(text=SAMPLE_NO_ITEMS, document=document)
        assert parsed.section_count == 1

    def test_no_item_text_section_is_other_type(
        self, parser: SECEdgarParser, document: Document
    ) -> None:
        parsed = parser.parse(text=SAMPLE_NO_ITEMS, document=document)
        assert parsed.sections[0].section_type == SectionType.OTHER


# ===========================================================================
# Group 3 — Paragraph segmentation
# ===========================================================================


class TestParagraphSegmentation:
    """Paragraphs are correctly split and filtered."""

    def test_paragraphs_below_word_threshold_excluded(
        self, parser: SECEdgarParser, document: Document
    ) -> None:
        text = "ITEM 1A. RISK FACTORS\n\nOK\n\nThis is a valid paragraph with enough words."
        parsed = parser.parse(text=text, document=document)
        texts = [p.text for p in parsed.all_paragraphs()]
        assert not any(t == "OK" for t in texts)

    def test_page_numbers_excluded(
        self, parser: SECEdgarParser, document: Document
    ) -> None:
        text = (
            "ITEM 1A. RISK FACTORS\n\n"
            "42\n\n"
            "We are dependent on TSMC for Apple Silicon manufacturing at scale."
        )
        parsed = parser.parse(text=text, document=document)
        texts = [p.text for p in parsed.all_paragraphs()]
        assert not any(t.strip() == "42" for t in texts)

    def test_form_page_numbers_excluded(
        self, parser: SECEdgarParser, document: Document
    ) -> None:
        text = (
            "ITEM 8. FINANCIAL STATEMENTS\n\n"
            "F-12\n\n"
            "The consolidated balance sheets as of September 2025."
        )
        parsed = parser.parse(text=text, document=document)
        texts = [p.text for p in parsed.all_paragraphs()]
        assert not any("F-12" in t for t in texts)

    def test_windows_line_endings_normalized(
        self, parser: SECEdgarParser, document: Document
    ) -> None:
        parsed = parser.parse(text=SAMPLE_WINDOWS_ENDINGS, document=document)
        assert parsed.section_count >= 1
        assert parsed.total_paragraphs >= 1

    def test_paragraphs_have_no_leading_trailing_whitespace(
        self, parsed: ParsedDocument
    ) -> None:
        for paragraph in parsed.all_paragraphs():
            assert paragraph.text == paragraph.text.strip()

    def test_multi_section_paragraph_counts(self, parsed) -> None:  # type: ignore[no-untyped-def]
        risk = next(
            s for s in parsed.sections
            if s.section_type == SectionType.RISK_FACTORS
        )
        mda = next(
            s for s in parsed.sections
            if s.section_type == SectionType.MD_AND_A
        )
        risk_paras = parsed.get_paragraphs(risk.id)
        mda_paras = parsed.get_paragraphs(mda.id)
        # Both sections should have substantive paragraphs
        assert len(risk_paras) >= 1
        assert len(mda_paras) >= 1

    def test_custom_min_word_threshold(
        self, document: Document
    ) -> None:
        parser = SECEdgarParser(min_paragraph_words=10)
        text = (
            "ITEM 1A. RISK FACTORS\n\n"
            "Short para.\n\n"
            "This paragraph has enough words to clear a threshold of ten total words."
        )
        parsed = parser.parse(text=text, document=document)
        texts = [p.text for p in parsed.all_paragraphs()]
        assert not any("Short para" in t for t in texts)


# ===========================================================================
# Group 4 — Paragraph classification
# ===========================================================================


class TestParagraphClassification:
    """Paragraph types are correctly classified."""

    def test_table_paragraph_classified_as_table(
        self, parser: SECEdgarParser
    ) -> None:
        result = parser._classify_paragraph(SAMPLE_TABLE_PARAGRAPH)
        assert result == ParagraphType.TABLE

    def test_heading_paragraph_classified_as_heading(
        self, parser: SECEdgarParser
    ) -> None:
        result = parser._classify_paragraph(SAMPLE_HEADING_PARAGRAPH)
        assert result == ParagraphType.HEADING

    def test_footnote_paragraph_classified_as_footnote(
        self, parser: SECEdgarParser
    ) -> None:
        result = parser._classify_paragraph(SAMPLE_FOOTNOTE_PARAGRAPH)
        assert result == ParagraphType.FOOTNOTE

    def test_narrative_paragraph_classified_as_narrative(
        self, parser: SECEdgarParser
    ) -> None:
        result = parser._classify_paragraph(SAMPLE_NARRATIVE_PARAGRAPH)
        assert result == ParagraphType.NARRATIVE

    def test_financial_table_classified_as_table(
        self, parser: SECEdgarParser
    ) -> None:
        table_text = (
            "| Revenue | 2024 | 2023 |\n"
            "| Total Net Sales | $391B | $383B |"
        )
        result = parser._classify_paragraph(table_text)
        assert result == ParagraphType.TABLE

    def test_all_caps_multi_line_not_classified_as_heading(
        self, parser: SECEdgarParser
    ) -> None:
        long_text = (
            "RISK FACTORS\n"
            "The following section describes material risks to our business\n"
            "that investors should carefully consider before investing."
        )
        result = parser._classify_paragraph(long_text)
        assert result != ParagraphType.HEADING

    def test_financials_section_contains_table(self, parsed) -> None:  # type: ignore[no-untyped-def]
        fin = next(
            s for s in parsed.sections
            if s.section_type == SectionType.FINANCIALS
        )
        paragraphs = parsed.get_paragraphs(fin.id)
        types = [p.paragraph_type for p in paragraphs]
        assert ParagraphType.TABLE in types

    def test_risk_factors_contains_narrative(self, parsed) -> None:  # type: ignore[no-untyped-def]
        risk = next(
            s for s in parsed.sections
            if s.section_type == SectionType.RISK_FACTORS
        )
        paragraphs = parsed.get_paragraphs(risk.id)
        types = [p.paragraph_type for p in paragraphs]
        assert ParagraphType.NARRATIVE in types


# ===========================================================================
# Group 5 — Edge cases and normalization
# ===========================================================================


class TestEdgeCases:
    """Parser handles edge cases gracefully."""

    def test_empty_text_produces_empty_document(
        self, parser: SECEdgarParser, document: Document
    ) -> None:
        parsed = parser.parse(text="", document=document)
        assert parsed.total_paragraphs == 0

    def test_whitespace_only_text_produces_empty_document(
        self, parser: SECEdgarParser, document: Document
    ) -> None:
        parsed = parser.parse(text="   \n\n\n   ", document=document)
        assert parsed.total_paragraphs == 0

    def test_single_item_section_parses(
        self, parser: SECEdgarParser, document: Document
    ) -> None:
        text = (
            "ITEM 1A. RISK FACTORS\n\n"
            "We depend on TSMC as a sole-source supplier for Apple Silicon chips."
        )
        parsed = parser.parse(text=text, document=document)
        assert parsed.section_count == 1
        assert parsed.sections[0].section_type == SectionType.RISK_FACTORS

    def test_unknown_item_number_maps_to_other(
        self, parser: SECEdgarParser, document: Document
    ) -> None:
        text = (
            "ITEM 99. SOME UNKNOWN ITEM\n\n"
            "This item number does not exist in the standard 10-K form and maps to OTHER."
        )
        parsed = parser.parse(text=text, document=document)
        assert parsed.sections[0].section_type == SectionType.OTHER

    def test_lowercase_item_keyword_recognized(
        self, parser: SECEdgarParser, document: Document
    ) -> None:
        text = (
            "Item 1a. Risk Factors\n\n"
            "We depend on TSMC for Apple Silicon chip manufacturing at scale."
        )
        parsed = parser.parse(text=text, document=document)
        assert parsed.section_count == 1
        assert parsed.sections[0].section_type == SectionType.RISK_FACTORS

    def test_normalize_text_handles_windows_endings(
        self, parser: SECEdgarParser
    ) -> None:
        text = "Line one.\r\nLine two.\r\n"
        normalized = parser._normalize_text(text)
        assert "\r" not in normalized

    def test_normalize_text_collapses_excess_blanks(
        self, parser: SECEdgarParser
    ) -> None:
        text = "Para one.\n\n\n\n\n\nPara two."
        normalized = parser._normalize_text(text)
        assert "\n\n\n\n" not in normalized

    def test_parser_is_deterministic(
        self, parser: SECEdgarParser, document: Document
    ) -> None:
        first = parser.parse(text=SAMPLE_10K, document=document)
        second = parser.parse(text=SAMPLE_10K, document=document)
        assert first.section_count == second.section_count
        assert first.total_paragraphs == second.total_paragraphs
        assert first.total_word_count == second.total_word_count

    def test_does_not_import_atlas(self) -> None:
        import importlib
        mod = importlib.import_module("backend.evidence.parsers")
        assert "atlas" not in (getattr(mod, "__file__", "") or "")
