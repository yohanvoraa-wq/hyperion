"""Tests for backend/api/serializers.py and golden response — ED-007.

These tests verify:
  1. DTOs serialize correctly to Pydantic schemas
  2. Pydantic schemas produce valid JSON
  3. The complete API response matches the golden reference

The golden test is the most important one in this file. It freezes the
expected output for the canonical demo portfolio (Apple + NVIDIA + Microsoft)
on TEST_DATE = "2024-12-31". If the golden test fails after a refactor,
the API contract has changed in a way that affects consumers.

Volatile fields (metadata.processing_time_ms, metadata.request_id,
metadata.processed_at) are excluded from the golden comparison since
they vary per invocation by design.
"""

from __future__ import annotations

import json

import pytest

from backend.api.mapper import map_analyze_response
from backend.api.schemas import AnalyzeResponseSchema
from backend.api.serializers import serialize_response
from backend.atlas import build
from backend.finance_dna import evaluate
from backend.ingestion import load_asset_registry, load_portfolio
from backend.janus import reason
from backend.models import BlindSpot
from backend.titan import qualify

TEST_DATE = "2024-12-31"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _stable_fields(response_dict: dict) -> dict:  # type: ignore[type-arg]
    """Strip volatile fields before golden comparison.

    Removes fields that vary per invocation (timing, UUID, timestamp)
    so the golden comparison is deterministic across runs.
    """
    stable = dict(response_dict)
    if "metadata" in stable:
        meta = dict(stable["metadata"])
        meta.pop("processing_time_ms", None)
        meta.pop("request_id", None)
        meta.pop("processed_at", None)
        stable["metadata"] = meta
    return stable


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def full_schema() -> AnalyzeResponseSchema:
    """Run the real pipeline and serialize to Pydantic schema once."""
    portfolio = load_portfolio(["Apple", "NVIDIA", "Microsoft"])
    registry = load_asset_registry()
    all_assets = list(registry.assets)
    dnas = {a.id: evaluate(a, as_of=TEST_DATE) for a in portfolio.assets}
    graph = build(all_assets, dnas)
    artifacts = {a.id: reason(a.id, graph) for a in portfolio.assets}
    blind_spots: dict[str, BlindSpot | None] = {
        a_id: qualify(art) if art is not None else None for a_id, art in artifacts.items()
    }
    dto = map_analyze_response(
        portfolio=portfolio,
        blind_spots=blind_spots,
        unknown_identifiers=[],
        graph=graph,
        processing_time_ms=42,
        as_of=TEST_DATE,
    )
    return serialize_response(dto)


# ---------------------------------------------------------------------------
# Group 1 — Schema structure
# ---------------------------------------------------------------------------


class TestSchemaStructure:
    def test_response_is_analyze_response_schema(self, full_schema: AnalyzeResponseSchema) -> None:
        assert isinstance(full_schema, AnalyzeResponseSchema)

    def test_metadata_fields_all_present(self, full_schema: AnalyzeResponseSchema) -> None:
        assert full_schema.metadata.hyperion_version == "0.1"
        assert full_schema.metadata.finance_dna_schema == "0.2"
        assert len(full_schema.metadata.processed_at) > 0
        assert full_schema.metadata.processing_time_ms == 42
        assert len(full_schema.metadata.request_id) > 0

    def test_blind_spot_has_three_sections(self, full_schema: AnalyzeResponseSchema) -> None:
        assert len(full_schema.blind_spots) >= 1
        bs = full_schema.blind_spots[0]
        assert bs.summary is not None
        assert bs.explanation is not None
        assert bs.evidence is not None

    def test_explanation_uses_steps_not_reasoning_chain(
        self, full_schema: AnalyzeResponseSchema
    ) -> None:
        """Per Change 1: no engine terminology in the public contract."""
        bs = full_schema.blind_spots[0]
        schema_dict = bs.model_dump()
        # 'reasoning_chain' must not appear anywhere in the serialized output
        assert "reasoning_chain" not in json.dumps(schema_dict)
        # 'explanation' with 'steps' must be present
        assert "explanation" in schema_dict
        assert "steps" in schema_dict["explanation"]

    def test_step_has_traceability_fields(self, full_schema: AnalyzeResponseSchema) -> None:
        """Per Change 6: every step exposes relationship_type, source, target."""
        for bs in full_schema.blind_spots:
            for step in bs.explanation.steps:
                assert hasattr(step, "relationship_type")
                assert hasattr(step, "source_id")
                assert hasattr(step, "target_id")
                assert hasattr(step, "source_label")
                assert hasattr(step, "target_label")

    def test_categories_are_lowercase_strings(self, full_schema: AnalyzeResponseSchema) -> None:
        for bs in full_schema.blind_spots:
            for cat in bs.summary.categories:
                assert cat == cat.lower()

    def test_severity_field_present(self, full_schema: AnalyzeResponseSchema) -> None:
        """Per Change 5: severity is frozen now even if computed later."""
        for bs in full_schema.blind_spots:
            assert bs.summary.severity in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


