"""Titan qualification engine.

Justified by: docs/03-BLIND-SPOT-FRAMEWORK.md §7 (Qualification Criteria)
and docs/07-SYSTEM-ARCHITECTURE.md §5 (Janus → Titan hop).

Titan's responsibility in one sentence:
Titan evaluates a ReasoningArtifact against the Blind Spot qualification
framework and produces a BlindSpot artifact only if every qualification
criterion is satisfied.

The four criteria below map directly to 03-BLIND-SPOT-FRAMEWORK.md §7.
No new criteria are introduced. No criteria are omitted. No interpretation
beyond what the document states.

V0.1 deterministic implementations
-----------------------------------
The Blind Spot Framework defines four criteria qualitatively. V0.1
encodes each as a deterministic check against the ReasoningArtifact's
fields. Each criterion's docstring states both the §7 text and the V0.1
rule so future contributors can distinguish the conceptual requirement from
its current implementation.

Confidence (Decision 4 — frozen):
Titan never recalculates confidence. It inherits ReasoningArtifact.confidence
directly. Janus owns confidence; Titan only qualifies based on it.

Return behaviour (Decision 3 — frozen):
Any criterion that evaluates False causes qualify() to return None.
No partial BlindSpot. No weak BlindSpot. Silence is preferable to a
conclusion that cannot be fully defended.
"""

from __future__ import annotations

from backend.models import BlindSpot, ReasoningArtifact
from backend.models.enums import BlindSpotCategory

# ---------------------------------------------------------------------------
# V0.1 thresholds — frozen for this version
# ---------------------------------------------------------------------------

_MIN_CONFIDENCE: float = 0.5
"""Minimum confidence for a ReasoningArtifact to be considered meaningful.
Same threshold as Janus's MIN_CONFIDENCE_PRODUCT — both modules agree on
the minimum evidential bar an artifact must clear to be worth surfacing."""

_MIN_STEPS_MEANINGFUL: int = 1
"""Minimum reasoning steps for criterion 1 (meaningful).
Even a single-hop connection can be meaningful if it has sufficient confidence.
Criterion 2 (non-obvious) handles the depth requirement separately."""

_MIN_STEPS_NON_OBVIOUS: int = 2
"""Minimum reasoning steps for criterion 2 (non-obvious).
A direct single-hop connection between an Asset and a Macro Factor is more
likely to be known to the investor — it appears directly in portfolio
documentation. Two or more hops implies structural indirection that most
investors would not have traced explicitly."""

# ---------------------------------------------------------------------------
# The four qualification criteria — direct encoding of §7
# ---------------------------------------------------------------------------


def _is_meaningful(artifact: ReasoningArtifact) -> bool:
    """Criterion 1 — Meaningful.

    §7: 'It would change how the investor thinks about risk or opportunity
    in their Portfolio, not just add a minor data point.'

    V0.1 rule: The artifact contains at least one reasoning step (something
    concrete happened along the chain) AND the confidence meets the minimum
    threshold. A high-confidence trivial observation is meaningful; a
    low-confidence chain is not — regardless of its length.
    """
    return (
        len(artifact.reasoning_steps) >= _MIN_STEPS_MEANINGFUL
        and artifact.confidence >= _MIN_CONFIDENCE
    )


def _is_non_obvious(artifact: ReasoningArtifact) -> bool:
    """Criterion 2 — Non-obvious.

    §7: 'Most investors, before seeing it, would be surprised. An investor
    who already knew about it would not be.'

    V0.1 rule: The reasoning chain contains at least two hops. A single-hop
    direct connection (Asset EXPOSED_TO Macro Factor) is observable from
    standard portfolio documentation. Two or more hops implies a structural
    indirection — a supply chain exposure that passes through an intermediate
    entity — that most investors would not have traced explicitly.
    """
    return len(artifact.reasoning_steps) >= _MIN_STEPS_NON_OBVIOUS


