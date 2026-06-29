# 06 — Janus

**Version:** 1.0
**Status:** Active — Sections 1–6 complete
**Last Updated:** 28 June 2026
**Document Owner:** Hyperion Core

**Depends On:**
- `00-CONSTITUTION.md`
- `01-VISION.md`
- `02-FOUNDATIONAL-CONCEPTS.md`
- `03-BLIND-SPOT-FRAMEWORK.md`
- `04-FINANCE-DNA.md`
- `05-ATLAS.md`

**Used By:**
- `07-SYSTEM-ARCHITECTURE.md`

**Artifact:** Reasoning Model

**Research Question:**
How should Hyperion transform evidence into explainable reasoning?

---

## 1. Why Janus Exists

Information connected together is still not reasoning.

Atlas can answer how everything is connected, exhaustively. Given a Company, it can return every qualified Reasoning Path radiating out from it — through Commodities, Geographies, Macro Factors, Economic Events — all of them real, all of them evidence-traceable, all of them canonical. And none of that, by itself, concludes anything. A graph full of true paths is not the same thing as a reason why a particular Portfolio is exposed to a particular risk today. Something still has to choose, weigh, and conclude. Atlas was deliberately built not to do that — Section 8 of `05-ATLAS.md` says so directly: Atlas does not predict, rank, recommend, or infer. It represents.

Janus is what does the rest.

### Identity, Relationships, Logic

Three modules, three different kinds of question, in order:

```
   Finance DNA          Atlas                Janus
   "What is this?"  →  "How is this    →  "What follows
                         connected?"          from these
                                              connections?"

      Identity      →   Relationships   →      Logic
```

Finance DNA gives Hyperion its vocabulary. Atlas gives it grammar. Janus is what lets isolated, grammatically correct sentences become an actual argument — the difference between a graph that *could* explain something and a conclusion that *does*.

### Why this can't live inside Atlas

The honest objection, the same shape as the one Atlas had to answer about Finance DNA: if Atlas already knows every valid path, why not have it just pick the best one and call that the answer?

Because picking is a fundamentally different responsibility than storing, and conflating them breaks the thing that makes Atlas trustworthy. Atlas's value comes from being a neutral, canonical substrate — the same graph has to serve every question anyone will ever ask of it, not just the one being asked right now. The moment Atlas starts favoring one traversal over another, it stops being a representation of what's true and starts being an answer to a specific question, baked into the structure meant to serve all questions equally. Choosing belongs outside the substrate being chosen from.

Janus's responsibility, stated as narrowly as Finance DNA's and Atlas's founding principles were:

**Janus converts structured knowledge into justified conclusions.**

That's the entire scope. Not data. Not storage. Not graphs. Not features. Not UI. One sentence, and everything in this document either serves it or doesn't belong here.

### The founding principle

Finance DNA: every Dimension must justify its existence. Atlas: every Relationship must justify its existence. Janus inherits the same discipline, applied to its own primitive:

**Every inference must preserve the chain of evidence that produced it.**

An inference that arrives at a stronger conclusion than its evidence supports has not reasoned — it has guessed and dressed the guess in the language of reasoning. Section 2 makes this enforceable rather than aspirational.

---

## 2. What Makes a Valid Inference?

An inference is the smallest unit of reasoning Janus performs: one step, from something already established to something new. Before Janus is allowed to chain inferences into a Reasoning Chain, each individual inference has to clear its own test — the same discipline Finance DNA applied to dimensions and Atlas applied to relationships, applied now to the act of concluding itself.

An inference qualifies only if it satisfies all five criteria below.

**Logical validity.** An inference's premise must be something already established — a directly qualified Atlas relationship, an observation, or the conclusion of a prior inference in the same chain — and the conclusion must legitimately follow from that premise, not merely come after it. *Fails this test:* concluding "margins will fall" using a premise that was never stated earlier in the chain and doesn't trace back to any Evidence.

**Evidence preservation.** An inference cannot produce more certainty than its weakest input justifies. Combining five well-evidenced steps does not earn a sixth conclusion more confidence than the least-supported step among them. *Fails this test:* treating a chain with one Derived, lower-Confidence relationship (per `05-ATLAS.md` Section 5) as if its conclusion were as certain as a chain built entirely from Disclosed relationships.

**No unsupported assumptions.** Every premise an inference depends on must be either a qualified Atlas relationship or an assumption explicitly flagged as one. Nothing enters a chain silently. *Fails this test:* an inference that quietly assumes "Brazil's coffee harvest is representative of global supply" without ever stating that assumption out loud.

**Reproducibility.** The same inputs — the same Reasoning Path, the same Evidence — must produce the same inference every time. An inference that depends on anything outside its stated inputs, however well it reads, fails this criterion regardless of output quality. *Fails this test:* an inference whose conclusion changes between two runs over an identical, unchanged graph.

