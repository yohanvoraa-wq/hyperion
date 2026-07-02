"""Asset domain model.

Justified by: docs/02-FOUNDATIONAL-CONCEPTS.md (concept #2 — Asset) and
docs/04-FINANCE-DNA.md §4 (Scope: Version 1 covers publicly traded companies).

An Asset is the smallest unit Hyperion reasons about. Under Version 1's scope
this is always a publicly traded Company. The AssetType field allows future
versions to extend to other asset classes without changing this model's shape.

Immutability: frozen=True enforces ED-005 (Data Ownership). Finance DNA owns
the Dimensions computed over an Asset; it never mutates the Asset itself.
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.models.enums import AssetType


@dataclass(frozen=True)
class Asset:
    """A single financial instrument capable of representing economic value.

    Fields are deliberately minimal — this model encodes identity, not
    valuation or characteristics (those belong to Dimension). Every field
    here is something an Asset *is*, not something it *measures*.
    """

    id: str
    """Stable, unique identifier. Ticker is not used as the primary key
    because the same company can trade on multiple exchanges under different
    tickers. A deterministic slug (e.g. 'apple-inc') is preferred for V0.1."""

    name: str
    """Human-readable full name (e.g. 'Apple Inc.')."""

    ticker: str | None
    """Primary ticker symbol, if publicly traded. None for Supply Chain
    Entities that appear in Atlas but have no public listing (Atlas §3)."""

    asset_type: AssetType
    """Node sub-type per Atlas §3. COMPANY for Version 1 scope."""

    sector: str | None
    """Broad sector classification (e.g. 'Technology'). Nullable — not every
    Asset resolution will have this on first ingestion."""

    industry: str | None
    """Narrower industry classification. Maps to the Industry node type in
    Atlas §3 via the belongs_to relationship, once Atlas is populated."""
