# 04 — Finance DNA

**Version:** 0.6 (Draft)
**Status:** In Progress — Sections 1–6 complete · Section 7 deliberately paused pending `05-ATLAS.md` · Section 8 pending
**Last Updated:** 28 June 2026
**Document Owner:** Hyperion Core

**Depends On:**
- `00-CONSTITUTION.md`
- `01-VISION.md`
- `02-FOUNDATIONAL-CONCEPTS.md`
- `03-BLIND-SPOT-FRAMEWORK.md`

**Used By:**
- `05-ATLAS.md`
- `06-JANUS.md`

**Artifact:** Finance DNA Representation Model

**Research Question:**
How can publicly traded companies be represented in a way that preserves the characteristics necessary for financial reasoning?

---

## 1. Why Finance DNA Exists

Financial statements describe performance.

Financial ratios describe valuation.

Finance DNA describes behavior.

Those are three different questions, and most financial tooling only ever answers the first two. A statement tells you what happened last quarter. A ratio tells you what the market is currently willing to pay for that. Neither tells you what the company actually *is* — and that gap is precisely where this document begins.

### The questions ratios can't answer

Ask an investor to compare Apple and Microsoft, and the instinct is to reach for P/E, margins, growth rate. Ask them to compare Nestlé and Reliance, and the same instinct produces numbers that don't mean the same thing in each context — a P/E of 25 says something different for a consumer staples company than it does for a conglomerate with an energy arm. The numbers are real. They're just not answering the question that was actually asked, which was never "what does the market currently pay for this" — it was "what kind of business is this."

This isn't a flaw in any individual ratio. It's a structural limitation of the category. Ratios are built to answer *how is this priced* or *how is this performing*, and they do that well. They were never built to answer *what is this*. Finance DNA exists to answer the question ratios were never designed to ask.

### Why Existing Representations Are Insufficient

**They conflate economic identity with valuation.**
A company's P/E can move sharply without anything about the company changing — sentiment shifts, a sector re-rates, a macro narrative takes hold. When the same number is used to describe both "what this company is" and "what the market currently thinks it's worth," those two ideas get tangled together, and there is no way to separate them after the fact. Finance DNA is only useful if it captures the part that *doesn't* move every time sentiment does — economic identity has to be allowed to be stable while valuation is volatile.

**They don't compare across categories.**
A bank's margin and a software company's margin are computed the same way and mean almost nothing in common. Ratios are calibrated to a sector, a business model, sometimes a single company's own history — which means they're excellent for tracking one Asset over time and poor for the thing Hyperion actually needs, which is comparing *unlike* Assets against each other on the same terms.

**They don't compose.**
You cannot average ten companies' P/E ratios and learn something true about the portfolio those ten companies form. Ratios are built to describe a single Asset in isolation; they were never designed to aggregate into something like a Portfolio DNA. Any representation Hyperion relies on has to survive being combined, not just observed one Asset at a time.

### Why this matters specifically for Blind Spots

This connects directly back to `03-BLIND-SPOT-FRAMEWORK.md`. A Blind Spot is a hidden Exposure or unexamined assumption — and finding one requires noticing that several Assets, which look unrelated on the surface, actually share an underlying characteristic. Two companies with wildly different P/E ratios can carry the exact same Macro Factor Dependency. Two companies with nearly identical ratios can be structurally nothing alike. If the only representation available is the one built for pricing and performance, that shared characteristic stays invisible — not because the data doesn't exist, but because the representation was never built to surface it.

Finance DNA exists to give Hyperion a representation where economic identity, rather than valuation, is the thing being compared — because economic identity is what Financial Relationships and Exposures are actually built on, and Blind Spot detection cannot proceed without it.

Finance DNA is not intended to replace existing financial representations. Instead, it introduces a complementary representation optimized for reasoning rather than valuation. Traditional financial metrics remain essential for understanding performance and pricing. Finance DNA provides the missing layer required to understand behavior, relationships, and systemic interactions.

---

## 2. What Makes a Valid Financial Dimension?

