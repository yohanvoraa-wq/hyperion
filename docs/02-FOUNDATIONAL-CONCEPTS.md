# Hyperion Foundational Concepts

**Version:** 1.0
**Status:** Active
**Last Updated:** 28 June 2026
**Document Owner:** Hyperion Core

**Depends On:**
- `00-CONSTITUTION.md`
- `01-VISION.md`

**Used By:**
- All future modules

---

## What This Document Is Not

This is **not** a glossary.

A glossary explains words that already have meaning elsewhere. This document does something different: it defines Hyperion's interpretation of these terms. If another company, paper, or platform defines "Portfolio" or "Diversification" differently, that's irrelevant here. This is Hyperion's definition, and it is the only one that governs how Hyperion's code, models, and UI behave.

Google has PageRank. Palantir has Ontology. Apple has the Human Interface Guidelines. Hyperion has Foundational Concepts.

---

## How These Concepts Are Organized

There are three levels, plus one concept that sits above all of them.

**Level 0 — The Container**
Before objects, before relationships, before reasoning, there is the system they all exist inside of. Markets are not a collection of independent prices — they are a system of interdependent parts, where a change in one component propagates, with varying intensity, through the rest. This is why **Financial System** is concept #1, not an afterthought.

**Level I — Fundamental Objects**
Things that exist. They don't depend on anything else to be defined.

**Level II — Relationships**
Objects don't matter unless they're connected. This is also where we draw a deliberate line between two ideas that are usually treated as interchangeable: **Correlation** and **Causality**. Markets correlate. Hyperion reasons about causes. Every Blind Spot Hyperion surfaces downstream depends on this distinction holding.

**Level III — Reasoning**
This is where Hyperion actually begins to think. Once the AI has vocabulary for objects and relationships, it has what it needs to reason — and to show its reasoning.

A note on scope: the original list of 20 included three terms — *Financial Knowledge Graph*, *Structural Risk*, and *Temporal State* — that aren't part of the reordered hierarchy below. I've followed the reordered list as the authoritative one, since it was the more deliberate pass. Those three terms aren't lost — they're strong candidates for an addendum once the Knowledge Graph and risk-modeling layers are further along, since they'll likely need definitions that reference concepts (like Reasoning Chain and Market State) that didn't exist yet when the original 20 were drafted.

---

## The Concept Template

Every concept in this document follows the same five-part structure:

- **Definition** — what it is, in one or two sentences.
- **Purpose** — why Hyperion needs this concept to exist.
- **Examples** — what it looks like in practice.
- **Relationships** — which already-defined concepts it depends on. No repetition of prior definitions — only references.
- **Future Implications** — where this concept is headed as Hyperion matures.

---

## 1. Financial System

**Definition**
A Financial System is a network of interacting assets, institutions, market participants, and macroeconomic forces whose relationships collectively determine market behavior.

**Purpose**
Every other concept in this document exists inside a Financial System. Without it, "Asset" and "Portfolio" would be isolated objects instead of participants in something larger. The Financial System is what makes a shock in one market a Blind Spot in a portfolio that looks, on the surface, completely unrelated.

**Examples**
The global equity markets, a national bond market, a sector, a currency regime — each is a Financial System, or a sub-system nested inside a larger one.

**Relationships**
This is the root concept. Nothing precedes it.

**Future Implications**
As Hyperion's Financial Knowledge Graph matures, the Financial System becomes the graph's outer boundary — the full space the graph is mapping, even if Hyperion only ever surfaces the relevant subset to a given user.

---

## 2. Asset

**Definition**
A single financial instrument capable of representing economic value while carrying both potential return and risk — including stocks, bonds, commodities, currencies, and derivatives.

**Purpose**
The smallest unit Hyperion reasons about. Every higher-level concept — Portfolio, Finance DNA, Exposure — is ultimately built from Assets.

**Examples**
A share of a company, a 10-year government bond, an ounce of gold, a currency pair.

**Relationships**
Exists within a Financial System.

**Future Implications**
As Hyperion expands beyond public markets, "Asset" will need to comfortably include private equity positions, real estate, and other less liquid instruments without changing its core definition.

---

