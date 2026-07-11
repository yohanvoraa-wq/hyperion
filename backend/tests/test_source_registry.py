"""Tests for backend/evidence/registry.py — Milestone 14.

Six test groups covering registry loading, source lookup,
trust levels, document type filtering, CSV integrity, and immutability.

Target: 40 assertions.
These are registry integrity tests — not parser tests, not ingestion tests.

Stop list:
    NO file downloads
    NO SEC API calls
    NO PDF parsing
    NO Evidence creation
    NO Atlas imports
"""

from __future__ import annotations

from types import MappingProxyType

import pytest

from backend.evidence import (
    SOURCE_REGISTRY,
    DocumentType,
    Source,
    SourceTier,
    all_sources,
    find_source,
    is_trusted,
    supported_document_types,
    trust_level,
)

# ---------------------------------------------------------------------------
# Known source IDs — defined here as constants so tests are self-documenting
# ---------------------------------------------------------------------------

SEC_10K = "sec-edgar-10k"
SEC_10Q = "sec-edgar-10q"
SEC_8K = "sec-edgar-8k"
FED_RESERVE = "federal-reserve"
UNKNOWN = "reddit-finance-blog"


# ===========================================================================
# Group 1 — Registry loading
# ===========================================================================


class TestRegistryLoading:
    """SOURCE_REGISTRY loads correctly from trusted_sources.csv."""

    def test_registry_is_not_empty(self) -> None:
        assert len(SOURCE_REGISTRY) > 0

    def test_registry_contains_four_sources(self) -> None:
        assert len(SOURCE_REGISTRY) == 4

    def test_all_three_sec_sources_present(self) -> None:
        assert SEC_10K in SOURCE_REGISTRY
        assert SEC_10Q in SOURCE_REGISTRY
        assert SEC_8K in SOURCE_REGISTRY

    def test_federal_reserve_present(self) -> None:
        assert FED_RESERVE in SOURCE_REGISTRY

    def test_registry_is_mapping_proxy(self) -> None:
        assert isinstance(SOURCE_REGISTRY, MappingProxyType)

    def test_all_values_are_source_objects(self) -> None:
        for source in SOURCE_REGISTRY.values():
            assert isinstance(source, Source)

    def test_registry_loads_deterministically(self) -> None:
        """Same registry state on every import — no randomness."""
        from backend.evidence.registry import _load_registry

        first = _load_registry()
        second = _load_registry()
        assert list(first.keys()) == list(second.keys())
        assert list(first.values()) == list(second.values())


# ===========================================================================
# Group 2 — Source lookup
# ===========================================================================


class TestSourceLookup:
    """find_source() and is_trusted() return correct results."""

    def test_find_known_source_returns_source(self) -> None:
        source = find_source(SEC_10K)
        assert source is not None
        assert source.id == SEC_10K

    def test_find_unknown_source_returns_none(self) -> None:
        assert find_source(UNKNOWN) is None

    def test_find_empty_string_returns_none(self) -> None:
        assert find_source("") is None

    def test_is_trusted_known_source(self) -> None:
        assert is_trusted(SEC_10K) is True
        assert is_trusted(SEC_10Q) is True
        assert is_trusted(SEC_8K) is True
        assert is_trusted(FED_RESERVE) is True

    def test_is_trusted_unknown_source(self) -> None:
        assert is_trusted(UNKNOWN) is False
        assert is_trusted("wikipedia") is False
        assert is_trusted("bloomberg") is False  # not yet registered

    def test_source_name_is_descriptive(self) -> None:
        source = find_source(SEC_10K)
        assert source is not None
        assert len(source.name) > 10

    def test_source_trust_note_is_present(self) -> None:
        for source_id in [SEC_10K, SEC_10Q, SEC_8K, FED_RESERVE]:
            source = find_source(source_id)
            assert source is not None
            assert len(source.trust_note) > 0


# ===========================================================================
# Group 3 — Trust levels
# ===========================================================================


class TestTrustLevels:
    """trust_level() returns correct SourceTier values."""

    def test_sec_10k_is_tier_one(self) -> None:
        assert trust_level(SEC_10K) == SourceTier.ONE

    def test_sec_10q_is_tier_one(self) -> None:
        assert trust_level(SEC_10Q) == SourceTier.ONE

    def test_sec_8k_is_tier_one(self) -> None:
        assert trust_level(SEC_8K) == SourceTier.ONE

    def test_federal_reserve_is_tier_two(self) -> None:
        assert trust_level(FED_RESERVE) == SourceTier.TWO

    def test_unknown_source_trust_level_is_none(self) -> None:
        assert trust_level(UNKNOWN) is None

    def test_tier_one_outranks_tier_two(self) -> None:
        """Trust ordering: Tier 1 < Tier 2 (lower number = higher trust)."""
        tier1 = trust_level(SEC_10K)
        tier2 = trust_level(FED_RESERVE)
        assert tier1 is not None and tier2 is not None
        assert tier1 < tier2

    def test_all_registered_sources_have_valid_tier(self) -> None:
        valid_tiers = set(SourceTier)
        for source in SOURCE_REGISTRY.values():
            assert source.tier in valid_tiers


