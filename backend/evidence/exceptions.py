"""Evidence Layer exception hierarchy.

Justified by: docs/12-EVIDENCE-DOMAIN-MODEL.md.

Simple hierarchy rooted at EvidenceError.
All invariant violations raise a subclass of EvidenceError.

Never import from this module outside backend/evidence/.
The public interface is backend/evidence/__init__.py.
"""

from __future__ import annotations


class EvidenceError(Exception):
    """Base exception for all Evidence Layer violations."""


class InvalidEvidenceError(EvidenceError):
    """Raised when an Evidence object fails invariant validation.

    Examples:
        - confidence outside [0.0, 1.0]
        - superseded_by set without valid_until
        - reviewed_at set without reviewer_id
    """


class InvalidCandidateError(EvidenceError):
    """Raised when a RelationshipCandidate fails invariant validation.

    Examples:
        - source_id equals target_id
        - APPROVED status without reviewer fields
        - REJECTED status without rejection_reason
        - PENDING status with reviewer fields set
    """


class DocumentIntegrityError(EvidenceError):
    """Raised when document hierarchy integrity is violated.

    Examples:
        - char_end <= char_start in an Excerpt
        - char_end exceeds paragraph text length
        - duplicate index within a Section or Document
        - word_count inconsistent with text
    """
