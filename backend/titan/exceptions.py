"""Titan layer exceptions.

Justified by: docs/03-BLIND-SPOT-FRAMEWORK.md §7 and the frozen design
decisions for Titan V0.

Two exception types matching the two distinct failure modes:
  TitanError          — base class
  QualificationError  — raised when qualify() is called explicitly wanting
                        a BlindSpot but the ReasoningArtifact fails at
                        least one qualification criterion.

Note: qualify() itself returns None rather than raising in the normal case.
QualificationError exists for callers that treat disqualification as an
error condition — for example, a future pipeline step that asserts every
surfaced artifact must produce a BlindSpot.
"""


class TitanError(Exception):
    """Base class for all Titan layer errors."""


class QualificationError(TitanError):
    """Raised when a ReasoningArtifact fails one or more qualification criteria.

    Per 03-BLIND-SPOT-FRAMEWORK.md §7: all four criteria must hold.
    A single failing criterion is sufficient to disqualify the artifact.
    """

    def __init__(self, failed_criterion: str, reason: str) -> None:
        self.failed_criterion = failed_criterion
        self.reason = reason
        super().__init__(
            f"ReasoningArtifact failed qualification criterion "
            f"'{failed_criterion}': {reason}"
        )
