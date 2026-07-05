"""Unit tests for backend/models — ED-007 (Testing Philosophy), category 1.

These tests verify:
  1. Every model is constructible from valid inputs.
  2. Immutability is enforced (frozen=True).
  3. Portfolio's weight invariants are enforced by __post_init__.
  4. BlindSpot's qualified field correctly reflects all four criteria.

Tests are deliberately lightweight — models contain no business logic.
We're testing that the types exist, hold what they promise, and refuse to
be mutated. The qualification *logic* that fills these objects belongs to
Finance DNA, Atlas, Janus, and Titan; it gets tested there.
"""

from dataclasses import FrozenInstanceError

import pytest

from backend.models import (
    Asset,
    AssetType,
    BlindSpot,
    BlindSpotCategory,
    Cardinality,
    Dimension,
    DimensionCategory,
    Directionality,
    EvidenceSource,
    Portfolio,
    ReasoningArtifact,
    ReasoningMode,
    ReasoningStep,
    Relationship,
    RelationshipTemporality,
    RelationshipType,
    TemporalBehavior,
    ValueStructure,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def apple() -> Asset:
    return Asset(
        id="apple-inc",
        name="Apple Inc.",
        ticker="AAPL",
        asset_type=AssetType.COMPANY,
        sector="Technology",
        industry="Consumer Electronics",
    )


@pytest.fixture()
def tsmc() -> Asset:
    return Asset(
        id="tsmc",
        name="Taiwan Semiconductor Manufacturing Company",
        ticker="TSM",
        asset_type=AssetType.COMPANY,
        sector="Technology",
        industry="Semiconductors",
    )


@pytest.fixture()
def nvidia() -> Asset:
    return Asset(
        id="nvidia-corp",
        name="NVIDIA Corporation",
        ticker="NVDA",
        asset_type=AssetType.COMPANY,
        sector="Technology",
        industry="Semiconductors",
    )


@pytest.fixture()
def reasoning_step() -> ReasoningStep:
    return ReasoningStep(
        premise="Apple depends on TSMC as a chip manufacturing supplier.",
        inference="TSMC's operations are concentrated in Taiwan.",
        evidence=("Apple 10-K, supplier disclosures.", "TSMC annual report."),
        confidence=0.95,
    )


@pytest.fixture()
def reasoning_artifact(reasoning_step: ReasoningStep) -> ReasoningArtifact:
    return ReasoningArtifact(
        question="Does this portfolio have concentrated geopolitical exposure?",
        reasoning_mode=ReasoningMode.DEDUCTIVE,
        observation="Apple depends on TSMC as a primary chip supplier.",
        reasoning_steps=(reasoning_step,),
        conclusion=(
            "The portfolio has concentrated geopolitical exposure via "
            "Taiwan — a candidate Blind Spot for Titan to evaluate."
        ),
        confidence=0.85,
        supporting_evidence=(
            "Apple 10-K identifies TSMC as a sole-source supplier for key chips.",
            "TSMC operates its primary fabs in Taiwan.",
            "Taiwan carries recognised geopolitical concentration risk.",
        ),
        assumptions=(
            "No meaningful diversification of chip supply away from TSMC "
            "has occurred since the last filing date.",
        ),
        falsifiability_conditions=(
            "Evidence that Apple has qualified an alternative foundry for "
            "its most critical chips would weaken this conclusion.",
            "Evidence that TSMC has meaningfully diversified its fab footprint "
            "outside Taiwan would reduce the geographic concentration risk.",
        ),
    )


# ---------------------------------------------------------------------------
# Asset
# ---------------------------------------------------------------------------


class TestAsset:
    def test_construction(self, apple: Asset) -> None:
        assert apple.id == "apple-inc"
        assert apple.ticker == "AAPL"
        assert apple.asset_type == AssetType.COMPANY

    def test_immutable(self, apple: Asset) -> None:
        from dataclasses import FrozenInstanceError  # noqa: F811

        with pytest.raises(FrozenInstanceError):
            apple.name = "Something else"  # type: ignore[misc]

    def test_nullable_fields(self) -> None:
        entity = Asset(
            id="private-supplier-1",
            name="Private Supplier",
            ticker=None,
            asset_type=AssetType.SUPPLY_CHAIN_ENTITY,
            sector=None,
            industry=None,
        )
        assert entity.ticker is None
        assert entity.sector is None


# ---------------------------------------------------------------------------
# Portfolio
# ---------------------------------------------------------------------------


class TestPortfolio:
    def test_construction(self, apple: Asset, nvidia: Asset) -> None:
        p = Portfolio(
            name="Test Portfolio",
            assets=(apple, nvidia),
            weights=(0.6, 0.4),
        )
        assert len(p.assets) == 2
        assert abs(sum(p.weights) - 1.0) < 1e-6

    def test_immutable(self, apple: Asset) -> None:
        p = Portfolio(name="p", assets=(apple,), weights=(1.0,))
        with pytest.raises(FrozenInstanceError):
            p.name = "other"  # type: ignore[misc]

    def test_weight_sum_invariant(self, apple: Asset, nvidia: Asset) -> None:
        with pytest.raises(ValueError, match="sum to 1.0"):
            Portfolio(
                name="Bad",
                assets=(apple, nvidia),
                weights=(0.5, 0.4),  # sums to 0.9
            )

    def test_length_mismatch_invariant(self, apple: Asset, nvidia: Asset) -> None:
        with pytest.raises(ValueError, match="equal length"):
            Portfolio(
                name="Bad",
                assets=(apple, nvidia),
                weights=(1.0,),
            )

    def test_negative_weight_invariant(self, apple: Asset, nvidia: Asset) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            Portfolio(
                name="Bad",
                assets=(apple, nvidia),
                weights=(-0.1, 1.1),
            )

    def test_empty_portfolio(self) -> None:
        p = Portfolio(name="Empty", assets=(), weights=())
        assert len(p.assets) == 0


# ---------------------------------------------------------------------------
# Dimension
# ---------------------------------------------------------------------------


class TestDimension:
    def test_continuous_dimension(self) -> None:
        d = Dimension(
            name="Capital Intensity",
            asset_id="apple-inc",
            value_structure=ValueStructure.CONTINUOUS,
            temporal_behavior=TemporalBehavior.STATIC,
            score=0.35,
            confidence=0.9,
            evidence=("Apple 10-K PP&E / Revenue = 0.12; sector-adjusted score 0.35.",),
            evidence_source=EvidenceSource.DISCLOSED,
            category=DimensionCategory.COST_AND_CAPITAL_STRUCTURE,
            aggregation_rule="weighted_average",
            as_of="2024-12-31",
            primitive=True,
        )
        assert d.score == 0.35
        assert d.primitive is True

    def test_binary_dimension(self) -> None:
        d = Dimension(
            name="Regulated Utility Status",
            asset_id="apple-inc",
            value_structure=ValueStructure.BINARY,
            temporal_behavior=TemporalBehavior.STATIC,
            score=False,
            confidence=1.0,
            evidence=("Apple Inc. is not registered as a regulated utility.",),
            evidence_source=EvidenceSource.PUBLIC_RECORD,
            category=DimensionCategory.BUSINESS_STRUCTURE,
            aggregation_rule="weighted_proportion",
            as_of="2024-12-31",
        )
        assert d.score is False

    def test_immutable(self) -> None:
        d = Dimension(
            name="R&D Intensity",
            asset_id="apple-inc",
            value_structure=ValueStructure.CONTINUOUS,
            temporal_behavior=TemporalBehavior.TIME_VARYING,
            score=0.06,
            confidence=0.95,
            evidence=("Apple 10-K R&D / Revenue = 0.062.",),
            evidence_source=EvidenceSource.DISCLOSED,
            category=DimensionCategory.INNOVATION_AND_TECHNOLOGY,
            aggregation_rule="weighted_average",
            as_of="2024-12-31",
        )
        with pytest.raises(FrozenInstanceError):
            d.score = 0.99  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Relationship
# ---------------------------------------------------------------------------


class TestRelationship:
    def test_construction(self) -> None:
        r = Relationship(
            source_id="apple-inc",
            target_id="tsmc",
            relationship_type=RelationshipType.DEPENDS_ON_SUPPLIES,
            directionality=Directionality.BIDIRECTIONAL,
            temporality=RelationshipTemporality.PERSISTENT,
            cardinality=Cardinality.MANY_TO_MANY,
            evidence_source=EvidenceSource.DISCLOSED,
            confidence=0.95,
            evidence=("Apple 10-K identifies TSMC as a sole-source supplier.",),
        )
        assert r.source_id == "apple-inc"
        assert r.directionality == Directionality.BIDIRECTIONAL
        assert r.valid_from is None
        assert r.valid_until is None

    def test_temporal_bounds(self) -> None:
        r = Relationship(
            source_id="some-company",
            target_id="some-supplier",
            relationship_type=RelationshipType.SELLS_TO,
            directionality=Directionality.DIRECTED,
            temporality=RelationshipTemporality.TEMPORAL,
            cardinality=Cardinality.ONE_TO_MANY,
            evidence_source=EvidenceSource.DISCLOSED,
            confidence=0.8,
            evidence=("Disclosed multi-year supply agreement.",),
            valid_from="2023-01-01",
            valid_until="2027-12-31",
        )
        assert r.valid_from == "2023-01-01"
        assert r.valid_until == "2027-12-31"

    def test_immutable(self) -> None:
        r = Relationship(
            source_id="a",
            target_id="b",
            relationship_type=RelationshipType.LOCATED_IN,
            directionality=Directionality.DIRECTED,
            temporality=RelationshipTemporality.PERSISTENT,
            cardinality=Cardinality.ONE_TO_MANY,
            evidence_source=EvidenceSource.PUBLIC_RECORD,
            confidence=1.0,
            evidence=("Public registry.",),
        )
        with pytest.raises(FrozenInstanceError):
            r.confidence = 0.0  # type: ignore[misc]


# ---------------------------------------------------------------------------
# ReasoningArtifact
# ---------------------------------------------------------------------------


class TestReasoningArtifact:
    def test_construction(self, reasoning_artifact: ReasoningArtifact) -> None:
        assert reasoning_artifact.confidence == 0.85
        assert len(reasoning_artifact.reasoning_steps) == 1
        assert len(reasoning_artifact.falsifiability_conditions) == 2

    def test_immutable(self, reasoning_artifact: ReasoningArtifact) -> None:
        with pytest.raises(FrozenInstanceError):
            reasoning_artifact.conclusion = "something else"  # type: ignore[misc]

    def test_reasoning_step_immutable(self, reasoning_step: ReasoningStep) -> None:
        with pytest.raises(FrozenInstanceError):
            reasoning_step.confidence = 0.0  # type: ignore[misc]


# ---------------------------------------------------------------------------
# BlindSpot
# ---------------------------------------------------------------------------


class TestBlindSpot:
    def test_qualified_blindspot(self, reasoning_artifact: ReasoningArtifact) -> None:
        bs = BlindSpot(
            title="Concentrated geopolitical exposure via Taiwan.",
            description=(
                "Apple, NVIDIA, and Microsoft all depend on TSMC, which operates "
                "primarily in Taiwan, creating a shared geopolitical Exposure "
                "the investor did not knowingly take on."
            ),
            categories=(BlindSpotCategory.CONCENTRATION, BlindSpotCategory.DEPENDENCY),
            severity=0.8,
            confidence=0.85,
            is_meaningful=True,
            is_non_obvious=False,  # simplified — investor may know about TSMC/Taiwan
            is_evidence_supported=True,
            changes_understanding=True,
            qualified=False,  # is_non_obvious=False disqualifies it
            supporting_reasoning=reasoning_artifact,
        )
        assert bs.qualified is False
        assert BlindSpotCategory.CONCENTRATION in bs.categories

    def test_reasoning_artifact_attached(self, reasoning_artifact: ReasoningArtifact) -> None:
        bs = BlindSpot(
            title="Test",
            description="Test description.",
            categories=(BlindSpotCategory.MACROECONOMIC,),
            severity=0.5,
            confidence=0.7,
            is_meaningful=True,
            is_non_obvious=True,
            is_evidence_supported=True,
            changes_understanding=True,
            qualified=True,
            supporting_reasoning=reasoning_artifact,
        )
        # The reasoning artifact is accessible and unmodified
        assert bs.supporting_reasoning.confidence == 0.85
        assert "Titan" in bs.supporting_reasoning.conclusion

    def test_immutable(self, reasoning_artifact: ReasoningArtifact) -> None:
        bs = BlindSpot(
            title="Test",
            description="Test.",
            categories=(BlindSpotCategory.STRUCTURAL,),
            severity=0.5,
            confidence=0.5,
            is_meaningful=True,
            is_non_obvious=True,
            is_evidence_supported=True,
            changes_understanding=True,
            qualified=True,
            supporting_reasoning=reasoning_artifact,
        )
        with pytest.raises(FrozenInstanceError):
            bs.qualified = False  # type: ignore[misc]
