"""Atlas layer exceptions.

Justified by: docs/05-ATLAS.md §2 (What Makes a Valid Relationship?) and
the four invariants enforced by KnowledgeGraph.__init__.

Three exception types cover the distinct Atlas failure modes:
  AtlasError             — base class; catch-all for Atlas failures
  DuplicateNodeError     — same node id appears twice
  OrphanedRelationshipError — relationship endpoint not a registered node

KnowledgeGraph itself raises ValueError for evidence and confidence
invariants (since those are structural invariants of the shared model).
AtlasError subtypes cover failures at the Atlas build layer — things that
can be caught and reported as 'the graph could not be constructed because...'
rather than generic ValueErrors from a model constructor.
"""


class AtlasError(Exception):
    """Base class for all Atlas layer errors."""


class DuplicateNodeError(AtlasError):
    """Raised when two nodes with the same id would be added to the graph.

    Atlas §1: every meaningful financial relationship has one canonical
    representation, regardless of how many assets depend on it. Two nodes
    with the same id violate that principle — they represent the same entity
    twice, which means any relationship pointing to that id is ambiguous.
    """

    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        super().__init__(
            f"Cannot add node '{node_id}' — a node with this id already exists. "
            "Atlas maintains one canonical node per entity. "
            "Check datasets/atlas/context_nodes.csv and asset resolution for duplicates."
        )


class OrphanedRelationshipError(AtlasError):
    """Raised when a seed relationship references a node that doesn't exist.

    Atlas §2 criterion 2: both endpoints of a relationship must be canonical
    nodes. A relationship pointing at a non-existent node is not a valid edge —
    it's a reference to something Atlas doesn't know about, which would silently
    produce an incorrect graph.
    """

    def __init__(self, source_id: str, target_id: str, missing_id: str) -> None:
        self.source_id = source_id
        self.target_id = target_id
        self.missing_id = missing_id
        super().__init__(
            f"Seed relationship {source_id} → {target_id} references "
            f"'{missing_id}' which is not a registered node. "
            "Add the missing node to context_nodes.csv or assets.csv "
            "before adding relationships that reference it."
        )
