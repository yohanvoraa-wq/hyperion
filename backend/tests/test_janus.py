"""Tests for backend/janus — ED-007.

Five test groups:

  Group 1 — Traversal
    get_candidate_paths finds paths ending at qualifying node types.
    Ignores Geography, Industry, and other non-qualifying endpoints.
    Respects max_depth.

  Group 2 — Ranking
    rank_paths applies all four significance criteria.
    Returns None when nothing qualifies.
    Returns highest-confidence-product path when multiple qualify.
    Explicitly tests the no-repeated-nodes guard.

  Group 3 — Reasoning
    build_reasoning_artifact answers all five explainability questions.
    V0.1 assumption strings are present.
    Confidence is rounded product of edge confidences.
    ReasoningSteps match relationship count.

  Group 4 — Public API
    reason() returns None for assets with no qualifying path.
    reason() returns ReasoningArtifact for the V0.1 demo path.
    Output is immutable.
    Deterministic: same inputs → same output every run.

  Group 5 — End-to-end demo path (real seed data)
    reason("apple-inc", real_graph) produces the exact demo chain.
    reason("nvidia", real_graph) shares the TSMC path.
    reason("microsoft", real_graph) now returns an artifact via Interest Rate Sensitivity (V0.2).
"""

from __future__ import annotations

import pytest

from backend.janus import reason
from backend.janus.ranker import (
    _confidence_product,
    _has_no_repeated_nodes,
    _is_significant,
    rank_paths,
)
from backend.janus.reasoner import V01_ASSUMPTIONS, build_reasoning_artifact
from backend.janus.traversal import (
    MAX_DEPTH,
    get_candidate_paths,
)
from backend.models import (
    AssetType,
    Cardinality,
    ContextNodeType,
    Directionality,
    EvidenceSource,
    GraphNode,
    KnowledgeGraph,
    ReasoningArtifact,
    Relationship,
    RelationshipTemporality,
    RelationshipType,
)

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _node(
    node_id: str,
    label: str,
    node_class: AssetType | ContextNodeType = ContextNodeType.GEOGRAPHY,
) -> GraphNode:
    return GraphNode(id=node_id, node_class=node_class, label=label)


def _rel(
    source: str,
    target: str,
    rel_type: RelationshipType = RelationshipType.LOCATED_IN,
    confidence: float = 0.9,
    evidence: str = "Test evidence.",
) -> Relationship:
    return Relationship(
        source_id=source,
        target_id=target,
        relationship_type=rel_type,
        directionality=Directionality.DIRECTED,
        temporality=RelationshipTemporality.PERSISTENT,
        cardinality=Cardinality.ONE_TO_MANY,
        evidence_source=EvidenceSource.DISCLOSED,
        confidence=confidence,
        evidence=(evidence,),
    )


# ---------------------------------------------------------------------------
# Fixture graphs
# ---------------------------------------------------------------------------


@pytest.fixture()
def demo_graph() -> KnowledgeGraph:
    """Minimal graph matching the V0.1 demo path: Apple → TSMC → Taiwan → Geo Risk."""
    apple = _node("apple-inc", "Apple Inc.", AssetType.COMPANY)
    tsmc = _node("tsmc", "TSMC", AssetType.COMPANY)
    taiwan = _node("taiwan", "Taiwan", ContextNodeType.GEOGRAPHY)
    geo_risk = _node("geo-risk-taiwan", "Taiwan Geopolitical Risk", ContextNodeType.MACRO_FACTOR)
    r1 = _rel(
        "apple-inc",
        "tsmc",
        RelationshipType.DEPENDS_ON_SUPPLIES,
        confidence=0.95,
        evidence="Apple 10-K: TSMC sole-source supplier.",
    )
    r2 = _rel("tsmc", "taiwan", confidence=1.0, evidence="TSMC fabs in Taiwan.")
    r3 = _rel(
        "taiwan",
        "geo-risk-taiwan",
        RelationshipType.AFFECTED_BY,
        confidence=0.85,
        evidence="Taiwan Strait tensions.",
    )
    return KnowledgeGraph([apple, tsmc, taiwan, geo_risk], [r1, r2, r3])


