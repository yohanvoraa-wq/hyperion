"""Evidence Layer — public interface."""

from __future__ import annotations

from backend.evidence.document import DocumentBuilder, ParsedDocument
from backend.evidence.enums import (
    CandidateStatus,
    DocumentType,
    EvidenceType,
    ParagraphType,
    SectionType,
    SourceTier,
    TERMINAL_STATUSES,
    VALID_TRANSITIONS,
)
from backend.evidence.exceptions import (
    DocumentIntegrityError,
    EvidenceError,
    InvalidCandidateError,
    InvalidEvidenceError,
)
from backend.evidence.models import (
    Document,
    Evidence,
    EvidenceBundle,
    Excerpt,
    Paragraph,
    RelationshipCandidate,
    Section,
    Source,
)
from backend.evidence.registry import (
    SOURCE_REGISTRY,
    all_sources,
    find_source,
    is_trusted,
    supported_document_types,
    trust_level,
)

__all__ = [
    "CandidateStatus",
    "DocumentType",
    "EvidenceType",
    "ParagraphType",
    "SectionType",
    "SourceTier",
    "TERMINAL_STATUSES",
    "VALID_TRANSITIONS",
    "DocumentIntegrityError",
    "EvidenceError",
    "InvalidCandidateError",
    "InvalidEvidenceError",
    "Document",
    "Evidence",
    "EvidenceBundle",
    "Excerpt",
    "Paragraph",
    "RelationshipCandidate",
    "Section",
    "Source",
    "DocumentBuilder",
    "ParsedDocument",
    "SOURCE_REGISTRY",
    "all_sources",
    "find_source",
    "is_trusted",
    "supported_document_types",
    "trust_level",
]
