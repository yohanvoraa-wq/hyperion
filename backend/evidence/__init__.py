"""Evidence Layer — public interface.

Justified by: docs/12-EVIDENCE-DOMAIN-MODEL.md.

Every public type in the Evidence Layer is exported here.
No internal implementation details are exposed.
"""

from __future__ import annotations

from backend.evidence.document import DocumentBuilder, ParsedDocument
from backend.evidence.enums import (
    TERMINAL_STATUSES,
    VALID_TRANSITIONS,
    CandidateStatus,
    DocumentType,
    EvidenceType,
    ParagraphType,
    SectionType,
    SourceTier,
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
    "DocumentBuilder",
    "DocumentIntegrityError",
    "DocumentType",
    "Document",
    "EvidenceBundle",
    "EvidenceError",
    "EvidenceType",
    "Evidence",
    "Excerpt",
    "InvalidCandidateError",
    "InvalidEvidenceError",
    "Paragraph",
    "ParagraphType",
    "ParsedDocument",
    "RelationshipCandidate",
    "SOURCE_REGISTRY",
    "SectionType",
    "Section",
    "SourceTier",
    "Source",
    "TERMINAL_STATUSES",
    "VALID_TRANSITIONS",
    "all_sources",
    "find_source",
    "is_trusted",
    "supported_document_types",
    "trust_level",
]