@pytest.fixture()
def no_qualifying_graph() -> KnowledgeGraph:
    """Graph where Microsoft only reaches INDUSTRY nodes — no qualifying endpoint."""
    msft = _node("microsoft", "Microsoft Corporation", AssetType.COMPANY)
    sw_industry = _node("software-industry", "Software", ContextNodeType.INDUSTRY)
    r = _rel(
        "microsoft",
        "software-industry",
        RelationshipType.BELONGS_TO,
        confidence=1.0,
        evidence="Microsoft is classified as Software.",
    )
    return KnowledgeGraph([msft, sw_industry], [r])


@pytest.fixture()
def two_path_graph() -> KnowledgeGraph:
    """Graph where Apple has two qualifying paths — ranker must pick the best."""
    apple = _node("apple-inc", "Apple Inc.", AssetType.COMPANY)
    taiwan = _node("taiwan", "Taiwan", ContextNodeType.GEOGRAPHY)
    geo_risk = _node("geo-risk-taiwan", "Taiwan Geopolitical Risk", ContextNodeType.MACRO_FACTOR)
    currency_risk = _node("usd-cny-risk", "USD/CNY Currency Risk", ContextNodeType.MACRO_FACTOR)
    r1 = _rel("apple-inc", "taiwan", confidence=0.9, evidence="Apple manufactures in Taiwan.")
    r2 = _rel(
        "taiwan",
        "geo-risk-taiwan",
        RelationshipType.AFFECTED_BY,
        confidence=0.85,
        evidence="Taiwan Strait tensions.",
    )
    r3 = _rel(
        "apple-inc",
        "usd-cny-risk",
        RelationshipType.EXPOSED_TO,
        confidence=0.70,
        evidence="Apple China revenue exposure.",
    )
    return KnowledgeGraph([apple, taiwan, geo_risk, currency_risk], [r1, r2, r3])


# ---------------------------------------------------------------------------
# Group 1 — Traversal
# ---------------------------------------------------------------------------


class TestTraversal:
    def test_finds_macro_factor_endpoint(self, demo_graph: KnowledgeGraph) -> None:
        paths = get_candidate_paths("apple-inc", demo_graph)
        assert len(paths) >= 1

    def test_finds_path_of_correct_length(self, demo_graph: KnowledgeGraph) -> None:
        paths = get_candidate_paths("apple-inc", demo_graph)
        assert any(len(p) == 3 for p in paths)

    def test_excludes_geography_endpoints(self, demo_graph: KnowledgeGraph) -> None:
        """Paths that stop at Taiwan (Geography) must not appear as candidates."""
        paths = get_candidate_paths("apple-inc", demo_graph)
        for path in paths:
            endpoint_node = demo_graph.find_node(path[-1].target_id)
            assert endpoint_node is not None
            assert endpoint_node.node_class in {
                ContextNodeType.MACRO_FACTOR,
                ContextNodeType.ECONOMIC_EVENT,
            }

    def test_no_qualifying_path_returns_empty(self, no_qualifying_graph: KnowledgeGraph) -> None:
        paths = get_candidate_paths("microsoft", no_qualifying_graph)
        assert paths == ()

    def test_unknown_asset_returns_empty(self, demo_graph: KnowledgeGraph) -> None:
        paths = get_candidate_paths("nonexistent-asset", demo_graph)
        assert paths == ()

    def test_respects_max_depth(self) -> None:
        """A path requiring more than MAX_DEPTH hops should not be returned."""
        # Build a chain longer than MAX_DEPTH
        nodes = [_node(f"n{i}", f"Node {i}", ContextNodeType.GEOGRAPHY) for i in range(7)]
        endpoint = _node("endpoint", "Endpoint", ContextNodeType.MACRO_FACTOR)
        all_nodes = nodes + [endpoint]
        rels = [_rel(f"n{i}", f"n{i + 1}", evidence=f"edge {i}") for i in range(6)]
        rels.append(_rel("n6", "endpoint", RelationshipType.AFFECTED_BY, evidence="final"))
        graph = KnowledgeGraph(all_nodes, rels)
        paths = get_candidate_paths("n0", graph)
        # Path length is 7 hops — beyond MAX_DEPTH=4
        assert all(len(p) <= MAX_DEPTH for p in paths)

    def test_finds_both_qualifying_paths(self, two_path_graph: KnowledgeGraph) -> None:
        paths = get_candidate_paths("apple-inc", two_path_graph)
        # Should find both geo-risk path (2 hops) and currency-risk path (1 hop)
        assert len(paths) >= 2