**Boundedness.** Every inference must be capable, in principle, of being wrong — it must imply, even if not yet stated to the user, what evidence would overturn it. An inference that cannot be falsified by any conceivable future evidence isn't reasoning; it's assertion wearing reasoning's structure. *Fails this test:* "this company is fundamentally strong," a claim no specific piece of contrary evidence could ever be shown to contradict.

### Why all five must hold

An inference can follow logically and still overstate its own certainty — the second criterion catches that. It can be properly bounded in confidence and still smuggle in an assumption nobody agreed to — the third catches that. It can be honest about its assumptions and still be unreproducible, which means it was never really following from its inputs at all — the fourth catches that. And it can satisfy all of that and still be unfalsifiable, which means it was never a real claim to begin with — the fifth catches that.

An inference that passes four out of five has not earned its place in a Reasoning Chain — exactly the standard every prior module's primitive has been held to.

These criteria define what counts as a valid inference, independent of which model, algorithm, or technology Janus uses to produce it. If the underlying model changes, this test does not.

---

## 3. Types of Reasoning

Not algorithms. Not models. Reasoning *modes* — the different shapes a justified conclusion can take, each one a different way of traversing what Finance DNA and Atlas already provide.

**Deductive** — a single forward traversal along one Reasoning Path, to its natural conclusion.
```
Coffee shortage → Coffee price rises → Nestlé margins pressured
```

**Comparative** — the same pattern, traversed from two different starting nodes, set side by side.
```
Portfolio A's Commodity Exposure   vs.   Portfolio B's Commodity Exposure
```

**Analogical** — matching the *shape* of a Reasoning Path against a historical instance of the same shape, rather than the same nodes.
```
Current situation  ──(same pattern as)──▶  a prior, structurally similar Market State
```

**Counterfactual** — the same traversal, with one edge hypothetically altered or removed, to see what conclusion no longer holds.
```
What if Interest Rate Sensitivity had not risen? → does Margin Pressure still follow?
```

**Exploratory** — traversal outward from a single node across every available edge, with no predetermined destination — the mode behind "what else depends on this?"
```
Brazilian Coffee ──▶ {every Asset connected by depends_on}
```

Five modes, not five technologies. Whatever model eventually executes them, the mode is what determines which shape of question Janus is answering — a single chain, a side-by-side, a structural echo, a hypothetical, or an open traversal.

---

## 4. Reasoning Chains

This is where Janus actually consumes what Atlas produces.

```
   ATLAS produces:        Node ──edge──▶ Node ──edge──▶ Node

   JANUS produces:   Observation → Evidence → Inference → Conclusion
```

A Reasoning Path, as defined in `05-ATLAS.md` Section 7, is a structural fact: a traversal exists, every edge along it is canonical and qualified. That is not yet a Reasoning Chain, as defined in `02-FOUNDATIONAL-CONCEPTS.md`. A Reasoning Chain is what results once Janus applies Section 2's criteria to that traversal and reshapes it into something that *argues*, not just *connects*.

Worked example — the same chain `05-ATLAS.md` used to motivate Reasoning Paths, now passed through Janus:

| Atlas (structure) | Janus (argument) |
|---|---|
| Nestlé —depends_on→ Coffee | **Observation:** Nestlé depends on coffee as a commodity input. |
| Coffee —located_in→ Brazil | **Evidence:** Coffee sourcing is concentrated in Brazil (Geographic Footprint, Pattern B). |
| Brazil —affected_by→ Drought | **Evidence:** Brazil is currently affected by a qualified Economic Event — drought. |
| *(no further edge — this is where Atlas stops)* | **Inference:** A drought in a concentrated sourcing region reduces coffee supply, which raises coffee prices. |
| *(not represented in Atlas at all)* | **Inference:** Higher input prices pressure Nestlé's margins, given its Commodity Input Exposure (`04-FINANCE-DNA.md`, Section 6). |
| *(not represented in Atlas at all)* | **Conclusion:** Nestlé carries a hidden, climate-linked margin risk the investor did not knowingly take on — therefore producing a candidate Blind Spot for Titan to evaluate. |

The first three rows are pure Atlas — structure that already existed. The last three rows are where Janus actually operates: turning a chain of facts into a chain of *claims*, each one satisfying Section 2 before the next is allowed to build on it. Atlas stores the possibility that this path exists. Janus is what selects it, in response to a specific question, and accepts responsibility for every inference layered on top of it.

This is also where Section 2's criteria stop being abstract. "Evidence preservation" means the Conclusion's Confidence cannot exceed the weakest Evidence row above it. "Logical validity" means each Inference's premise is a row already on this table, and that the next row genuinely follows from it — never a fact introduced only at the bottom.

