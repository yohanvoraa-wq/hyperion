"""Pipeline integration tests — ED-007 category 2 (integration tests).

These are the most important tests in the repository.
They execute the complete Hyperion pipeline with real data and no mocks.
If every test in this file passes, Hyperion works as designed.

The five verbs compose:

    load_portfolio() → evaluate() → build() → reason() → qualify()

No step is skipped. No fixture data is injected. No module is replaced.
This is the pipeline that scripts/demo.py executes, under test discipline.

Fixture scope: 'module' — the expensive pipeline runs once per test
session, not once per test function. All tests in this file share the
same pipeline results.
"""

from __future__ import annotations

import pytest

from backend.atlas import build
from backend.finance_dna import evaluate
from backend.ingestion import load_asset_registry, load_portfolio
from backend.janus import reason
from backend.models import BlindSpot, FinanceDNA, ReasoningArtifact
from backend.titan import qualify

# ---------------------------------------------------------------------------
# Configuration — mirrors scripts/demo.py
# ---------------------------------------------------------------------------

DEMO_PORTFOLIO = ["Apple", "NVIDIA", "Microsoft"]
TEST_DATE = "2024-12-31"


# ---------------------------------------------------------------------------
# Module-scoped pipeline fixture
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def pipeline() -> dict[str, object]:
    """Run the full pipeline once and return all intermediate results.

    Using module scope means the pipeline executes once per test session,
    not once per test function. This keeps the test suite fast while
    still exercising real data at every stage.
    """
    # Step 1 — Ingestion
    portfolio = load_portfolio(DEMO_PORTFOLIO)
    registry = load_asset_registry()
    all_assets = list(registry.assets)

    # Step 2 — Finance DNA
    finance_dnas: dict[str, FinanceDNA] = {
        asset.id: evaluate(asset, as_of=TEST_DATE) for asset in portfolio.assets
    }

    # Step 3 — Atlas
    graph = build(all_assets, finance_dnas)

    # Step 4 — Janus
    artifacts: dict[str, ReasoningArtifact | None] = {
        asset.id: reason(asset.id, graph) for asset in portfolio.assets
    }

    # Step 5 — Titan
    blind_spots: dict[str, BlindSpot | None] = {
        asset_id: qualify(artifact) if artifact is not None else None
        for asset_id, artifact in artifacts.items()
    }

    return {
        "portfolio": portfolio,
        "finance_dnas": finance_dnas,
        "graph": graph,
        "artifacts": artifacts,
        "blind_spots": blind_spots,
    }


# ---------------------------------------------------------------------------
# Step 1 — Ingestion
# ---------------------------------------------------------------------------


class TestIngestionStep:
    def test_portfolio_contains_three_assets(self, pipeline: dict) -> None:  # type: ignore[type-arg]
        assert len(pipeline["portfolio"].assets) == 3

    def test_all_demo_companies_resolved(self, pipeline: dict) -> None:  # type: ignore[type-arg]
        asset_ids = {a.id for a in pipeline["portfolio"].assets}
        assert "apple-inc" in asset_ids
        assert "nvidia" in asset_ids
        assert "microsoft" in asset_ids


# ---------------------------------------------------------------------------
# Step 2 — Finance DNA
# ---------------------------------------------------------------------------


class TestFinanceDNAStep:
    def test_all_portfolio_assets_evaluated(self, pipeline: dict) -> None:  # type: ignore[type-arg]
        dnas = pipeline["finance_dnas"]
        assert "apple-inc" in dnas
        assert "nvidia" in dnas
        assert "microsoft" in dnas

    def test_finance_dna_version_is_01(self, pipeline: dict) -> None:  # type: ignore[type-arg]
        from backend.finance_dna import FINANCE_DNA_VERSION

        for dna in pipeline["finance_dnas"].values():
            assert dna.version == FINANCE_DNA_VERSION == "0.2"

    def test_each_dna_has_fifteen_dimensions(self, pipeline: dict) -> None:  # type: ignore[type-arg]
        for dna in pipeline["finance_dnas"].values():
            assert len(dna.dimensions) == 15


# ---------------------------------------------------------------------------
# Step 3 — Atlas
# ---------------------------------------------------------------------------