# ---------------------------------------------------------------------------
# Group 2 — JSON serialization
# ---------------------------------------------------------------------------


class TestJSONSerialization:
    def test_response_serializes_to_valid_json(self, full_schema: AnalyzeResponseSchema) -> None:
        json_str = full_schema.model_dump_json()
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)

    def test_json_contains_metadata_key(self, full_schema: AnalyzeResponseSchema) -> None:
        parsed = json.loads(full_schema.model_dump_json())
        assert "metadata" in parsed

    def test_json_contains_blind_spots_key(self, full_schema: AnalyzeResponseSchema) -> None:
        parsed = json.loads(full_schema.model_dump_json())
        assert "blind_spots" in parsed
        assert isinstance(parsed["blind_spots"], list)

    def test_json_contains_no_findings_key(self, full_schema: AnalyzeResponseSchema) -> None:
        parsed = json.loads(full_schema.model_dump_json())
        assert "no_findings" in parsed

    def test_json_contains_errors_key(self, full_schema: AnalyzeResponseSchema) -> None:
        parsed = json.loads(full_schema.model_dump_json())
        assert "errors" in parsed

    def test_janus_terminology_absent_from_json(self, full_schema: AnalyzeResponseSchema) -> None:
        """Engine module names must never appear in the wire format."""
        json_str = full_schema.model_dump_json()
        for term in ["janus", "titan", "ReasoningArtifact", "reasoning_chain"]:
            assert term not in json_str.lower(), (
                f"Engine term '{term}' found in JSON output. "
                "The API contract must not expose engine internals."
            )


# ---------------------------------------------------------------------------
# Group 3 — Golden response comparison
# ---------------------------------------------------------------------------


class TestGoldenResponse:
    """The canonical golden test. Freezes the V0.1 demo output.

    If this test fails after a refactor, something that was stable has
    changed — investigate before changing the golden values. A failing
    golden test is information, not an obstacle.

    Volatile fields (processing_time_ms, request_id, processed_at) are
    excluded from comparison since they vary per invocation by design.
    """

    @pytest.fixture()
    def parsed_response(self, full_schema: AnalyzeResponseSchema) -> dict:  # type: ignore[type-arg]
        return _stable_fields(json.loads(full_schema.model_dump_json()))

    def test_golden_metadata_versions(self, parsed_response: dict) -> None:  # type: ignore[type-arg]
        assert parsed_response["metadata"]["hyperion_version"] == "0.1"
        assert parsed_response["metadata"]["finance_dna_schema"] == "0.2"

    def test_golden_portfolio_names(self, parsed_response: dict) -> None:  # type: ignore[type-arg]
        assert parsed_response["portfolio"] == [
            "Apple Inc.",
            "NVIDIA Corporation",
            "Microsoft Corporation",
        ]

    def test_golden_three_blind_spots(self, parsed_response: dict) -> None:  # type: ignore[type-arg]
        assert len(parsed_response["blind_spots"]) == 3

    def test_golden_apple_company_id(self, parsed_response: dict) -> None:  # type: ignore[type-arg]
        apple = parsed_response["blind_spots"][0]
        assert apple["summary"]["company_id"] == "apple-inc"

    def test_golden_apple_confidence(self, parsed_response: dict) -> None:  # type: ignore[type-arg]
        apple = parsed_response["blind_spots"][0]
        assert abs(apple["summary"]["confidence"] - 0.8075) < 1e-4

    def test_golden_apple_three_steps(self, parsed_response: dict) -> None:  # type: ignore[type-arg]
        apple = parsed_response["blind_spots"][0]
        assert len(apple["explanation"]["steps"]) == 3

    def test_golden_apple_step_one_source_and_target(
        self,
        parsed_response: dict,  # type: ignore[type-arg]
    ) -> None:
        """The first step of the golden example: Apple → TSMC."""
        step = parsed_response["blind_spots"][0]["explanation"]["steps"][0]
        assert step["source_id"] == "apple-inc"
        assert step["target_id"] == "tsmc"
        assert step["relationship_type"] == "depends_on_supplies"

    def test_golden_apple_last_step_reaches_geopolitical_risk(
        self,
        parsed_response: dict,  # type: ignore[type-arg]
    ) -> None:
        """The last step: Taiwan → Taiwan Geopolitical Risk."""
        steps = parsed_response["blind_spots"][0]["explanation"]["steps"]
        last = steps[-1]
        assert last["target_id"] == "geopolitical-risk-taiwan"
        assert last["relationship_type"] == "affected_by"

    def test_golden_microsoft_not_in_no_findings(
        self,
        parsed_response: dict,  # type: ignore[type-arg]
    ) -> None:
        # Microsoft now qualifies a blind spot — no_findings is empty for this portfolio
        no_findings = parsed_response["no_findings"]
        assert len(no_findings) == 0

    def test_golden_no_errors(self, parsed_response: dict) -> None:  # type: ignore[type-arg]
        assert parsed_response["errors"] == []