def _is_evidence_supported(artifact: ReasoningArtifact) -> bool:
    """Criterion 3 — Evidence-supported.

    §7: 'It traces back to a Reasoning Chain that can be inspected, not an
    unexplained pattern-match.'

    V0.1 rule: The artifact has at least one reasoning step, at least one
    piece of supporting evidence, and every evidence string is non-empty.
    An artifact with steps but no evidence is an assertion, not an argument.
    """
    return (
        len(artifact.reasoning_steps) >= 1
        and len(artifact.supporting_evidence) >= 1
        and all(e.strip() for e in artifact.supporting_evidence)
    )


def _changes_understanding(artifact: ReasoningArtifact) -> bool:
    """Criterion 4 — Changes the user's understanding.

    §7: 'After encountering it, the investor's mental model of their Portfolio
    is measurably more accurate than before.'

    V0.1 rule: The artifact has at least one falsifiability condition. An
    artifact that cannot state what would make it wrong is not a genuine
    claim about the world — it cannot change understanding because it cannot
    be checked. A falsifiable conclusion is one the investor can act on or
    monitor; an unfalsifiable one is empty reassurance.
    """
    return len(artifact.falsifiability_conditions) >= 1


# ---------------------------------------------------------------------------
# BlindSpot construction helpers
# ---------------------------------------------------------------------------


def _derive_categories(
    artifact: ReasoningArtifact,
) -> tuple[BlindSpotCategory, ...]:
    """Assign Blind Spot taxonomy categories from the artifact.

    V0.1: All Janus artifacts end at MACRO_FACTOR or ECONOMIC_EVENT (enforced
    by traversal.py). The path always includes at least one dependency hop
    (the V0.1 pattern is Asset → Dependency → Geography → Macro Risk).
    Both DEPENDENCY and MACROECONOMIC apply to every V0.1 finding.

    Future versions will inspect reasoning_steps' relationship types to
    assign categories more precisely — for example, detecting STRUCTURAL
    when the chain passes through a supply chain entity, or TEMPORAL when
    a time-limited relationship is involved.
    """
    return (BlindSpotCategory.DEPENDENCY, BlindSpotCategory.MACROECONOMIC)


# ---------------------------------------------------------------------------
# Public qualification function
# ---------------------------------------------------------------------------


def qualify(
    reasoning_artifact: ReasoningArtifact,
) -> BlindSpot | None:
    """Evaluate a ReasoningArtifact against all four Blind Spot criteria.

    This is the only public function in the Titan module.

    Each of the four criteria from 03-BLIND-SPOT-FRAMEWORK.md §7 is
    evaluated independently. If any criterion evaluates False, the function
    returns None immediately. No partial BlindSpot is produced.

    Titan never modifies the ReasoningArtifact it receives. The
    supporting_reasoning field of the returned BlindSpot is a direct
    reference to the artifact passed in — not a copy.

    Parameters
    ----------
    reasoning_artifact:
        The complete ReasoningArtifact produced by Janus. Titan reads this;
        it never mutates it.

    Returns
    -------
    BlindSpot
        Fully qualified with all four boolean criteria True and
        qualified=True. Confidence and supporting_reasoning are
        inherited directly from the artifact.
    None
        When any criterion is unsatisfied. Per Decision 3: silence is
        preferable to a conclusion that cannot be fully defended.
    """
    meaningful = _is_meaningful(reasoning_artifact)
    non_obvious = _is_non_obvious(reasoning_artifact)
    evidence_supported = _is_evidence_supported(reasoning_artifact)
    understanding = _changes_understanding(reasoning_artifact)

    if not (meaningful and non_obvious and evidence_supported and understanding):
        return None

    return BlindSpot(
        title=reasoning_artifact.observation,
        description=reasoning_artifact.conclusion,
        categories=_derive_categories(reasoning_artifact),
        severity=round(reasoning_artifact.confidence, 4),
        confidence=reasoning_artifact.confidence,
        is_meaningful=True,
        is_non_obvious=True,
        is_evidence_supported=True,
        changes_understanding=True,
        qualified=True,
        supporting_reasoning=reasoning_artifact,
    )