# ===========================================================================
# Group 4 — Document type filtering
# ===========================================================================


class TestDocumentTypeFiltering:
    """all_sources() and supported_document_types() filter correctly."""

    def test_all_sources_returns_four(self) -> None:
        assert len(all_sources()) == 4

    def test_all_sources_tier_one_returns_three(self) -> None:
        tier_one = all_sources(tier=SourceTier.ONE)
        assert len(tier_one) == 3

    def test_all_sources_tier_two_returns_one(self) -> None:
        tier_two = all_sources(tier=SourceTier.TWO)
        assert len(tier_two) == 1
        assert tier_two[0].id == FED_RESERVE

    def test_all_sources_tier_three_returns_empty(self) -> None:
        tier_three = all_sources(tier=SourceTier.THREE)
        assert len(tier_three) == 0

    def test_all_sources_tier_four_returns_empty(self) -> None:
        tier_four = all_sources(tier=SourceTier.FOUR)
        assert len(tier_four) == 0

    def test_supported_document_types_contains_annual_filing(self) -> None:
        assert DocumentType.ANNUAL_FILING in supported_document_types()

    def test_supported_document_types_contains_quarterly_filing(self) -> None:
        assert DocumentType.QUARTERLY_FILING in supported_document_types()

    def test_supported_document_types_contains_current_report(self) -> None:
        assert DocumentType.CURRENT_REPORT in supported_document_types()

    def test_supported_document_types_contains_government_report(self) -> None:
        assert DocumentType.GOVERNMENT_REPORT in supported_document_types()

    def test_supported_document_types_does_not_contain_research_report(self) -> None:
        """RESEARCH_REPORT is Tier 4 — not registered in V0.3."""
        assert DocumentType.RESEARCH_REPORT not in supported_document_types()

    def test_tier_one_does_not_include_government_report(self) -> None:
        tier_one_types = supported_document_types(tier=SourceTier.ONE)
        assert DocumentType.GOVERNMENT_REPORT not in tier_one_types

    def test_tier_two_includes_government_report(self) -> None:
        tier_two_types = supported_document_types(tier=SourceTier.TWO)
        assert DocumentType.GOVERNMENT_REPORT in tier_two_types


# ===========================================================================
# Group 5 — Registry integrity
# ===========================================================================


class TestRegistryIntegrity:
    """All registered sources satisfy the Source model invariants."""

    def test_all_source_ids_are_unique(self) -> None:
        ids = list(SOURCE_REGISTRY.keys())
        assert len(ids) == len(set(ids))

    def test_all_source_ids_are_lowercase(self) -> None:
        for source_id in SOURCE_REGISTRY:
            assert source_id == source_id.lower(), (
                f"Source ID {source_id!r} contains uppercase characters"
            )

    def test_all_source_ids_contain_only_valid_characters(self) -> None:
        for source_id in SOURCE_REGISTRY:
            assert all(c.islower() or c.isdigit() or c == "-" for c in source_id), (
                f"Source ID {source_id!r} contains invalid characters"
            )

    def test_all_sources_have_url_patterns(self) -> None:
        """All V0.3 sources have URL patterns — they are official public sources."""
        for source in SOURCE_REGISTRY.values():
            assert source.url_pattern is not None, (
                f"Source {source.id!r} missing url_pattern"
            )

    def test_registry_key_matches_source_id(self) -> None:
        """Registry key must match the Source.id field."""
        for key, source in SOURCE_REGISTRY.items():
            assert key == source.id, (
                f"Registry key {key!r} does not match Source.id {source.id!r}"
            )

    def test_no_unregistered_tier_values(self) -> None:
        """Every tier value in the CSV is a valid SourceTier member."""
        valid_tiers = {t.value for t in SourceTier}
        for source in SOURCE_REGISTRY.values():
            assert source.tier.value in valid_tiers

    def test_no_unregistered_document_type_values(self) -> None:
        """Every document_type in the CSV is a valid DocumentType member."""
        valid_types = {t.value for t in DocumentType}
        for source in SOURCE_REGISTRY.values():
            assert source.document_type.value in valid_types


# ===========================================================================
# Group 6 — Immutability
# ===========================================================================


class TestImmutability:
    """SOURCE_REGISTRY is read-only — no runtime modification is possible."""

    def test_registry_rejects_new_entry(self) -> None:
        with pytest.raises(TypeError):
            SOURCE_REGISTRY["new-source"] = None  # type: ignore[index]

    def test_registry_rejects_deletion(self) -> None:
        with pytest.raises(TypeError):
            del SOURCE_REGISTRY[SEC_10K]  # type: ignore[attr-defined]

    def test_source_objects_are_frozen(self) -> None:
        """Source objects inside the registry are immutable."""
        from dataclasses import FrozenInstanceError
        source = SOURCE_REGISTRY[SEC_10K]
        with pytest.raises(FrozenInstanceError):
            source.name = "Hacked"  # type: ignore[misc]