# ---------------------------------------------------------------------------
# Group 2 — Ranking
# ---------------------------------------------------------------------------


class TestRanking:
    def test_rank_paths_empty_returns_none(self) -> None:
        assert rank_paths(()) is None

    def test_rank_paths_below_threshold_returns_none(self) -> None:
        """Confidence product 0.3 × 0.3 = 0.09 < 0.5 threshold."""
        path = (
            _rel("a", "b", confidence=0.3, evidence="e1"),
            _rel("b", "c", confidence=0.3, evidence="e2"),
        )
        assert rank_paths((path,)) is None

    def test_rank_paths_selects_highest_confidence(self, two_path_graph: KnowledgeGraph) -> None:
        """When two paths qualify, the one with higher confidence product wins."""
        paths = get_candidate_paths("apple-inc", two_path_graph)
        best = rank_paths(tuple(paths))
        assert best is not None
        # geo-risk path: 0.9 × 0.85 = 0.765 vs currency-risk: 0.70 — geo wins
        assert best[-1].target_id == "geo-risk-taiwan"

    def test_is_significant_passes_valid_path(self, demo_graph: KnowledgeGraph) -> None:
        paths = get_candidate_paths("apple-inc", demo_graph)
        assert any(_is_significant(p) for p in paths)

    def test_is_significant_fails_empty_path(self) -> None:
        assert not _is_significant(())

    def test_is_significant_fails_below_confidence(self) -> None:
        path = (_rel("a", "b", confidence=0.1, evidence="e"),)
        assert not _is_significant(path)

    def test_confidence_product_correct(self) -> None:
        path = (
            _rel("a", "b", confidence=0.95, evidence="e1"),
            _rel("b", "c", confidence=1.0, evidence="e2"),
            _rel("c", "d", confidence=0.85, evidence="e3"),
        )
        product = _confidence_product(path)
        assert abs(product - (0.95 * 1.0 * 0.85)) < 1e-9

    def test_confidence_product_empty_is_zero(self) -> None:
        assert _confidence_product(()) == 0.0

    def test_no_repeated_nodes_passes_simple_path(self) -> None:
        path = (
            _rel("a", "b", evidence="e1"),
            _rel("b", "c", evidence="e2"),
        )
        assert _has_no_repeated_nodes(path)

    def test_repeated_node_fails(self) -> None:
        """Apple → TSMC → Taiwan → TSMC should fail the repeated-node check."""
        path = (
            _rel("apple-inc", "tsmc", evidence="e1"),
            _rel("tsmc", "taiwan", evidence="e2"),
            _rel("taiwan", "tsmc", evidence="e3"),  # TSMC repeated
        )
        assert not _has_no_repeated_nodes(path)

    def test_rank_paths_rejects_repeated_nodes(self) -> None:
        path = (
            _rel("a", "b", confidence=0.9, evidence="e1"),
            _rel("b", "a", confidence=0.9, evidence="e2"),  # a repeated
        )
        assert rank_paths((path,)) is None


# ---------------------------------------------------------------------------
# Group 3 — Reasoning
# ---------------------------------------------------------------------------


