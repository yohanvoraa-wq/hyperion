"""Source Registry — Hyperion's epistemology layer.

Justified by: docs/11-EVIDENCE-ARCHITECTURE.md (Trusted Source Hierarchy),
              docs/12-EVIDENCE-DOMAIN-MODEL.md §2 (Source).

This module answers one question before any Evidence is created:

    When Hyperion encounters a document, should it trust its source?

Without this registry, all sources would be treated equally.
A Random finance blog and an SEC 10-K both say Apple depends on TSMC.
They are not equal. This registry encodes why.

Architecture:
    trusted_sources.csv → _load_registry() → SOURCE_REGISTRY (read-only)

The registry is loaded once at import time. It is immutable after loading.
No source can be added or removed at runtime.

Public functions:
    find_source()             — lookup by ID
    trust_level()             — SourceTier for a source
    is_trusted()              — boolean membership check
    all_sources()             — all registered sources (optionally filtered)
    supported_document_types() — document types covered by registered sources

What this module never does:
    - Downloads filings
    - Connects to SEC or any external API
    - Creates Evidence objects
    - Parses documents
    - Imports from backend.atlas, backend.janus, backend.titan,
      backend.finance_dna, or backend.api
"""

from __future__ import annotations

import csv
from pathlib import Path
from types import MappingProxyType

from backend.evidence.enums import DocumentType, SourceTier
from backend.evidence.models import Source

# ---------------------------------------------------------------------------
# CSV path — resolved relative to this file's location.
# From backend/evidence/registry.py:
#   .parent      = backend/evidence/
#   .parent      = backend/
#   .parent      = project root
#   / datasets/sources/trusted_sources.csv
# ---------------------------------------------------------------------------

_SOURCES_CSV: Path = (
    Path(__file__).resolve().parent.parent.parent
    / "datasets"
    / "sources"
    / "trusted_sources.csv"
)


def _load_registry() -> dict[str, Source]:
    """Load Source definitions from trusted_sources.csv.

    Raises:
        FileNotFoundError: If trusted_sources.csv does not exist.
        ValueError: If any source ID is duplicated in the CSV.
        ValueError: If any row contains an invalid tier or document_type.

    Returns:
        Dict mapping source ID to Source, ordered by CSV row.
    """
    sources: dict[str, Source] = {}

    with open(_SOURCES_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            source_id = row["id"].strip()

            if source_id in sources:
                raise ValueError(
                    f"Duplicate source ID in trusted_sources.csv: {source_id!r}"
                )

            source = Source(
                id=source_id,
                name=row["name"].strip(),
                tier=SourceTier(int(row["tier"].strip())),
                document_type=DocumentType(row["document_type"].strip()),
                update_frequency=row["update_frequency"].strip(),
                url_pattern=row["url_pattern"].strip() or None,
                trust_note=row["trust_note"].strip(),
            )
            sources[source_id] = source

    return sources


# ---------------------------------------------------------------------------
# SOURCE_REGISTRY — the singleton.
#
# MappingProxyType makes it read-only. No runtime modification is possible.
# Loaded once at import time. Every call to find_source() etc. reads from
# this immutable mapping.
# ---------------------------------------------------------------------------

SOURCE_REGISTRY: MappingProxyType[str, Source] = MappingProxyType(_load_registry())


# ---------------------------------------------------------------------------
# Public lookup functions
# ---------------------------------------------------------------------------


def find_source(source_id: str) -> Source | None:
    """Return the Source for a given ID, or None if not registered.

    Args:
        source_id: The stable source slug (e.g., "sec-edgar-10k").

    Returns:
        The Source object if found, None otherwise.

    Example:
        >>> source = find_source("sec-edgar-10k")
        >>> source.tier
        <SourceTier.ONE: 1>
    """
    return SOURCE_REGISTRY.get(source_id)


def trust_level(source_id: str) -> SourceTier | None:
    """Return the SourceTier for a given source ID.

    Lower tier number = higher trust.
    Tier 1 is the highest trust (regulatory filings).
    Tier 4 is the lowest trust (secondary research).

    Args:
        source_id: The stable source slug.

    Returns:
        SourceTier if the source is registered, None otherwise.

    Example:
        >>> trust_level("sec-edgar-10k")
        <SourceTier.ONE: 1>
        >>> trust_level("reddit")
        None
    """
    source = SOURCE_REGISTRY.get(source_id)
    return source.tier if source is not None else None


def is_trusted(source_id: str) -> bool:
    """True if the source_id is registered as a trusted source.

    A source is trusted if and only if it appears in trusted_sources.csv.
    An unregistered source is never trusted, regardless of its name.

    Args:
        source_id: The stable source slug.

    Returns:
        True if registered, False otherwise.

    Example:
        >>> is_trusted("sec-edgar-10k")
        True
        >>> is_trusted("random-blog")
        False
    """
    return source_id in SOURCE_REGISTRY


def all_sources(tier: SourceTier | None = None) -> tuple[Source, ...]:
    """Return all registered sources, optionally filtered by tier.

    Args:
        tier: If provided, return only sources with this SourceTier.
              If None, return all registered sources.

    Returns:
        Tuple of Source objects in CSV registration order.

    Example:
        >>> len(all_sources())
        4
        >>> len(all_sources(tier=SourceTier.ONE))
        3
    """
    sources = tuple(SOURCE_REGISTRY.values())
    if tier is not None:
        sources = tuple(s for s in sources if s.tier == tier)
    return sources


def supported_document_types(
    tier: SourceTier | None = None,
) -> frozenset[DocumentType]:
    """Return all document types covered by registered sources.

    Args:
        tier: If provided, return only document types from sources at
              this tier. If None, return all supported document types.

    Returns:
        Frozenset of DocumentType values.

    Example:
        >>> DocumentType.ANNUAL_FILING in supported_document_types()
        True
        >>> DocumentType.RESEARCH_REPORT in supported_document_types(tier=SourceTier.ONE)
        False
    """
    return frozenset(s.document_type for s in all_sources(tier=tier))
