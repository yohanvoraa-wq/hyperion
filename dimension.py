"""Atlas builder — the single public entry point.

Justified by: docs/05-ATLAS.md (the module as a whole) and
docs/07-SYSTEM-ARCHITECTURE.md §5 (Finance DNA → Atlas hop).

One public function: build(assets, finance_dnas) -> KnowledgeGraph.

Build sequence
--------------
1. Create one GraphNode per Asset, attaching Finance DNA if available.
2. Load context nodes from datasets/atlas/context_nodes.csv.
3. Validate no duplicate node ids across Asset nodes and context nodes.
4. Load seed relationships from datasets/atlas/seed_relationships.csv,
   validating every endpoint against the registered node set.
5. Construct and return an immutable KnowledgeGraph.

The builder never invents nodes or relationships. Every node comes from
either the Asset list (resolved by Ingestion) or the context nodes CSV.
Every relationship comes from the seed relationships CSV. Nothing is
inferred or generated — Atlas §2 criterion 1: a relationship must reflect
a real mechanism, not a pattern that 'merely happens to co-occur'.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from backend.atlas.exceptions import DuplicateNodeError
from backend.atlas.loader import load_context_nodes, load_seed_relationships
from backend.models import Asset, FinanceDNA, GraphNode, KnowledgeGraph


def build(
    assets: Sequence[Asset],
    finance_dnas: Mapping[str, FinanceDNA] | None = None,
    *,
    context_nodes_path: Path | None = None,
    relationships_path: Path | None = None,
) -> KnowledgeGraph:
    """Build the Atlas KnowledgeGraph from Assets and optional Finance DNA.

    This is the only public function in the Atlas module.

    Parameters
    ----------
    assets:
        All Assets to register as nodes. Typically: all assets from the
        Ingestion registry (not just the portfolio assets) so that
        relationships referencing non-portfolio companies like TSMC
        resolve correctly.
    finance_dnas:
        Optional mapping of asset_id → FinanceDNA. Assets present in
        this mapping get their Finance DNA attached to their GraphNode.
        Assets without a FinanceDNA entry get finance_dna=None on
        their node — the node exists and can be traversed, but Janus
        will not find dimension scores on it.
    context_nodes_path:
        Override datasets/atlas/context_nodes.csv (used by tests).
    relationships_path:
        Override datasets/atlas/seed_relationships.csv (used by tests).

    Returns
    -------
    KnowledgeGraph
        Immutable graph with all four Atlas §2 invariants enforced.

    Raises
    ------
    DuplicateNodeError
        If an Asset id collides with a context node id.
    OrphanedRelationshipError
        If a seed relationship references a node not in the graph.
    ValueError
        If any KnowledgeGraph construction invariant is violated
        (missing evidence, invalid confidence, etc.).
    """
    dnas = finance_dnas or {}

    # --- Step 1: Asset nodes ------------------------------------------
    asset_nodes: list[GraphNode] = [
        GraphNode(
            id=asset.id,
            node_class=asset.asset_type,  # AssetType.COMPANY for V0.1
            label=asset.name,
            finance_dna=dnas.get(asset.id),
        )
        for asset in assets
    ]

    # --- Step 2: Context nodes ----------------------------------------
    context_nodes = list(load_context_nodes(context_nodes_path))

    # --- Step 3: Duplicate validation ---------------------------------
    asset_ids = {n.id for n in asset_nodes}
    for ctx_node in context_nodes:
        if ctx_node.id in asset_ids:
            raise DuplicateNodeError(ctx_node.id)

    all_nodes = asset_nodes + context_nodes
    all_node_ids = frozenset(n.id for n in all_nodes)

    # --- Step 4: Seed relationships -----------------------------------
    relationships = load_seed_relationships(all_node_ids, relationships_path)

    # --- Step 5: Construct and return ---------------------------------
    return KnowledgeGraph(nodes=all_nodes, relationships=relationships)
