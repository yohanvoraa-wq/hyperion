"""Atlas seed data loader.

Justified by: docs/05-ATLAS.md §3 (Node types) and §4 (Relationship types).

This module reads the two seed data files in datasets/atlas/ and returns
typed GraphNode and Relationship objects that the builder uses to construct
the KnowledgeGraph. It is internal to Atlas — nothing outside this module
reads the CSV files directly.

V0.1 data model
---------------
All V0.1 Atlas knowledge comes from two hand-seeded CSV files:
  datasets/atlas/context_nodes.csv     — non-Asset nodes
  datasets/atlas/seed_relationships.csv — canonical edges

These files are the equivalent of SCORING-RATIONALE.md for Finance DNA:
they are the human-curated ground truth that makes Atlas's graph real
rather than invented. Future milestones will supplement or replace them
with automated relationship discovery from financial filings.

Technology constraint: stdlib csv only. No pandas, no SQL, no JSON.
Same constraint as ingestion/loader.py (ED-009).
"""

from __future__ import annotations

import csv
from pathlib import Path

from backend.atlas.exceptions import OrphanedRelationshipError
from backend.models import AssetType, ContextNodeType, GraphNode, Relationship
from backend.models.enums import (
    Cardinality,
    Directionality,
    EvidenceSource,
    RelationshipTemporality,
    RelationshipType,
)

_ATLAS_DATA: Path = Path(__file__).parent.parent.parent / "datasets" / "atlas"

_CONTEXT_NODES_CSV: Path = _ATLAS_DATA / "context_nodes.csv"
_RELATIONSHIPS_CSV: Path = _ATLAS_DATA / "seed_relationships.csv"


# ---------------------------------------------------------------------------
# Node class parsing
# ---------------------------------------------------------------------------


def _parse_node_class(raw: str) -> AssetType | ContextNodeType:
    """Parse a node class string into the appropriate enum member.

    Tries AssetType first (for COMPANY, SUPPLY_CHAIN_ENTITY), then
    ContextNodeType (for GEOGRAPHY, MACRO_FACTOR, INDUSTRY, etc.).
    """
    raw = raw.strip()
    try:
        return AssetType[raw]
    except KeyError:
        pass
    try:
        return ContextNodeType[raw]
    except KeyError:
        raise ValueError(
            f"Unknown node_class '{raw}'. Must be a member of AssetType "
            f"({[m.name for m in AssetType]}) or ContextNodeType "
            f"({[m.name for m in ContextNodeType]})."
        ) from None


# ---------------------------------------------------------------------------
# Context node loader
# ---------------------------------------------------------------------------


def load_context_nodes(
    csv_path: Path | None = None,
) -> tuple[GraphNode, ...]:
    """Read context_nodes.csv and return typed GraphNode objects.

    Context nodes are non-Asset nodes: Geographies, Macro Factors,
    Industries, Commodities, Regulations, and Economic Events.
    They carry no Finance DNA (finance_dna=None).

    Parameters
    ----------
    csv_path:
        Override the default datasets/atlas/context_nodes.csv path.
        Used by tests to inject fixture data.
    """
    path = csv_path or _CONTEXT_NODES_CSV

    nodes: list[GraphNode] = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            node_id = row.get("id", "").strip()
            raw_class = row.get("node_class", "").strip()
            label = row.get("label", "").strip()

            if not node_id:
                raise ValueError(f"context_nodes.csv: row has empty 'id' field: {dict(row)}")
            if not label:
                raise ValueError(f"context_nodes.csv: node '{node_id}' has empty label.")

            nodes.append(
                GraphNode(
                    id=node_id,
                    node_class=_parse_node_class(raw_class),
                    label=label,
                    finance_dna=None,  # context nodes never carry Finance DNA
                )
            )

    return tuple(nodes)


# ---------------------------------------------------------------------------
# Relationship loader
# ---------------------------------------------------------------------------


def load_seed_relationships(
    known_node_ids: frozenset[str],
    csv_path: Path | None = None,
) -> tuple[Relationship, ...]:
    """Read seed_relationships.csv and return typed Relationship objects.

    Parameters
    ----------
    known_node_ids:
        All node ids already registered in the graph (both Asset nodes and
        context nodes). Used to validate that every relationship endpoint
        exists before the relationship is constructed. Raises
        OrphanedRelationshipError if any endpoint is missing.
    csv_path:
        Override the default datasets/atlas/seed_relationships.csv path.
    """
    path = csv_path or _RELATIONSHIPS_CSV

    relationships: list[Relationship] = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            source_id = row["source_id"].strip()
            target_id = row["target_id"].strip()

            # Validate endpoints exist before constructing Relationship.
            if source_id not in known_node_ids:
                raise OrphanedRelationshipError(source_id, target_id, source_id)
            if target_id not in known_node_ids:
                raise OrphanedRelationshipError(source_id, target_id, target_id)

            try:
                rel_type = RelationshipType[row["relationship_type"].strip()]
                directionality = Directionality[row["directionality"].strip()]
                temporality = RelationshipTemporality[row["temporality"].strip()]
                cardinality = Cardinality[row["cardinality"].strip()]
                evidence_source = EvidenceSource[row["evidence_source"].strip()]
                confidence = float(row["confidence"].strip())
                evidence_text = row["evidence"].strip()
            except KeyError as exc:
                raise ValueError(
                    f"seed_relationships.csv: unrecognised enum value in row "
                    f"{source_id} → {target_id}: {exc}"
                ) from exc

            relationships.append(
                Relationship(
                    source_id=source_id,
                    target_id=target_id,
                    relationship_type=rel_type,
                    directionality=directionality,
                    temporality=temporality,
                    cardinality=cardinality,
                    evidence_source=evidence_source,
                    confidence=confidence,
                    evidence=(evidence_text,),
                )
            )

    return tuple(relationships)