class TestReasoning:
    def test_build_artifact_returns_reasoning_artifact(self, demo_graph: KnowledgeGraph) -> None:
        paths = get_candidate_paths("apple-inc", demo_graph)
        best = rank_paths(tuple(paths))
        assert best is not None
        artifact = build_reasoning_artifact("apple-inc", best, demo_graph)
        assert isinstance(artifact, ReasoningArtifact)

    def test_reasoning_steps_match_path_length(self, demo_graph: KnowledgeGraph) -> None:
        paths = get_candidate_paths("apple-inc", demo_graph)
        best = rank_paths(tuple(paths))
        assert best is not None
        artifact = build_reasoning_artifact("apple-inc", best, demo_graph)
        assert len(artifact.reasoning_steps) == len(best)

    def test_confidence_is_product_of_edges(self, demo_graph: KnowledgeGraph) -> None:
        paths = get_candidate_paths("apple-inc", demo_graph)
        best = rank_paths(tuple(paths))
        assert best is not None
        artifact = build_reasoning_artifact("apple-inc", best, demo_graph)
        expected = round(0.95 * 1.0 * 0.85, 4)
        assert abs(artifact.confidence - expected) < 1e-6

    def test_v01_assumptions_present(self, demo_graph: KnowledgeGraph) -> None:
        paths = get_candidate_paths("apple-inc", demo_graph)
        best = rank_paths(tuple(paths))
        assert best is not None
        artifact = build_reasoning_artifact("apple-inc", best, demo_graph)
        for assumption in V01_ASSUMPTIONS:
            assert assumption in artifact.assumptions

    def test_supporting_evidence_non_empty(self, demo_graph: KnowledgeGraph) -> None:
        paths = get_candidate_paths("apple-inc", demo_graph)
        best = rank_paths(tuple(paths))
        assert best is not None
        artifact = build_reasoning_artifact("apple-inc", best, demo_graph)
        assert len(artifact.supporting_evidence) > 0

    def test_falsifiability_conditions_non_empty(self, demo_graph: KnowledgeGraph) -> None:
        paths = get_candidate_paths("apple-inc", demo_graph)
        best = rank_paths(tuple(paths))
        assert best is not None
        artifact = build_reasoning_artifact("apple-inc", best, demo_graph)
        assert len(artifact.falsifiability_conditions) > 0

    def test_conclusion_references_endpoint(self, demo_graph: KnowledgeGraph) -> None:
        paths = get_candidate_paths("apple-inc", demo_graph)
        best = rank_paths(tuple(paths))
        assert best is not None
        artifact = build_reasoning_artifact("apple-inc", best, demo_graph)
        # Conclusion should mention the endpoint label
        assert "Taiwan Geopolitical Risk" in artifact.conclusion

    def test_each_step_has_evidence(self, demo_graph: KnowledgeGraph) -> None:
        paths = get_candidate_paths("apple-inc", demo_graph)
        best = rank_paths(tuple(paths))
        assert best is not None
        artifact = build_reasoning_artifact("apple-inc", best, demo_graph)
        for step in artifact.reasoning_steps:
            assert len(step.evidence) > 0

    def test_artifact_is_immutable(self, demo_graph: KnowledgeGraph) -> None:
        from dataclasses import FrozenInstanceError

        paths = get_candidate_paths("apple-inc", demo_graph)
        best = rank_paths(tuple(paths))
        assert best is not None
        artifact = build_reasoning_artifact("apple-inc", best, demo_graph)
        with pytest.raises(FrozenInstanceError):
            artifact.conclusion = "Hacked"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Group 4 — Public API
# ---------------------------------------------------------------------------


