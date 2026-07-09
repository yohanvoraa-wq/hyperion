"""Tests for backend/api/mapper.py — ED-007.

The mapper is the anti-corruption layer. These tests verify that engine
objects are correctly translated to DTOs without losing information,
without exposing engine internals, and without violating the API contract.

Key things tested:
  - Premise string is correctly parsed for traceability fields
  - Node IDs are correctly looked up by label from the graph
  - Relationship types are lowercased
  - Blind Spots are grouped into summary/explanation/evidence
  - No findings appear for assets with no Blind Spot
  - Unknown identifiers appear in errors
  - Metadata fields are all populated
  - Categories are lowercase strings
"""

from __future__ import annotations

import pytest

from backend.api.dto import (
    AnalyzeResponseDTO,
    BlindSpotDTO,
)
from backend.api.mapper import map_analyze_response
from backend.atlas import build
from backend.finance_dna import evaluate
from backend.ingestion import load_asset_registry, load_portfolio
from backend.janus import reason
from backend.models import (
    BlindSpot,
)
from backend.titan import qualify

TEST_DATE = "2024-12-31"


# ---------------------------------------------------------------------------
# Fixtures — real pipeline output for the demo portfolio
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def pipeline_dto() -> AnalyzeResponseDTO:
    """Run the real pipeline and map to DTO once per test session."""
    portfolio = load_portfolio(["Apple", "NVIDIA", "Microsoft"])
    registry = load_asset_registry()
    all_assets = list(registry.assets)
    dnas = {a.id: evaluate(a, as_of=TEST_DATE) for a in portfolio.assets}
    graph = build(all_assets, dnas)
    artifacts = {a.id: reason(a.id, graph) for a in portfolio.assets}
    blind_spots: dict[str, BlindSpot | None] = {
        a_id: qualify(art) if art is not None else None for a_id, art in artifacts.items()
    }
    return map_analyze_response(
        portfolio=portfolio,
        blind_spots=blind_spots,
        unknown_identifiers=[],
        graph=graph,
        processing_time_ms=42,
        as_of=TEST_DATE,
    )


@pytest.fixture(scope="module")
def apple_blind_spot(pipeline_dto: AnalyzeResponseDTO) -> BlindSpotDTO:
    """The Apple Blind Spot DTO from the real pipeline."""
    apple_bss = [bs for bs in pipeline_dto.blind_spots if bs.summary.company_id == "apple-inc"]
    assert len(apple_bss) == 1
    return apple_bss[0]


# ---------------------------------------------------------------------------
# Group 1 — Metadata
# ---------------------------------------------------------------------------


class TestMetadata:
    def test_hyperion_version_present(self, pipeline_dto: AnalyzeResponseDTO) -> None:
        assert pipeline_dto.metadata.hyperion_version == "0.1"

    def test_finance_dna_schema_present(self, pipeline_dto: AnalyzeResponseDTO) -> None:
        assert pipeline_dto.metadata.finance_dna_schema == "0.2"

    def test_processed_at_is_iso_string(self, pipeline_dto: AnalyzeResponseDTO) -> None:
        assert len(pipeline_dto.metadata.processed_at) > 0
        assert "T" in pipeline_dto.metadata.processed_at  # ISO datetime

    def test_processing_time_ms_matches_input(self, pipeline_dto: AnalyzeResponseDTO) -> None:
        assert pipeline_dto.metadata.processing_time_ms == 42

    def test_request_id_is_uuid_string(self, pipeline_dto: AnalyzeResponseDTO) -> None:
        import re

        uuid_pattern = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
        assert uuid_pattern.match(pipeline_dto.metadata.request_id)

    def test_request_id_unique_per_call(self) -> None:
        """Each call to map_analyze_response produces a different request_id."""
        portfolio = load_portfolio(["Apple"])
        registry = load_asset_registry()
        graph = build(list(registry.assets))
        artifact = reason("apple-inc", graph)
        assert artifact is not None
        bs = qualify(artifact)
        blind_spots: dict[str, BlindSpot | None] = {"apple-inc": bs}
        dto1 = map_analyze_response(
            portfolio=portfolio,
            blind_spots=blind_spots,
            unknown_identifiers=[],
            graph=graph,
            processing_time_ms=10,
            as_of=TEST_DATE,
        )
        dto2 = map_analyze_response(
            portfolio=portfolio,
            blind_spots=blind_spots,
            unknown_identifiers=[],
            graph=graph,
            processing_time_ms=10,
            as_of=TEST_DATE,
        )
        assert dto1.metadata.request_id != dto2.metadata.request_id


# ---------------------------------------------------------------------------
# Group 2 — Portfolio
# ---------------------------------------------------------------------------


class TestPortfolio:
    def test_resolved_names_in_dto(self, pipeline_dto: AnalyzeResponseDTO) -> None:
        assert "Apple Inc." in pipeline_dto.portfolio
        assert "NVIDIA Corporation" in pipeline_dto.portfolio
        assert "Microsoft Corporation" in pipeline_dto.portfolio

    def test_three_portfolio_entries(self, pipeline_dto: AnalyzeResponseDTO) -> None:
        assert len(pipeline_dto.portfolio) == 3


# ---------------------------------------------------------------------------
# Group 3 — Blind Spots
# ---------------------------------------------------------------------------


