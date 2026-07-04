"""Tests for backend/atlas and backend/models/knowledge_graph — ED-007.

Six test groups:

  Group 1 — Graph construction
    build() produces correct nodes and relationships from seed data.
    Asset nodes and context nodes all present.
    Finance DNA attached where provided.

  Group 2 — Node traversal
    find_node, nodes_by_type, get_neighbors.

  Group 3 — Relationship traversal
    get_relationships_from, get_relationships_to,
    get_all_relationships_involving, find_paths (BFS).

  Group 4 — KnowledgeGraph invariants
    Duplicate nodes rejected. Orphaned relationships rejected.
    Missing evidence rejected. Invalid confidence rejected.

  Group 5 — Immutability
    KnowledgeGraph blocks post-construction mutation.
    GraphNode is frozen=True.

  Group 6 — Seed data integrity
    The V0.1 demo path Apple → TSMC → Taiwan → Geopolitical Risk exists.
    All seed relationship endpoints are registered nodes.

All tests use self-contained fixture assets and fixture CSV files where
possible (Group 6 uses the real seed data to validate the demo path).
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from backend.atlas import DuplicateNodeError, build
from backend.models import (
    Asset,
    AssetType,
    Cardinality,
    ContextNodeType,
    Directionality,
    EvidenceSource,
    FinanceDNA,
    GraphNode,
    KnowledgeGraph,
    Relationship,
    RelationshipTemporality,
    RelationshipType,
)

# ---------------------------------------------------------------------------
# Fixture assets — same as ingestion tests for consistency
# ---------------------------------------------------------------------------

APPLE = Asset(
    id="apple-inc",
    name="Apple Inc.",
    ticker="AAPL",
    asset_type=AssetType.COMPANY,
    sector="Technology",
    industry="Consumer Electronics",
)
MICROSOFT = Asset(
    id="microsoft",
    name="Microsoft Corporation",
    ticker="MSFT",
    asset_type=AssetType.COMPANY,
    sector="Technology",
    industry="Software",
)
NVIDIA = Asset(
    id="nvidia",
    name="NVIDIA Corporation",
    ticker="NVDA",
    asset_type=AssetType.COMPANY,
    sector="Technology",
    industry="Semiconductors",
)
TSMC = Asset(
    id="tsmc",
    name="Taiwan Semiconductor Manufacturing Company",
    ticker="TSM",
    asset_type=AssetType.COMPANY,
    sector="Technology",
    industry="Semiconductors",
)

ALL_FIXTURE_ASSETS = (APPLE, MICROSOFT, NVIDIA, TSMC)

TEST_DATE = "2024-12-31"


# ---------------------------------------------------------------------------
# Fixture graph helpers
# ---------------------------------------------------------------------------


def _make_relationship(
    source_id: str,
    target_id: str,
    rel_type: RelationshipType = RelationshipType.LOCATED_IN,
    evidence: str = "Test evidence.",
    confidence: float = 0.9,
) -> Relationship:
    return Relationship(
        source_id=source_id,
        target_id=target_id,
        relationship_type=rel_type,
        directionality=Directionality.DIRECTED,
        temporality=RelationshipTemporality.PERSISTENT,
        cardinality=Cardinality.ONE_TO_MANY,
        evidence_source=EvidenceSource.DISCLOSED,
        confidence=confidence,
        evidence=(evidence,),
    )


def _make_context_node(
    node_id: str,
    label: str,
    node_class: ContextNodeType = ContextNodeType.GEOGRAPHY,
) -> GraphNode:
    return GraphNode(id=node_id, node_class=node_class, label=label)


def _make_asset_node(asset: Asset, finance_dna: FinanceDNA | None = None) -> GraphNode:
    return GraphNode(
        id=asset.id,
        node_class=asset.asset_type,
        label=asset.name,
        finance_dna=finance_dna,
    )


# ---------------------------------------------------------------------------
# Fixture CSV files for loader tests
# ---------------------------------------------------------------------------


@pytest.fixture()
def context_nodes_csv(tmp_path: Path) -> Path:
    content = "id,node_class,label\n"
    content += "taiwan,GEOGRAPHY,Taiwan\n"
    content += "geo-risk,MACRO_FACTOR,Geopolitical Risk\n"
    content += "semis,INDUSTRY,Semiconductors\n"
    p = tmp_path / "context_nodes.csv"
    p.write_text(content)
    return p


@pytest.fixture()
def relationships_csv(tmp_path: Path) -> Path:
    header = (
        "source_id,target_id,relationship_type,directionality,"
        "temporality,cardinality,evidence_source,confidence,evidence\n"
    )
    rows = [
        "tsmc,taiwan,LOCATED_IN,DIRECTED,PERSISTENT,"
        "ONE_TO_MANY,PUBLIC_RECORD,1.0,TSMC fabs in Taiwan\n",
        "taiwan,geo-risk,AFFECTED_BY,DIRECTED,EVENT_DRIVEN,"
        "ONE_TO_MANY,PUBLIC_RECORD,0.85,Taiwan Strait tensions\n",
        "apple-inc,tsmc,DEPENDS_ON_SUPPLIES,BIDIRECTIONAL,PERSISTENT,"
        "MANY_TO_MANY,DISCLOSED,0.95,Apple TSMC dependency\n",
    ]
    content = header + "".join(rows)
    p = tmp_path / "relationships.csv"
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# Group 1 — Graph construction
# ---------------------------------------------------------------------------


class TestGraphConstruction:
    def test_build_returns_knowledge_graph(
        self,
        context_nodes_csv: Path,
        relationships_csv: Path,
    ) -> None:
        graph = build(
            ALL_FIXTURE_ASSETS,
            context_nodes_path=context_nodes_csv,
            relationships_path=relationships_csv,
        )
        assert isinstance(graph, KnowledgeGraph)

    def test_asset_nodes_present(
        self,
        context_nodes_csv: Path,
        relationships_csv: Path,
    ) -> None:
        graph = build(
            ALL_FIXTURE_ASSETS,
            context_nodes_path=context_nodes_csv,
            relationships_path=relationships_csv,
        )
        for asset in ALL_FIXTURE_ASSETS:
            node = graph.find_node(asset.id)
            assert node is not None, f"Missing node for asset {asset.id}"
            assert node.label == asset.name

    def test_context_nodes_present(
        self,
        context_nodes_csv: Path,
        relationships_csv: Path,
    ) -> None:
        graph = build(
            ALL_FIXTURE_ASSETS,
            context_nodes_path=context_nodes_csv,
            relationships_path=relationships_csv,
        )
        assert graph.find_node("taiwan") is not None
        assert graph.find_node("geo-risk") is not None
        assert graph.find_node("semis") is not None

    def test_total_node_count(
        self,
        context_nodes_csv: Path,
        relationships_csv: Path,
    ) -> None:
        graph = build(
            ALL_FIXTURE_ASSETS,
            context_nodes_path=context_nodes_csv,
            relationships_path=relationships_csv,
        )
        # 4 asset nodes + 3 context nodes = 7
        assert len(graph) == 7

    def test_finance_dna_attached_when_provided(
        self,
        context_nodes_csv: Path,
        relationships_csv: Path,
    ) -> None:
        from backend.finance_dna import evaluate

        apple_dna = evaluate(APPLE, as_of=TEST_DATE)
        graph = build(
            ALL_FIXTURE_ASSETS,
            finance_dnas={"apple-inc": apple_dna},
            context_nodes_path=context_nodes_csv,
            relationships_path=relationships_csv,
        )
        apple_node = graph.find_node("apple-inc")
        assert apple_node is not None
        assert apple_node.finance_dna is not None
        assert apple_node.finance_dna.asset_id == "apple-inc"

    def test_finance_dna_none_when_not_provided(
        self,
        context_nodes_csv: Path,
        relationships_csv: Path,
    ) -> None:
        graph = build(
            ALL_FIXTURE_ASSETS,
            context_nodes_path=context_nodes_csv,
            relationships_path=relationships_csv,
        )
        # No finance_dnas provided — all asset nodes get finance_dna=None
        for asset in ALL_FIXTURE_ASSETS:
            node = graph.find_node(asset.id)
            assert node is not None
            assert node.finance_dna is None

    def test_context_nodes_never_get_finance_dna(
        self,
        context_nodes_csv: Path,
        relationships_csv: Path,
    ) -> None:
        from backend.finance_dna import evaluate

        dnas = {a.id: evaluate(a, as_of=TEST_DATE) for a in ALL_FIXTURE_ASSETS}
        graph = build(
            ALL_FIXTURE_ASSETS,
            finance_dnas=dnas,
            context_nodes_path=context_nodes_csv,
            relationships_path=relationships_csv,
        )
        taiwan = graph.find_node("taiwan")
        assert taiwan is not None
        assert taiwan.finance_dna is None  # context nodes never get Finance DNA

    def test_seed_relationships_loaded(
        self,
        context_nodes_csv: Path,
        relationships_csv: Path,
    ) -> None:
        graph = build(
            ALL_FIXTURE_ASSETS,
            context_nodes_path=context_nodes_csv,
            relationships_path=relationships_csv,
        )
        assert len(graph.relationships) == 3

    def test_duplicate_node_id_raises(
        self, context_nodes_csv: Path, relationships_csv: Path, tmp_path: Path
    ) -> None:
        """A context node id matching an asset id raises DuplicateNodeError."""
        bad_csv = tmp_path / "bad_ctx.csv"
        bad_csv.write_text(
            "id,node_class,label\napple-inc,GEOGRAPHY,Taiwan\n"  # clashes with Asset
        )
        with pytest.raises(DuplicateNodeError) as exc_info:
            build(
                ALL_FIXTURE_ASSETS,
                context_nodes_path=bad_csv,
                relationships_path=relationships_csv,
            )
        assert exc_info.value.node_id == "apple-inc"


# ---------------------------------------------------------------------------
# Group 2 — Node traversal
# ---------------------------------------------------------------------------


class TestNodeTraversal:
    @pytest.fixture()
    def simple_graph(self) -> KnowledgeGraph:
        apple = _make_asset_node(APPLE)
        taiwan = _make_context_node("taiwan", "Taiwan")
        geo_risk = _make_context_node("geo-risk", "Geopolitical Risk", ContextNodeType.MACRO_FACTOR)
        rel1 = _make_relationship("apple-inc", "taiwan")
        rel2 = _make_relationship("taiwan", "geo-risk", RelationshipType.AFFECTED_BY)
        return KnowledgeGraph([apple, taiwan, geo_risk], [rel1, rel2])

    def test_find_node_returns_correct_node(self, simple_graph: KnowledgeGraph) -> None:
        node = simple_graph.find_node("taiwan")
        assert node is not None
        assert node.label == "Taiwan"
        assert node.node_class == ContextNodeType.GEOGRAPHY

    def test_find_node_returns_none_for_missing(self, simple_graph: KnowledgeGraph) -> None:
        assert simple_graph.find_node("does-not-exist") is None

    def test_nodes_by_type_company(self, simple_graph: KnowledgeGraph) -> None:
        company_nodes = simple_graph.nodes_by_type(AssetType.COMPANY)
        assert len(company_nodes) == 1
        assert company_nodes[0].id == "apple-inc"

    def test_nodes_by_type_geography(self, simple_graph: KnowledgeGraph) -> None:
        geo_nodes = simple_graph.nodes_by_type(ContextNodeType.GEOGRAPHY)
        assert len(geo_nodes) == 1
        assert geo_nodes[0].id == "taiwan"

    def test_get_neighbors_from_apple(self, simple_graph: KnowledgeGraph) -> None:
        neighbors = simple_graph.get_neighbors("apple-inc")
        neighbor_ids = {n.id for n in neighbors}
        assert "taiwan" in neighbor_ids

    def test_get_neighbors_from_taiwan(self, simple_graph: KnowledgeGraph) -> None:
        neighbors = simple_graph.get_neighbors("taiwan")
        neighbor_ids = {n.id for n in neighbors}
        assert "apple-inc" in neighbor_ids  # incoming
        assert "geo-risk" in neighbor_ids  # outgoing


# ---------------------------------------------------------------------------
# Group 3 — Relationship traversal
# ---------------------------------------------------------------------------


class TestRelationshipTraversal:
    @pytest.fixture()
    def chain_graph(self) -> KnowledgeGraph:
        """Apple → TSMC → Taiwan → Geo Risk"""
        apple = _make_asset_node(APPLE)
        tsmc = _make_asset_node(TSMC)
        taiwan = _make_context_node("taiwan", "Taiwan")
        geo_risk = _make_context_node("geo-risk", "Geopolitical Risk", ContextNodeType.MACRO_FACTOR)
        r1 = _make_relationship(
            "apple-inc", "tsmc", RelationshipType.DEPENDS_ON_SUPPLIES, "Apple depends on TSMC."
        )
        r2 = _make_relationship("tsmc", "taiwan", evidence="TSMC fabs in Taiwan.")
        r3 = _make_relationship(
            "taiwan", "geo-risk", RelationshipType.AFFECTED_BY, "Taiwan Strait tensions."
        )
        return KnowledgeGraph([apple, tsmc, taiwan, geo_risk], [r1, r2, r3])

    def test_get_relationships_from_apple(self, chain_graph: KnowledgeGraph) -> None:
        rels = chain_graph.get_relationships_from("apple-inc")
        assert len(rels) == 1
        assert rels[0].target_id == "tsmc"

    def test_get_relationships_to_taiwan(self, chain_graph: KnowledgeGraph) -> None:
        rels = chain_graph.get_relationships_to("taiwan")
        assert len(rels) == 1
        assert rels[0].source_id == "tsmc"

    def test_get_all_relationships_involving_tsmc(self, chain_graph: KnowledgeGraph) -> None:
        rels = chain_graph.get_all_relationships_involving("tsmc")
        endpoints = {(r.source_id, r.target_id) for r in rels}
        assert ("apple-inc", "tsmc") in endpoints  # incoming
        assert ("tsmc", "taiwan") in endpoints  # outgoing

    def test_find_paths_apple_to_geo_risk(self, chain_graph: KnowledgeGraph) -> None:
        """The core V0.1 demo path must be discoverable."""
        paths = chain_graph.find_paths("apple-inc", "geo-risk")
        assert len(paths) >= 1
        # The path should be: apple → tsmc → taiwan → geo-risk (3 hops)
        assert any(len(p) == 3 for p in paths)

    def test_find_paths_respects_max_depth(self, chain_graph: KnowledgeGraph) -> None:
        """max_depth=1 should find no path Apple → Geo Risk (needs 3 hops)."""
        paths = chain_graph.find_paths("apple-inc", "geo-risk", max_depth=1)
        assert paths == ()

    def test_find_paths_same_node_returns_empty_path(self, chain_graph: KnowledgeGraph) -> None:
        paths = chain_graph.find_paths("apple-inc", "apple-inc")
        assert paths == ((),)

    def test_find_paths_no_connection_returns_empty(self, chain_graph: KnowledgeGraph) -> None:
        """There is no path from geo-risk back to apple-inc (directed graph)."""
        paths = chain_graph.find_paths("geo-risk", "apple-inc")
        assert paths == ()

    def test_get_relationships_from_unconnected_node_returns_empty(
        self, chain_graph: KnowledgeGraph
    ) -> None:
        rels = chain_graph.get_relationships_from("geo-risk")
        assert rels == ()


# ---------------------------------------------------------------------------
# Group 4 — KnowledgeGraph invariants
# ---------------------------------------------------------------------------


class TestKnowledgeGraphInvariants:
    def test_duplicate_node_id_raises_value_error(self) -> None:
        node1 = _make_context_node("taiwan", "Taiwan")
        node2 = _make_context_node("taiwan", "Taiwan (duplicate)")
        with pytest.raises(ValueError, match="Duplicate"):
            KnowledgeGraph([node1, node2], [])

    def test_orphaned_relationship_source_raises(self) -> None:
        taiwan = _make_context_node("taiwan", "Taiwan")
        bad_rel = _make_relationship("does-not-exist", "taiwan")
        with pytest.raises(ValueError, match="does-not-exist"):
            KnowledgeGraph([taiwan], [bad_rel])

    def test_orphaned_relationship_target_raises(self) -> None:
        taiwan = _make_context_node("taiwan", "Taiwan")
        bad_rel = _make_relationship("taiwan", "does-not-exist")
        with pytest.raises(ValueError, match="does-not-exist"):
            KnowledgeGraph([taiwan], [bad_rel])

    def test_empty_evidence_raises(self) -> None:
        taiwan = _make_context_node("taiwan", "Taiwan")
        geo_risk = _make_context_node("geo-risk", "Geo Risk")
        bad_rel = Relationship(
            source_id="taiwan",
            target_id="geo-risk",
            relationship_type=RelationshipType.AFFECTED_BY,
            directionality=Directionality.DIRECTED,
            temporality=RelationshipTemporality.PERSISTENT,
            cardinality=Cardinality.ONE_TO_MANY,
            evidence_source=EvidenceSource.DISCLOSED,
            confidence=0.9,
            evidence=(),  # empty — violates Atlas §2 criterion 4
        )
        with pytest.raises(ValueError, match="evidence"):
            KnowledgeGraph([taiwan, geo_risk], [bad_rel])

    def test_zero_confidence_raises(self) -> None:
        taiwan = _make_context_node("taiwan", "Taiwan")
        geo_risk = _make_context_node("geo-risk", "Geo Risk")
        with pytest.raises(ValueError, match="confidence"):
            KnowledgeGraph(
                [taiwan, geo_risk],
                [_make_relationship("taiwan", "geo-risk", confidence=0.0)],
            )

    def test_confidence_above_one_raises(self) -> None:
        taiwan = _make_context_node("taiwan", "Taiwan")
        geo_risk = _make_context_node("geo-risk", "Geo Risk")
        with pytest.raises(ValueError, match="confidence"):
            KnowledgeGraph(
                [taiwan, geo_risk],
                [_make_relationship("taiwan", "geo-risk", confidence=1.1)],
            )

    def test_empty_graph_is_valid(self) -> None:
        graph = KnowledgeGraph([], [])
        assert len(graph) == 0

    def test_single_node_no_relationships_is_valid(self) -> None:
        taiwan = _make_context_node("taiwan", "Taiwan")
        graph = KnowledgeGraph([taiwan], [])
        assert len(graph) == 1
        assert graph.find_node("taiwan") is not None


# ---------------------------------------------------------------------------
# Group 5 — Immutability
# ---------------------------------------------------------------------------


class TestImmutability:
    def test_knowledge_graph_blocks_post_construction_mutation(self) -> None:
        graph = KnowledgeGraph([], [])
        with pytest.raises(AttributeError, match="immutable"):
            graph._nodes = ()

    def test_graph_node_is_frozen(self) -> None:
        node = _make_context_node("taiwan", "Taiwan")
        with pytest.raises(FrozenInstanceError):
            node.label = "Hacked"  # type: ignore[misc]

    def test_nodes_property_returns_tuple(self) -> None:
        taiwan = _make_context_node("taiwan", "Taiwan")
        graph = KnowledgeGraph([taiwan], [])
        assert isinstance(graph.nodes, tuple)

    def test_relationships_property_returns_tuple(self) -> None:
        taiwan = _make_context_node("taiwan", "Taiwan")
        geo = _make_context_node("geo", "Geo")
        rel = _make_relationship("taiwan", "geo")
        graph = KnowledgeGraph([taiwan, geo], [rel])
        assert isinstance(graph.relationships, tuple)


# ---------------------------------------------------------------------------
# Group 6 — Seed data integrity (uses real datasets/atlas/ CSV files)
# ---------------------------------------------------------------------------


class TestSeedDataIntegrity:
    """These tests use the real seed data files to validate the V0.1 demo path."""

    @pytest.fixture()
    def full_registry_graph(self) -> KnowledgeGraph:
        """Build the graph with all 7 assets from datasets/assets.csv."""
        from backend.ingestion import load_asset_registry

        registry = load_asset_registry()
        all_assets = list(registry.assets)
        return build(all_assets)  # uses real seed CSV files

    def test_demo_path_apple_tsmc_taiwan_geo_risk_exists(
        self, full_registry_graph: KnowledgeGraph
    ) -> None:
        """The V0.1 demo Blind Spot path must be traversable end to end."""
        paths = full_registry_graph.find_paths("apple-inc", "geopolitical-risk-taiwan")
        assert len(paths) >= 1, (
            "No path found from apple-inc to geopolitical-risk-taiwan. "
            "The V0.1 demo Blind Spot depends on this path existing."
        )

    def test_demo_path_nvidia_tsmc_taiwan_geo_risk_exists(
        self, full_registry_graph: KnowledgeGraph
    ) -> None:
        """NVIDIA shares the same geopolitical exposure via TSMC."""
        paths = full_registry_graph.find_paths("nvidia", "geopolitical-risk-taiwan")
        assert len(paths) >= 1

    def test_all_seed_relationship_endpoints_are_nodes(
        self, full_registry_graph: KnowledgeGraph
    ) -> None:
        """Every relationship in the graph has both endpoints registered."""
        node_ids = {n.id for n in full_registry_graph.nodes}
        for rel in full_registry_graph.relationships:
            assert rel.source_id in node_ids, f"Source '{rel.source_id}' not in graph nodes."
            assert rel.target_id in node_ids, f"Target '{rel.target_id}' not in graph nodes."

    def test_all_relationships_have_evidence(self, full_registry_graph: KnowledgeGraph) -> None:
        for rel in full_registry_graph.relationships:
            assert len(rel.evidence) > 0
            assert all(len(e.strip()) > 0 for e in rel.evidence)

    def test_tsmc_node_exists_as_asset(self, full_registry_graph: KnowledgeGraph) -> None:
        tsmc_node = full_registry_graph.find_node("tsmc")
        assert tsmc_node is not None
        assert tsmc_node.node_class == AssetType.COMPANY

    def test_taiwan_node_exists_as_geography(self, full_registry_graph: KnowledgeGraph) -> None:
        taiwan = full_registry_graph.find_node("taiwan")
        assert taiwan is not None
        assert taiwan.node_class == ContextNodeType.GEOGRAPHY
