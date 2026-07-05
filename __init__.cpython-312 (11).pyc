"""KnowledgeGraph domain model — Atlas's cross-module artifact.

Justified by: docs/05-ATLAS.md (the module as a whole) and
docs/07-SYSTEM-ARCHITECTURE.md §5 (Atlas → Janus hop).

KnowledgeGraph is the artifact Atlas produces and Janus consumes. It lives
in backend/models/ for the same reason every cross-module artifact does.

Design decisions
----------------
Not a frozen dataclass: KnowledgeGraph needs internal lookup indices
(node_index, adjacency maps) built at construction time for O(1) traversal.
A frozen dataclass cannot hold dicts. Instead, immutability is enforced
structurally: all public properties return tuples (immutable), all internal
dicts are wrapped in MappingProxyType (prevents external mutation), and
__setattr__ is overridden to block post-construction assignment.

Traversal methods live here, not in a separate Atlas query module: Janus
needs to traverse the graph; Janus imports from backend.models, not from
backend.atlas. Keeping traversal here maintains the clean module boundary.

Atlas §2 invariants enforced at construction:
  1. No duplicate node IDs.
  2. Every relationship endpoint must exist as a node.
  3. Every relationship carries non-empty evidence.
  4. Every relationship confidence is in (0.0, 1.0].
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from types import MappingProxyType

from backend.models.enums import AssetType, ContextNodeType
from backend.models.graph_node import GraphNode
from backend.models.relationship import Relationship


class KnowledgeGraph:
    """Immutable knowledge graph artifact. Build once via Atlas; traverse many times.

    Internally maintains four lookup structures, all wrapped in MappingProxyType:
      _node_index   : id → GraphNode          (O(1) node lookup)
      _outgoing     : source_id → (Relationship, ...) (outgoing edges)
      _incoming     : target_id → (Relationship, ...) (incoming edges)

    Post-construction mutation is blocked by __setattr__.
    """

    # Class-level annotations required by mypy --strict for instance attributes.
    _nodes: tuple[GraphNode, ...]
    _relationships: tuple[Relationship, ...]
    _node_index: Mapping[str, GraphNode]
    _outgoing: Mapping[str, tuple[Relationship, ...]]
    _incoming: Mapping[str, tuple[Relationship, ...]]
    _initialised: bool

    def __init__(
        self,
        nodes: Sequence[GraphNode],
        relationships: Sequence[Relationship],
    ) -> None:
        """Build and validate a KnowledgeGraph.

        Parameters
        ----------
        nodes:
            All nodes in the graph. Every node must have a unique id.
        relationships:
            All edges in the graph. Both endpoints of every edge must be
            registered in nodes.

        Raises
        ------
        ValueError
            If any Atlas §2 invariant is violated (duplicate node,
            orphaned relationship, missing evidence, invalid confidence).
        """
        # Mark as not yet initialised so __setattr__ allows the initial sets.
        object.__setattr__(self, "_initialised", False)

        node_list = list(nodes)
        rel_list = list(relationships)

        # --- Invariant 1: no duplicate node IDs ---------------------
        seen_ids: set[str] = set()
        for node in node_list:
            if node.id in seen_ids:
                raise ValueError(
                    f"Duplicate node id '{node.id}' in KnowledgeGraph. "
                    "Atlas §1: every meaningful relationship has one "
                    "canonical representation. Two nodes with the same id "
                    "violate that principle."
                )
            seen_ids.add(node.id)

        # Build node index early (needed for relationship validation).
        raw_node_index: dict[str, GraphNode] = {n.id: n for n in node_list}

        # --- Invariant 2: every relationship endpoint must be a node --
        for rel in rel_list:
            if rel.source_id not in raw_node_index:
                raise ValueError(
                    f"Relationship {rel.relationship_type.name} references "
                    f"source '{rel.source_id}' which is not a registered node. "
                    "Add the node before adding relationships that reference it."
                )
            if rel.target_id not in raw_node_index:
                raise ValueError(
                    f"Relationship {rel.relationship_type.name} references "
                    f"target '{rel.target_id}' which is not a registered node. "
                    "Add the node before adding relationships that reference it."
                )

        # --- Invariant 3: every relationship must carry evidence ------
        for rel in rel_list:
            if not rel.evidence or all(not e.strip() for e in rel.evidence):
                raise ValueError(
                    f"Relationship {rel.source_id} → {rel.target_id} "
                    f"({rel.relationship_type.name}) has no evidence. "
                    "Atlas §2 criterion 4: every relationship must be "
                    "evidence-traceable."
                )

        # --- Invariant 4: confidence must be in (0, 1] ---------------
        for rel in rel_list:
            if not (0.0 < rel.confidence <= 1.0):
                raise ValueError(
                    f"Relationship {rel.source_id} → {rel.target_id} "
                    f"has confidence {rel.confidence}, which is outside (0, 1]. "
                    "Confidence of 0.0 is meaningless; confidence > 1.0 is invalid."
                )

        # --- Build adjacency indices ----------------------------------
        raw_outgoing: dict[str, list[Relationship]] = defaultdict(list)
        raw_incoming: dict[str, list[Relationship]] = defaultdict(list)
        for rel in rel_list:
            raw_outgoing[rel.source_id].append(rel)
            raw_incoming[rel.target_id].append(rel)

        # --- Freeze everything ---------------------------------------
        object.__setattr__(self, "_nodes", tuple(node_list))
        object.__setattr__(self, "_relationships", tuple(rel_list))
        object.__setattr__(
            self,
            "_node_index",
            MappingProxyType(raw_node_index),
        )
        object.__setattr__(
            self,
            "_outgoing",
            MappingProxyType({k: tuple(v) for k, v in raw_outgoing.items()}),
        )
        object.__setattr__(
            self,
            "_incoming",
            MappingProxyType({k: tuple(v) for k, v in raw_incoming.items()}),
        )
        object.__setattr__(self, "_initialised", True)

    def __setattr__(self, name: str, value: object) -> None:
        """Block post-construction mutation."""
        if getattr(self, "_initialised", False):
            raise AttributeError(
                "KnowledgeGraph is immutable after construction. "
                "Build a new KnowledgeGraph with Atlas to change the graph."
            )
        object.__setattr__(self, name, value)

    # ------------------------------------------------------------------
    # Properties — read-only access to the frozen internals
    # ------------------------------------------------------------------

    @property
    def nodes(self) -> tuple[GraphNode, ...]:
        """All nodes in the graph, in insertion order."""
        return self._nodes

    @property
    def relationships(self) -> tuple[Relationship, ...]:
        """All relationships in the graph, in insertion order."""
        return self._relationships

    def __len__(self) -> int:
        """Number of nodes in the graph."""
        return len(self._nodes)

    def __repr__(self) -> str:
        return (
            f"KnowledgeGraph("
            f"{len(self._nodes)} nodes, "
            f"{len(self._relationships)} relationships)"
        )

    # ------------------------------------------------------------------
    # Traversal — Phase 3 query interface
    # ------------------------------------------------------------------

    def find_node(self, node_id: str) -> GraphNode | None:
        """Return the node with this id, or None if not found."""
        return self._node_index.get(node_id)

    def nodes_by_type(
        self,
        node_class: AssetType | ContextNodeType,
    ) -> tuple[GraphNode, ...]:
        """Return all nodes of a specific type."""
        return tuple(n for n in self._nodes if n.node_class == node_class)

    def get_relationships_from(self, node_id: str) -> tuple[Relationship, ...]:
        """Return all relationships where node_id is the source.

        For DIRECTED and BIDIRECTIONAL edges stored with this node as source.
        For SYMMETRIC edges, both directions are stored; use
        get_all_relationships_involving() to see both.
        """
        return self._outgoing.get(node_id, ())

    def get_relationships_to(self, node_id: str) -> tuple[Relationship, ...]:
        """Return all relationships where node_id is the target."""
        return self._incoming.get(node_id, ())

    def get_all_relationships_involving(
        self,
        node_id: str,
    ) -> tuple[Relationship, ...]:
        """Return all relationships where node_id appears as source or target.

        Used by Janus when it needs to traverse bidirectional edges from
        either endpoint — e.g. 'what does TSMC supply?' requires looking
        at relationships where TSMC is the target of DEPENDS_ON_SUPPLIES.
        """
        outgoing = set(self._outgoing.get(node_id, ()))
        incoming = set(self._incoming.get(node_id, ()))
        return tuple(outgoing | incoming)

    def get_neighbors(self, node_id: str) -> tuple[GraphNode, ...]:
        """Return all nodes directly reachable from node_id via any edge.

        Includes both outgoing targets and incoming sources, so bidirectional
        edges are traversable from either endpoint.
        """
        neighbor_ids: set[str] = set()
        for rel in self._outgoing.get(node_id, ()):
            neighbor_ids.add(rel.target_id)
        for rel in self._incoming.get(node_id, ()):
            neighbor_ids.add(rel.source_id)
        neighbor_ids.discard(node_id)  # exclude self-loops if any
        return tuple(
            self._node_index[nid]
            for nid in neighbor_ids
            if nid in self._node_index
        )

    def find_paths(
        self,
        from_id: str,
        to_id: str,
        *,
        max_depth: int = 6,
    ) -> tuple[tuple[Relationship, ...], ...]:
        """Find all simple paths from from_id to to_id within max_depth hops.

        Returns a tuple of paths, each path being a tuple of Relationships
        in traversal order. Returns an empty tuple if no path exists.

        This is the primary method Janus uses to discover Reasoning Paths.
        Atlas stores the paths; Janus selects which one answers a question.
        Per Atlas §7: 'Atlas stores possibilities. Janus chooses paths.'

        Uses BFS to find shortest paths first. Simple paths only (no cycles).
        """
        if from_id not in self._node_index or to_id not in self._node_index:
            return ()
        if from_id == to_id:
            return ((),)

        # BFS: queue of (current_node_id, path_so_far, visited_ids)
        found: list[tuple[Relationship, ...]] = []
        queue: list[tuple[str, tuple[Relationship, ...], frozenset[str]]] = [
            (from_id, (), frozenset({from_id}))
        ]

        while queue:
            current_id, path, visited = queue.pop(0)
            if len(path) >= max_depth:
                continue
            for rel in self.get_relationships_from(current_id):
                next_id = rel.target_id
                if next_id in visited:
                    continue
                new_path = (*path, rel)
                if next_id == to_id:
                    found.append(new_path)
                else:
                    queue.append((next_id, new_path, visited | {next_id}))

        return tuple(found)