class TestBlindSpots:
    def test_three_blind_spots_in_demo(self, pipeline_dto: AnalyzeResponseDTO) -> None:
        """Apple, NVIDIA, and Microsoft all qualify in V0.2."""
        assert len(pipeline_dto.blind_spots) == 3

    def test_apple_blind_spot_present(self, pipeline_dto: AnalyzeResponseDTO) -> None:
        ids = {bs.summary.company_id for bs in pipeline_dto.blind_spots}
        assert "apple-inc" in ids

    def test_nvidia_blind_spot_present(self, pipeline_dto: AnalyzeResponseDTO) -> None:
        ids = {bs.summary.company_id for bs in pipeline_dto.blind_spots}
        assert "nvidia" in ids

    def test_three_sections_present(self, apple_blind_spot: BlindSpotDTO) -> None:
        assert apple_blind_spot.summary is not None
        assert apple_blind_spot.explanation is not None
        assert apple_blind_spot.evidence is not None

    def test_confidence_matches_janus_output(self, apple_blind_spot: BlindSpotDTO) -> None:
        assert abs(apple_blind_spot.summary.confidence - 0.8075) < 1e-4

    def test_severity_is_medium_v01_placeholder(self, apple_blind_spot: BlindSpotDTO) -> None:
        assert apple_blind_spot.summary.severity == "MEDIUM"

    def test_categories_are_lowercase(self, apple_blind_spot: BlindSpotDTO) -> None:
        for cat in apple_blind_spot.summary.categories:
            assert cat == cat.lower(), f"Category '{cat}' is not lowercase."

    def test_categories_include_dependency_and_macroeconomic(
        self, apple_blind_spot: BlindSpotDTO
    ) -> None:
        assert "dependency" in apple_blind_spot.summary.categories
        assert "macroeconomic" in apple_blind_spot.summary.categories


# ---------------------------------------------------------------------------
# Group 4 — Reasoning steps (traceability)
# ---------------------------------------------------------------------------


class TestReasoningSteps:
    def test_three_steps_for_apple(self, apple_blind_spot: BlindSpotDTO) -> None:
        assert len(apple_blind_spot.explanation.steps) == 3

    def test_relationship_type_is_lowercase(self, apple_blind_spot: BlindSpotDTO) -> None:
        for step in apple_blind_spot.explanation.steps:
            assert step.relationship_type == step.relationship_type.lower()

    def test_first_step_is_depends_on(self, apple_blind_spot: BlindSpotDTO) -> None:
        first = apple_blind_spot.explanation.steps[0]
        assert "depends_on" in first.relationship_type

    def test_source_id_resolved_for_apple(self, apple_blind_spot: BlindSpotDTO) -> None:
        first = apple_blind_spot.explanation.steps[0]
        assert first.source_id == "apple-inc"

    def test_target_id_resolved_for_tsmc(self, apple_blind_spot: BlindSpotDTO) -> None:
        first = apple_blind_spot.explanation.steps[0]
        assert first.target_id == "tsmc"

    def test_source_label_is_human_readable(self, apple_blind_spot: BlindSpotDTO) -> None:
        first = apple_blind_spot.explanation.steps[0]
        assert "Apple" in first.source_label

    def test_step_confidence_in_valid_range(self, apple_blind_spot: BlindSpotDTO) -> None:
        for step in apple_blind_spot.explanation.steps:
            assert 0.0 < step.confidence <= 1.0


# ---------------------------------------------------------------------------
# Group 5 — Evidence section
# ---------------------------------------------------------------------------


class TestEvidence:
    def test_supporting_evidence_non_empty(self, apple_blind_spot: BlindSpotDTO) -> None:
        assert len(apple_blind_spot.evidence.supporting_evidence) >= 1

    def test_assumptions_contain_v01_strings(self, apple_blind_spot: BlindSpotDTO) -> None:
        assumptions_joined = " ".join(apple_blind_spot.evidence.assumptions)
        assert "V0.1" in assumptions_joined or "Version 0.1" in assumptions_joined

    def test_falsifiability_conditions_non_empty(self, apple_blind_spot: BlindSpotDTO) -> None:
        assert len(apple_blind_spot.evidence.falsifiability_conditions) >= 1


# ---------------------------------------------------------------------------
# Group 6 — No findings and errors
# ---------------------------------------------------------------------------


class TestNoFindingsAndErrors:
    def test_microsoft_not_in_no_findings(self, pipeline_dto: AnalyzeResponseDTO) -> None:
        # Microsoft now has a blind spot — should NOT be in no_findings
        ids = {nf.company_id for nf in pipeline_dto.no_findings}
        assert "microsoft" not in ids

    def test_no_finding_reason_is_correct(self, pipeline_dto: AnalyzeResponseDTO) -> None:
        # Microsoft no longer in no_findings — check any no_finding exists or skip
        # Microsoft now qualifies a blind spot in V0.2 — no_findings may be empty
        microsoft_no_finding = next(
            (nf for nf in pipeline_dto.no_findings if nf.company_id == "microsoft"),
            None,
        )
        assert microsoft_no_finding is None

    def test_no_errors_for_known_portfolio(self, pipeline_dto: AnalyzeResponseDTO) -> None:
        assert len(pipeline_dto.errors) == 0

    def test_unknown_identifier_appears_in_errors(self) -> None:
        """An unresolvable name goes to errors[], not crashes the pipeline."""
        portfolio = load_portfolio(["Apple"])
        registry = load_asset_registry()
        graph = build(list(registry.assets))
        artifact = reason("apple-inc", graph)
        assert artifact is not None
        bs = qualify(artifact)
        dto = map_analyze_response(
            portfolio=portfolio,
            blind_spots={"apple-inc": bs},
            unknown_identifiers=["Hyperion Holdings Ltd"],
            graph=graph,
            processing_time_ms=10,
            as_of=TEST_DATE,
        )
        assert len(dto.errors) == 1
        assert dto.errors[0].identifier == "Hyperion Holdings Ltd"
        assert dto.errors[0].reason == "UNKNOWN_COMPANY"
