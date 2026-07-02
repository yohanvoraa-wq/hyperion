"""BlindSpot domain model — Titan's output.

Justified by: docs/03-BLIND-SPOT-FRAMEWORK.md, specifically:
  - §1  (Definition: hidden Exposure or unexamined assumption)
  - §3  (Taxonomy: six categories; a BlindSpot may belong to more than one)
  - §7  (Qualification Criteria: the four criteria that must ALL hold)

And: docs/07-SYSTEM-ARCHITECTURE.md §5 (Titan → Output):
  'Titan owns the qualification decision. The Output layer owns
  presentation only — it may format, visualize, or summarize, but
  the artifact it's presenting is not its own to alter.'

The four qualification criteria from Blind Spot Framework §7 are explicit
boolean fields here, not inferred from other fields. This makes Titan's
decision transparent and auditable: a BlindSpot object with qualified=False
is a record of what was evaluated and why it didn't pass, not a discarded
object. Hyperion should surface this to future reasoning.

Titan V0 sets these deterministically against the criteria text. Later
versions will compute them from the attached ReasoningArtifact's evidence.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.models.enums import BlindSpotCategory
from backend.models.reasoning_artifact import ReasoningArtifact


@dataclass(frozen=True)
class BlindSpot:
    """A candidate or qualified Blind Spot, as evaluated by Titan.

    A BlindSpot exists at two possible states:
      qualified=False — candidate, evaluated but not yet fully qualified
      qualified=True  — passed all four Blind Spot Framework §7 criteria

    The attached ReasoningArtifact is always present. Titan never creates
    a BlindSpot without one — a Blind Spot without an inspectable Reasoning
    Chain is just an assertion, and assertions have no place in Hyperion.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    title: str
    """Short, human-readable name for this Blind Spot.
    E.g. 'Concentrated geopolitical exposure via Taiwan semiconductor supply.'
    """

    description: str
    """One or two sentences describing the hidden Exposure or unexamined
    assumption this Blind Spot represents.
    Blind Spot Framework §1: hidden, unexamined, and unknowing — the
    description should make all three properties evident."""

    # ------------------------------------------------------------------
    # Taxonomy — Blind Spot Framework §3
    # ------------------------------------------------------------------

    categories: tuple[BlindSpotCategory, ...]
    """One or more taxonomy categories. A BlindSpot may belong to multiple
    categories simultaneously; the taxonomy exists to improve explanation,
    not to force single classification. Blind Spot Framework §3."""

    # ------------------------------------------------------------------
    # Severity and confidence
    # ------------------------------------------------------------------

    severity: float
    """0.0–1.0. How significantly this Blind Spot could affect the Portfolio
    if the underlying risk materialises. Titan determines this from the
    ReasoningArtifact's confidence and the Exposure magnitude it describes.
    This is not a price prediction — it is a reasoning-quality signal."""

    confidence: float
    """0.0–1.0. Inherits from supporting_reasoning.confidence — Titan cannot
    claim higher confidence in a Blind Spot than Janus had in the Reasoning
    Artifact that supports it. Per 07-SYSTEM-ARCHITECTURE.md §5: Titan may
    not edit the reasoning, so it may not inflate the confidence either."""

    # ------------------------------------------------------------------
    # Four qualification criteria — Blind Spot Framework §7
    # ------------------------------------------------------------------

    is_meaningful: bool
    """Criterion 1: would change how the investor thinks about risk or
    opportunity — not merely add a minor data point."""

    is_non_obvious: bool
    """Criterion 2: most investors, before seeing it, would be surprised.
    An investor who already knew would not be."""

    is_evidence_supported: bool
    """Criterion 3: traces back to a ReasoningArtifact that can be
    inspected — not an unexplained pattern-match."""

    changes_understanding: bool
    """Criterion 4: after encountering it, the investor's mental model of
    their Portfolio is measurably more accurate than before."""

    qualified: bool
    """True if and only if all four criteria above are True.
    Titan sets this; nothing downstream may change it. A BlindSpot with
    qualified=False is a valid, inspectable record — not a discarded object."""

    # ------------------------------------------------------------------
    # Reasoning — the mandatory attachment
    # ------------------------------------------------------------------

    supporting_reasoning: ReasoningArtifact
    """The complete Reasoning Artifact from Janus that produced this candidate.
    Per 07-SYSTEM-ARCHITECTURE.md §5: Titan evaluates this artifact, accepts
    or rejects it, and may not edit the reasoning inside it.
    A BlindSpot without a ReasoningArtifact is an assertion.
    Hyperion does not produce assertions."""
