"""Ingestion layer exceptions.

Justified by: docs/07-SYSTEM-ARCHITECTURE.md §5 (Entry hop) and
docs/04-FINANCE-DNA.md §4 (Scope: Version 1 covers publicly traded companies).

Custom exceptions serve two architectural purposes:
  1. They make Ingestion failures explicitly distinguishable from any other
     Python exception — a caller can catch IngestionError and know exactly
     which layer failed, without guessing from a generic ValueError.
  2. They carry the raw input that caused the failure, so the Output layer
     can surface a precise, inspectable error message rather than a traceback.
     This is the first expression of Hyperion's Explainability principle at
     the engineering layer: even failures must be traceable to their cause.

No new architectural concept is introduced here. The four exception types
below correspond directly to the four failure modes the Ingestion layer can
encounter: an unresolvable identifier, a duplicate Asset, an empty request,
and malformed source data.
"""


class IngestionError(Exception):
    """Base class for all Ingestion layer errors.

    All Ingestion failures are subtypes of this class so that callers can
    catch the entire category with a single except clause when appropriate.
    """


class UnknownAssetError(IngestionError):
    """Raised when a raw identifier cannot be resolved to any known Asset.

    Per 07-SYSTEM-ARCHITECTURE.md §5: the Ingestion layer owns normalization
    and resolution; if resolution fails, the failure belongs here, not in
    Finance DNA or any downstream module.
    """

    def __init__(self, raw: str) -> None:
        self.raw = raw
        super().__init__(
            f"Cannot resolve '{raw}' to a known Asset. "
            "Check that the identifier matches a name, ticker, or alias "
            "in datasets/assets.csv."
        )


class DuplicateAssetError(IngestionError):
    """Raised when two or more raw identifiers resolve to the same Asset.

    Example: ['Apple', 'AAPL'] both resolve to 'apple-inc'. A Portfolio
    cannot hold the same Asset twice — that would misrepresent the actual
    holding structure and corrupt any Portfolio DNA computed downstream.
    """

    def __init__(self, asset_id: str, raw_identifiers: tuple[str, ...]) -> None:
        self.asset_id = asset_id
        self.raw_identifiers = raw_identifiers
        super().__init__(
            f"Asset '{asset_id}' was resolved from multiple identifiers: "
            f"{raw_identifiers}. A Portfolio cannot hold the same Asset twice."
        )


class EmptyPortfolioError(IngestionError):
    """Raised when an empty list of identifiers is provided.

    An empty Portfolio is structurally invalid per
    02-FOUNDATIONAL-CONCEPTS.md (concept #3): a Portfolio is a collection
    of Assets; a collection of zero Assets is not a Portfolio.
    """

    def __init__(self) -> None:
        super().__init__(
            "Cannot create a Portfolio from an empty identifier list. "
            "Provide at least one company name or ticker."
        )


class AssetDataError(IngestionError):
    """Raised when a row in the asset dataset is structurally malformed.

    Separates data-quality failures (a broken CSV row) from resolution
    failures (an identifier that simply isn't in the dataset). A caller
    that catches UnknownAssetError should not also be catching CSV parse
    errors — those are a different problem with a different fix.
    """

    def __init__(self, row: dict[str, str], reason: str) -> None:
        self.row = row
        self.reason = reason
        super().__init__(f"Malformed asset row in datasets/assets.csv: {reason}. Row: {row}")
