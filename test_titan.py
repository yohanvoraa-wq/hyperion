"""Tests for backend/ingestion — ED-007 (Testing Philosophy), category 1.

Covers every scenario from the Milestone 3 specification:
  - Known company by full name
  - Known company by ticker
  - Known company by alias
  - Case-insensitive lookup
  - Unknown identifier → UnknownAssetError
  - Duplicate resolution → DuplicateAssetError
  - Empty list → EmptyPortfolioError
  - Three-company portfolio with correct equal weights
  - Single-asset portfolio with weight = 1.0
  - Portfolio is immutable
  - Assets inside Portfolio are immutable
  - Asset fields populated correctly from CSV
  - Custom portfolio name preserved
  - Registry size matches dataset
  - Resolve with pre-loaded registry (separate from load_portfolio)
  - Malformed CSV row → AssetDataError
  - Weight arithmetic: weights always sum to exactly 1.0

Tests use a small, self-contained fixture CSV rather than the real
datasets/assets.csv so they are deterministic and independent of dataset
changes. This is the right pattern for unit tests per ED-007: test the
behaviour of the ingestion code, not the content of the dataset.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from backend.ingestion import (
    AssetDataError,
    AssetRegistry,
    DuplicateAssetError,
    EmptyPortfolioError,
    UnknownAssetError,
    load_asset_registry,
    load_portfolio,
    resolve_portfolio,
)
from backend.models import AssetType, Portfolio

# ---------------------------------------------------------------------------
# Fixture CSV — minimal, self-contained, deterministic
# ---------------------------------------------------------------------------

FIXTURE_CSV_CONTENT = """\
id,ticker,name,sector,industry,aliases
apple-inc,AAPL,Apple Inc.,Technology,Consumer Electronics,apple
microsoft,MSFT,Microsoft Corporation,Technology,Software,msft
nvidia,NVDA,NVIDIA Corporation,Technology,Semiconductors,nvda
tsmc,TSM,Taiwan Semiconductor Manufacturing Company,Technology,Semiconductors,tsmc
"""

MALFORMED_CSV_CONTENT = """\
id,ticker,name,sector,industry,aliases
,AAPL,Apple Inc.,Technology,Consumer Electronics,
"""


@pytest.fixture()
def fixture_csv(tmp_path: Path) -> Path:
    """Write the fixture CSV to a temp file and return its path."""
    csv_file = tmp_path / "assets.csv"
    csv_file.write_text(FIXTURE_CSV_CONTENT, encoding="utf-8")
    return csv_file


@pytest.fixture()
def malformed_csv(tmp_path: Path) -> Path:
    csv_file = tmp_path / "bad_assets.csv"
    csv_file.write_text(MALFORMED_CSV_CONTENT, encoding="utf-8")
    return csv_file


@pytest.fixture()
def registry(fixture_csv: Path) -> AssetRegistry:
    return load_asset_registry(fixture_csv)


# ---------------------------------------------------------------------------
# 1. Registry loading
# ---------------------------------------------------------------------------


class TestLoadAssetRegistry:
    def test_registry_size_matches_dataset(self, registry: AssetRegistry) -> None:
        """Registry contains exactly as many assets as the fixture CSV has rows."""
        assert len(registry) == 4

    def test_all_assets_are_company_type(self, registry: AssetRegistry) -> None:
        """V0.1 scope: every Asset is AssetType.COMPANY (04-FINANCE-DNA.md §4)."""
        for asset in registry.assets:
            assert asset.asset_type == AssetType.COMPANY

    def test_asset_fields_populated_correctly(self, registry: AssetRegistry) -> None:
        """Asset fields match the CSV row exactly."""
        asset = registry.find("apple-inc")
        assert asset is not None
        assert asset.id == "apple-inc"
        assert asset.name == "Apple Inc."
        assert asset.ticker == "AAPL"
        assert asset.sector == "Technology"
        assert asset.industry == "Consumer Electronics"

    def test_malformed_row_raises_asset_data_error(self, malformed_csv: Path) -> None:
        """A row with an empty required field raises AssetDataError."""
        with pytest.raises(AssetDataError, match="required field 'id'"):
            load_asset_registry(malformed_csv)

    def test_missing_file_raises_file_not_found(self, tmp_path: Path) -> None:
        """Missing CSV raises FileNotFoundError — a setup error, not an ingestion error."""
        with pytest.raises(FileNotFoundError):
            load_asset_registry(tmp_path / "does_not_exist.csv")


# ---------------------------------------------------------------------------
# 2. Identifier resolution
# ---------------------------------------------------------------------------


class TestResolution:
    def test_lookup_by_full_name(self, registry: AssetRegistry) -> None:
        asset = registry.find("Apple Inc.")
        assert asset is not None
        assert asset.id == "apple-inc"

    def test_lookup_by_ticker(self, registry: AssetRegistry) -> None:
        asset = registry.find("AAPL")
        assert asset is not None
        assert asset.id == "apple-inc"

    def test_lookup_by_alias(self, registry: AssetRegistry) -> None:
        """'TSMC' is an alias for 'tsmc' in the fixture CSV."""
        asset = registry.find("TSMC")
        assert asset is not None
        assert asset.id == "tsmc"

    def test_lookup_case_insensitive_name(self, registry: AssetRegistry) -> None:
        """'apple', 'Apple', 'APPLE' all resolve to the same Asset."""
        lower = registry.find("apple")
        upper = registry.find("Apple")
        assert lower is not None
        assert upper is not None
        assert lower.id == upper.id == "apple-inc"

    def test_lookup_case_insensitive_ticker(self, registry: AssetRegistry) -> None:
        """'aapl' and 'AAPL' resolve to the same Asset."""
        assert registry.find("aapl") == registry.find("AAPL")

    def test_lookup_name_without_legal_suffix(self, registry: AssetRegistry) -> None:
        """'Microsoft' resolves even though the CSV name is 'Microsoft Corporation'."""
        asset = registry.find("Microsoft")
        assert asset is not None
        assert asset.id == "microsoft"

    def test_unknown_identifier_returns_none(self, registry: AssetRegistry) -> None:
        assert registry.find("UnknownCompany XYZ") is None

    def test_lookup_by_asset_id(self, registry: AssetRegistry) -> None:
        """Exact asset id resolves (used programmatically in tests / scripts)."""
        asset = registry.find("nvidia-corp")
        # 'nvidia-corp' is not in fixture — should return None
        assert asset is None
        asset = registry.find("nvidia")
        assert asset is not None and asset.id == "nvidia"


# ---------------------------------------------------------------------------
# 3. Portfolio construction
# ---------------------------------------------------------------------------


class TestResolvePortfolio:
    def test_three_company_portfolio(self, registry: AssetRegistry) -> None:
        """The ED-009 demo portfolio resolves correctly."""
        portfolio = resolve_portfolio(["Apple", "NVIDIA", "Microsoft"], registry, name="Demo")
        assert len(portfolio.assets) == 3
        assert portfolio.name == "Demo"
        ids = {a.id for a in portfolio.assets}
        assert ids == {"apple-inc", "nvidia", "microsoft"}

    def test_three_company_portfolio_equal_weights(self, registry: AssetRegistry) -> None:
        portfolio = resolve_portfolio(["Apple", "NVIDIA", "Microsoft"], registry)
        assert abs(sum(portfolio.weights) - 1.0) < 1e-9
        for w in portfolio.weights:
            assert abs(w - 1.0 / 3) < 1e-9

    def test_single_asset_portfolio_weight_is_one(self, registry: AssetRegistry) -> None:
        portfolio = resolve_portfolio(["Apple"], registry)
        assert portfolio.weights == (1.0,)

    def test_custom_portfolio_name_preserved(self, registry: AssetRegistry) -> None:
        portfolio = resolve_portfolio(["Apple"], registry, name="My Portfolio")
        assert portfolio.name == "My Portfolio"

    def test_unknown_identifier_raises(self, registry: AssetRegistry) -> None:
        with pytest.raises(UnknownAssetError) as exc_info:
            resolve_portfolio(["Apple", "UnknownCo"], registry)
        assert exc_info.value.raw == "UnknownCo"

    def test_duplicate_by_different_identifier_raises(self, registry: AssetRegistry) -> None:
        """'Apple' and 'AAPL' both resolve to 'apple-inc' — this is a duplicate."""
        with pytest.raises(DuplicateAssetError) as exc_info:
            resolve_portfolio(["Apple", "AAPL"], registry)
        assert exc_info.value.asset_id == "apple-inc"
        assert "Apple" in exc_info.value.raw_identifiers
        assert "AAPL" in exc_info.value.raw_identifiers

    def test_duplicate_same_name_raises(self, registry: AssetRegistry) -> None:
        with pytest.raises(DuplicateAssetError):
            resolve_portfolio(["Apple", "Apple"], registry)

    def test_empty_list_raises(self, registry: AssetRegistry) -> None:
        with pytest.raises(EmptyPortfolioError):
            resolve_portfolio([], registry)

    def test_asset_order_preserved(self, registry: AssetRegistry) -> None:
        """Assets appear in the Portfolio in the same order as the input list."""
        portfolio = resolve_portfolio(["Microsoft", "Apple", "NVIDIA"], registry)
        assert portfolio.assets[0].id == "microsoft"
        assert portfolio.assets[1].id == "apple-inc"
        assert portfolio.assets[2].id == "nvidia"


# ---------------------------------------------------------------------------
# 4. Immutability (ED-005 — Data Ownership)
# ---------------------------------------------------------------------------


class TestImmutability:
    def test_portfolio_is_immutable(self, registry: AssetRegistry) -> None:
        portfolio = resolve_portfolio(["Apple"], registry)
        with pytest.raises(FrozenInstanceError):
            portfolio.name = "Hacked"  # type: ignore[misc]

    def test_assets_inside_portfolio_are_immutable(self, registry: AssetRegistry) -> None:
        portfolio = resolve_portfolio(["Apple"], registry)
        with pytest.raises(FrozenInstanceError):
            portfolio.assets[0].name = "Hacked"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 5. load_portfolio convenience function (ED-009 entry point)
# ---------------------------------------------------------------------------


class TestLoadPortfolio:
    def test_load_portfolio_end_to_end(self, fixture_csv: Path) -> None:
        """The exact call from ED-009 works with the fixture dataset."""
        portfolio = load_portfolio(
            ["Apple", "NVIDIA", "Microsoft"],
            name="MVP Portfolio",
            csv_path=fixture_csv,
        )
        assert isinstance(portfolio, Portfolio)
        assert len(portfolio.assets) == 3
        assert portfolio.name == "MVP Portfolio"

    def test_load_portfolio_weights_sum_to_one(self, fixture_csv: Path) -> None:
        portfolio = load_portfolio(["Apple", "NVIDIA", "Microsoft"], csv_path=fixture_csv)
        assert abs(sum(portfolio.weights) - 1.0) < 1e-9

    def test_load_portfolio_unknown_raises(self, fixture_csv: Path) -> None:
        with pytest.raises(UnknownAssetError):
            load_portfolio(["Hyperion Holdings Ltd"], csv_path=fixture_csv)

    def test_load_portfolio_empty_raises(self, fixture_csv: Path) -> None:
        with pytest.raises(EmptyPortfolioError):
            load_portfolio([], csv_path=fixture_csv)
