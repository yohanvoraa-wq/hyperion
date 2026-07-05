"""ReasoningArtifact domain model — Janus's output.

Justified by: docs/06-JANUS.md, specifically:
  - §2  (What Makes a Valid Inference? — five criteria become the fields'
          constraints, not separate validation objects)
  - §3  (Reasoning Modes — the reasoning_mode field)
  - §4  (Reasoning Chains — the steps field: Observation→Evidence→Inference)
  - §5  (Explainability — the five questions every artifact must answer)
  - §6  (Output: The Reasoning Artifact — the official name and boundary)

Janus owns ReasoningArtifact objects permanently. Per 07-SYSTEM-ARCHITECTURE.md
§5: Titan may evaluate a ReasoningArtifact and accept or reject it, but it may
not edit the reasoning inside it. A Titan that rewrites a Reasoning Chain to
make a Blind Spot look stronger has stopped being Titan.

The five explainability questions from Janus §5, mapped to fields:
  Why?                    → reasoning_steps (the chain itself, in order)
  Supported by what?      → supporting_evidence
  How confident?          → confidence
  What assumptions?       → assumptions
  What would change this? → falsifiability_conditions
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.models.enums import ReasoningMode


@dataclass(frozen=True)
class ReasoningStep:
    """One inference in a Reasoning Chain.

    Justified by: Janus §4's Atlas→Janus table, which shows each step
    is either an Observation, an Evidence citation, or an Inference
    that legitimately follows from what came before it.

    The five Janus §2 criteria are enforced here structurally:
      Logical validity    → inference must follow from premise (by convention;
                            Janus V0 produces these deterministically, so the
                            output is always valid by construction)
      Evidence preservation → confidence cannot exceed weakest upstream step
                              (enforced in Janus, not here — this model only
                               stores the result, not how it was produced)
      No unsupported assumptions → see ReasoningArtifact.assumptions
      Reproducibility    → same inputs always produce the same steps
                           (enforced in Janus by deterministic construction)
      Boundedness        → see ReasoningArtifact.falsifiability_conditions
    """

    premise: str
    """The fact or prior conclusion this step's inference depends on.
    Must be either a directly qualified Atlas Relationship, an Observation,
    or the conclusion of a prior ReasoningStep — never a new claim introduced
    silently. Janus §2: Logical validity."""

    inference: str
    """The new claim this step produces from its premise.
    This is what Janus §4 labels 'Inference' or 'Conclusion' in the
    Atlas→Janus worked example table."""

    evidence: tuple[str, ...]
    """The inspectable facts supporting this specific step.
    Janus §2: Evidence preservation and No unsupported assumptions."""

    confidence: float
    """Step-level confidence, 0.0–1.0. The ReasoningArtifact's overall
    confidence cannot exceed the minimum across all steps' confidence values.
    Janus §2: Evidence preservation."""


@dataclass(frozen=True)
class ReasoningArtifact:
    """The complete, explainable output of one Janus reasoning process.

    Per Janus §6 (Output: The Reasoning Artifact): 'Janus's responsibility
    ends once it has produced a fully explainable reasoning artifact
    containing the observation, evidence, reasoning chain, conclusion,
    confidence, assumptions, and conditions under which that conclusion
    would change.'

    This is the exact artifact Titan receives. Titan qualifies or rejects it.
    It may not edit it.
    """

    # ------------------------------------------------------------------
    # Question and mode — Janus §3
    # ------------------------------------------------------------------

    question: str
    """The question this reasoning process was initiated to answer.
    Determines which ReasoningMode is appropriate and which part of
    the Atlas graph Janus traverses."""

    reasoning_mode: ReasoningMode
    """One of the five modes from Janus §3. Determines the shape of the
    conclusion (single path for DEDUCTIVE, set of possibilities for
    EXPLORATORY and COUNTERFACTUAL, etc.)."""

    # ------------------------------------------------------------------
    # The Reasoning Chain — Janus §4
    # ------------------------------------------------------------------

    observation: str
    """The initial fact the chain starts from — the first row in Janus §4's
    Atlas→Janus table: 'Nestlé depends on coffee as a commodity input.'"""

    reasoning_steps: tuple[ReasoningStep, ...]
    """Ordered steps connecting observation to conclusion. Each step's
    premise must trace to a prior step's inference or to the observation
    above — Janus §2: Logical validity; no gaps allowed."""

    conclusion: str
    """The final claim the chain produces. Per Janus §4: 'therefore
    producing a candidate Blind Spot for Titan to evaluate.'"""

    # ------------------------------------------------------------------
    # Explainability fields — Janus §5 (the five questions)
    # ------------------------------------------------------------------

    confidence: float
    """Overall confidence, 0.0–1.0.
    Must equal min(step.confidence for step in reasoning_steps).
    Janus §2: Evidence preservation — the chain cannot claim more
    certainty than its weakest step."""

    supporting_evidence: tuple[str, ...]
    """Aggregate evidence across the full chain, for surface-level display.
    Janus §5: 'Supported by what?'"""

    assumptions: tuple[str, ...]
    """Every premise that was not a direct, qualified Atlas Relationship —
    stated explicitly rather than buried in the chain.
    Janus §2: No unsupported assumptions; Janus §5: 'What assumptions?'"""

    falsifiability_conditions: tuple[str, ...]
    """The specific evidence that would overturn this conclusion.
    Janus §2: Boundedness; Janus §5: 'What would change this?'
    A ReasoningArtifact with an empty tuple here has not satisfied
    Janus §2's Boundedness criterion and is not yet complete."""