Before naming a single dimension, Finance DNA needs a test that any candidate dimension has to pass. Without one, the dimension list becomes a matter of taste — and a representation built on taste cannot be trusted to support reasoning. This section defines that test. Section 6 will not introduce a single dimension that hasn't been checked against it.

A Financial Dimension qualifies only if it satisfies all five criteria below.

**It reflects economic identity, not valuation.**
A dimension must be stable under sentiment and move only when the underlying business actually changes. This is the criterion Section 1 already argued for directly — it's restated here as a hard test rather than an observation. A measure that rises and falls with market mood, independent of any change in the business itself, is a valuation signal wearing a dimension's clothing. *Fails this test:* "P/E relative to historical average." Nothing about the company changed; the market's opinion did.

**It is comparable across dissimilar Assets.**
A dimension has to mean the same thing whether it's applied to a bank, a miner, or a software company. If a measure only makes sense relative to sector peers — calibrated to a sector average, a sector-specific accounting convention, or a sector's typical scale — it cannot do the one thing Finance DNA exists to do: let Hyperion compare Apple to Nestlé on common terms. *Fails this test:* "Margin percentile within sector." It's a useful number, but only inside the sector that produced it — it goes silent the moment you ask how that company compares to one outside it.

**It is composable.**
A dimension must survive being aggregated across many Assets into a Portfolio DNA without losing meaning. This is the direct counter to the third failure mode from Section 1 — a representation that can only describe one Asset in isolation is not a representation Hyperion can build a portfolio-level view from. *Fails this test:* a dimension expressed only as a rank or percentile, since ranks don't aggregate — the average of several percentiles is not itself a meaningful percentile of anything.

The first three criteria establish whether a characteristic can serve as a stable representation. The remaining two determine whether that representation is suitable for financial reasoning.

**It influences a Financial Relationship, Exposure, or Dependency.**
A dimension has to matter, not merely be true. Plenty of facts about a company are accurate and economically inert — they describe the company without connecting to how risk, opportunity, or sensitivity actually propagates through it or beyond it. A dimension only belongs in Finance DNA if it changes how the company relates to something else: another Asset, a Macro Factor, or the broader Financial System. *Fails this test:* "number of patents filed in a given year" as a standalone figure — interesting, but inert unless it's shown to connect to something like pricing power or competitive Exposure.

**It is evidence-traceable.**
Every value assigned along a dimension must be groundable in a verifiable fact — a disclosed financial statement, a reported contract, an observable operational figure — not an unexplained judgment call. This is the same standard the Blind Spot Framework holds Evidence to, and Finance DNA cannot relax it just because it sits a layer below Blind Spot detection. A dimension that can't show its Evidence can't support a Reasoning Chain that depends on it. *Fails this test:* a dimension defined as "perceived brand strength," with no disclosed methodology behind the number — the claim might be true, but it isn't yet inspectable.

### Why all five must hold

Each criterion guards against a different way a dimension can quietly fail. A dimension can be true and still be valuation in disguise — the first criterion catches that. It can be stable and still be too sector-bound to compare — the second catches that. It can compare well one Asset at a time and still collapse when combined into a portfolio — the third catches that. It can survive all of that and still be economically irrelevant — the fourth catches that. And it can matter enormously and still rest on nothing inspectable — the fifth catches that.

None of the five is sufficient on its own, and skipping any one of them reopens exactly the gap Section 1 spent its argument closing. A dimension that passes all five has earned a place in Finance DNA. A dimension that passes four is not a weaker dimension — it has failed.

These criteria define the representation itself, independent of how Finance DNA is stored, calculated, or implemented.

---

## 3. Types of Financial Dimensions

This section does not name a single dimension. That's deliberate, and worth restating before going further: Section 6 names dimensions; this section defines the kinds of values a dimension is allowed to hold. Skipping this step and going straight to a dimension list would mean inventing the type system implicitly, one dimension at a time, which is exactly how inconsistency creeps into a representation — two dimensions that should behave the same way end up encoded differently simply because no one had decided the rules yet.