class TestAtlasStep:
    def test_graph_has_twenty_six_nodes(self, pipeline: dict) -> None:  # type: ignore[type-arg]
        assert len(pipeline["graph"].nodes) == 26

    def test_graph_has_twenty_six_relationships(self, pipeline: dict) -> None:  # type: ignore[type-arg]
        assert len(pipeline["graph"].relationships) == 26

    def test_apple_finance_dna_attached_to_node(self, pipeline: dict) -> None:  # type: ignore[type-arg]
        graph = pipeline["graph"]
        apple_node = graph.find_node("apple-inc")
        assert apple_node is not None
        assert apple_node.finance_dna is not None
        assert apple_node.finance_dna.asset_id == "apple-inc"

    def test_tsmc_node_exists(self, pipeline: dict) -> None:  # type: ignore[type-arg]
        assert pipeline["graph"].find_node("tsmc") is not None

    def test_taiwan_node_exists(self, pipeline: dict) -> None:  # type: ignore[type-arg]
        assert pipeline["graph"].find_node("taiwan") is not None


# ---------------------------------------------------------------------------
# Step 4 — Janus
# ---------------------------------------------------------------------------


class TestJanusStep:
    def test_apple_produces_reasoning_artifact(self, pipeline: dict) -> None:  # type: ignore[type-arg]
        assert pipeline["artifacts"]["apple-inc"] is not None

    def test_nvidia_produces_reasoning_artifact(self, pipeline: dict) -> None:  # type: ignore[type-arg]
        assert pipeline["artifacts"]["nvidia"] is not None

    def test_microsoft_produces_an_artifact(self, pipeline: dict) -> None:  # type: ignore[type-arg]
        """Microsoft now finds Interest Rate Sensitivity path in V0.2 Atlas."""
        assert pipeline["artifacts"]["microsoft"] is not None

    def test_apple_artifact_has_reasoning_steps(self, pipeline: dict) -> None:  # type: ignore[type-arg]
        artifact = pipeline["artifacts"]["apple-inc"]
        assert artifact is not None
        assert len(artifact.reasoning_steps) >= 2


# ---------------------------------------------------------------------------
# Step 5 — Titan
# ---------------------------------------------------------------------------


class TestTitanStep:
    def test_apple_produces_blind_spot(self, pipeline: dict) -> None:  # type: ignore[type-arg]
        assert pipeline["blind_spots"]["apple-inc"] is not None

    def test_nvidia_produces_blind_spot(self, pipeline: dict) -> None:  # type: ignore[type-arg]
        assert pipeline["blind_spots"]["nvidia"] is not None

    def test_microsoft_qualifies_blind_spot(self, pipeline: dict) -> None:  # type: ignore[type-arg]
        """Microsoft now qualifies a blind spot via Interest Rate Sensitivity (V0.2)."""
        assert pipeline["blind_spots"]["microsoft"] is not None

    def test_apple_blind_spot_is_qualified(self, pipeline: dict) -> None:  # type: ignore[type-arg]
        bs = pipeline["blind_spots"]["apple-inc"]
        assert bs is not None
        assert bs.qualified is True

    def test_blind_spot_confidence_inherited_from_janus(
        self,
        pipeline: dict,  # type: ignore[type-arg]
    ) -> None:
        """Titan Decision 4: confidence is never recalculated."""
        artifact = pipeline["artifacts"]["apple-inc"]
        bs = pipeline["blind_spots"]["apple-inc"]
        assert artifact is not None and bs is not None
        assert bs.confidence == artifact.confidence


# ---------------------------------------------------------------------------
# Golden Example — The canonical V0.1 demonstration
# ---------------------------------------------------------------------------


