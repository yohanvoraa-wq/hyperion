"""Tests for backend/finance_dna — ED-007, category 1 (unit) and 3 (snapshot).

Five test groups per the milestone specification:

  Group 1 — Individual dimension evaluation
    Parametrised over all 7 fixture assets × 6 dimensions.
    Verifies scores are in expected ranges and Dimension fields are correct.

  Group 2 — Invalid and edge-case inputs
    Missing sector, missing industry (uses fallback), unknown sector.

  Group 3 — Determinism
    Same asset + same as_of → byte-for-byte identical FinanceDNA.
    100 consecutive evaluations produce identical output.
    Score values are independent of the evaluated_at date.

  Group 4 — Complete Finance DNA
    evaluate() produces exactly 6 dimensions with correct metadata,
    no duplicates, correct asset_id on every Dimension, correct version,
    and the artifact is immutable.

  Group 5 — Registry integrity
    Every registered evaluator returns a Dimension whose name, category,
    and value_structure match the registered DimensionDefinition.
    Prevents category-swap wiring bugs (e.g. Capital Intensity definition
    accidentally attached to Commodity Exposure evaluator).

Test date: all tests use TEST_DATE = '2024-12-31' injected via as_of so
results are reproducible regardless of when the suite runs (ED-004).
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from backend.finance_dna import (
    FINANCE_DNA_VERSION,
    MissingAssetDataError,
    evaluate,
)
from backend.finance_dna.dimensions import (
    ALL_DEFINITIONS,
    CAPITAL_INTENSITY,
)
from backend.finance_dna.registry import REGISTRY
from backend.finance_dna.rules import (
    evaluate_capital_intensity,
    evaluate_commodity_input_exposure,
    evaluate_geographic_revenue_concentration,
    evaluate_innovation_intensity,
    evaluate_regulatory_exposure,
    evaluate_supply_chain_complexity,
)
from backend.models import Asset, AssetType, FinanceDNA, ValueStructure

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

TEST_DATE = "2024-12-31"

# ---------------------------------------------------------------------------
# Fixture assets — defined at module level for reuse across all test groups.
# These mirror datasets/assets.csv exactly so any future integration test
# that loads from the CSV will produce matching results.
# ---------------------------------------------------------------------------

APPLE = Asset(
    id="apple-inc",
    name="Apple Inc.",
    ticker="AAPL",
    asset_type=AssetType.COMPANY,
    sector="Technology",
    industry="Consumer Electronics",
)
MICROSOFT = Asset(
    id="microsoft",
    name="Microsoft Corporation",
    ticker="MSFT",
    asset_type=AssetType.COMPANY,
    sector="Technology",
    industry="Software",
)
NVIDIA = Asset(
    id="nvidia",
    name="NVIDIA Corporation",
    ticker="NVDA",
    asset_type=AssetType.COMPANY,
    sector="Technology",
    industry="Semiconductors",
)
TSMC = Asset(
    id="tsmc",
    name="Taiwan Semiconductor Manufacturing Company",
    ticker="TSM",
    asset_type=AssetType.COMPANY,
    sector="Technology",
    industry="Semiconductors",
)
AMAZON = Asset(
    id="amazon",
    name="Amazon.com Inc.",
    ticker="AMZN",
    asset_type=AssetType.COMPANY,
    sector="Consumer Discretionary",
    industry="E-Commerce & Cloud Services",
)
ALPHABET = Asset(
    id="alphabet",
    name="Alphabet Inc.",
    ticker="GOOGL",
    asset_type=AssetType.COMPANY,
    sector="Technology",
    industry="Internet Services",
)
NESTLE = Asset(
    id="nestle",
    name="Nestle S.A.",
    ticker="NESN",
    asset_type=AssetType.COMPANY,
    sector="Consumer Staples",
    industry="Food & Beverages",
)

ALL_ASSETS = (APPLE, MICROSOFT, NVIDIA, TSMC, AMAZON, ALPHABET, NESTLE)


# ---------------------------------------------------------------------------
# Group 1 — Individual dimension evaluation
# ---------------------------------------------------------------------------


class TestCapitalIntensity:
    @pytest.mark.parametrize(
        "asset, score_min, score_max",
        [
            (TSMC, 0.80, 0.90),  # fab-heavy semiconductor
            (NVIDIA, 0.80, 0.90),  # same sector as TSMC
            (APPLE, 0.45, 0.65),  # consumer electronics: mid
            (MICROSOFT, 0.10, 0.30),  # software: asset-light
            (AMAZON, 0.40, 0.60),  # fulfilment + cloud
            (ALPHABET, 0.25, 0.45),  # internet: data centres but software
            (NESTLE, 0.50, 0.70),  # food manufacturing
        ],
    )
    def test_score_in_expected_range(
        self, asset: Asset, score_min: float, score_max: float
    ) -> None:
        d = evaluate_capital_intensity(asset, TEST_DATE)
        assert isinstance(d.score, float)
        assert score_min <= float(d.score) <= score_max

    def test_returns_correct_dimension_name(self) -> None:
        d = evaluate_capital_intensity(APPLE, TEST_DATE)
        assert d.name == CAPITAL_INTENSITY.name

    def test_returns_correct_category(self) -> None:
        d = evaluate_capital_intensity(APPLE, TEST_DATE)
        assert d.category == CAPITAL_INTENSITY.category

    def test_asset_id_matches_input(self) -> None:
        d = evaluate_capital_intensity(TSMC, TEST_DATE)
        assert d.asset_id == TSMC.id

    def test_as_of_matches_injected_date(self) -> None:
        d = evaluate_capital_intensity(APPLE, TEST_DATE)
        assert d.as_of == TEST_DATE

    def test_evidence_is_non_empty(self) -> None:
        d = evaluate_capital_intensity(APPLE, TEST_DATE)
        assert len(d.evidence) > 0
        assert all(len(e) > 0 for e in d.evidence)


class TestCommodityInputExposure:
    @pytest.mark.parametrize(
        "asset, score_min, score_max",
        [
            (TSMC, 0.85, 0.95),  # silicon, rare earths, specialty gases
            (NVIDIA, 0.85, 0.95),  # same sector
            (APPLE, 0.55, 0.75),  # metals, rare earths, battery
            (MICROSOFT, 0.00, 0.10),  # near-zero
            (AMAZON, 0.20, 0.40),  # packaging, energy
            (ALPHABET, 0.05, 0.25),  # data centre energy
            (NESTLE, 0.80, 0.90),  # agricultural commodities
        ],
    )
    def test_score_in_expected_range(
        self, asset: Asset, score_min: float, score_max: float
    ) -> None:
        d = evaluate_commodity_input_exposure(asset, TEST_DATE)
        assert score_min <= float(d.score) <= score_max

    def test_semiconductors_highest(self) -> None:
        """Semiconductors should have the highest commodity exposure in Technology."""
        tsmc_d = evaluate_commodity_input_exposure(TSMC, TEST_DATE)
        msft_d = evaluate_commodity_input_exposure(MICROSOFT, TEST_DATE)
        assert float(tsmc_d.score) > float(msft_d.score)


class TestSupplyChainComplexity:
    @pytest.mark.parametrize(
        "asset, score_min, score_max",
        [
            (TSMC, 0.90, 1.00),  # most complex on earth
            (NVIDIA, 0.90, 1.00),  # same sector
            (APPLE, 0.80, 0.90),  # complex global assembly
            (MICROSOFT, 0.00, 0.20),  # minimal physical supply chain
            (AMAZON, 0.60, 0.80),  # vast logistics
            (ALPHABET, 0.20, 0.40),  # hardware procurement, mostly software
            (NESTLE, 0.55, 0.75),  # agricultural + distribution
        ],
    )
    def test_score_in_expected_range(
        self, asset: Asset, score_min: float, score_max: float
    ) -> None:
        d = evaluate_supply_chain_complexity(asset, TEST_DATE)
        assert score_min <= float(d.score) <= score_max

    def test_semiconductors_more_complex_than_software(self) -> None:
        tsmc_d = evaluate_supply_chain_complexity(TSMC, TEST_DATE)
        msft_d = evaluate_supply_chain_complexity(MICROSOFT, TEST_DATE)
        assert float(tsmc_d.score) > float(msft_d.score)


class TestInnovationIntensity:
    @pytest.mark.parametrize(
        "asset, score_min, score_max",
        [
            (TSMC, 0.80, 0.90),  # process node R&D
            (NVIDIA, 0.80, 0.90),  # GPU architecture R&D
            (APPLE, 0.70, 0.80),  # device + silicon R&D
            (MICROSOFT, 0.75, 0.85),  # software + cloud + AI
            (AMAZON, 0.65, 0.75),  # logistics tech + AWS
            (ALPHABET, 0.80, 0.90),  # AI + search + hardware
            (NESTLE, 0.10, 0.30),  # incremental product improvement
        ],
    )
    def test_score_in_expected_range(
        self, asset: Asset, score_min: float, score_max: float
    ) -> None:
        d = evaluate_innovation_intensity(asset, TEST_DATE)
        assert score_min <= float(d.score) <= score_max

    def test_food_company_significantly_lower_than_technology(self) -> None:
        tech_d = evaluate_innovation_intensity(MICROSOFT, TEST_DATE)
        food_d = evaluate_innovation_intensity(NESTLE, TEST_DATE)
        assert float(tech_d.score) > float(food_d.score) + 0.40


class TestRegulatoryExposure:
    @pytest.mark.parametrize(
        "asset, score_min, score_max",
        [
            (TSMC, 0.50, 0.70),  # export controls, trade restrictions
            (NVIDIA, 0.50, 0.70),  # same sector
            (APPLE, 0.45, 0.65),  # FCC, product safety, tariffs
            (MICROSOFT, 0.55, 0.75),  # data privacy, antitrust
            (AMAZON, 0.55, 0.75),  # antitrust, labour, consumer protection
            (ALPHABET, 0.70, 0.90),  # highest: antitrust + data + AI regulation
            (NESTLE, 0.60, 0.80),  # food safety + labelling + sustainability
        ],
    )
    def test_score_in_expected_range(
        self, asset: Asset, score_min: float, score_max: float
    ) -> None:
        d = evaluate_regulatory_exposure(asset, TEST_DATE)
        assert score_min <= float(d.score) <= score_max

    def test_internet_services_highest_regulatory(self) -> None:
        alphabet_d = evaluate_regulatory_exposure(ALPHABET, TEST_DATE)
        apple_d = evaluate_regulatory_exposure(APPLE, TEST_DATE)
        assert float(alphabet_d.score) > float(apple_d.score)


class TestGeographicRevenueConcentration:
    @pytest.mark.parametrize(
        "asset, score_min, score_max",
        [
            (TSMC, 0.50, 0.70),  # Taiwan supply-chain concentration
            (NVIDIA, 0.50, 0.70),  # same sector
            (APPLE, 0.35, 0.55),  # some China concentration
            (MICROSOFT, 0.25, 0.45),  # global software
            (AMAZON, 0.45, 0.65),  # US-heavy
            (ALPHABET, 0.25, 0.45),  # global internet
            (NESTLE, 0.35, 0.55),  # global but regional categories
        ],
    )
    def test_score_in_expected_range(
        self, asset: Asset, score_min: float, score_max: float
    ) -> None:
        d = evaluate_geographic_revenue_concentration(asset, TEST_DATE)
        assert score_min <= float(d.score) <= score_max


# ---------------------------------------------------------------------------
# Group 2 — Invalid and edge-case inputs
# ---------------------------------------------------------------------------


class TestInvalidInputs:
    def test_missing_sector_raises_missing_asset_data_error(self) -> None:
        asset_no_sector = Asset(
            id="unknown",
            name="Unknown Co",
            ticker=None,
            asset_type=AssetType.COMPANY,
            sector=None,  # <-- triggers error
            industry="Software",
        )
        with pytest.raises(MissingAssetDataError) as exc_info:
            evaluate_capital_intensity(asset_no_sector, TEST_DATE)
        assert exc_info.value.asset_id == "unknown"
        assert exc_info.value.missing_field == "sector"

    @pytest.mark.parametrize(
        "evaluator",
        [
            evaluate_capital_intensity,
            evaluate_commodity_input_exposure,
            evaluate_supply_chain_complexity,
            evaluate_innovation_intensity,
            evaluate_regulatory_exposure,
            evaluate_geographic_revenue_concentration,
        ],
    )
    def test_all_evaluators_raise_on_missing_sector(self, evaluator: object) -> None:
        """All six evaluators require sector; None raises MissingAssetDataError."""
        assert callable(evaluator)
        fn = evaluator
        asset_no_sector = Asset(
            id="x",
            name="X",
            ticker=None,
            asset_type=AssetType.COMPANY,
            sector=None,
            industry=None,
        )
        with pytest.raises(MissingAssetDataError):
            fn(asset_no_sector, TEST_DATE)

    def test_missing_industry_uses_sector_fallback(self) -> None:
        """industry=None falls back to sector-level score without raising."""
        asset_no_industry = Asset(
            id="tech-co",
            name="Tech Co",
            ticker=None,
            asset_type=AssetType.COMPANY,
            sector="Technology",
            industry=None,  # should use sector fallback
        )
        d = evaluate_capital_intensity(asset_no_industry, TEST_DATE)
        assert isinstance(d.score, float)
        # Sector fallback for Technology is 0.45
        assert d.score == 0.45

    def test_unknown_sector_raises(self) -> None:
        asset_unknown = Asset(
            id="x",
            name="X",
            ticker=None,
            asset_type=AssetType.COMPANY,
            sector="Underwater Basket Weaving",
            industry=None,
        )
        with pytest.raises(MissingAssetDataError) as exc_info:
            evaluate_capital_intensity(asset_unknown, TEST_DATE)
        assert "unrecognised" in exc_info.value.missing_field

    def test_error_carries_dimension_name(self) -> None:
        asset_no_sector = Asset(
            id="x",
            name="X",
            ticker=None,
            asset_type=AssetType.COMPANY,
            sector=None,
            industry=None,
        )
        with pytest.raises(MissingAssetDataError) as exc_info:
            evaluate_capital_intensity(asset_no_sector, TEST_DATE)
        assert exc_info.value.dimension_name == CAPITAL_INTENSITY.name


# ---------------------------------------------------------------------------
# Group 3 — Determinism
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_100_evaluations_produce_identical_finance_dna(self) -> None:
        """Core determinism test: same input → same output, always."""
        first = evaluate(APPLE, as_of=TEST_DATE)
        for _ in range(99):
            result = evaluate(APPLE, as_of=TEST_DATE)
            assert result == first, (
                "evaluate() produced different output on a repeated call "
                "with identical inputs. Finance DNA must be deterministic."
            )

    @pytest.mark.parametrize("asset", list(ALL_ASSETS))
    def test_same_as_of_same_output(self, asset: Asset) -> None:
        """Identical asset + identical date → identical FinanceDNA."""
        first = evaluate(asset, as_of=TEST_DATE)
        second = evaluate(asset, as_of=TEST_DATE)
        assert first == second

    def test_scores_independent_of_evaluated_at_date(self) -> None:
        """Changing the evaluation date must not change dimension scores."""
        dna_dec = evaluate(APPLE, as_of="2024-12-31")
        dna_jan = evaluate(APPLE, as_of="2025-01-15")
        # Dates differ
        assert dna_dec.evaluated_at != dna_jan.evaluated_at
        # But all scores must be identical
        scores_dec = {d.name: d.score for d in dna_dec.dimensions}
        scores_jan = {d.name: d.score for d in dna_jan.dimensions}
        assert scores_dec == scores_jan


# ---------------------------------------------------------------------------
# Group 4 — Complete Finance DNA
# ---------------------------------------------------------------------------


class TestCompleteFinanceDNA:
    @pytest.mark.parametrize("asset", list(ALL_ASSETS))
    def test_contains_exactly_fifteen_dimensions(self, asset: Asset) -> None:
        dna = evaluate(asset, as_of=TEST_DATE)
        assert len(dna.dimensions) == 15

    @pytest.mark.parametrize("asset", list(ALL_ASSETS))
    def test_no_duplicate_dimension_names(self, asset: Asset) -> None:
        dna = evaluate(asset, as_of=TEST_DATE)
        names = [d.name for d in dna.dimensions]
        assert len(names) == len(set(names)), (
            f"Duplicate dimension names in FinanceDNA for {asset.id}: {names}"
        )

    @pytest.mark.parametrize("asset", list(ALL_ASSETS))
    def test_all_dimension_asset_ids_match(self, asset: Asset) -> None:
        dna = evaluate(asset, as_of=TEST_DATE)
        for d in dna.dimensions:
            assert d.asset_id == asset.id, (
                f"Dimension '{d.name}' has asset_id '{d.asset_id}' "
                f"but FinanceDNA.asset_id is '{asset.id}'"
            )

    def test_finance_dna_version_is_correct(self) -> None:
        dna = evaluate(APPLE, as_of=TEST_DATE)
        assert dna.version == FINANCE_DNA_VERSION == "0.2"

    def test_finance_dna_is_immutable(self) -> None:
        dna = evaluate(APPLE, as_of=TEST_DATE)
        with pytest.raises(FrozenInstanceError):
            dna.asset_id = "hacked"  # type: ignore[misc]

    def test_dimensions_inside_dna_are_immutable(self) -> None:
        dna = evaluate(APPLE, as_of=TEST_DATE)
        with pytest.raises(FrozenInstanceError):
            dna.dimensions[0].score = 0.0  # type: ignore[misc]

    def test_evaluated_at_matches_injected_date(self) -> None:
        dna = evaluate(APPLE, as_of=TEST_DATE)
        assert dna.evaluated_at == TEST_DATE

    @pytest.mark.parametrize("asset", list(ALL_ASSETS))
    def test_all_scores_are_floats_in_unit_interval(self, asset: Asset) -> None:
        """Every V0.1 dimension is CONTINUOUS; all scores must be in [0, 1]."""
        dna = evaluate(asset, as_of=TEST_DATE)
        for d in dna.dimensions:
            assert d.value_structure == ValueStructure.CONTINUOUS
            assert isinstance(d.score, float)
            assert 0.0 <= float(d.score) <= 1.0, (
                f"Score {d.score} for '{d.name}' on {asset.id} is outside [0, 1]."
            )

    def test_asset_id_mismatch_raises_on_construction(self) -> None:
        """FinanceDNA.__post_init__ rejects Dimensions with mismatched asset_id."""
        from backend.models import (
            Dimension,
            DimensionCategory,
            EvidenceSource,
            TemporalBehavior,
            ValueStructure,
        )

        wrong_dimension = Dimension(
            name="Capital Intensity",
            asset_id="other-asset",  # mismatch
            value_structure=ValueStructure.CONTINUOUS,
            temporal_behavior=TemporalBehavior.STATIC,
            score=0.5,
            confidence=0.6,
            evidence=("test",),
            evidence_source=EvidenceSource.DERIVED,
            category=DimensionCategory.COST_AND_CAPITAL_STRUCTURE,
            aggregation_rule="weighted_average",
            as_of=TEST_DATE,
        )
        with pytest.raises(ValueError, match="asset_id"):
            FinanceDNA(
                version="0.1",
                asset_id="apple-inc",
                dimensions=(wrong_dimension,),
                evaluated_at=TEST_DATE,
            )

    def test_duplicate_dimension_names_raise_on_construction(self) -> None:
        """FinanceDNA.__post_init__ rejects duplicate dimension names.

        Capital Intensity appearing twice means Atlas receives two conflicting
        scores for the same characteristic — the artifact should never be
        constructable in that state.
        """
        from backend.models import (
            Dimension,
            DimensionCategory,
            EvidenceSource,
            TemporalBehavior,
            ValueStructure,
        )

        dim = Dimension(
            name="Capital Intensity",
            asset_id="apple-inc",
            value_structure=ValueStructure.CONTINUOUS,
            temporal_behavior=TemporalBehavior.STATIC,
            score=0.5,
            confidence=0.6,
            evidence=("test",),
            evidence_source=EvidenceSource.DERIVED,
            category=DimensionCategory.COST_AND_CAPITAL_STRUCTURE,
            aggregation_rule="weighted_average",
            as_of=TEST_DATE,
        )
        with pytest.raises(ValueError, match="Duplicate"):
            FinanceDNA(
                version="0.1",
                asset_id="apple-inc",
                dimensions=(dim, dim),  # same dimension twice
                evaluated_at=TEST_DATE,
            )

    def test_evaluation_order_matches_registry_insertion_order(self) -> None:
        """dimensions[i].name == REGISTRY[i].definition.name for all i.

        Atlas will access dimensions by position; order must be stable and
        match the registry's declared sequence. This test makes the guarantee
        explicit rather than relying on tuple-ordering implementation details.
        """
        dna = evaluate(APPLE, as_of=TEST_DATE)
        expected_order = [r.definition.name for r in REGISTRY]
        actual_order = [d.name for d in dna.dimensions]
        assert actual_order == expected_order, (
            "Dimension order in FinanceDNA does not match REGISTRY insertion "
            f"order.\nExpected: {expected_order}\nActual:   {actual_order}"
        )


# ---------------------------------------------------------------------------
# Group 5 — Registry integrity
# ---------------------------------------------------------------------------


class TestRegistryIntegrity:
    """Verify that every registered evaluator is correctly wired to its definition.

    Without these tests, a refactoring mistake (swapping evaluator A to
    definition B) would only surface as a wrong dimension name in Atlas,
    long after Finance DNA itself passed all other tests.
    """

    @pytest.mark.parametrize(
        "registered",
        list(REGISTRY),
        ids=[r.definition.name for r in REGISTRY],
    )
    def test_evaluator_returns_dimension_with_matching_name(self, registered: object) -> None:
        from backend.finance_dna.registry import RegisteredDimension

        assert isinstance(registered, RegisteredDimension)
        dimension = registered.evaluator(APPLE, TEST_DATE)
        assert dimension.name == registered.definition.name, (
            f"Evaluator for '{registered.definition.name}' returned a "
            f"Dimension named '{dimension.name}'. Wiring mismatch in registry.py."
        )

    @pytest.mark.parametrize(
        "registered",
        list(REGISTRY),
        ids=[r.definition.name for r in REGISTRY],
    )
    def test_evaluator_returns_correct_category(self, registered: object) -> None:
        from backend.finance_dna.registry import RegisteredDimension

        assert isinstance(registered, RegisteredDimension)
        dimension = registered.evaluator(APPLE, TEST_DATE)
        assert dimension.category == registered.definition.category

    @pytest.mark.parametrize(
        "registered",
        list(REGISTRY),
        ids=[r.definition.name for r in REGISTRY],
    )
    def test_evaluator_returns_correct_value_structure(self, registered: object) -> None:
        from backend.finance_dna.registry import RegisteredDimension

        assert isinstance(registered, RegisteredDimension)
        dimension = registered.evaluator(APPLE, TEST_DATE)
        assert dimension.value_structure == registered.definition.value_structure

    def test_registry_length_matches_all_definitions(self) -> None:
        """REGISTRY and ALL_DEFINITIONS must be in sync."""
        assert len(REGISTRY) == len(ALL_DEFINITIONS), (
            f"REGISTRY has {len(REGISTRY)} entries but ALL_DEFINITIONS "
            f"has {len(ALL_DEFINITIONS)}. Add or remove from both together."
        )

    def test_registry_contains_no_duplicate_names(self) -> None:
        names = [r.definition.name for r in REGISTRY]
        assert len(names) == len(set(names)), f"Duplicate names in REGISTRY: {names}"

    @pytest.mark.parametrize(
        "registered",
        list(REGISTRY),
        ids=[r.definition.name for r in REGISTRY],
    )
    def test_evaluator_aggregation_rule_matches_definition(self, registered: object) -> None:
        from backend.finance_dna.registry import RegisteredDimension

        assert isinstance(registered, RegisteredDimension)
        dimension = registered.evaluator(APPLE, TEST_DATE)
        assert dimension.aggregation_rule == registered.definition.aggregation_rule


# ===========================================================================
# V0.2 Finance DNA Tests — 9 new dimensions
# ===========================================================================

from backend.finance_dna.rules import (  # noqa: E402
    evaluate_currency_exposure,
    evaluate_customer_concentration,
    evaluate_debt_sensitivity,
    evaluate_energy_dependency,
    evaluate_labour_intensity,
    evaluate_pricing_power,
    evaluate_regulatory_compliance_cost,
    evaluate_revenue_diversification,
    evaluate_supplier_concentration,
)
from backend.models.enums import ApproximationLevel  # noqa: E402


class TestV02Dimensions:
    """Tests for all nine V0.2 Finance DNA dimensions.

    Structure mirrors V0.1 test groups:
      Group A — Score values (spot checks per asset)
      Group B — Score ranges (all values in [0.0, 1.0])
      Group C — Approximation Level (all V0.2 = Level B)
      Group D — Confidence (all V0.2 = 0.65)
      Group E — Determinism (100 runs, same result)
      Group F — Registry integrity (evaluator produces matching name)
    """

    # --- Group A: Score spot checks -----------------------------------------

    def test_pricing_power_semiconductor_is_high(self) -> None:
        d = evaluate_pricing_power(NVIDIA, TEST_DATE)
        assert d.score == 0.85

    def test_pricing_power_software_is_high(self) -> None:
        d = evaluate_pricing_power(MICROSOFT, TEST_DATE)
        assert d.score == 0.85

    def test_pricing_power_consumer_electronics_is_medium(self) -> None:
        d = evaluate_pricing_power(APPLE, TEST_DATE)
        assert d.score == 0.60

    def test_pricing_power_food_beverages_is_medium(self) -> None:
        d = evaluate_pricing_power(NESTLE, TEST_DATE)
        assert d.score == 0.50

    def test_customer_concentration_semiconductor_is_high(self) -> None:
        d = evaluate_customer_concentration(TSMC, TEST_DATE)
        assert d.score == 0.70

    def test_customer_concentration_consumer_electronics_is_low(self) -> None:
        d = evaluate_customer_concentration(APPLE, TEST_DATE)
        assert d.score == 0.15

    def test_customer_concentration_software_is_low(self) -> None:
        d = evaluate_customer_concentration(MICROSOFT, TEST_DATE)
        assert d.score == 0.25

    def test_supplier_concentration_semiconductor_is_very_high(self) -> None:
        d = evaluate_supplier_concentration(NVIDIA, TEST_DATE)
        assert d.score == 0.90

    def test_supplier_concentration_software_is_very_low(self) -> None:
        d = evaluate_supplier_concentration(MICROSOFT, TEST_DATE)
        assert d.score == 0.10

    def test_supplier_concentration_consumer_electronics_is_high(self) -> None:
        d = evaluate_supplier_concentration(APPLE, TEST_DATE)
        assert d.score == 0.80

    def test_revenue_diversification_semiconductor_is_low(self) -> None:
        d = evaluate_revenue_diversification(NVIDIA, TEST_DATE)
        assert d.score == 0.30

    def test_revenue_diversification_food_beverages_is_high(self) -> None:
        d = evaluate_revenue_diversification(NESTLE, TEST_DATE)
        assert d.score == 0.75

    def test_revenue_diversification_software_is_medium_high(self) -> None:
        d = evaluate_revenue_diversification(MICROSOFT, TEST_DATE)
        assert d.score == 0.65

    def test_debt_sensitivity_software_is_very_low(self) -> None:
        d = evaluate_debt_sensitivity(MICROSOFT, TEST_DATE)
        assert d.score == 0.15

    def test_debt_sensitivity_consumer_electronics_is_very_low(self) -> None:
        d = evaluate_debt_sensitivity(APPLE, TEST_DATE)
        assert d.score == 0.15

    def test_debt_sensitivity_food_beverages_is_medium(self) -> None:
        d = evaluate_debt_sensitivity(NESTLE, TEST_DATE)
        assert d.score == 0.50

    def test_currency_exposure_semiconductor_is_high(self) -> None:
        d = evaluate_currency_exposure(TSMC, TEST_DATE)
        assert d.score == 0.80

    def test_currency_exposure_food_beverages_is_high(self) -> None:
        d = evaluate_currency_exposure(NESTLE, TEST_DATE)
        assert d.score == 0.80

    def test_currency_exposure_ecommerce_is_lower(self) -> None:
        d = evaluate_currency_exposure(AMAZON, TEST_DATE)
        assert d.score == 0.45

    def test_energy_dependency_semiconductor_is_very_high(self) -> None:
        d = evaluate_energy_dependency(TSMC, TEST_DATE)
        assert d.score == 0.85

    def test_energy_dependency_ecommerce_cloud_is_high(self) -> None:
        d = evaluate_energy_dependency(AMAZON, TEST_DATE)
        assert d.score == 0.75

    def test_energy_dependency_software_is_very_low(self) -> None:
        d = evaluate_energy_dependency(MICROSOFT, TEST_DATE)
        assert d.score == 0.15

    def test_labour_intensity_ecommerce_is_very_high(self) -> None:
        d = evaluate_labour_intensity(AMAZON, TEST_DATE)
        assert d.score == 0.80

    def test_labour_intensity_software_is_low(self) -> None:
        d = evaluate_labour_intensity(MICROSOFT, TEST_DATE)
        assert d.score == 0.25

    def test_labour_intensity_food_beverages_is_high(self) -> None:
        d = evaluate_labour_intensity(NESTLE, TEST_DATE)
        assert d.score == 0.65

    def test_regulatory_compliance_cost_internet_services_is_high(self) -> None:
        d = evaluate_regulatory_compliance_cost(ALPHABET, TEST_DATE)
        assert d.score == 0.75

    def test_regulatory_compliance_cost_software_is_medium(self) -> None:
        d = evaluate_regulatory_compliance_cost(MICROSOFT, TEST_DATE)
        assert d.score == 0.45

    def test_regulatory_compliance_cost_food_beverages_is_high(self) -> None:
        d = evaluate_regulatory_compliance_cost(NESTLE, TEST_DATE)
        assert d.score == 0.65

    # --- Group B: Score ranges -----------------------------------------------

    @pytest.mark.parametrize("asset", list(ALL_ASSETS))
    def test_all_v02_scores_in_range(self, asset: Asset) -> None:
        """All nine V0.2 evaluators must produce scores in [0.0, 1.0]."""
        evaluators = [
            evaluate_pricing_power,
            evaluate_customer_concentration,
            evaluate_supplier_concentration,
            evaluate_revenue_diversification,
            evaluate_debt_sensitivity,
            evaluate_currency_exposure,
            evaluate_energy_dependency,
            evaluate_labour_intensity,
            evaluate_regulatory_compliance_cost,
        ]
        for evaluator in evaluators:
            d = evaluator(asset, TEST_DATE)
            assert isinstance(d.score, float), (
                f"{evaluator.__name__}: score must be float, got {type(d.score)}"
            )
            assert 0.0 <= d.score <= 1.0, (
                f"{evaluator.__name__} for {asset.id}: score {d.score} out of range"
            )

    # --- Group C: Approximation Level ----------------------------------------

    @pytest.mark.parametrize("asset", list(ALL_ASSETS))
    def test_all_v02_dimensions_are_level_b(self, asset: Asset) -> None:
        """All V0.2 dimensions must carry ApproximationLevel.B."""
        evaluators = [
            evaluate_pricing_power,
            evaluate_customer_concentration,
            evaluate_supplier_concentration,
            evaluate_revenue_diversification,
            evaluate_debt_sensitivity,
            evaluate_currency_exposure,
            evaluate_energy_dependency,
            evaluate_labour_intensity,
            evaluate_regulatory_compliance_cost,
        ]
        for evaluator in evaluators:
            d = evaluator(asset, TEST_DATE)
            assert d.approximation_level == ApproximationLevel.B, (
                f"{evaluator.__name__} for {asset.id}: "
                f"expected Level B, got {d.approximation_level}"
            )

    @pytest.mark.parametrize("asset", list(ALL_ASSETS))
    def test_all_v01_dimensions_are_level_c(self, asset: Asset) -> None:
        """V0.1 dimensions must carry ApproximationLevel.C (retroactive classification)."""
        dna = evaluate(asset, as_of=TEST_DATE)
        v01_names = {
            "Capital Intensity", "Commodity Input Exposure", "Supply Chain Complexity",
            "Innovation Intensity", "Regulatory Exposure", "Geographic Revenue Concentration",
        }
        for d in dna.dimensions:
            if d.name in v01_names:
                assert d.approximation_level == ApproximationLevel.C, (
                    f"V0.1 dimension '{d.name}' for {asset.id}: "
                    f"expected Level C, got {d.approximation_level}"
                )

    # --- Group D: Confidence -------------------------------------------------

    @pytest.mark.parametrize("asset", list(ALL_ASSETS))
    def test_v02_confidence_is_065(self, asset: Asset) -> None:
        """All V0.2 dimensions must use confidence = 0.65."""
        evaluators = [
            evaluate_pricing_power,
            evaluate_customer_concentration,
            evaluate_supplier_concentration,
            evaluate_revenue_diversification,
            evaluate_debt_sensitivity,
            evaluate_currency_exposure,
            evaluate_energy_dependency,
            evaluate_labour_intensity,
            evaluate_regulatory_compliance_cost,
        ]
        for evaluator in evaluators:
            d = evaluator(asset, TEST_DATE)
            assert d.confidence == pytest.approx(0.65), (
                f"{evaluator.__name__} for {asset.id}: confidence should be 0.65"
            )

    # --- Group E: Determinism ------------------------------------------------

    def test_v02_dimensions_deterministic_100_runs(self) -> None:
        """100 evaluations of each V0.2 dimension for Apple must produce identical results."""
        evaluators = [
            evaluate_pricing_power,
            evaluate_customer_concentration,
            evaluate_supplier_concentration,
            evaluate_revenue_diversification,
            evaluate_debt_sensitivity,
            evaluate_currency_exposure,
            evaluate_energy_dependency,
            evaluate_labour_intensity,
            evaluate_regulatory_compliance_cost,
        ]
        for evaluator in evaluators:
            first = evaluator(APPLE, TEST_DATE)
            for _ in range(99):
                assert evaluator(APPLE, TEST_DATE) == first, (
                    f"{evaluator.__name__} is not deterministic"
                )

    # --- Group F: Registry integrity -----------------------------------------

    def test_v02_registry_evaluators_produce_correct_names(self) -> None:
        """Each V0.2 registered evaluator must produce a Dimension whose name
        matches its DimensionDefinition — catches definition/evaluator wiring bugs."""
        from backend.finance_dna.registry import REGISTRY
        v02_names = {
            "Pricing Power", "Customer Concentration", "Supplier Concentration",
            "Revenue Diversification", "Debt Sensitivity", "Currency Exposure",
            "Energy Dependency", "Labour Intensity", "Regulatory Compliance Cost",
        }
        for registered in REGISTRY:
            if registered.definition.name in v02_names:
                produced = registered.evaluator(APPLE, TEST_DATE)
                assert produced.name == registered.definition.name, (
                    f"Wiring bug: definition '{registered.definition.name}' "
                    f"produces Dimension named '{produced.name}'"
                )

    def test_total_registry_has_fifteen_dimensions(self) -> None:
        from backend.finance_dna.registry import REGISTRY
        assert len(REGISTRY) == 15

    def test_no_duplicate_names_in_registry(self) -> None:
        from backend.finance_dna.registry import REGISTRY
        names = [r.definition.name for r in REGISTRY]
        assert len(names) == len(set(names)), f"Duplicate names in REGISTRY: {names}"

    # --- Full pipeline smoke test -------------------------------------------

    @pytest.mark.parametrize("asset", list(ALL_ASSETS))
    def test_full_15_dimension_pipeline(self, asset: Asset) -> None:
        """Full evaluate() must return 15 dimensions for every registered asset."""
        dna = evaluate(asset, as_of=TEST_DATE)
        assert len(dna.dimensions) == 15
        assert dna.version == "0.2"
        names = [d.name for d in dna.dimensions]
        assert len(names) == len(set(names)), f"Duplicate dimensions for {asset.id}"