## 3. Portfolio

**Definition**
An ordered collection of Assets held by an investor at a point in time.

**Purpose**
Hyperion doesn't reason about Assets in isolation — it reasons about how they combine. The Portfolio is the unit a real investor actually holds and worries about.

**Examples**
A retirement account holding ten stocks and two bonds. A single position is the simplest possible Portfolio.

**Relationships**
A Portfolio is composed of Assets, and exists within a Financial System.

**Future Implications**
Future versions of Hyperion may treat a Portfolio not as a static snapshot but as a trajectory — a sequence of Portfolios over time, which ties directly into how Market State is eventually modeled.

---

## 4. Financial Dimension

**Definition**
A single axis along which an Asset or Portfolio can be measured or described — for example, volatility, sector, liquidity, geography, or duration.

**Purpose**
Financial Dimensions are the building blocks of Finance DNA. Without them, "describing" an Asset would mean listing arbitrary, inconsistent facts rather than measuring it along a shared, comparable scale.

**Examples**
Volatility, sector classification, geographic exposure, credit quality, liquidity, duration.

**Relationships**
Measures an Asset or a Portfolio.

**Future Implications**
The list of Financial Dimensions Hyperion tracks is expected to grow significantly as the platform matures — this is one of the most extensible parts of the system.

---

## 5. Finance DNA

**Definition**
A multidimensional representation of an Asset, built from its Financial Dimensions.

**Purpose**
A single number — price, P/E ratio, beta — can't capture what an Asset really is. Finance DNA is Hyperion's attempt to represent an Asset as a profile rather than a number.

**Examples**
A vector capturing a stock's volatility, sector, liquidity, and macro sensitivity simultaneously, rather than any one of those in isolation.

**Relationships**
Built from the Financial Dimensions of an Asset.

**Future Implications**
Finance DNA is the natural candidate for embedding-based similarity search — finding Assets that "behave like" a given one, even across different sectors or geographies.

---

## 6. Portfolio DNA

**Definition**
The aggregation of the Finance DNA vectors belonging to every Asset in a Portfolio, weighted by position size.

**Purpose**
This is what lets Hyperion describe the "personality" of an entire Portfolio in the same multidimensional language it uses for a single Asset — which is what makes comparison, Blind Spot detection, and Exposure analysis possible at the Portfolio level.

**Examples**
A Portfolio's overall sensitivity to interest rates, its effective sector concentration, its aggregate liquidity profile.

**Relationships**
Aggregates the Finance DNA of every Asset in a Portfolio.

**Future Implications**
Portfolio DNA only becomes meaningful when compared against something — which is exactly the role Market State plays next.

---

## 7. Market State

**Definition**
The condition of the Financial System at a specific moment in time — for example, bull, bear, high-volatility, or risk-on/risk-off.

**Purpose**
A Portfolio DNA in isolation tells you what a Portfolio looks like. A Portfolio DNA evaluated against a Market State tells you what it's likely to *do*.

**Examples**
A "risk-off, high-rate" Market State; a "low-volatility bull" Market State.

**Relationships**
Describes the condition of a Financial System; gives context to Portfolio DNA.

**Future Implications**
Market State is the natural anchor for Historical Similarities and Scenario Analysis — both depend on comparing the current Market State to prior ones.

---

## 8. Macro Factor

**Definition**
An external force, originating outside any single Asset or Portfolio, that influences many Assets simultaneously.

**Purpose**
Many Blind Spots don't come from a single bad holding — they come from an unrecognized shared sensitivity to the same Macro Factor across many holdings that look unrelated.

**Examples**
Interest rates, inflation, currency moves, geopolitical events, commodity price shocks.

**Relationships**
Influences Assets and Portfolios; helps define Market State.

**Future Implications**
Macro Factors are likely to become one of the primary node types in the Financial Knowledge Graph, since they're what connects otherwise-unrelated Assets.

---

## 9. Financial Relationship

**Definition**
Any link between two or more Assets, Portfolios, or Macro Factors.

**Purpose**
This is the general category Hyperion's more specific relationship types — Exposure, Dependency, Correlation, Causality — are drawn from. Without naming the category, those four would look like an arbitrary list rather than a coherent family.

