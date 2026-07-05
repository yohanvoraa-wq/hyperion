"""Janus layer exceptions.

Justified by: docs/06-JANUS.md and the frozen design decisions for V0.

Two exception types, matching the two ways Janus can fail:
  JanusError           — base class
  NoReasoningPathError — raised when reason() is called explicitly wanting
                         an artifact but the graph contains no significant
                         path for the given asset.

Note: reason() itself returns None rather than raising NoReasoningPathError
in the normal case. NoReasoningPathError exists for callers that treat
the absence of a path as an error condition (e.g. a future pipeline step
that asserts every portfolio asset must have at least one reasoning path).
"""


class JanusError(Exception):
    """Base class for all Janus layer errors."""


class NoReasoningPathError(JanusError):
    """Raised when no significant reasoning path exists for an asset.

    Significant means: ends at a MACRO_FACTOR or ECONOMIC_EVENT node,
    confidence_product >= 0.5, depth <= 4, no repeated nodes.
    Silence (returning None) is the normal V0 behavior when this occurs.
    """

    def __init__(self, asset_id: str) -> None:
        self.asset_id = asset_id
        super().__init__(
            f"No significant reasoning path found for asset '{asset_id}'. "
            "The Atlas graph may not contain a path from this asset to a "
            "MACRO_FACTOR or ECONOMIC_EVENT node that meets the significance "
            "criteria (confidence_product >= 0.5, depth <= 4, no cycles)."
        )
