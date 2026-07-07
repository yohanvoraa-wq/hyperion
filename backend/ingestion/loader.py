"""Asset registry loader.

Justified by: docs/07-SYSTEM-ARCHITECTURE.md §5 (Entry: Portfolio ->
Normalization -> Asset Resolution -> Finance DNA) and
docs/04-FINANCE-DNA.md §4 (Scope: Version 1 covers publicly traded companies).

Responsibility: read datasets/assets.csv and return an AssetRegistry that
resolver.py can query. Nothing else. No Finance DNA logic, no graph logic,
no scoring.

Technology constraints (ED-009, ED-004):
  - stdlib csv module only — no pandas, no SQL, no external dependencies.
  - stdlib pathlib.Path for file handling.
  - All returned objects are immutable (Asset is frozen=True; registry
    internals use MappingProxyType).

AssetRegistry is an ingestion-internal type. It is not a cross-module
artifact and is not exported from backend/models/. It exists only to
give resolver.py a clean, queryable interface over the CSV data.
"""

import csv
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

from backend.ingestion.exceptions import AssetDataError
from backend.models import Asset, AssetType

# ---------------------------------------------------------------------------
# Default dataset path — relative to repository root, per ED-003.
# ---------------------------------------------------------------------------

_DATASET_PATH: Path = Path(__file__).parent.parent.parent / "datasets" / "assets.csv"

# ---------------------------------------------------------------------------
# Name normalisation
# ---------------------------------------------------------------------------

_COMPANY_SUFFIXES: frozenset[str] = frozenset(
    {
        "inc",
        "inc.",
        "incorporated",
        "corp",
        "corp.",
        "corporation",
        "co",
        "co.",
        "ltd",
        "ltd.",
        "limited",
        "sa",
        "s.a.",
        "s.a",
        "plc",
        "llc",
        "ag",
        "nv",
        "company",
    }
)


def _normalize(raw: str) -> str:
    """Return a lowercase, suffix-stripped, punctuation-reduced string.

    Used to build lookup keys for company names and aliases so that
    'Apple Inc.', 'Apple Inc', and 'apple' all resolve to the same key.

    This function is intentionally narrow — it strips common legal suffixes
    and normalises whitespace. It does not perform fuzzy matching, phonetic
    matching, or any probabilistic transformation. Every lookup is exact
    after normalisation; ambiguity is a data-quality problem to be fixed
    in datasets/assets.csv, not a signal to guess.
    """
    tokens = raw.lower().strip().split()
    cleaned: list[str] = []
    for token in tokens:
        stripped = token.strip(".,;")
        if stripped not in _COMPANY_SUFFIXES:
            cleaned.append(stripped)
    return " ".join(cleaned)


# ---------------------------------------------------------------------------
# AssetRegistry
# ---------------------------------------------------------------------------


class AssetRegistry:
    """Queryable, immutable registry of all Assets known to Hyperion V0.1.

    Internal to the Ingestion layer — not a cross-module artifact.
    Constructed by load_asset_registry(); consumed by resolver.py.

    Lookup order inside find():
      1. Uppercase ticker  (e.g. 'AAPL')
      2. Normalised name   (e.g. 'apple', from 'Apple Inc.')
      3. Normalised alias  (e.g. 'tsmc', from the aliases column)
      4. Exact asset id    (e.g. 'apple-inc', for programmatic use)

    All internal dicts are wrapped in MappingProxyType to prevent
    mutation after construction — consistent with ED-004 principle 2
    (Never duplicate knowledge) and ED-005 (Data Ownership).
    """

    # Class-level attribute annotations required by mypy --strict.
    _by_id: Mapping[str, Asset]
    _by_ticker: Mapping[str, str]  # normalised ticker  → asset_id
    _by_name: Mapping[str, str]  # normalised name    → asset_id
    _by_alias: Mapping[str, str]  # normalised alias   → asset_id

    def __init__(
        self,
        by_id: dict[str, Asset],
        by_ticker: dict[str, str],
        by_name: dict[str, str],
        by_alias: dict[str, str],
    ) -> None:
        self._by_id = MappingProxyType(by_id)
        self._by_ticker = MappingProxyType(by_ticker)
        self._by_name = MappingProxyType(by_name)
        self._by_alias = MappingProxyType(by_alias)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def find(self, raw: str) -> Asset | None:
        """Return the Asset matching raw, or None if not found.

        Tries four lookup strategies in priority order so that the caller
        does not need to know which kind of identifier it has — a ticker,
        a full legal name, a common alias, or an internal id all resolve
        transparently.
        """
        # 1. Ticker (uppercase, stripped)
        ticker_key = raw.strip().upper()
        if ticker_key in self._by_ticker:
            return self._by_id[self._by_ticker[ticker_key]]

        # 2. Normalised name
        name_key = _normalize(raw)
        if name_key in self._by_name:
            return self._by_id[self._by_name[name_key]]

        # 3. Normalised alias
        if name_key in self._by_alias:
            return self._by_id[self._by_alias[name_key]]

        # 4. Exact asset id (programmatic / test use)
        if raw in self._by_id:
            return self._by_id[raw]

        return None

    @property
    def assets(self) -> tuple[Asset, ...]:
        """All Assets in the registry, in load order."""
        return tuple(self._by_id.values())

    def __len__(self) -> int:
        return len(self._by_id)


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def load_asset_registry(csv_path: Path | None = None) -> AssetRegistry:
    """Read the asset CSV and return an AssetRegistry.

    Justified by: 07-SYSTEM-ARCHITECTURE.md §5 — the Ingestion layer owns
    normalization and resolution. This function is the first half of that
    responsibility: turning raw CSV rows into a queryable, immutable registry
    of Asset objects.

    Parameters
    ----------
    csv_path:
        Path to the asset CSV file. Defaults to datasets/assets.csv relative
        to the repository root. Passing an explicit path is the mechanism
        used by tests to point at a fixture CSV without modifying global state.

    Raises
    ------
    FileNotFoundError
        If the CSV file does not exist. This is a configuration/setup error,
        not an ingestion error — callers should not catch it silently.
    AssetDataError
        If any row in the CSV is structurally malformed (missing required
        fields, empty id, etc.).
    """
    path = csv_path or _DATASET_PATH

    by_id: dict[str, Asset] = {}
    by_ticker: dict[str, str] = {}
    by_name: dict[str, str] = {}
    by_alias: dict[str, str] = {}

    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)

        for row in reader:
            # --- Validate required fields -----------------------------------
            for field in ("id", "ticker", "name", "sector", "industry"):
                if not row.get(field, "").strip():
                    raise AssetDataError(dict(row), f"required field '{field}' is empty or missing")

            asset_id = row["id"].strip()
            ticker = row["ticker"].strip()
            name = row["name"].strip()

            asset = Asset(
                id=asset_id,
                name=name,
                ticker=ticker,
                asset_type=AssetType.COMPANY,  # V0.1 scope: companies only
                sector=row["sector"].strip() or None,
                industry=row["industry"].strip() or None,
            )

            by_id[asset_id] = asset
            by_ticker[ticker.upper()] = asset_id
            by_name[_normalize(name)] = asset_id

            # --- Aliases (optional column) ----------------------------------
            raw_aliases = row.get("aliases", "")
            for alias in raw_aliases.split(";"):
                alias = alias.strip()
                if alias:
                    by_alias[_normalize(alias)] = asset_id
                    # Also register the alias as-is in uppercase for
                    # ticker-style aliases like 'TSMC'
                    by_ticker[alias.upper()] = asset_id

    return AssetRegistry(by_id, by_ticker, by_name, by_alias)