**Examples**
Any connection between two Assets, or between an Asset and a Macro Factor.

**Relationships**
Connects Assets, Portfolios, and Macro Factors.

**Future Implications**
Financial Relationships are the edges of the Financial Knowledge Graph; everything that follows in Level II is a specific type of edge.

---

## 10. Exposure

**Definition**
The degree to which a Portfolio's value is affected by a change in a given Asset, Macro Factor, or Market State.

**Purpose**
Exposure quantifies sensitivity — it answers "how much" a Portfolio is affected, which is the first step toward identifying Blind Spots.

**Examples**
A Portfolio's exposure to rising interest rates; a single stock's outsized exposure to one sector.

**Relationships**
A type of Financial Relationship.

**Future Implications**
Exposure is the metric most likely to feed directly into the Confidence Layer of a Blind Spot conclusion.

---

## 11. Dependency

**Definition**
A relationship where the state of one Asset, Factor, or Portfolio component relies on another.

**Purpose**
Exposure measures sensitivity; Dependency measures structural reliance. A Portfolio can have low Exposure to something it is nonetheless deeply Dependent on — and that gap is often exactly where a Blind Spot hides.

**Examples**
A company's revenue Dependency on a single supplier; a bond fund's Dependency on a specific rate-setting policy.

**Relationships**
A type of Financial Relationship, distinct from Exposure.

**Future Implications**
Dependencies are likely to be the hardest Financial Relationship type to detect automatically, since they're often structural rather than statistical.

---

## 12. Diversification

**Definition**
The degree to which the Exposures within a Portfolio are spread across independent, rather than redundant, Financial Relationships.

**Purpose**
Real Diversification isn't counting how many Assets a Portfolio holds — it's counting how many genuinely independent relationships exist among them. Ten stocks with the same underlying Exposure is not Diversification.

**Examples**
A Portfolio of ten companies across different sectors, geographies, and Macro Factor sensitivities is genuinely diversified; ten companies all exposed to the same Macro Factor are not, regardless of how different their names look.

**Relationships**
Depends on Exposure and Financial Relationship.

**Future Implications**
Diversification will likely be one of the first Blind Spot categories Hyperion can detect automatically and explain through an Evidence Graph.

---

## 13. Correlation

**Definition**
A statistical relationship describing how two Assets or Factors move together over time.

**Purpose**
Correlation is observable and computable, but it says nothing about *why* two things move together — which is precisely why Hyperion treats it as a starting point, not a conclusion.

**Examples**
Two stocks in the same sector that historically rise and fall together.

**Relationships**
A type of Financial Relationship; precedes and is distinct from Causality.

**Future Implications**
Mistaking Correlation for Causality is one of the most common sources of Blind Spots Hyperion is designed to catch.

---

## 14. Causality

**Definition**
A relationship where a change in one Asset or Factor produces a change in another.

**Purpose**
This is the distinction that separates Hyperion from every tool that stops at Correlation. Markets correlate. Hyperion reasons about causes.

**Examples**
A central bank rate hike causing a measurable shift in bond yields, as opposed to two unrelated stocks that simply happen to move together.

**Relationships**
A type of Financial Relationship, deliberately separated from Correlation.

**Future Implications**
Causality is the relationship type that will demand the most rigor from Hyperion's Reasoning Chain — claiming Causality without sufficient Evidence is the single easiest way for Hyperion to lose credibility.

---

## 15. Blind Spot

**Definition**
A hidden Exposure or unexamined assumption within a Portfolio that the investor did not knowingly take on.

**Purpose**
This is the core deliverable of Hyperion's reasoning layer. Everything in Level I and Level II exists, ultimately, to make Blind Spots detectable and explainable.

**Examples**
Discovering that five "unrelated" holdings actually share the same underlying Macro Factor Exposure; mistaking a Correlation for a Causal relationship and building a Portfolio around that mistake.

**Relationships**
Emerges from undetected Dependencies, Exposures, or Correlations mistaken for Causality.

**Future Implications**
Every Blind Spot Hyperion surfaces must be backed by a Reasoning Chain — an assertion without one is not a Blind Spot, it's a guess.

