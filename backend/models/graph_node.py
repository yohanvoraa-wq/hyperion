"""GraphNode domain model — an Atlas node.

Justified by: docs/05-ATLAS.md §3 (What Kinds of Nodes Exist?) and
docs/07-SYSTEM-ARCHITECTURE.md §3 (Atlas owns Relationships).

GraphNode lives in backend/models/ because it crosses the Atlas→Janus
boundary. Atlas produces GraphNodes inside a KnowledgeGraph; Janus reads
them when traversing Reasoning Paths. Neither module should know the
other's internals — only the shared model definition here.

Two classes of node, per Atlas §3:
  ECONOMIC ACTORS   — things that act and hold Finance DNA (AssetType)
  ECONOMIC CONTEXT  — things actors depend on (ContextNodeType)

The finance_dna field is None for Economic Context nodes (they have no
Finance DNA) and populated for Economic Actor (Asset) nodes. This is what
lets Janus, when traversing a path through Atlas, read the Dimension scores
of every company along the chain without calling Finance DNA directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.models.enums import AssetType, ContextNodeType
from backend.models.finance_dna import FinanceDNA


@dataclass(frozen=True)
class GraphNode:
    """An immutable node in the Atlas KnowledgeGraph.

    Every node is either an Economic Actor (an Asset — a company with
    Finance DNA) or an Economic Context (a Commodity, Geography, Macro
    Factor, Industry, Regulation, or Economic Event).

    The distinction matters for traversal: Janus can read the Finance DNA
    of any Asset node it reaches. Context nodes carry a label and type
    only — no scoring.
    """

    id: str
    """Canonical identifier. For Asset nodes: Asset.id. For context nodes:
    a stable slug (e.g. 'taiwan', 'geopolitical-risk-taiwan') defined in
    datasets/atlas/context_nodes.csv. Once set, never changes — Atlas §1:
    every meaningful relationship has one canonical representation."""

    node_class: AssetType | ContextNodeType
    """The specific node type from Atlas §3.
    AssetType.COMPANY          — publicly traded company (V0.1 scope)
    AssetType.SUPPLY_CHAIN_ENTITY — non-Asset supply chain participant
    ContextNodeType.GEOGRAPHY  — country or region
    ContextNodeType.MACRO_FACTOR — external force affecting many Assets
    ContextNodeType.INDUSTRY   — sector classification
    ContextNodeType.COMMODITY  — fungible physical/financial input
    ContextNodeType.CURRENCY   — unit of account
    ContextNodeType.REGULATION — regulatory regime
    ContextNodeType.ECONOMIC_EVENT — discrete occurrence (drought, etc.)
    """

    label: str
    """Human-readable display name (e.g. 'Apple Inc.', 'Taiwan')."""

    finance_dna: FinanceDNA | None = field(default=None)
    """Finance DNA artifact for this node.
    Populated for AssetType nodes; None for all ContextNodeType nodes.
    Atlas §3: Economic Context nodes 'carry no Finance DNA of their own.'
    This field is what lets Janus read dimension scores at traversal time
    without re-entering the Finance DNA module."""
