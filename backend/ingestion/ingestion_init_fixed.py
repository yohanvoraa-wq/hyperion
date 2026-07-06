"""Portfolio Ingestion Layer -- public interface.

Justified by: docs/07-SYSTEM-ARCHITECTURE.md Section 4 (hop 1) and Section 5
(Entry: Portfolio -> Normalization -> Asset Resolution -> Finance DNA).

Single responsibility: convert a list of raw company identifiers into
an immutable Portfolio of resolved Asset objects.

Public API
----------
load_portfolio(raw_identifiers, *, name, csv_path) -> Portfolio
    One-call convenience function. Entry point for all callers.

resolve_portfolio(raw_identifiers, registry, *, name) -> Portfolio
    Resolution against a pre-loaded registry. Use when resolving
    multiple portfolios without reloading the CSV each time.

load_asset_registry(csv_path) -> AssetRegistry
    Load the registry independently (e.g. for tests or inspection).

AssetRegistry
    The internal registry type, exposed for type annotations.

IngestionError, UnknownAssetError, DuplicateAssetError,
EmptyPortfolioError, AssetDataError
    Exception types for structured error handling.

Boundary contract (07-SYSTEM-ARCHITECTURE.md section 6):
    This module imports from backend.models only.
    It never imports from finance_dna, atlas, janus, or titan.
    Finance DNA never sees raw strings; it only ever receives
    the Portfolio this module produces.
"""

from backend.ingestion.exceptions import (
    AssetDataError,
    DuplicateAssetError,
    EmptyPortfolioError,
    IngestionError,
    UnknownAssetError,
)
from backend.ingestion.loader import AssetRegistry, load_asset_registry
from backend.ingestion.resolver import load_portfolio, resolve_portfolio

__all__ = [
    # Primary entry point
    "load_portfolio",
    # Lower-level functions
    "resolve_portfolio",
    "load_asset_registry",
    # Internal registry type (for type annotations)
    "AssetRegistry",
    # Exceptions
    "IngestionError",
    "UnknownAssetError",
    "DuplicateAssetError",
    "EmptyPortfolioError",
    "AssetDataError",
]