---

## 16. Reasoning Chain

**Definition**
An ordered sequence of logical steps, grounded in Evidence, that leads from raw data to a conclusion.

**Purpose**
A Reasoning Chain is what separates a Hyperion conclusion from a black-box AI output. It's the difference between "trust me" and "here's exactly how I got here."

**Examples**
The step-by-step path from raw price data to the conclusion "this Portfolio has a hidden Blind Spot in rate-sensitive assets."

**Relationships**
Used to support a Blind Spot or any other conclusion; built from Evidence.

**Future Implications**
Reasoning Chains are what get rendered visually as an Evidence Graph — the chain is the logic, the graph is its presentation.

---

## 17. Evidence

**Definition**
A discrete, verifiable fact or data point used to support a step within a Reasoning Chain.

**Purpose**
Without Evidence, a Reasoning Chain is just a sequence of assertions. Evidence is what makes each step checkable.

**Examples**
A specific historical price move, a disclosed Macro Factor sensitivity, a verified Dependency between two companies.

**Relationships**
Supports a step in a Reasoning Chain.

**Future Implications**
Every piece of Evidence will eventually need a traceable source, since Explainability depends on Evidence being inspectable, not just present.

---

## 18. Evidence Graph

**Definition**
The visual structure connecting multiple pieces of Evidence into the Reasoning Chain supporting a conclusion.

**Purpose**
A Reasoning Chain is logic; an Evidence Graph is how that logic becomes something a user can actually see, follow, and question.

**Examples**
A node-and-edge diagram showing how five pieces of Evidence connect to produce a single Blind Spot conclusion.

**Relationships**
Visualizes a Reasoning Chain built from Evidence.

**Future Implications**
The Evidence Graph is likely to become one of Hyperion's most recognizable UI surfaces — it's where "explainable" stops being a claim and becomes something visible.

---

## 19. Confidence Layer

**Definition**
The certainty assigned to a conclusion, reflecting the strength and completeness of the Evidence behind its Reasoning Chain.

**Purpose**
Not every conclusion deserves equal trust. The Confidence Layer keeps Hyperion honest about how strong its own reasoning actually is.

**Examples**
A Blind Spot supported by five independent pieces of Evidence carries a higher Confidence Layer than one supported by a single weak Correlation.

**Relationships**
Assigned to a conclusion based on its Reasoning Chain and Evidence.

**Future Implications**
The Confidence Layer is a strong candidate for becoming a first-class, user-facing number — not just an internal scoring mechanism.

---

## 20. Explainability

**Definition**
Hyperion's capacity to expose its full Reasoning Chain, Evidence, and Confidence Layer for any conclusion it reaches, rather than presenting a conclusion as a black-box output.

**Purpose**
This is the concept every other concept in this document ultimately serves. It is also Hyperion's primary KPI, as defined in the Vision.

**Examples**
A user clicking on any Hyperion conclusion and being shown the exact Evidence Graph and Confidence Layer behind it — never just a bare assertion.

**Relationships**
Depends on Reasoning Chain, Evidence, Evidence Graph, and Confidence Layer all being present and inspectable.

**Future Implications**
Explainability is the standard every future module must be held to. A feature that cannot expose its reasoning does not belong in Hyperion, regardless of how accurate it is.

---

## Concept Hierarchy

```
Financial System
│
├── Assets
│
├── Portfolios
│     │
│     ├── Financial Dimension
│     ├── Finance DNA
│     ├── Portfolio DNA
│     │
│     ├── Market State
│     ├── Macro Factor
│     │
│     └── Financial Relationship
│           ├── Exposure
│           ├── Dependency
│           ├── Diversification
│           ├── Correlation
│           └── Causality
│                 │
│                 └── Blind Spot
│
└── Reasoning
      │
      ├── Reasoning Chain
      ├── Evidence
      ├── Evidence Graph
      ├── Confidence Layer
      └── Explainability
```

Every engineer should be able to understand Hyperion from this picture alone, then drill into any branch for the full definition.

---

## Revision History

| Version | Date | Summary |
|---|---|---|
| 1.0 | 28 June 2026 | Initial release. |
