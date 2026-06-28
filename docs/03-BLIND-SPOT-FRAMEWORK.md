# 03 — Blind Spot Framework

**Version:** 1.0
**Status:** Active
**Last Updated:** 28 June 2026
**Document Owner:** Hyperion Core

**Depends On:**
- `00-CONSTITUTION.md`
- `01-VISION.md`
- `02-FOUNDATIONAL-CONCEPTS.md`

**Used By:**
- `04-FINANCE-DNA.md`
- `05-ATLAS.md`
- `06-JANUS.md`

**Artifact:** Blind Spot Taxonomy

**Research Question:**
How can an investor possess meaningful portfolio risk or opportunity without realizing it?

---

## Why This Document Exists

Investors rarely make poor decisions because they lack information. Markets have never been more transparent — prices, statements, ratios, and commentary are available to anyone, instantly. And yet portfolios still fail in ways their owners never saw coming.

The reason isn't missing data. It's an incomplete mental model.

Every investor holds a working theory of their own portfolio — what it's exposed to, what it depends on, how its pieces relate. That theory is never complete. It can't be; no one holds the entire Financial System in their head at once. So every portfolio carries assumptions its owner has never explicitly stated, let alone tested.

A Blind Spot emerges when reality exposes an assumption the investor never realized they were making.

This document exists to answer, precisely and without reference to any particular technology, what that means.

---

## 1. What Is a Portfolio Blind Spot?

A **Blind Spot** is a hidden Exposure or unexamined assumption within a Portfolio that the investor did not knowingly take on.

Three words in that definition carry the weight:

- **Hidden** — it is not absent from the data; it is absent from the investor's awareness of the data.
- **Unexamined** — the investor never evaluated it, not because it's untrue, but because it never surfaced as a question.
- **Unknowingly** — the investor did not choose this Exposure; it arrived as a side effect of other choices.

This distinguishes a Blind Spot from a known risk. A Blind Spot is therefore defined not by the existence of risk, but by the absence of awareness. An investor who deliberately holds a volatile Asset and accepts the volatility has not encountered a Blind Spot — they've made an informed decision. A Blind Spot only exists in the gap between what a Portfolio actually does and what its owner believes it does.

---

## 2. Why Do Blind Spots Exist?

Not as a technical failure. As a structural one.

> Portfolios are built incrementally.
>
> Markets behave as systems.
>
> Blind Spots emerge in the gap between the two.

**Aggregation outpaces systemic awareness.**
Most portfolios are assembled position by position, often across years, each addition justified on its own terms. The Financial System doesn't evaluate positions one at a time — it expresses Financial Relationships across all of them simultaneously. A portfolio built through a sequence of locally reasonable decisions can still produce a Portfolio DNA that no one designed.

**Correlation hides as Diversification.**
Holding many Assets feels like spreading risk. But Diversification depends on independent Financial Relationships, not on the count of holdings. Ten Assets that share a Dependency on the same Macro Factor offer the appearance of Diversification while providing almost none of its substance.

**Causality is harder to observe than Correlation.**
Investors can see that two things moved together. They can rarely see why. In the absence of a clear causal explanation, Correlation quietly stands in for understanding — and a Correlation mistaken for Causality is one of the most common origins of a Blind Spot.

**Assumptions don't expire when they stop being true.**
A Portfolio built under one Market State carries assumptions that may not survive a shift to another. Nothing forces an investor to revisit those assumptions when conditions change, so they persist, unexamined, long after the conditions that justified them are gone.

In short: Blind Spots exist because portfolios are constructed sequentially, evaluated locally, and rarely re-examined as a whole — while the Financial System they sit inside behaves the opposite way on all three counts.

---

## 3. What Kinds of Blind Spots Exist?

A working taxonomy — proposed here as a starting point, not a final answer:

- **Structural** — arises from how a Portfolio is built or organized, independent of market conditions. Example: a Portfolio is technically diversified by Asset count but structurally concentrated by ownership chain.
- **Concentration** — arises from an Exposure that is larger, in practice, than it appears on the surface, because multiple positions express the same underlying bet.
- **Dependency** — arises from a structural reliance between Assets or Factors that isn't visible in price behavior at all, and so won't show up as Correlation.
- **Macroeconomic** — arises from shared Dependency on the same Macro Factor across positions that otherwise look unrelated.
- **Temporal** — arises because an assumption that was once valid has not been re-evaluated since the Market State that justified it changed.
- **Behavioral** — arises from a decision pattern in how the Portfolio was assembled or maintained, rather than from any single position.

A Blind Spot may belong to multiple categories simultaneously. The taxonomy exists to improve explanation, not to force every Blind Spot into a single classification. A single Blind Spot, for instance, often has both a Structural origin and a Macroeconomic expression. This list should be treated as a draft until we've stress-tested it against real portfolios.

---

## 4. How Are Blind Spots Formed?

This is a question about origin, not detection — the difference between asking why a fire started and asking how it was discovered.

A Blind Spot tends to form through one of a small number of structural patterns:

- **Aggregation without re-evaluation.** Positions are added over time, each reasonable on its own, but the combination is never re-assessed as a whole.
- **Shared ancestry.** Several Assets appear unrelated but trace back to the same Macro Factor or the same underlying Dependency, so a single shock propagates through all of them at once.
- **Substitution of Correlation for Causality.** A relationship is assumed to be causal because it has reliably held in the past, without ever being tested for why it holds.
- **Stale assumptions under a changed Market State.** A belief about how a Portfolio would behave was accurate once, under a Market State that no longer applies.

None of these require a mistake at the moment a position was added. That's precisely what makes Blind Spots dangerous — they form through the accumulation of individually defensible decisions, not through any single error.

---

## 5. Conceptual Discovery Process

Conceptually — not algorithmically.

A Blind Spot is discovered by comparing what a Portfolio's Financial Relationships actually express against what its composition would suggest. This means:

- Evaluating Portfolio DNA against the full set of Financial Relationships among its Assets, not just the Assets in isolation.
- Treating apparent Diversification as a hypothesis to be tested, not a property to be assumed from Asset count.
- Distinguishing, wherever possible, Correlation from Causality before treating either as an explanation.
- Re-evaluating Portfolio DNA against the current Market State, rather than the Market State the Portfolio happened to be built under.

The output of this process is not certainty. It is a hypothesis supported by evidence — a candidate Blind Spot, a specific, falsifiable claim about a hidden Exposure or assumption, which only earns the name "Blind Spot" once it survives the criteria in Section 7.

---

## 6. How Should Hyperion Explain Them?

A Blind Spot that cannot be explained is indistinguishable from a guess. Explanation is not a feature added after detection — it's the condition that makes a candidate worth surfacing at all.

This connects directly to the reasoning vocabulary already established in `02-FOUNDATIONAL-CONCEPTS.md`:

- The **Reasoning Chain** is the ordered argument connecting raw observations to the Blind Spot conclusion.
- **Evidence** is each individual fact the Reasoning Chain depends on — a specific Dependency, a specific shared Macro Factor, a specific historical Market State.
- The **Evidence Graph** is how that Reasoning Chain becomes visible and inspectable to a user, rather than asserted.
- The **Confidence Layer** reflects how strong and complete the underlying Evidence actually is — a Blind Spot built on five independent pieces of Evidence is not the same claim as one built on a single weak Correlation, and Hyperion should never present them as equivalent.

A Blind Spot is complete only when its reasoning can be inspected, challenged, and defended. Anything less is not yet a Blind Spot by Hyperion's definition.

---

## 7. Qualification Criteria

Not every observation deserves to become a Blind Spot. Without a filter, Hyperion would eventually surface trivial, obvious, or weakly supported claims under the same label as genuinely important ones — and the label would stop meaning anything.

A candidate Blind Spot qualifies only if it satisfies all four criteria:

- **It's meaningful.** It would change how the investor thinks about risk or opportunity in their Portfolio, not just add a minor data point.
- **It's not immediately obvious.** An investor who already knew about it wouldn't be surprised — but most investors, before seeing it, would be.
- **It's supported by Evidence.** It traces back to a Reasoning Chain that can be inspected, not an unexplained pattern-match.
- **It changes the user's understanding.** After encountering it, the investor's mental model of their own Portfolio is measurably more accurate than before.

These four criteria are a deliberate filter against noise. A true but trivial observation fails the first criterion. A real risk the investor already knows about fails the second. A plausible-sounding but unsupported claim fails the third. An accurate but inconsequential fact fails the fourth. All four must hold.

---

## Design Implications

- Hyperion's reasoning layer should be built around producing *candidates* first and filtering them against Section 7's criteria second — detection and qualification are separate stages, not one step.
- The Blind Spot taxonomy in Section 3 should be treated as a living draft, refined against real portfolios rather than finalized in the abstract.
- No Blind Spot should ever be presented to a user without an attached Reasoning Chain, Evidence, and Confidence Layer — this is non-negotiable per the Constitution's commitment to Explainability.
- Blind Spot detection and Blind Spot explanation should remain separate responsibilities throughout the system.

## Open Questions

- How many independent pieces of Evidence should be required before a candidate is allowed to cross from "interesting pattern" to "Blind Spot"?
- Can a single Blind Spot belong to more than one taxonomy category simultaneously, and if so, how should Hyperion communicate that without confusing the user?
- How should Hyperion handle a Blind Spot that was real under a past Market State but is no longer active under the current one — surface it as history, or suppress it entirely?
- Should the criteria in Section 7 be weighted, or are they strictly binary — all four required, none more important than another?

## Future Extensions

- A formal scoring relationship between the Confidence Layer and the four qualification criteria in Section 7.
- A method for tracking how a given Blind Spot evolves as a Portfolio or Market State changes over time, rather than treating each detection as a one-time event.
- A cross-reference layer connecting Blind Spot categories in this taxonomy to the relationship types defined in `05-ATLAS.md`, once that document exists.
- A mechanism for discovering relationships between Blind Spots themselves, allowing multiple findings to be grouped into a higher-level portfolio narrative.
