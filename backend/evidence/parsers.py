"""SEC EDGAR 10-K parser for the Evidence Layer.

Justified by: docs/11-EVIDENCE-ARCHITECTURE.md (Phase B — Knowledge Acquisition),
              ROADMAP.md Milestone 16.

Milestone 16 builds the first parser in the Evidence Layer.
One source. Done well.

Architecture:
    raw 10-K text
           ↓
    _normalize_text()        — line endings, encoding, whitespace
           ↓
    _identify_sections()     — ITEM X. pattern matching → SectionType
           ↓
    _segment_paragraphs()    — blank-line splitting, noise filtering
           ↓
    _classify_paragraph()    — TABLE / HEADING / FOOTNOTE / NARRATIVE
           ↓
    ParsedDocument

The parser operates on text that has ALREADY been retrieved.
Downloading from SEC EDGAR is a separate future concern (Milestone 16.5+).
This separation means the parser is fully testable without network access.

Limitations (V0.3 — documented, not hidden):
    - Plain-text format only. HTML parsing is V0.4 work.
    - Section detection by ITEM X. regex. Unusual formatting may be missed.
    - Paragraph type classification is heuristic, not structural.
    - No table content parsing — tables are classified but not structured.
    - Page numbers and headers filtered by simple patterns.

What this module never does:
    - Makes network requests
    - Reads files from disk
    - Creates Evidence or Excerpt objects
    - Writes to Atlas
    - Calls LLMs
    - Imports from backend.atlas, backend.janus, backend.titan,
      backend.finance_dna, or backend.api
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from backend.evidence.document import DocumentBuilder, ParsedDocument
from backend.evidence.enums import ParagraphType, SectionType
from backend.evidence.models import Document

# ---------------------------------------------------------------------------
# SEC ITEM number → SectionType mapping
# ---------------------------------------------------------------------------

_ITEM_SECTION_MAP: dict[str, SectionType] = {
    "1": SectionType.BUSINESS,
    "1A": SectionType.RISK_FACTORS,
    "1B": SectionType.OTHER,   # Unresolved Staff Comments
    "2": SectionType.OTHER,    # Properties
    "3": SectionType.OTHER,    # Legal Proceedings
    "4": SectionType.OTHER,    # Mine Safety Disclosures
    "5": SectionType.OTHER,    # Market for Common Equity
    "6": SectionType.OTHER,    # Selected Financial Data (deprecated)
    "7": SectionType.MD_AND_A,
    "7A": SectionType.OTHER,   # Quantitative Disclosures about Market Risk
    "8": SectionType.FINANCIALS,
    "9": SectionType.OTHER,    # Changes in / Disagreements with Accountants
    "9A": SectionType.OTHER,   # Controls and Procedures
    "9B": SectionType.OTHER,   # Other Information
    "9C": SectionType.OTHER,   # Disclosure Regarding Foreign Jurisdictions
    "10": SectionType.OTHER,   # Directors and Executive Officers
    "11": SectionType.OTHER,   # Executive Compensation
    "12": SectionType.OTHER,   # Security Ownership
    "13": SectionType.OTHER,   # Relationships and Transactions
    "14": SectionType.OTHER,   # Accounting Fees
    "15": SectionType.NOTES,   # Exhibits and Financial Statement Schedules
    "16": SectionType.OTHER,   # Form 10-K Summary
}

# ---------------------------------------------------------------------------
# Compiled patterns
# ---------------------------------------------------------------------------

# ITEM X. header — case-insensitive, handles "ITEM 1A.", "Item 1.", etc.
_ITEM_PATTERN: re.Pattern[str] = re.compile(
    r"(?:^|\n)\s*(?:ITEM|Item)\s+(\d+[A-Za-z]?)\s*[.\-:]\s*([^\n]*)",
    re.MULTILINE,
)

# Paragraph noise: page numbers, form header artifacts
_PAGE_NUMBER_PATTERN: re.Pattern[str] = re.compile(r"^\s*(?:F-\d+|\d+)\s*$")

# Table indicators: multiple pipe chars, aligned dashes
_TABLE_PATTERN: re.Pattern[str] = re.compile(
    r"[\|]{1,}.*[\|]{1,}|^\s*[-]{3,}\s*[-]{3,}",
    re.MULTILINE,
)

# Heading: all-caps short line (10+ chars), typically section sub-heading
_HEADING_PATTERN: re.Pattern[str] = re.compile(
    r"^[A-Z][A-Z\s,\-\.&\(\)\'\"]{9,}$"
)

# Footnote: starts with a numeric or letter reference
_FOOTNOTE_PATTERN: re.Pattern[str] = re.compile(
    r"^\s*(?:\(\d+\)|\[\d+\]|\d+\.|[a-z]\))\s+[A-Za-z]"
)

# Excess blank lines
_EXCESS_BLANKS: re.Pattern[str] = re.compile(r"\n{4,}")


# ---------------------------------------------------------------------------
# Internal data class
# ---------------------------------------------------------------------------


@dataclass
class _SectionBoundary:
    """Internal representation of a discovered section boundary.

    Mutable — end is set after finding the next section's start.
    Not exported.
    """

    title: str
    section_type: SectionType
    start: int
    end: int = field(default=0)


# ---------------------------------------------------------------------------
# SECEdgarParser
# ---------------------------------------------------------------------------


class SECEdgarParser:
    """Parses SEC EDGAR 10-K plain-text filings into ParsedDocument objects.

    This parser accepts raw text that has already been retrieved from EDGAR.
    It does not download, cache, or store documents.

    Usage:
        parser = SECEdgarParser()

        document = Document(
            id="...",
            source_id="sec-edgar-10k",
            title="Apple Inc. Form 10-K FY2025",
            published_at="2025-11-01",
            retrieved_at="2025-11-15T09:00:00Z",
            company_id="apple-inc",
        )

        parsed = parser.parse(text=raw_text, document=document)

        # Now use parsed.all_paragraphs() to find evidence candidates.

    Justified by: ROADMAP.md Milestone 16.
    """

    def __init__(self, min_paragraph_words: int = 3) -> None:
        """Initialise the parser.

        Args:
            min_paragraph_words: Minimum number of words for a paragraph
                to be retained. Shorter paragraphs are filtered as noise.
                Default is 3.
        """
        self._min_paragraph_words = min_paragraph_words

    def parse(
        self,
        *,
        text: str,
        document: Document,
    ) -> ParsedDocument:
        """Parse raw 10-K text into a structured ParsedDocument.

        Args:
            text: Raw text of the 10-K filing. May contain Windows line
                  endings, encoding artifacts, or blank-line-separated sections.
            document: The Document metadata object. Must already be created —
                      the parser populates sections and paragraphs, not metadata.

        Returns:
            A ParsedDocument containing structured sections and paragraphs
            in document reading order.
        """
        normalized = self._normalize_text(text)
        boundaries = self._identify_sections(normalized)
        builder = DocumentBuilder(document)

        if not boundaries:
            # No ITEM X. markers found — treat entire text as one section.
            section = builder.add_section(
                title="Document Content",
                section_type=SectionType.OTHER,
            )
            for para_text in self._segment_paragraphs(normalized):
                builder.add_paragraph(
                    section_id=section.id,
                    text=para_text,
                    paragraph_type=self._classify_paragraph(para_text),
                )
        else:
            for boundary in boundaries:
                section = builder.add_section(
                    title=boundary.title,
                    section_type=boundary.section_type,
                )
                section_text = normalized[boundary.start : boundary.end]
                for para_text in self._segment_paragraphs(section_text):
                    builder.add_paragraph(
                        section_id=section.id,
                        text=para_text,
                        paragraph_type=self._classify_paragraph(para_text),
                    )

        return builder.build()

    # --- Internal methods ---------------------------------------------------

    def _normalize_text(self, text: str) -> str:
        """Normalise line endings, encoding artifacts, and excessive whitespace.

        Steps:
            1. Windows (\\r\\n) and old Mac (\\r) line endings → Unix (\\n)
            2. Collapse runs of 4+ blank lines to 3 (preserve paragraph breaks)
            3. Strip leading/trailing whitespace

        Args:
            text: Raw input text.

        Returns:
            Normalised text string.
        """
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = _EXCESS_BLANKS.sub("\n\n\n", text)
        return text.strip()

    def _identify_sections(self, text: str) -> list[_SectionBoundary]:
        """Find section boundaries using ITEM X. patterns.

        Matches "ITEM 1.", "Item 1A.", "ITEM 7 -" and similar variants.
        Maps item numbers to SectionType using _ITEM_SECTION_MAP.
        Unknown item numbers default to OTHER.

        Args:
            text: Normalised document text.

        Returns:
            List of _SectionBoundary objects in document order.
            Empty list if no ITEM patterns are found.
        """
        matches = list(_ITEM_PATTERN.finditer(text))
        if not matches:
            return []

        boundaries: list[_SectionBoundary] = []

        for i, match in enumerate(matches):
            item_num = match.group(1).upper()
            title_suffix = match.group(2).strip()

            section_type = _ITEM_SECTION_MAP.get(item_num, SectionType.OTHER)

            title = f"Item {item_num}"
            if title_suffix:
                # Clean up title suffix — remove trailing dots, normalise case
                clean_suffix = title_suffix.rstrip(".").strip()
                if clean_suffix:
                    title = f"{title}. {clean_suffix}"

            # Content starts immediately after the header line ends
            content_start = match.end()

            # Content ends where the next ITEM header starts
            content_end = (
                matches[i + 1].start() if i + 1 < len(matches) else len(text)
            )

            boundaries.append(
                _SectionBoundary(
                    title=title,
                    section_type=section_type,
                    start=content_start,
                    end=content_end,
                )
            )

        return boundaries

    def _segment_paragraphs(self, text: str) -> list[str]:
        """Split a section's text into individual paragraphs.

        Splits on two or more consecutive blank lines, then filters:
            - Empty strings after stripping
            - Lines that look like page numbers (F-1, 42, etc.)
            - Paragraphs below the minimum word count threshold

        Args:
            text: Section text to segment.

        Returns:
            List of cleaned paragraph strings in document order.
        """
        paragraphs: list[str] = []

        for raw in re.split(r"\n\n+", text):
            cleaned = raw.strip()

            if not cleaned:
                continue

            # Filter page number artifacts
            if _PAGE_NUMBER_PATTERN.match(cleaned):
                continue

            # Filter noise below word threshold
            if len(cleaned.split()) < self._min_paragraph_words:
                continue

            # Normalise internal whitespace — collapse single newlines in prose
            # but preserve table structure (lines with pipes)
            if "|" not in cleaned:
                cleaned = re.sub(r"(?<!\n)\n(?!\n)", " ", cleaned)
                cleaned = re.sub(r" {2,}", " ", cleaned)

            paragraphs.append(cleaned)

        return paragraphs

    def _classify_paragraph(self, text: str) -> ParagraphType:
        """Classify a paragraph type using heuristics.

        Classification rules (in priority order):
            1. TABLE: contains pipe characters suggesting column structure
            2. HEADING: short all-caps line (likely a sub-section heading)
            3. FOOTNOTE: starts with a numbered or lettered reference marker
            4. NARRATIVE: everything else (default)

        Args:
            text: The cleaned paragraph text.

        Returns:
            The ParagraphType enum value.
        """
        # TABLE: pipe characters or aligned dashes in tabular structure
        if _TABLE_PATTERN.search(text):
            return ParagraphType.TABLE

        # HEADING: first line is all-caps and the paragraph is short (≤ 2 lines)
        first_line = text.split("\n")[0].strip()
        if (
            len(first_line) >= 10
            and _HEADING_PATTERN.match(first_line)
            and len(text.split("\n")) <= 2  # noqa: PLR2004
        ):
            return ParagraphType.HEADING

        # FOOTNOTE: starts with a numeric or letter reference
        if _FOOTNOTE_PATTERN.match(text):
            return ParagraphType.FOOTNOTE

        return ParagraphType.NARRATIVE