class TestGoldenExample:
    """The canonical demonstration: Apple → TSMC → Taiwan → Geopolitical Risk.

    These tests freeze the expected output of the V0.1 demo. If any of these
    fail after a refactor, the architecture has changed in a way that
    breaks the core reasoning chain. Fix the root cause, not the test.
    """

    @pytest.fixture()
    def apple_blind_spot(self, pipeline: dict) -> BlindSpot:  # type: ignore[type-arg]
        bs = pipeline["blind_spots"]["apple-inc"]
        assert isinstance(bs, BlindSpot)
        return bs

    def test_reasoning_chain_passes_through_tsmc(self, apple_blind_spot: BlindSpot) -> None:
        premises = " ".join(
            s.premise for s in apple_blind_spot.supporting_reasoning.reasoning_steps
        )
        assert "TSMC" in premises or "Taiwan Semiconductor" in premises

    def test_reasoning_chain_passes_through_taiwan(self, apple_blind_spot: BlindSpot) -> None:
        premises = " ".join(
            s.premise for s in apple_blind_spot.supporting_reasoning.reasoning_steps
        )
        assert "Taiwan" in premises

    def test_reasoning_chain_reaches_geopolitical_risk(self, apple_blind_spot: BlindSpot) -> None:
        conclusion = apple_blind_spot.supporting_reasoning.conclusion
        assert "Geopolitical" in conclusion or "geopolitical" in conclusion

    def test_confidence_above_minimum_threshold(self, apple_blind_spot: BlindSpot) -> None:
        assert apple_blind_spot.confidence >= 0.5

    def test_five_explainability_questions_answered(self, apple_blind_spot: BlindSpot) -> None:
        """Every Janus §5 explainability question must be answered."""
        artifact = apple_blind_spot.supporting_reasoning
        assert len(artifact.reasoning_steps) >= 1  # Why?
        assert len(artifact.supporting_evidence) >= 1  # Supported by what?
        assert artifact.confidence > 0  # How confident?
        assert len(artifact.assumptions) >= 1  # What assumptions?
        assert len(artifact.falsifiability_conditions) >= 1  # What changes this?

    def test_both_companies_qualify_blind_spots(
        self,
        pipeline: dict,  # type: ignore[type-arg]
    ) -> None:
        """Apple and NVIDIA both qualify for Blind Spots through different patterns."""
        apple_bs = pipeline["blind_spots"]["apple-inc"]
        nvidia_bs = pipeline["blind_spots"]["nvidia"]
        assert apple_bs is not None
        assert nvidia_bs is not None
        # Apple: Taiwan supply chain path
        assert "Taiwan" in apple_bs.supporting_reasoning.conclusion
        # NVIDIA: export controls path (higher confidence than Taiwan path)
        assert nvidia_bs.supporting_reasoning.confidence >= 0.75


# ---------------------------------------------------------------------------
# Pipeline-level properties
# ---------------------------------------------------------------------------


class TestPipelineProperties:
    def test_pipeline_is_deterministic(self) -> None:
        """Same inputs, same date → identical BlindSpot outputs every run."""
        portfolio = load_portfolio(["Apple"])
        registry = load_asset_registry()
        all_assets = list(registry.assets)
        dnas = {a.id: evaluate(a, as_of=TEST_DATE) for a in portfolio.assets}
        graph = build(all_assets, dnas)
        artifact = reason("apple-inc", graph)
        assert artifact is not None
        first = qualify(artifact)
        for _ in range(3):
            result = qualify(artifact)
            assert result == first

    def test_five_verbs_compose_into_complete_pipeline(self) -> None:
        """The architectural pattern: one public verb per module."""
        # load_portfolio (Ingestion)
        portfolio = load_portfolio(["Apple", "NVIDIA"])
        registry = load_asset_registry()
        all_assets = list(registry.assets)
        # evaluate (Finance DNA)
        dnas = {a.id: evaluate(a, as_of=TEST_DATE) for a in portfolio.assets}
        # build (Atlas)
        graph = build(all_assets, dnas)
        # reason (Janus)
        artifacts = {a.id: reason(a.id, graph) for a in portfolio.assets}
        # qualify (Titan)
        blind_spots = {a_id: qualify(art) for a_id, art in artifacts.items() if art is not None}
        assert "apple-inc" in blind_spots
        assert blind_spots["apple-inc"] is not None

    def test_no_module_mutates_upstream_artifacts(self) -> None:
        """Each module reads its inputs; none mutate them."""
        portfolio = load_portfolio(["Apple"])
        registry = load_asset_registry()
        asset = portfolio.assets[0]
        original_id = asset.id
        original_name = asset.name
        dna = evaluate(asset, as_of=TEST_DATE)
        original_dna_version = dna.version
        graph = build(list(registry.assets), {asset.id: dna})
        artifact = reason(asset.id, graph)
        assert artifact is not None
        qualify(artifact)
        # Nothing mutated
        assert asset.id == original_id
        assert asset.name == original_name
        assert dna.version == original_dna_version