---

## 5. Explainability

This is Hyperion's differentiator, and it deserves to stand on its own rather than be folded into Section 2's qualification test. Every conclusion Janus produces must be able to answer five questions, on demand, not just in principle:

- **Why?** — the Reasoning Chain itself, in order.
- **Supported by what?** — the Evidence behind each step, traceable back to Atlas and Finance DNA.
- **How confident?** — the compounding Confidence Layer (`05-ATLAS.md`, Section 5), never overstated past its weakest link.
- **What assumptions?** — every premise that wasn't a direct, qualified fact, named explicitly rather than buried.
- **What would change this?** — the falsifiability already required by Section 2's Boundedness criterion, made concrete: what specific evidence would overturn the conclusion.

These five questions are not new requirements invented for the user's benefit after the fact. Each one is the user-facing version of something Section 2 already demanded internally — Why traces Logical validity; Supported by what traces Evidence preservation; What assumptions traces No unsupported assumptions; What would change this traces Boundedness. Explainability isn't a feature layered on top of Janus's reasoning. It's that reasoning, made visible.

A conclusion that cannot answer all five, on request, has not finished being reasoned about — regardless of how confident it sounds.

---

## 6. Design Implications

### What Janus is not

Janus is not an LLM. Not a chatbot. Not a prediction engine. Not a recommendation engine. Not a classifier. Janus is a reasoning engine — a process defined by Section 2's criteria and Section 4's structure, independent of whatever specific model executes it. If the underlying model is replaced tomorrow, Janus's definition does not change; only its implementation does. That portability is the test of whether this abstraction was drawn correctly.

### The boundary with Titan

Janus does not discover Blind Spots. Titan does. Janus explains them.

```
   Titan asks:   "What matters?"
   Janus answers: "Why?"
```

Titan's job is to decide which candidate findings, out of everything Atlas and Finance DNA make possible, are worth surfacing to a user at all — the qualification discipline `03-BLIND-SPOT-FRAMEWORK.md` Section 7 already defined. Janus's job begins after that decision is made: given a finding Titan has already decided matters, construct and defend the Reasoning Chain behind it. Janus never decides what's important. It only ever explains what already has been decided to be.

### Output: The Reasoning Artifact

Janus's responsibility ends once it has produced a fully explainable reasoning artifact containing the observation, evidence, reasoning chain, conclusion, confidence, assumptions, and conditions under which that conclusion would change. Janus produces reasoning, not presentation; how that artifact is visualized or surfaced to the user belongs to later modules.

This gives Janus a clean boundary on both sides:

```
   Input:   Finance DNA  +  Atlas
                  │
                  ▼
              [ JANUS ]
                  │
                  ▼
   Output:  Reasoning Artifact
                  │
                  ▼
   Titan evaluates it.  UI renders it.
```

Everything in Sections 1–5 describes how the artifact is built. This paragraph is what closes the module: once that artifact exists, satisfying Section 5's five questions in full, Janus's job is finished — regardless of what happens to it next.

### Scope

Janus operates over Reasoning Paths already qualified by `05-ATLAS.md` and dimensions already qualified by `04-FINANCE-DNA.md`. It does not independently source new facts, qualify new relationships, or qualify new dimensions — those remain Atlas's and Finance DNA's responsibilities respectively. Janus's scope is the conversion step between qualified knowledge and a justified conclusion, nothing upstream of that and nothing downstream of Titan's decision to surface a finding.

### Future Extensions

- Formal scoring for how Confidence should compound across the five reasoning modes in Section 3, not just along a single Deductive chain.
- A standard format for presenting Counterfactual and Exploratory conclusions to a user, since both produce a set of possibilities rather than Deductive reasoning's single conclusion.
- Versioning for Reasoning Chains whose underlying Atlas relationships later change — what happens to a conclusion already shown to a user when one of its Evidence rows is updated.

### Open Questions

- Should Janus be allowed to combine reasoning modes within a single Reasoning Chain — for instance, a Deductive chain that includes one Comparative step — or should each chain commit to a single mode?
- How should an Inference's Confidence formally compound across multiple prior Inferences, beyond "no higher than the weakest input" — is there a precise function, or does this remain qualitative for now?
- When a user asks "what would change this conclusion?", how specific does Janus's answer need to be before it counts as having actually answered Section 5's fifth question, rather than gesturing at it?

---

## Revision History

| Version | Date | Summary |
|---|---|---|
| 1.0 | 28 June 2026 | Initial release. Sections 1–6 complete. Logical continuity renamed to Logical validity; Section 4 made the Janus→Titan handoff explicit; added Output: The Reasoning Artifact to Section 6. |
