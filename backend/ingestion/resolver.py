"""Portfolio resolver.

Justified by: docs/07-SYSTEM-ARCHITECTURE.md §5 (Entry: Portfolio ->
Normalization -> Asset Resolution -> Finance DNA).

Responsibility: take a list of raw string identifiers, resolve each one to
an Asset via the AssetRegistry, detect duplicates, assign equal weights, and
return an immutable Portfolio.

This module is the second and final step of the Ingestion layer. Its output
— a Portfolio of resolved, immutable Asset objects — is the exact artifact
Finance DNA expects. Finance DNA never sees raw strings; it never sees the
CSV; it never calls into this module. The boundary is clean.

What this module deliberately does not do:
  - Assign non-equal weights (no business logic belongs here)
  - Score Assets (Finance DNA's job)
  - Build graph relationships (Atlas's job)
  - Reason about the portfolio (Janus's job)
  - Make any external API call
"""

from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path

from backend.ingestion.exceptions import (
    DuplicateAssetError,
    EmptyPortfolioError,
    UnknownAssetError,
)
from backend.ingestion.loader import AssetRegistry, load_asset_registry
from backend.models import Asset, Portfolio

# ---------------------------------------------------------------------------
# Core resolution function
# ---------------------------------------------------------------------------


def resolve_portfolio(
    raw_identifiers: Sequence[str],
    registry: AssetRegistry,
    *,
    name: str = "Portfolio",
) -> Portfolio:
    """Resolve raw identifiers to a Portfolio using a pre-loaded registry.

    This is the primary function of the Ingestion layer. It maps the
    'Entry' hop in 07-SYSTEM-ARCHITECTURE.md §4 from a raw list of
    company names/tickers to the Portfolio artifact Finance DNA expects.

    Parameters
    ----------
    raw_identifiers:
        One or more company names, tickers, or aliases. Order is preserved
        in the resulting Portfolio. Case is irrelevant.
    registry:
        A pre-loaded AssetRegistry from load_asset_registry(). Separating
        registry loading from resolution allows tests to inject a minimal
        fixture registry without touching the filesystem, and allows a
        production caller to load the registry once and resolve many
        portfolios against it.
    name:
        Human-readable name for the resulting Portfolio.

    Returns
    -------
    Portfolio
        Immutable Portfolio with equal weights (1 / n per Asset).

    Raises
    ------
    EmptyPortfolioError
        If raw_identifiers is empty.
    UnknownAssetError
        If any identifier cannot be resolved to a known Asset.
    DuplicateAssetError
        If two or more identifiers resolve to the same Asset (e.g.
        ['Apple', 'AAPL'] both resolve to 'apple-inc').
    """
    if not raw_identifiers:
        raise EmptyPortfolioError()

    # --- Resolve each identifier -------------------------------------------
    resolved: list[Asset] = []
    for raw in raw_identifiers:
        asset = registry.find(raw)
        if asset is None:
            raise UnknownAssetError(raw)
        resolved.append(asset)

    # --- Detect duplicates --------------------------------------------------
    # Group raw identifiers by the asset_id they resolved to. If any
    # asset_id appears more than once, the same Asset was named twice.
    id_to_raws: dict[str, list[str]] = defaultdict(list)
    for raw, asset in zip(raw_identifiers, resolved, strict=True):
        id_to_raws[asset.id].append(raw)

    for asset_id, raws in id_to_raws.items():
        if len(raws) > 1:
            raise DuplicateAssetError(asset_id, tuple(raws))

    # --- Assign equal weights -----------------------------------------------
    # Finance DNA and Atlas will use asset identity, not weights — weights
    # matter for Portfolio DNA aggregation downstream. For V0.1, equal
    # weighting is the only correct assumption: we know nothing about
    # actual position sizes from a bare list of company names.
    weights = _equal_weights(len(resolved))

    return Portfolio(
        name=name,
        assets=tuple(resolved),
        weights=weights,
    )


# ---------------------------------------------------------------------------
# Convenience function — the public entry point
# ---------------------------------------------------------------------------


def load_portfolio(
    raw_identifiers: Sequence[str],
    *,
    name: str = "Portfolio",
    csv_path: Path | None = None,
) -> Portfolio:
    """Load the asset registry and resolve a Portfolio in one call.

    This is the function referenced in ED-009 (MVP Scope):
        portfolio = load_portfolio(["Apple", "NVIDIA", "Microsoft"])

    It is a convenience wrapper over load_asset_registry() +
    resolve_portfolio(). Use resolve_portfolio() directly when you need
    to resolve multiple portfolios without reloading the registry each time.

    Parameters
    ----------
    raw_identifiers:
        Company names, tickers, or aliases in any order.
    name:
        Human-readable Portfolio name. Defaults to 'Portfolio'.
    csv_path:
        Override the default datasets/assets.csv path. Used by tests.
    """
    registry = load_asset_registry(csv_path)
    return resolve_portfolio(raw_identifiers, registry, name=name)


# ---------------------------------------------------------------------------
# Internal utilities
# ---------------------------------------------------------------------------


def _equal_weights(n: int) -> tuple[float, ...]:
    """Return n equal weights that sum to exactly 1.0.

    The naive [1.0 / n] * n can produce a sum of 0.9999999999999999 for
    some values of n due to floating-point representation. The final weight
    absorbs the rounding remainder so Portfolio's __post_init__ invariant
    (sum within 1e-6 of 1.0) is always satisfied.
    """
    if n == 0:
        return ()
    weight = 1.0 / n
    weights = [weight] * (n - 1)
    weights.append(1.0 - weight * (n - 1))
    return tuple(weights)