class TestPublicAPI:
    def test_reason_returns_none_for_no_qualifying_path(
        self, no_qualifying_graph: KnowledgeGraph
    ) -> None:
        result = reason("microsoft", no_qualifying_graph)
        assert result is None

    def test_reason_returns_artifact_for_demo_path(self, demo_graph: KnowledgeGraph) -> None:
        result = reason("apple-inc", demo_graph)
        assert isinstance(result, ReasoningArtifact)

    def test_reason_returns_none_for_unknown_asset(self, demo_graph: KnowledgeGraph) -> None:
        result = reason("completely-unknown-asset", demo_graph)
        assert result is None

    def test_reason_deterministic_same_inputs(self, demo_graph: KnowledgeGraph) -> None:
        """Same asset_id + same graph → identical ReasoningArtifact every run."""
        first = reason("apple-inc", demo_graph)
        for _ in range(9):
            result = reason("apple-inc", demo_graph)
            assert result == first

    def test_reason_does_not_modify_graph(self, demo_graph: KnowledgeGraph) -> None:
        """Janus must never modify the KnowledgeGraph it receives."""
        original_node_count = len(demo_graph)
        original_rel_count = len(demo_graph.relationships)
        reason("apple-inc", demo_graph)
        assert len(demo_graph) == original_node_count
        assert len(demo_graph.relationships) == original_rel_count

    def test_reason_confidence_in_valid_range(self, demo_graph: KnowledgeGraph) -> None:
        result = reason("apple-inc", demo_graph)
        assert result is not None
        assert 0.0 < result.confidence <= 1.0


# ---------------------------------------------------------------------------
# Group 5 — End-to-end demo path (real seed data)
# ---------------------------------------------------------------------------


class TestEndToEnd:
    """These tests use the real Atlas seed data to validate the V0.1 demo."""

    @pytest.fixture()
    def real_graph(self) -> KnowledgeGraph:
        from backend.atlas import build
        from backend.ingestion import load_asset_registry

        registry = load_asset_registry()
        return build(list(registry.assets))

    def test_apple_produces_reasoning_artifact(self, real_graph: KnowledgeGraph) -> None:
        result = reason("apple-inc", real_graph)
        assert result is not None, (
            "reason() returned None for apple-inc. "
            "The V0.1 demo depends on Apple having a qualifying path."
        )

    def test_apple_path_reaches_geopolitical_risk(self, real_graph: KnowledgeGraph) -> None:
        result = reason("apple-inc", real_graph)
        assert result is not None
        assert "Taiwan Geopolitical Risk" in result.conclusion

    def test_apple_reasoning_chain_passes_through_tsmc_taiwan(
        self, real_graph: KnowledgeGraph
    ) -> None:
        result = reason("apple-inc", real_graph)
        assert result is not None
        premises = " ".join(s.premise for s in result.reasoning_steps)
        assert "TSMC" in premises or "Taiwan Semiconductor" in premises
        assert "Taiwan" in premises

    def test_nvidia_produces_reasoning_artifact(self, real_graph: KnowledgeGraph) -> None:
        """NVIDIA shares the TSMC/Taiwan path — should also produce an artifact."""
        result = reason("nvidia", real_graph)
        assert result is not None, (
            "NVIDIA has the same TSMC dependency as Apple. "
            "Janus should produce a ReasoningArtifact for it."
        )

    def test_microsoft_returns_artifact(self, real_graph: KnowledgeGraph) -> None:
        """Microsoft now finds Interest Rate Sensitivity path in V0.2 Atlas."""
        result = reason("microsoft", real_graph)
        assert result is not None, (
            "Microsoft should find US → Fed Rate path in V0.2 Atlas."
        )

    def test_artifact_five_questions_all_answered(self, real_graph: KnowledgeGraph) -> None:
        """Every Janus §5 explainability question must be answered."""
        result = reason("apple-inc", real_graph)
        assert result is not None
        # Why? → reasoning_steps
        assert len(result.reasoning_steps) > 0
        # Supported by what? → supporting_evidence
        assert len(result.supporting_evidence) > 0
        # How confident? → confidence
        assert result.confidence > 0
        # What assumptions? → assumptions
        assert len(result.assumptions) >= 2
        # What would change this? → falsifiability_conditions
        assert len(result.falsifiability_conditions) > 0
