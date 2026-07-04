"""Janus reasoner — ReasoningArtifact construction.

Justified by: docs/06-JANUS.md §4 (Reasoning Chains), §5 (Explainability),
and §6 (Output: The Reasoning Artifact).

Single responsibility: given a ranked path (a tuple of Relationships) and
the KnowledgeGraph it came from, produce a complete ReasoningArtifact that
answers all five explainability questions from Janus §5:

  Why?                    → reasoning_steps (the chain in order)
  Supported by what?      → supporting_evidence
  How confident?          → confidence (product of edge confidences)
  What assumptions?       → assumptions (V0.1 constants — Decision 5)
  What would change this? → falsifiability_conditions

No traversal. No ranking. No graph modification. Just construction.

V0.1 Assumptions (Decision 5 — frozen constants):
  Two fixed strings, not generated, not inferred. Every ReasoningArtifact
  produced by V0 Janus carries these two assumptions verbatim.
"""

from __future__ import annotations

from backend.models import KnowledgeGraph, ReasoningArtifact, ReasoningStep, Relationship
from backend.models.enums import ReasoningMode, RelationshipType

# ---------------------------------------------------------------------------
# V0.1 frozen constants — Decision 5
# ---------------------------------------------------------------------------

V01_ASSUMPTIONS: tuple[str, ...] = (
    "Finance DNA dimensions are sector-level approximations (V0.1).",
    "Atlas relationships are hand-seeded for Version 0.1.",
)
"""Fixed assumption strings for every V0 ReasoningArtifact.
Not generated. Not inferred. Constant strings per Decision 5.
These acknowledge the known limitations of V0.1 data so that no
downstream module (Titan, Output) treats a V0 artifact as if it
were backed by company-specific, disclosure-quality data."""

_V01_QUESTION: str = (
    "Does this asset have material hidden exposure through its dependency "
    "relationships in the financial knowledge graph?"
)
"""The single reasoning question Janus V0 answers.
Per the frozen design: V0 supports exactly one reasoning pattern
(Asset → Dependency → Geography → Macro Risk). One question covers it."""

# ---------------------------------------------------------------------------
# Inference templates — deterministic, per relationship type
# ---------------------------------------------------------------------------

_INFERENCE_TEMPLATES: dict[RelationshipType, str] = {
    RelationshipType.DEPENDS_ON_SUPPLIES: ("{source} has a supply chain dependency on {target}."),
    RelationshipType.LOCATED_IN: (
        "{source}'s operations are geographically concentrated in {target}."
    ),
    RelationshipType.AFFECTED_BY: ("{source} is directly exposed to the risk or event: {target}."),
    RelationshipType.BELONGS_TO: ("{source} belongs to the industry classification: {target}."),
    RelationshipType.EXPOSED_TO: ("{source} has a structural exposure to: {target}."),
    RelationshipType.REGULATED_BY: (
        "{source} is subject to regulatory requirements from: {target}."
    ),
    RelationshipType.COMPETES_WITH: ("{source} operates in direct competition with: {target}."),
    RelationshipType.SELLS_TO: (
        "{source} has a material commercial relationship selling to: {target}."
    ),
    RelationshipType.EXPORTS_TO: ("{source} has significant export revenue exposure to: {target}."),
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _label(node_id: str, graph: KnowledgeGraph) -> str:
    """Return the human-readable label for a node, or its id if not found."""
    node = graph.find_node(node_id)
    return node.label if node is not None else node_id


def _confidence_product(path: tuple[Relationship, ...]) -> float:
    product = 1.0
    for rel in path:
        product *= rel.confidence
    return product


def _build_step(rel: Relationship, graph: KnowledgeGraph) -> ReasoningStep:
    """Convert one Relationship into one ReasoningStep."""
    source_label = _label(rel.source_id, graph)
    target_label = _label(rel.target_id, graph)
    template = _INFERENCE_TEMPLATES.get(
        rel.relationship_type,
        "{source} is connected to {target}.",
    )
    return ReasoningStep(
        premise=(f"{source_label} → {rel.relationship_type.name} → {target_label}"),
        inference=template.format(source=source_label, target=target_label),
        evidence=rel.evidence,
        confidence=rel.confidence,
    )


def _build_falsifiability(
    path: tuple[Relationship, ...],
    graph: KnowledgeGraph,
    asset_id: str,
) -> tuple[str, ...]:
    """Generate the 'what would change this' conditions from the path."""
    asset_label = _label(asset_id, graph)
    endpoint_label = _label(path[-1].target_id, graph) if path else "unknown"
    return (
        f"Evidence that {asset_label} has materially reduced its supply "
        f"chain exposure would weaken this conclusion.",
        f"Evidence that '{endpoint_label}' no longer poses material risk "
        f"would weaken this conclusion.",
        "Updated Atlas relationships that supersede V0.1 hand-seeded data "
        "would require re-evaluation of this reasoning chain.",
    )


def _build_path_description(
    path: tuple[Relationship, ...],
    graph: KnowledgeGraph,
) -> str:
    """Build a readable chain description: A → B → C → D."""
    if not path:
        return ""
    nodes: list[str] = [_label(path[0].source_id, graph)]
    for rel in path:
        nodes.append(_label(rel.target_id, graph))
    return " → ".join(nodes)


# ---------------------------------------------------------------------------
# Public construction function
# ---------------------------------------------------------------------------


def build_reasoning_artifact(
    asset_id: str,
    path: tuple[Relationship, ...],
    graph: KnowledgeGraph,
) -> ReasoningArtifact:
    """Convert a ranked path into a complete, explainable ReasoningArtifact.

    Every field in the returned artifact answers one of Janus §5's five
    explainability questions. No field is left empty or populated with a
    placeholder — if this function is called, a complete artifact is produced.

    The returned artifact is immutable (frozen dataclass) per ED-005.
    """
    asset_label = _label(asset_id, graph)
    endpoint_label = _label(path[-1].target_id, graph)
    path_desc = _build_path_description(path, graph)
    confidence = round(_confidence_product(path), 4)

    return ReasoningArtifact(
        question=_V01_QUESTION,
        reasoning_mode=ReasoningMode.DEDUCTIVE,
        observation=(
            f"{asset_label} has dependency relationships in the Atlas "
            "graph that connect it to a significant macro-level risk endpoint."
        ),
        reasoning_steps=tuple(_build_step(rel, graph) for rel in path),
        conclusion=(
            f"{asset_label} has a {len(path)}-hop reasoning path to "
            f"'{endpoint_label}': {path_desc}. This represents a "
            f"potentially hidden exposure the investor may not have "
            f"explicitly accounted for."
        ),
        confidence=confidence,
        supporting_evidence=tuple(e for rel in path for e in rel.evidence),
        assumptions=V01_ASSUMPTIONS,
        falsifiability_conditions=_build_falsifiability(path, graph, asset_id),
    )