A Financial Dimension's type is not one property. It's two, and they're independent of each other: the form of the value it holds, and the way that value behaves over time. Neither property is sufficient on its own — together, they define the dimension's type.

### Axis 1 — Value Structure

This axis describes the shape of the value a dimension holds at any given moment.

**Continuous.** A bounded scalar representing degree or intensity — not a price, but a position along a low-to-high scale. Commodity Exposure is continuous: a company can have more or less of it, and the difference between two companies is a matter of degree, not kind. Continuous dimensions compose naturally — a weighted average across a Portfolio's holdings still means something.

**Categorical.** One of a fixed, mutually exclusive, unordered set of labels. Primary Business Model is categorical: a company is a manufacturer, a service provider, or a platform business, and "more manufacturer" is not a meaningful idea the way "more commodity exposure" is. Categorical dimensions don't average — they aggregate into a distribution. A Portfolio's Business Model dimension isn't a single category; it's the share of the Portfolio falling into each one.

**Binary.** A dimension with exactly two states — present or absent. Binary is technically a special case of Categorical, but it earns its own type because it's common enough, and structurally important enough, to deserve explicit handling rather than being treated as an incidental two-label category. Whether a company is a Regulated Utility is binary, and that single fact often gates whether other dimensions even apply — a company's Regulatory Exposure profile looks completely different depending on which side of that binary it falls on. Binary dimensions aggregate as a proportion: the share of a Portfolio, by weight, on the "present" side.

### Axis 2 — Temporal Behavior

This axis is independent of value structure, and it's easy to conflate the two if it isn't named explicitly. A dimension's type tells you what kind of value it holds; this axis tells you how that value behaves as time passes.

**Static.** The value is not expected to change except through a structural event — something that, if it happened, would itself be worth noticing. Primary Business Model is static in this sense: it doesn't drift gradually, it changes (rarely) when a company materially restructures what it does.

**Time-varying.** The value is expected to drift gradually as the business evolves, and a single snapshot is not sufficient to represent it honestly. Commodity Exposure is time-varying — a company's revenue mix shifts year over year, and its exposure shifts with it, without any single dramatic event marking the change. A time-varying dimension has to be tracked as a value paired with the Market State or period it was observed in, not stored as one permanent number.

Crossing these two axes matters in practice: Commodity Exposure is Continuous and Time-varying. Regulated Utility status is Binary and mostly Static. Primary Business Model is Categorical and mostly Static. A dimension's full type is the pair — value structure and temporal behavior together — not either one alone.

### Why the type has to be explicit

This isn't a classification exercise for its own sake. Both halves of this type system trace directly back to the criteria in Section 2.

**Comparability depends on type consistency.** If one Asset's Commodity Exposure were encoded as a continuous score and another Asset's were encoded as a binary "exposed or not," the two would no longer be comparable, even though they share a name. The type has to be fixed once, for the dimension itself, and applied identically to every Asset it's measured against.

**Composability depends on knowing which aggregation rule applies.** A Portfolio DNA is built by aggregating Finance DNA across holdings, and the correct way to aggregate a dimension depends entirely on its value structure — averaging works for Continuous, a distribution works for Categorical, a weighted proportion works for Binary. Treating all dimensions as if they aggregate the same way would silently produce a Portfolio DNA that means nothing.

**Representing economic identity accurately depends on temporal behavior.** A Static dimension can be trusted to represent a company accurately for a long stretch of time. A Time-varying dimension cannot — using last year's value as if it still holds today would quietly violate the very standard Section 1 set: that Finance DNA must track what a company actually is, not what it used to be.

Every dimension introduced in Section 6 will be assigned a type from each axis before anything else is said about it. The type isn't a footnote to the definition — it's part of the definition.

---

## 4. Scope

**Version 1 of Finance DNA applies to publicly traded companies.**

That's the entire boundary. Everything in Sections 5–7 is built against that scope, and nothing past this section should be read as a general-purpose model for every kind of Asset.

### What Version 1 deliberately excludes

