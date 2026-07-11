"""Document assembly layer for the Evidence Layer.

Justified by: docs/12-EVIDENCE-DOMAIN-MODEL.md (Section 2 — object hierarchy),
              ROADMAP.md Milestone 15.

Milestone 13 froze the vocabulary: Document, Section, Paragraph, Excerpt.
Milestone 15 builds the assembly layer: the tools that let parsers construct
complete Document hierarchies efficiently and correctly.

Two components:

    ParsedDocument — the immutable aggregate containing a Document with all
    its Sections and Paragraphs in a single consistent unit. Enforces
    cross-object consistency invariants that individual frozen dataclasses
    cannot enforce alone.

    DocumentBuilder — fluent builder that constructs ParsedDocument objects.
    Auto-generates UUIDs and indices. Validates consistency at build() time.

Every parser in Milestone 16+ will produce a ParsedDocument.
Whether the source is SEC EDGAR today or ESMA tomorrow — the output is always
the same type. That is the universal language of the Evidence Layer.

    10-K → SECParser → DocumentBuilder → ParsedDocument
    BoE publication → FutureParser → DocumentBuilder → ParsedDocument

What this module never does:
    - Reads files from disk
    - Downloads documents
    - Parses PDF, HTML, or any file format
    - Creates Evidence objects
    - Imports from backend.atlas, backend.janus, backend.titan,
      backend.finance_dna, or backend.api
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from types import MappingProxyType

from backend.evidence.enums import ParagraphType, SectionType
from backend.evidence.exceptions import DocumentIntegrityError
from backend.evidence.models import Document, Paragraph, Section

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _new_id() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# ParsedDocument — the immutable aggregate
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ParsedDocument:
    """A fully assembled Document with all its Sections and Paragraphs.

    This is the standard output of all parsers (Milestone 16+) and the
    standard input to the Relationship Extractor (Milestone 17).

    ParsedDocument enforces the cross-object consistency invariants that the
    individual frozen dataclasses cannot enforce alone:

    Invariants:
        All Section.document_id == document.id
        All Paragraph.document_id == document.id
        All Paragraph.section_id is a registered section in this document
        Section indices are 0-based and sequential (no gaps, no duplicates)
        Paragraph indices within each section are 0-based and sequential
        paragraphs_by_section keys are a subset of section IDs

    Construction:
        Use DocumentBuilder — do not construct ParsedDocument directly.
        The builder auto-generates IDs and indices and calls build().

    Justified by: docs/12-EVIDENCE-DOMAIN-MODEL.md §2 (Document hierarchy).
    """

    document: Document
    sections: tuple[Section, ...]
    paragraphs_by_section: MappingProxyType[str, tuple[Paragraph, ...]]

    def __post_init__(self) -> None:
        self._validate_consistency()

    def _validate_consistency(self) -> None:
        """Enforce all cross-object invariants at construction time."""
        doc_id = self.document.id
        section_ids = {s.id for s in self.sections}

        # 1. All sections belong to this document
        for section in self.sections:
            if section.document_id != doc_id:
                raise DocumentIntegrityError(
                    f"Section {section.id!r} has document_id="
                    f"{section.document_id!r} but expected {doc_id!r}"
                )

        # 2. Section indices are 0-based and sequential
        if self.sections:
            actual = sorted(s.index for s in self.sections)
            expected = list(range(len(actual)))
            if actual != expected:
                raise DocumentIntegrityError(
                    f"Section indices must be sequential from 0, "
                    f"got {actual}"
                )

        # 3. Section IDs are unique
        all_section_ids = [s.id for s in self.sections]
        if len(all_section_ids) != len(set(all_section_ids)):
            raise DocumentIntegrityError("Duplicate section IDs detected")

        # 4. paragraphs_by_section keys are valid section IDs
        for key in self.paragraphs_by_section:
            if key not in section_ids:
                raise DocumentIntegrityError(
                    f"paragraphs_by_section contains unknown "
                    f"section_id {key!r}"
                )

        # 5. All paragraphs are internally consistent
        seen_paragraph_ids: set[str] = set()
        for section_id, paragraphs in self.paragraphs_by_section.items():
            # Paragraph indices are sequential within each section
            if paragraphs:
                actual_para = sorted(p.index for p in paragraphs)
                expected_para = list(range(len(actual_para)))
                if actual_para != expected_para:
                    raise DocumentIntegrityError(
                        f"Paragraph indices in section {section_id!r} must be "
                        f"sequential from 0, got {actual_para}"
                    )

            for paragraph in paragraphs:
                # Paragraph belongs to this document
                if paragraph.document_id != doc_id:
                    raise DocumentIntegrityError(
                        f"Paragraph {paragraph.id!r} has document_id="
                        f"{paragraph.document_id!r} but expected {doc_id!r}"
                    )
                # Paragraph belongs to the section it is stored under
                if paragraph.section_id != section_id:
                    raise DocumentIntegrityError(
                        f"Paragraph {paragraph.id!r} has section_id="
                        f"{paragraph.section_id!r} but is stored under "
                        f"{section_id!r}"
                    )
                # No duplicate paragraph IDs
                if paragraph.id in seen_paragraph_ids:
                    raise DocumentIntegrityError(
                        f"Duplicate paragraph ID {paragraph.id!r}"
                    )
                seen_paragraph_ids.add(paragraph.id)

    # --- Computed properties ------------------------------------------------

    @property
    def total_paragraphs(self) -> int:
        """Total number of paragraphs across all sections."""
        return sum(len(ps) for ps in self.paragraphs_by_section.values())

    @property
    def total_word_count(self) -> int:
        """Total word count across all paragraphs."""
        return sum(
            p.word_count
            for ps in self.paragraphs_by_section.values()
            for p in ps
        )

    @property
    def section_count(self) -> int:
        """Number of sections in this document."""
        return len(self.sections)

    # --- Traversal methods --------------------------------------------------

    def all_paragraphs(self) -> tuple[Paragraph, ...]:
        """All paragraphs in document reading order.

        Returns paragraphs sorted by section index, then by paragraph index
        within each section. This is the order they appear in the source.

        Returns:
            Tuple of Paragraph objects in reading order.
        """
        result: list[Paragraph] = []
        for section in sorted(self.sections, key=lambda s: s.index):
            paragraphs = self.paragraphs_by_section.get(section.id, ())
            result.extend(sorted(paragraphs, key=lambda p: p.index))
        return tuple(result)

    def get_paragraphs(self, section_id: str) -> tuple[Paragraph, ...]:
        """Return all paragraphs in a specific section, in index order.

        Args:
            section_id: The ID of the section to retrieve paragraphs for.

        Returns:
            Tuple of Paragraph objects in index order.
            Empty tuple if section_id is not found or has no paragraphs.
        """
        paragraphs = self.paragraphs_by_section.get(section_id, ())
        return tuple(sorted(paragraphs, key=lambda p: p.index))

    def find_paragraph(self, paragraph_id: str) -> Paragraph | None:
        """Find a specific paragraph by its ID.

        Args:
            paragraph_id: The paragraph to find.

        Returns:
            The Paragraph if found, None otherwise.
        """
        for paragraphs in self.paragraphs_by_section.values():
            for paragraph in paragraphs:
                if paragraph.id == paragraph_id:
                    return paragraph
        return None

    def find_section(self, section_id: str) -> Section | None:
        """Find a specific section by its ID.

        Args:
            section_id: The section to find.

        Returns:
            The Section if found, None otherwise.
        """
        for section in self.sections:
            if section.id == section_id:
                return section
        return None


# ---------------------------------------------------------------------------
# DocumentBuilder — the only correct way to construct a ParsedDocument
# ---------------------------------------------------------------------------


class DocumentBuilder:
    """Fluent builder for ParsedDocument.

    The standard interface for all parsers (Milestone 16+) to produce
    ParsedDocument objects. Auto-generates UUIDs and section/paragraph
    indices. Validates all consistency invariants at build() time.

    Responsibilities:
        - Track section order → auto-assign Section.index
        - Track paragraph order within sections → auto-assign Paragraph.index
        - Auto-generate UUIDs for sections and paragraphs
        - Auto-compute word_count from paragraph text
        - Validate document_id consistency
        - Detect duplicate IDs

    Does NOT:
        - Parse file formats
        - Download documents
        - Create Evidence or Excerpt objects
        - Communicate with external services

    Usage:
        builder = DocumentBuilder(document)

        s1 = builder.add_section(
            title="Item 1A. Risk Factors",
            section_type=SectionType.RISK_FACTORS,
        )
        builder.add_paragraph(
            section_id=s1.id,
            text="We are dependent on TSMC as a sole-source supplier...",
            paragraph_type=ParagraphType.NARRATIVE,
            page=27,
        )

        parsed = builder.build()
    """

    def __init__(self, document: Document) -> None:
        self._document = document
        self._sections: list[Section] = []
        self._paragraphs: dict[str, list[Paragraph]] = {}
        self._section_ids: set[str] = set()
        self._paragraph_ids: set[str] = set()

    @property
    def document(self) -> Document:
        """The Document being assembled."""
        return self._document

    @property
    def section_count(self) -> int:
        """Number of sections added so far."""
        return len(self._sections)

    @property
    def paragraph_count(self) -> int:
        """Total number of paragraphs added so far (across all sections)."""
        return sum(len(ps) for ps in self._paragraphs.values())

    def add_section(
        self,
        *,
        title: str,
        section_type: SectionType,
        section_id: str | None = None,
    ) -> Section:
        """Add a Section to this document.

        Sections are indexed in the order they are added (0, 1, 2, ...).

        Args:
            title: Section heading text. Must be non-empty.
            section_type: Structural type (RISK_FACTORS, MD_AND_A, etc.).
            section_id: Explicit ID, or None to auto-generate a UUID.
                        If provided, must not have been used before.

        Returns:
            The created, immutable Section object.

        Raises:
            DocumentIntegrityError: If section_id is already registered.
        """
        sid = section_id if section_id is not None else _new_id()

        if sid in self._section_ids:
            raise DocumentIntegrityError(
                f"Duplicate section ID: {sid!r}"
            )

        section = Section(
            id=sid,
            document_id=self._document.id,
            title=title,
            index=len(self._sections),
            section_type=section_type,
        )

        self._sections.append(section)
        self._section_ids.add(sid)
        self._paragraphs[sid] = []

        return section

    def add_paragraph(
        self,
        *,
        section_id: str,
        text: str,
        paragraph_type: ParagraphType,
        page: int | None = None,
        paragraph_id: str | None = None,
    ) -> Paragraph:
        """Add a Paragraph to an existing section.

        Paragraphs within a section are indexed in the order they are added.
        word_count is computed automatically from the text.

        Args:
            section_id: ID of the section to add this paragraph to.
                        Must have been created with add_section().
            text: Full verbatim text of the paragraph. Must be non-empty.
            paragraph_type: Structural type (NARRATIVE, TABLE, etc.).
            page: Page number in the source document, or None if unknown.
            paragraph_id: Explicit ID, or None to auto-generate a UUID.
                          If provided, must not have been used before.

        Returns:
            The created, immutable Paragraph object.

        Raises:
            DocumentIntegrityError: If section_id is unknown.
            DocumentIntegrityError: If paragraph_id is already registered.
        """
        if section_id not in self._section_ids:
            raise DocumentIntegrityError(
                f"Unknown section_id {section_id!r} — "
                f"call add_section() before add_paragraph()"
            )

        pid = paragraph_id if paragraph_id is not None else _new_id()

        if pid in self._paragraph_ids:
            raise DocumentIntegrityError(
                f"Duplicate paragraph ID: {pid!r}"
            )

        paragraph = Paragraph(
            id=pid,
            section_id=section_id,
            document_id=self._document.id,
            index=len(self._paragraphs[section_id]),
            text=text,
            paragraph_type=paragraph_type,
            word_count=len(text.split()),
            page=page,
        )

        self._paragraphs[section_id].append(paragraph)
        self._paragraph_ids.add(pid)

        return paragraph

    def build(self) -> ParsedDocument:
        """Assemble and return the complete ParsedDocument.

        Can be called multiple times — each call returns a new, independent
        ParsedDocument reflecting the current builder state. Adding sections
        or paragraphs after calling build() does not modify previous results.

        Returns:
            An immutable ParsedDocument with all sections and paragraphs.

        Raises:
            DocumentIntegrityError: If any consistency invariant is violated.
                This should not occur when using the builder correctly —
                the builder maintains invariants incrementally.
        """
        paragraphs_by_section: dict[str, tuple[Paragraph, ...]] = {
            section_id: tuple(paragraphs)
            for section_id, paragraphs in self._paragraphs.items()
        }

        return ParsedDocument(
            document=self._document,
            sections=tuple(self._sections),
            paragraphs_by_section=MappingProxyType(paragraphs_by_section),
        )
