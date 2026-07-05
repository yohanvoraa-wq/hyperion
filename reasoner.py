"""Tests for backend/titan — ED-007.

Five test groups:

  Group 1 — Individual criterion functions
    Each of the four criterion functions tested independently.
    Passes and fails verified for each.

  Group 2 — qualify() failure behavior
    Each criterion failure causes qualify() to return None.
    No partial BlindSpot is ever returned.

  Group 3 — BlindSpot artifact integrity
    When all criteria pass, the BlindSpot is fully populated.
    Confidence and supporting_reasoning are inherited from artifact.
    BlindSpot is immutable.

  Group 4 — Public API
    qualify() is deterministic.
    qualify() does not modify its input.

  Group 5 — End-to-end pipeline (real data)
    Ingestion → Finance DNA → Atlas → Janus → Titan.
    Apple produces a qualified BlindSpot.
    BlindSpot.qualified == True.
    BlindSpot.supporting_reasoning matches Janus output.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from backend.models import (
    BlindSpot,
    BlindSpotCategory,
    ReasoningArtifact,
    ReasoningStep,
)
from backend.models.enums import ReasoningMode
from backend.titan import qualify
from backend.titan.qualifier import (
    _changes_understanding,
    _is_evidence_supported,
    _is_meaningful,
    _is_non_obvious,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_GOOD_EVIDENCE = ("Apple 10-K: TSMC sole-source supplier.",)
_GOOD_ASSUMPTIONS = (
    "Finance DNA dimensions are sector-level approximations (V0.1).",
    "Atlas relationships are hand-seeded for Version 0.1.",
)
_GOOD_FALSIFIABILITY = ("If Apple diversifies chip manufacturing, this conclusion weakens.",)


def _make_step(confidence: float = 0.9) -> ReasoningStep:
    return ReasoningStep(
        premise="Company A → REL → Company B",
        inference="Company A has a structural dependency on Company B.",
        evidence=("Disclosed in annual report.",),
        confidence=confidence,
    )


def _make_artifact(
    *,
    steps: int = 3,
    confidence: float = 0.81,
    evidence: tuple[str, ...] = _GOOD_EVIDENCE,
    assumptions: tuple[str, ...] = _GOOD_ASSUMPTIONS,
    falsifiability: tuple[str, ...] = _GOOD_FALSIFIABILITY,
) -> ReasoningArtifact:
    """Build a ReasoningArtifact with controllable properties for testing."""
    return ReasoningArtifact(
        question="Does this asset have hidden exposure?",
        reasoning_mode=ReasoningMode.DEDUCTIVE,
        observation="Asset has dependency relationships leading to macro risk.",
        reasoning_steps=tuple(_make_step() for _ in range(steps)),
        conclusion="Asset has a multi-hop path to a significant risk endpoint.",
        confidence=confidence,
        supporting_evidence=evidence,
        assumptions=assumptions,
        falsifiability_conditions=falsifiability,
    )


# ---------------------------------------------------------------------------
# Group 1 — Individual criterion functions
# ---------------------------------------------------------------------------


class TestCriterionFunctions:
    # --- is_meaningful ---

    def test_meaningful_passes_sufficient_steps_and_confidence(self) -> None:
        artifact = _make_artifact(steps=3, confidence=0.81)
        assert _is_meaningful(artifact) is True

    def test_meaningful_passes_minimum_one_step(self) -> None:
        artifact = _make_artifact(steps=1, confidence=0.8)
        assert _is_meaningful(artifact) is True

    def test_meaningful_fails_low_confidence(self) -> None:
        artifact = _make_artifact(steps=3, confidence=0.3)
        assert _is_meaningful(artifact) is False

    def test_meaningful_fails_exactly_at_threshold(self) -> None:
        """0.5 is the threshold — 0.499 fails, 0.5 passes."""
        below = _make_artifact(steps=2, confidence=0.499)
        at = _make_artifact(steps=2, confidence=0.5)
        assert _is_meaningful(below) is False
        assert _is_meaningful(at) is True

    # --- is_non_obvious ---

    def test_non_obvious_passes_two_or_more_steps(self) -> None:
        artifact = _make_artifact(steps=2)
        assert _is_non_obvious(artifact) is True

    def test_non_obvious_passes_three_steps(self) -> None:
        artifact = _make_artifact(steps=3)
        assert _is_non_obvious(artifact) is True

    def test_non_obvious_fails_one_step(self) -> None:
        """A single-hop direct connection is too obvious to qualify."""
        artifact = _make_artifact(steps=1)
        assert _is_non_obvious(artifact) is False

    # --- is_evidence_supported ---

    def test_evidence_supported_passes_with_evidence(self) -> None:
        artifact = _make_artifact(evidence=("TSMC sole-source per Apple 10-K.",))
        assert _is_evidence_supported(artifact) is True

    def test_evidence_supported_fails_empty_evidence_tuple(self) -> None:
        artifact = _make_artifact(evidence=())
        assert _is_evidence_supported(artifact) is False

    def test_evidence_supported_fails_whitespace_only_evidence(self) -> None:
        artifact = _make_artifact(evidence=("   ",))
        assert _is_evidence_supported(artifact) is False

    # --- changes_understanding ---

    def test_changes_understanding_passes_with_conditions(self) -> None:
        artifact = _make_artifact(falsifiability=("Condition A.",))
        assert _changes_understanding(artifact) is True

    def test_changes_understanding_fails_empty_falsifiability(self) -> None:
        artifact = _make_artifact(falsifiability=())
        assert _changes_understanding(artifact) is False


# ---------------------------------------------------------------------------
# Group 2 — qualify() failure behavior
# ---------------------------------------------------------------------------


class TestQualifyFailure:
    def test_all_criteria_pass_returns_blind_spot(self) -> None:
        artifact = _make_artifact()
        result = qualify(artifact)
        assert isinstance(result, BlindSpot)

    def test_criterion_1_fails_low_confidence_returns_none(self) -> None:
        """Meaningful criterion fails: confidence 0.3 < 0.5."""
        artifact = _make_artifact(steps=3, confidence=0.3)
        assert qualify(artifact) is None

    def test_criterion_2_fails_single_step_returns_none(self) -> None:
        """Non-obvious criterion fails: 1 hop is too direct."""
        artifact = _make_artifact(steps=1, confidence=0.9)
        assert qualify(artifact) is None

    def test_criterion_3_fails_no_evidence_returns_none(self) -> None:
        """Evidence-supported criterion fails: no supporting evidence."""
        artifact = _make_artifact(evidence=())
        assert qualify(artifact) is None

    def test_criterion_4_fails_no_falsifiability_returns_none(self) -> None:
        """Changes-understanding criterion fails: no falsifiability conditions."""
        artifact = _make_artifact(falsifiability=())
        assert qualify(artifact) is None

    def test_whitespace_evidence_returns_none(self) -> None:
        """Whitespace-only evidence strings fail criterion 3."""
        artifact = _make_artifact(evidence=("  ",))
        assert qualify(artifact) is None

    def test_silence_over_weak_chain(self) -> None:
        """Low confidence + 1 step: both criteria 1 and 2 fail. Still None."""
        artifact = _make_artifact(steps=1, confidence=0.2)
        assert qualify(artifact) is None


# ---------------------------------------------------------------------------
# Group 3 — BlindSpot artifact integrity
# ---------------------------------------------------------------------------


class TestBlindSpotIntegrity:
    @pytest.fixture()
    def qualified_artifact(self) -> ReasoningArtifact:
        return _make_artifact()

    @pytest.fixture()
    def blind_spot(self, qualified_artifact: ReasoningArtifact) -> BlindSpot:
        result = qualify(qualified_artifact)
        assert result is not None
        return result

    def test_qualified_is_true(self, blind_spot: BlindSpot) -> None:
        assert blind_spot.qualified is True

    def test_all_four_criteria_booleans_true(self, blind_spot: BlindSpot) -> None:
        assert blind_spot.is_meaningful is True
        assert blind_spot.is_non_obvious is True
        assert blind_spot.is_evidence_supported is True
        assert blind_spot.changes_understanding is True

    def test_confidence_inherited_from_artifact(
        self, qualified_artifact: ReasoningArtifact, blind_spot: BlindSpot
    ) -> None:
        """Decision 4: Titan never recalculates confidence."""
        assert blind_spot.confidence == qualified_artifact.confidence

    def test_severity_equals_confidence(self, blind_spot: BlindSpot) -> None:
        """V0.1: severity uses confidence as proxy."""
        assert blind_spot.severity == round(blind_spot.confidence, 4)

    def test_supporting_reasoning_is_original_artifact(
        self, qualified_artifact: ReasoningArtifact, blind_spot: BlindSpot
    ) -> None:
        """Titan never copies the artifact — it attaches the original."""
        assert blind_spot.supporting_reasoning is qualified_artifact

    def test_categories_are_non_empty(self, blind_spot: BlindSpot) -> None:
        assert len(blind_spot.categories) >= 1

    def test_categories_include_macroeconomic(self, blind_spot: BlindSpot) -> None:
        """V0.1 always produces MACROECONOMIC since paths end at MACRO_FACTOR."""
        assert BlindSpotCategory.MACROECONOMIC in blind_spot.categories

    def test_categories_include_dependency(self, blind_spot: BlindSpot) -> None:
        """V0.1 always produces DEPENDENCY since paths contain supply chain hops."""
        assert BlindSpotCategory.DEPENDENCY in blind_spot.categories

    def test_blind_spot_is_immutable(self, blind_spot: BlindSpot) -> None:
        with pytest.raises(FrozenInstanceError):
            blind_spot.qualified = False  # type: ignore[misc]

    def test_title_is_non_empty(self, blind_spot: BlindSpot) -> None:
        assert len(blind_spot.title.strip()) > 0

    def test_description_is_non_empty(self, blind_spot: BlindSpot) -> None:
        assert len(blind_spot.description.strip()) > 0


# ---------------------------------------------------------------------------
# Group 4 — Public API
# ---------------------------------------------------------------------------


class TestPublicAPI:
    def test_qualify_is_deterministic(self) -> None:
        artifact = _make_artifact()
        first = qualify(artifact)
        for _ in range(9):
            result = qualify(artifact)
            assert result == first

    def test_qualify_does_not_modify_artifact(self) -> None:
        """Decision 5: Titan never edits the ReasoningArtifact it receives."""
        artifact = _make_artifact()
        original_confidence = artifact.confidence
        original_steps_count = len(artifact.reasoning_steps)
        original_evidence = artifact.supporting_evidence
        qualify(artifact)
        assert artifact.confidence == original_confidence
        assert len(artifact.reasoning_steps) == original_steps_count
        assert artifact.supporting_evidence == original_evidence

    def test_qualify_with_none_producing_artifact_returns_none(self) -> None:
        artifact = _make_artifact(steps=1, confidence=0.3)
        assert qualify(artifact) is None


# ---------------------------------------------------------------------------
# Group 5 — End-to-end pipeline (real seed data)
# ---------------------------------------------------------------------------


class TestEndToEnd:
    """Full pipeline: Ingestion → Finance DNA → Atlas → Janus → Titan."""

    @pytest.fixture()
    def apple_blind_spot(self) -> BlindSpot | None:
        from backend.atlas import build
        from backend.ingestion import load_asset_registry
        from backend.janus import reason

        registry = load_asset_registry()
        graph = build(list(registry.assets))
        artifact = reason("apple-inc", graph)
        if artifact is None:
            return None
        return qualify(artifact)

    def test_apple_produces_blind_spot(self, apple_blind_spot: BlindSpot | None) -> None:
        assert apple_blind_spot is not None, (
            "Apple's supply chain path through TSMC → Taiwan → "
            "Geopolitical Risk should qualify as a Blind Spot. "
            "Check seed data and Janus configuration."
        )

    def test_apple_blind_spot_is_qualified(self, apple_blind_spot: BlindSpot | None) -> None:
        assert apple_blind_spot is not None
        assert apple_blind_spot.qualified is True

    def test_apple_blind_spot_confidence_positive(self, apple_blind_spot: BlindSpot | None) -> None:
        assert apple_blind_spot is not None
        assert apple_blind_spot.confidence > 0.0

    def test_apple_blind_spot_has_reasoning_chain(self, apple_blind_spot: BlindSpot | None) -> None:
        assert apple_blind_spot is not None
        assert len(apple_blind_spot.supporting_reasoning.reasoning_steps) >= 2

    def test_apple_blind_spot_has_evidence(self, apple_blind_spot: BlindSpot | None) -> None:
        assert apple_blind_spot is not None
        assert len(apple_blind_spot.supporting_reasoning.supporting_evidence) >= 1

    def test_apple_blind_spot_has_falsifiability(self, apple_blind_spot: BlindSpot | None) -> None:
        assert apple_blind_spot is not None
        assert len(apple_blind_spot.supporting_reasoning.falsifiability_conditions) >= 1

    def test_full_pipeline_is_deterministic(self) -> None:
        from backend.atlas import build
        from backend.ingestion import load_asset_registry
        from backend.janus import reason

        registry = load_asset_registry()
        graph = build(list(registry.assets))
        artifact = reason("apple-inc", graph)
        assert artifact is not None
        first = qualify(artifact)
        for _ in range(4):
            result = qualify(artifact)
            assert result == first