- **Bonds.** A bond's economic identity is built around credit quality, duration, and issuer structure — concepts that don't map onto the dimension categories this document is about to define for an operating business.
- **Commodities.** A commodity has no business model, no revenue structure, no operational footprint. Most of Finance DNA's dimension categories wouldn't apply to it at all.
- **Currencies and derivatives.** Both derive their economic identity from something else entirely — a currency from a macroeconomic regime, a derivative from an underlying Asset. Representing them well would mean designing a different model, not stretching this one.

### Why these exclusions exist

Trying to generalize Finance DNA across every Asset class in Version 1 would force every dimension in Section 6 to be vague enough to apply to all of them — which is precisely the failure mode Section 2 already rules out. A dimension built to half-apply to five Asset classes satisfies none of the qualification criteria as well as a dimension built to fully apply to one. Scoping to public companies first lets every dimension be defined with full rigor, against a single, well-understood Asset class.

### What belongs in Future Extensions

Each excluded Asset class is a candidate for its own Finance DNA extension once this model has been tested against real public companies. Those extensions should inherit the qualification criteria and the type system from Sections 2 and 3 unchanged — only the dimension categories and individual dimensions in Sections 5 and 6 are expected to differ by Asset class.

---

## 5. Dimension Categories

Sections 1–4 answered a representation question: how should a single Financial Dimension be defined so that it's valid? Section 5 answers a different kind of question, at a different level of abstraction: how should many dimensions be organized so that the representation as a whole stays coherent as it grows?

That difference matters enough to state plainly:

```
Company
  ↓
Financial Dimensions
  ↓
Dimension Categories
  ↓
Finance DNA
```

A Financial Dimension is a property of a company — Commodity Exposure is true or false of Nestlé independent of anything Hyperion decides. A Dimension Category is not a property of any company at all. It's a property of the representation — a structural choice about how Finance DNA organizes the dimensions it contains. Dimension Categories aren't economic facts waiting to be discovered in the world. They're design decisions, and design decisions need design principles before they need names. "Business Characteristics," "Revenue Characteristics," and similar labels that surface as a first instinct aren't categories yet — they're hypotheses, and they stay hypotheses until they survive the criteria this section defines.

### A. Why Dimension Categories Exist

They don't exist for the math. A weighted average doesn't care whether the dimension it's averaging belongs to any category — aggregation happens at the dimension level, exactly as Section 3 defined it, with or without categories sitting above it. So if categories aren't load-bearing for the calculation, what are they for?

**They prevent the flat-list problem.** Finance DNA is not going to stop at four or five dimensions — Section 1's argument only holds if the representation is rich enough to capture real economic identity, which means dozens of dimensions over time. A flat, unordered list of forty dimensions has no structure to reason about — no way to ask "what kind of thing is this dimension" without re-deriving the answer from scratch each time. Categories give every dimension an address, not just a name.

**They make growth tractable instead of combinatorial.** Imagine Hyperion needs to add a new dimension a year from now — something like sensitivity to AI infrastructure costs. Without categories, the question "where does this belong, and does something like it already exist" requires comparing the new dimension against every existing dimension individually. With principled categories, the question becomes "which existing category does this belong to, if any" — a much smaller, much more tractable comparison, and one that scales as Finance DNA grows rather than degrading.

**They give Explainability a coarser vocabulary.** A Reasoning Chain that cites five individual dimensions is precise but can be hard to summarize. A Reasoning Chain that can also say "this Blind Spot draws primarily from the Macroeconomic category" gives Hyperion a second, higher-level layer of explanation — useful precisely because it sits above the dimension level rather than duplicating it.

None of these three justifications asks "what are the natural categories of a company." They ask "what structural problem does categorization solve." That's the right question to be answering before any category gets a name.

### B. Qualification Criteria for Dimension Categories

A Dimension Category qualifies only if it satisfies all five criteria below.

