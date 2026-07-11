"""Evidence Layer — public interface.

Justified by: docs/12-EVIDENCE-DOMAIN-MODEL.md.

Only public types are exported here. Internal implementation details
(validation logic, helpers) are not part of the public API.

This module has exactly one responsibility: defining the vocabulary
for the Evidence Layer.

What this module never does:
    - Reads files from disk
    - Makes network requests
    - Writes to Atlas
    - Imports from backend.atlas, backend.janus, backend.titan,
      backend.finance_dna, or backend.api
    - Contains business logic about relationship meaning
    - Makes decisions about what is true or false
"""

from __future__ import annotations

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

__all__ = [
    # Enums
    "CandidateStatus",
    "DocumentType",
    "EvidenceType",
    "ParagraphType",
    "SectionType",
    "SourceTier",
    # Lifecycle helpers
    "TERMINAL_STATUSES",
    "VALID_TRANSITIONS",
    # Exceptions
    "DocumentIntegrityError",
    "EvidenceError",
    "InvalidCandidateError",
    "InvalidEvidenceError",
    # Models
    "Document",
    "Evidence",
    "EvidenceBundle",
    "Excerpt",
    "Paragraph",
    "RelationshipCandidate",
    "Section",
    "Source",
]
from backend.evidence.registry import (
    SOURCE_REGISTRY,
    all_sources,
    find_source,
    is_trusted,
    supported_document_types,
    trust_level,
)

__all__ += [
    "SOURCE_REGISTRY",
    "all_sources",
    "find_source",
    "is_trusted",
    "supported_document_types",
    "trust_level",
]
from backend.evidence.document import (
    DocumentBuilder,
    ParsedDocument,
)

__all__ += [
    "DocumentBuilder",
    "ParsedDocument",
]