**It groups dimensions that describe the same aspect of economic identity.** The dimensions inside a category should share something real about what they're measuring, not just a vague family resemblance. *Fails this test:* a category built around dimensions that happen to use similar data sources rather than similar economic meaning — that's an implementation grouping wearing a category's clothing, the same mistake Section 1 warned against at the dimension level.

**It has a clear conceptual boundary.** Given any dimension, it should be possible to say with confidence whether it belongs to this category, without the answer depending on who's asking. *Fails this test:* a category defined broadly enough that half of all future dimensions could plausibly fit inside it — a boundary that wide isn't a boundary.

**It is mutually distinguishable from other categories.** Two categories shouldn't compete for the same dimensions. If a reasonable case can be made for placing a given dimension in either of two categories with equal justification, the categories haven't been separated cleanly enough yet. *Fails this test:* "Revenue Characteristics" and "Business Characteristics" as separate categories, if a dimension like revenue concentration could land in either one without a principled reason to prefer one over the other.

**It remains useful as Finance DNA expands.** A category has to hold up under dimensions that don't exist yet, not just the ones already in hand. This is the direct test the AI Infrastructure Dependence example points at: a well-designed category should make the answer to "where does this go" close to obvious, even for a dimension invented after the category was. *Fails this test:* a category so narrowly scoped to today's dimension list that any genuinely new dimension forces the creation of an entirely new category just to hold it.

**It improves reasoning rather than merely organization.** A category earns its place only if it makes Hyperion's explanations clearer — not just its file structure. A category that's tidy but never appears in how a Blind Spot or Reasoning Chain gets explained is decoration, not architecture. *Fails this test:* a category that exists purely for documentation convenience and never surfaces anywhere in Hyperion's actual reasoning output.

### Why all five must hold

A category can group genuinely related dimensions and still have a fuzzy boundary — the first criterion doesn't catch that, the second does. It can have a crisp boundary and still overlap another category entirely — the third catches that. It can be clean and distinct today and still buckle the first time a genuinely new dimension arrives — the fourth catches that. And it can satisfy all of the above and still contribute nothing to how Hyperion actually explains itself — the fifth catches that.

A category that passes four out of five has not earned its place — exactly as Section 2 established for dimensions, the same standard applies one level up.

These criteria define how categories qualify, not which categories exist. Naming the actual categories — and testing candidates like "Business Characteristics" or "Operational Characteristics" against these five criteria — is the next piece of work, not this one.

### C. The Official Categories

Running the candidates that survived qualification against Part B's criteria — rather than guessing categories first and fitting dimensions into them — produces six categories. Notably, none of them are named "Business Characteristics" or "Revenue Characteristics": the original first-instinct names didn't survive contact with real dimensions, which is exactly what this section's discipline was supposed to test for.

**Business Structure** — what kind of operating entity this is, independent of how it makes or spends money. *Primary Business Model, Regulated Utility Status, Seasonality.*

**Revenue Structure** — where and how revenue is generated, and how concentrated or recurring it is. *Revenue Concentration (by customer), Geographic Revenue Concentration, Export Dependence, Recurring Revenue Share, Distribution Channel Dependence.*

**Cost & Capital Structure** — how the business is financed and how its cost base behaves. The natural counterpart to Revenue Structure — the other side of the ledger. *Capital Intensity, Labor Intensity, Working Capital Intensity, Operating Leverage / Scalability, Leverage / Debt Reliance, Liquidity Position, Margin Stability.*

**Macroeconomic & Regulatory Sensitivity** — exposure to forces external to the company's own choices: market-based macro forces and policy/regulatory forces alike. These were tested as two candidate categories and merged, since no dimension cleanly separated "economic cycle" sensitivity from "regulatory and policy" sensitivity without an arbitrary line being drawn. *Commodity Input Exposure, Energy Dependence, Currency Exposure, Interest Rate Sensitivity, Inflation Sensitivity, Cyclicality, Regulatory Exposure, Regulatory Transition Exposure, Government Contract Dependence.*

**Innovation & Technology** — forward-looking competitive and technological posture. *R&D Intensity (merging the duplicate "Innovation Intensity" entry — same disclosed metric, two names), Patent / IP Intensity, Technology Obsolescence Risk.*

**Governance & Capital Allocation** — ownership structure and how capital is directed. Currently the thinnest category, with one qualified member — but it passes Criterion 4 (remains useful as Finance DNA expands) on the strength of what's waiting in the Needs Refinement pile: Management Tenure Stability and the eventual split of Capital Allocation Style into Dividend Payout, Buyback Intensity, and Reinvestment Rate all belong here once refined. A thin category that's conceptually load-bearing is being kept; a thin category that was just decoration would not be. *Insider / Founder Ownership Concentration.*

Six categories, holding 28 unique dimensions. This is the structure Section 6 will be organized under.

---

## 6. Individual Dimensions

Every dimension below already survived Section 2's five criteria on the Dimension Candidate Board — this section documents that decision, it doesn't relitigate it. No new dimensions are introduced here, and none of the Needs Refinement or Rejected candidates appear. Each entry lists: Definition, Type (Value Structure / Temporal Behavior, per Section 3), Aggregation Rule (per the type), Evidence Source, and Relationships (a preview — the full relationship map is Section 7's job, not this one).

### Business Structure

**Primary Business Model**
*Definition:* The fundamental way the company creates and captures value — manufacturer, service provider, platform, etc.
*Type:* Categorical / Static. *Aggregation:* Distribution across categories.
*Evidence:* Disclosed business description and segment reporting (10-K, GICS classification).
*Relationships:* Often gates which other dimensions are even meaningful for a given company.

**Regulated Utility Status**
*Definition:* Whether the company operates under formal utility-style rate regulation.
*Type:* Binary / Static. *Aggregation:* Weighted proportion.
*Evidence:* Public regulatory record.
*Relationships:* Gates Regulatory Exposure and Pricing Power-adjacent behavior.

**Seasonality**
*Definition:* The degree to which revenue or earnings follow a predictable intra-year pattern, independent of the broader economic cycle.
*Type:* Continuous / Static-leaning. *Aggregation:* Weighted average.
*Evidence:* Derivable from disclosed historical quarterly revenue.
*Relationships:* Distinct from Cyclicality — Seasonality is calendar-driven, Cyclicality is macro-driven.

### Revenue Structure

**Revenue Concentration (by customer)**
*Definition:* The share of revenue attributable to a company's largest customer(s).
*Type:* Continuous / Time-varying. *Aggregation:* Weighted average.
*Evidence:* Disclosed major-customer concentration (required above the 10% threshold).
*Relationships:* Overlaps with Distribution Channel Dependence where the "customer" is a retail or platform channel.

**Geographic Revenue Concentration**
*Definition:* The share of revenue attributable to a single country or region.
*Type:* Continuous / Time-varying. *Aggregation:* Weighted average (or distribution, if tracked per-region).
*Evidence:* Disclosed segment reporting.
*Relationships:* A primary input to Currency Exposure.

**Export Dependence**
*Definition:* The share of revenue generated outside the company's home market.
*Type:* Continuous / Time-varying. *Aggregation:* Weighted average.
*Evidence:* Disclosed domestic/international revenue split.
*Relationships:* Closely related to Geographic Revenue Concentration; distinguished by framing trade exposure rather than regional concentration.

**Recurring Revenue Share**
*Definition:* The share of revenue derived from subscriptions or contracted, repeating sources rather than one-time sales.
*Type:* Continuous / Time-varying. *Aggregation:* Weighted average.
*Evidence:* Increasingly disclosed directly; otherwise inferable from contract structure disclosures.
*Relationships:* A stabilizing counterweight to Seasonality and Cyclicality.

**Distribution Channel Dependence**
*Definition:* The share of revenue passing through a single distribution channel or intermediary (a retailer, a platform).
*Type:* Continuous / Time-varying. *Aggregation:* Weighted average.
*Evidence:* Disclosed where material.
*Relationships:* Conceptual overlap with Revenue Concentration (by customer) — likely to be reviewed for consolidation once both are in active use.

### Cost & Capital Structure

**Capital Intensity**
*Definition:* The degree to which a company relies on fixed assets relative to its output. *(The Section 2 reference example — see Section 2 for its full criterion-by-criterion record.)*
*Type:* Continuous / Static-leaning. *Aggregation:* Weighted average.
*Evidence:* Disclosed PP&E, total assets, revenue.
*Relationships:* A primary input to Interest Rate Sensitivity and Operating Leverage.

**Labor Intensity**
*Definition:* The degree to which a company's cost structure relies on labor relative to capital.
*Type:* Continuous / Static-leaning. *Aggregation:* Weighted average.
*Evidence:* Disclosed employee count and labor costs.
*Relationships:* The natural counterpart to Capital Intensity along the same structural axis.

**Working Capital Intensity**
*Definition:* The amount of working capital a business requires relative to its revenue.
*Type:* Continuous / Time-varying. *Aggregation:* Weighted average.
*Evidence:* Disclosed balance sheet (working capital / revenue).
*Relationships:* Affects Liquidity Position under stress scenarios.

**Operating Leverage / Scalability**
*Definition:* How much operating income changes in response to a change in revenue, driven by the fixed/variable cost mix.
*Type:* Continuous / Static-leaning. *Aggregation:* Weighted average.
*Evidence:* Derived from disclosed fixed/variable cost structure.
*Relationships:* A downstream consequence of Capital Intensity and Labor Intensity.

**Leverage / Debt Reliance**
*Definition:* The degree to which a company finances itself with debt relative to equity or assets.
*Type:* Continuous / Time-varying. *Aggregation:* Weighted average.
*Evidence:* Disclosed balance sheet.
*Relationships:* A primary input to Interest Rate Sensitivity.

**Liquidity Position**
*Definition:* A company's capacity to meet short-term obligations from readily available assets.
*Type:* Continuous / Time-varying. *Aggregation:* Weighted average.
*Evidence:* Disclosed balance sheet (current ratio, quick ratio, cash reserves).
*Relationships:* The dimension most directly relevant to acute stress scenarios rather than steady-state behavior.

**Margin Stability**
*Definition:* The degree to which a company's margins remain consistent over time, regardless of their absolute level.
*Type:* Continuous / Time-varying. *Aggregation:* Weighted average.
*Evidence:* Computable directly from disclosed historical financials.
*Relationships:* A useful cross-check against Pricing Power once that dimension is refined.

### Macroeconomic & Regulatory Sensitivity

**Commodity Input Exposure**
*Definition:* The degree to which a company's costs are tied to commodity prices.
*Type:* Continuous / Time-varying. *Aggregation:* Weighted average.
*Evidence:* Disclosed in risk factors / hedging disclosures.
*Relationships:* A primary input to Inflation Sensitivity.

**Energy Dependence**
*Definition:* The degree to which a company's operations depend on energy as a cost input.
*Type:* Continuous / Time-varying. *Aggregation:* Weighted average.
*Evidence:* Inferable from disclosed energy costs or sector intensity benchmarks.
*Relationships:* A specific case of Commodity Input Exposure, kept separate due to its distinct macro driver (energy markets, not commodities broadly).

**Currency Exposure**
*Definition:* The degree to which a company's results are affected by exchange rate movements.
*Type:* Continuous / Time-varying. *Aggregation:* Weighted average.
*Evidence:* Disclosed FX risk notes; also derivable from Geographic Revenue Concentration against cost geography.
*Relationships:* Derived from Geographic Revenue Concentration plus cost-geography data.

**Interest Rate Sensitivity**
*Definition:* The degree to which a company's results are affected by changes in prevailing interest rates.
*Type:* Continuous / Time-varying. *Aggregation:* Weighted average.
*Evidence:* Derived from disclosed fixed/floating debt structure plus Capital Intensity.
*Relationships:* Derived from Leverage / Debt Reliance and Capital Intensity.

**Inflation Sensitivity**
*Definition:* The degree to which a company's margins are affected by general price-level increases.
*Type:* Continuous / Time-varying. *Aggregation:* Weighted average.
*Evidence:* Derived from historical margin behavior against input cost structure.
*Relationships:* Derived from Commodity Input Exposure and Labor Intensity.

**Cyclicality**
*Definition:* The degree to which a company's results move with the broader economic cycle.
*Type:* Continuous / Static-leaning. *Aggregation:* Weighted average.
*Evidence:* Derived from disclosed financial history against macro data.
*Relationships:* Distinct from Seasonality (calendar-driven, not cycle-driven); overlapping with Capital Expenditure Cyclicality, which remains in Needs Refinement pending a merge decision.

**Regulatory Exposure**
*Definition:* The degree to which a company's operations are subject to regulatory oversight.
*Type:* Continuous-to-Categorical / Static-leaning. *Aggregation:* Weighted average or distribution, depending on final encoding.
*Evidence:* Disclosed in risk factors; regulatory body oversight is public record.
*Relationships:* Gated in part by Regulated Utility Status.

**Regulatory Transition Exposure**
*Definition:* The degree to which a company is exposed to the financial consequences of regulatory change tied to a structural transition (e.g. carbon policy).
*Type:* Continuous / Time-varying. *Aggregation:* Weighted average.
*Evidence:* Disclosed via emissions / sustainability reporting; data maturity still developing across jurisdictions.
*Relationships:* A forward-looking, narrower case of Regulatory Exposure.

**Government Contract Dependence**
*Definition:* The share of revenue derived from government contracts.
*Type:* Continuous / Time-varying. *Aggregation:* Weighted average.
*Evidence:* Disclosed for materially affected sectors (e.g. defense); evidence strength varies by sector.
*Relationships:* Connects Revenue Structure to policy-cycle sensitivity.

### Innovation & Technology

**R&D Intensity**
*Definition:* Research and development spend relative to revenue. *(Merges the original "Innovation Intensity" entry — same disclosed metric, two names on the candidate board.)*
*Type:* Continuous / Time-varying. *Aggregation:* Weighted average.
*Evidence:* Directly disclosed R&D spend.
*Relationships:* A primary input to Technology Obsolescence Risk.

**Patent / IP Intensity**
*Definition:* The volume and trajectory of a company's intellectual property output relative to its size.
*Type:* Continuous / Time-varying. *Aggregation:* Weighted average.
*Evidence:* Public patent filings; disclosed R&D spend as a secondary signal.
*Relationships:* A primary input to Technology Obsolescence Risk, distinct from R&D Intensity (output vs. input).

**Technology Obsolescence Risk**
*Definition:* The degree to which a company's core products or competitive advantage are vulnerable to being displaced by technological change. *(See Section 2 for its full criterion-by-criterion record as the framework's Primitive-vs-Derived test case.)*
*Type:* Continuous / Time-varying. *Aggregation:* Weighted average.
*Evidence:* Composite of R&D Intensity and Patent / IP Intensity; Product / Technology Cycle Length remains in Needs Refinement as a third intended input.
*Relationships:* Qualifies as Derived — depends on the two dimensions above.

### Governance & Capital Allocation

**Insider / Founder Ownership Concentration**
*Definition:* The share of shares held by company insiders or founders.
*Type:* Continuous / Static-leaning. *Aggregation:* Weighted average.
*Evidence:* Disclosed in proxy and ownership filings.
*Relationships:* The sole qualified member of its category for now — see Section 5C for why the category is kept despite this.

---

## 7. Relationships Between Dimensions

*[Deliberately paused. This section overlaps heavily with `05-ATLAS.md` — relationships between dimensions are, in effect, a preview of Atlas's subject matter. Several relationships are already visible in Section 6's entries (e.g. Currency Exposure deriving from Geographic Revenue Concentration), but the systematic mapping is being held until Atlas exists, so this section isn't built twice.]*

---

## 8. Design Implications

*[Placeholder — Section 8. Plus Open Questions and Future Extensions, in keeping with the established document template.]*
