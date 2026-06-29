# 05 — Atlas

**Version:** 1.0
**Status:** Active — Sections 1–8 complete
**Last Updated:** 28 June 2026
**Document Owner:** Hyperion Core

**Depends On:**
- `00-CONSTITUTION.md`
- `01-VISION.md`
- `02-FOUNDATIONAL-CONCEPTS.md`
- `03-BLIND-SPOT-FRAMEWORK.md`
- `04-FINANCE-DNA.md`

**Used By:**
- `06-JANUS.md`
- `07-SYSTEM-ARCHITECTURE.md`

**Artifact:** Knowledge Graph Ontology

**Research Question:**
How should financial knowledge be represented so that relationships become discoverable?

---

## 1. Why Atlas Exists

Finance DNA tells Hyperion what an Asset is in isolation. It cannot tell Hyperion why two Assets behave similarly, why one macroeconomic event affects hundreds of companies simultaneously, or why two Blind Spots share the same underlying cause. Those are questions of relationship, not identity — and Finance DNA, by design, only answers questions of identity.

### Intrinsic versus extrinsic

Every dimension in `04-FINANCE-DNA.md` describes something **intrinsic** — a characteristic that belongs to one Asset and can be stated without referring to anything outside it. Capital Intensity, Pricing Power, Interest Rate Sensitivity: each is true of a company on its own terms.

But a company is also defined by what it depends on, **extrinsically**: it uses copper, it sells into Europe, it depends on a single supplier in Taiwan, it shares that supplier with three of its competitors. None of these facts live inside the company. They live in the space between the company and something else. Finance DNA has no field for that space — not because it was built carelessly, but because intrinsic characteristics and extrinsic relationships are genuinely different kinds of facts, and a representation built to qualify one kind well (Section 2's five criteria) was never built to qualify the other.

Atlas exists to represent the extrinsic half of economic identity that Finance DNA was never designed to hold.

### Why this can't simply be added to Finance DNA

The honest first instinct is to ask why Atlas needs to exist separately at all — why not just add a "Relationships" field to each Asset's Finance DNA and call it done.

Here's why that fails: relationships are not properties of one Asset. They're shared. Nestlé, Starbucks, JDE Peet's, and Luckin Coffee all depend on coffee, which depends on Brazil, which depends on weather. If that chain were stored inside each company's Finance DNA individually, the same fact — coffee comes from Brazil, Brazil's harvest is exposed to drought — would exist four separate times, with no way of confirming all four copies say the same thing, or of noticing when a fifth company shares the same exposure. A representation that duplicates a single fact once per Asset that depends on it cannot stay consistent as Hyperion scales, and duplicated facts that drift apart are themselves a source of inconsistency.

This gives Atlas its own founding principle, distinct from anything Finance DNA needed:

**Atlas exists so that every meaningful financial relationship has one canonical representation, regardless of how many Assets depend on it.**

Coffee exists once. Brazil exists once. Drought exists once. Every Asset that depends on any of them points to the same underlying fact rather than carrying its own copy. That's what makes Atlas a graph rather than another table — a table duplicates; a graph references.

### Reasoning is traversal

`02-FOUNDATIONAL-CONCEPTS.md` defines a Reasoning Chain as an ordered sequence of steps connecting an observation to a conclusion. A chain requires something to traverse — and Finance DNA, however complete, provides none of that structure. It provides well-qualified, well-evidenced nodes, sitting next to each other with nothing connecting them. A list of forty scored dimensions is not a chain; it's a table.

This is also why Correlation and Causality could only be *named* as distinct concepts in `02`, not actually *told apart*. Distinguishing them requires an actual causal path — commodity, geography, climate event — not just two numbers that happen to move together with no visible mechanism between them. Finance DNA has no way to represent a path. Atlas is what makes a path representable at all.

It follows that an Evidence Graph, as defined in the Blind Spot Framework, is not something Hyperion generates fresh for each explanation. If it were, two Blind Spots tracing back to the same underlying cause would have no way of being recognized as the same thing — Hyperion would be explaining persuasively, but not consistently, and consistency is what Explainability actually requires. The Evidence Graph has to already exist, as part of Atlas, before any question is asked of it. Janus, when it eventually reasons over Atlas, doesn't construct the graph — it traverses one that's already there.

### What the Constitution already said

`00-CONSTITUTION.md` states that markets are difficult because relationships are obscured. At the time that read as philosophy. It's actually a specification: Atlas is the module whose sole job is to make those obscured relationships visible and inspectable, one canonical node and edge at a time.

### The answer to the research question

Why can't Hyperion reason without Atlas? Not because Atlas stores more information than Finance DNA does. Because reasoning is the act of traversing relationships, and Finance DNA provides the entities that can be reasoned about while supplying nothing to reason *across*. Without Atlas, Hyperion can describe Assets in detail and still have no consistent way to explain how one fact leads to another.

If Finance DNA gave Hyperion its vocabulary, Atlas gives it its grammar.

---

## 2. What Makes a Valid Relationship?

A graph is only as trustworthy as its edges. Without a test, Atlas would accumulate every true connection anyone could think to draw — same headquarters state, same auditor, same fiscal year-end — until the graph that was supposed to make hidden relationships visible instead buried them under thousands of true but inert ones. Before naming a single relationship type, Atlas needs the same kind of test Finance DNA needed before naming a single dimension.

A relationship qualifies only if it satisfies all five criteria below.

**It represents a real, verifiable connection, not a coincidence.** A relationship must reflect an actual mechanism linking two nodes — one depends on, supplies, competes with, is exposed to — not a pattern that merely happens to co-occur. This is the same line `02-FOUNDATIONAL-CONCEPTS.md` drew between Correlation and Causality, applied at the level of what's allowed to become an edge at all. *Fails this test:* "incorporated in the same jurisdiction." True of two companies, and connects nothing about how either one actually behaves.

**It connects two canonical nodes.** Both endpoints have to already exist in Atlas as well-defined entities — an Asset, a Macro Factor, a commodity, a geography — not a vague or freshly-invented placeholder created just to host this one edge. A relationship between something canonical and something ad hoc isn't really an edge in the graph; it's a note attached to one node, dressed up as a connection. *Fails this test:* "exposed to changing consumer tastes." "Changing consumer tastes" is not a node anything else in the graph could ever point to.

**It is canonical, not duplicated.** Before a relationship is added, the question is always whether it already exists under a different name pointing at the same underlying fact. This is the direct enforcement of Section 1's founding principle — a relationship that gets re-created every time a new Asset needs it has already failed, regardless of how accurate it is. *Fails this test:* adding a fresh "Coffee → Brazil" edge for Starbucks when that edge already exists from Nestlé's entry — the correct action is pointing to the existing edge, not creating a second one.

The first three criteria establish whether something is a well-formed edge at all. The remaining two determine whether that edge is worth Atlas carrying.

**It is evidence-traceable.** Every relationship must be groundable in a verifiable fact — a disclosed supply agreement, a segment filing, a commodity classification, a publicly known regulatory relationship — not an inferred or assumed connection. This is the same standard Section 2 of `04-FINANCE-DNA.md` holds dimensions to, and the same standard the Blind Spot Framework holds Evidence to; Atlas cannot relax it just because it sits one layer further from the user-facing conclusion. *Fails this test:* "likely sources cocoa from West Africa" with no disclosed sourcing data behind it — plausible, but not yet inspectable.

**It improves financial reasoning, not merely visual completeness.** A relationship earns its place only if some Reasoning Chain could actually traverse it — toward an Exposure, a Dependency, or a Blind Spot. A relationship that is true, well-evidenced, and connects two canonical nodes, but that no reasoning process would ever need to cross, is decoration on the graph rather than structure in it. *Fails this test:* "listed on the same stock exchange as." Real, canonical, evidence-traceable — and irrelevant to how either company actually behaves.

### Why all five must hold

A relationship can be perfectly true and still be a coincidence dressed as a connection — the first criterion catches that. It can reflect a real mechanism and still connect something that isn't a real node — the second catches that. It can be well-formed and still be a duplicate of something already in the graph — the third catches that. It can be unique and well-formed and still rest on nothing inspectable — the fourth catches that. And it can pass all of that and still never matter to anything Hyperion actually needs to explain — the fifth catches that.

A relationship that passes four out of five has not earned its place — the same standard Finance DNA's dimensions and categories were both held to, applied now one module further along.

These criteria define what counts as a relationship, independent of how Atlas stores, queries, or visualizes the graph.

---

## 3. What Kinds of Nodes Exist?

Not every company. Not every supplier. The node *types* — the ontology a relationship's endpoints are drawn from, per Section 2's second criterion: every edge needs two canonical nodes, and this section is what makes "canonical" mean something concrete.

Two classes of node, not one list:

```
                FINANCIAL SYSTEM
                       │
         ┌─────────────┴─────────────┐
         │                           │
    ECONOMIC ACTORS            ECONOMIC CONTEXT
   (things that act,          (things actors depend
    hold Finance DNA)          on or are exposed to)
         │                           │
    ┌────┴────┐         ┌────────────┼─────────────┬──────────┐
    │         │         │            │              │          │
  Asset   Supply     Commodity   Geography      Macro       Industry
          Chain                                  Factor         │
          Entity                                            Regulation
                                                                 │
                                                          Economic Event
```

**Asset** — per `02-FOUNDATIONAL-CONCEPTS.md`. Under Version 1's scope, this is instantiated as a publicly traded Company. Deliberately *not* split into a separate "Asset" node and "Company" node — they're the same node type at two altitudes, and adding a second name for the same thing would repeat the exact mistake Finance DNA's qualification round caught and merged (Innovation Intensity / R&D Intensity, two names for one fact).

**Supply Chain Entity** — an economic actor that participates in a Company's supply chain or customer base but isn't itself a tracked Asset: a private supplier, an unlisted distributor. This node type exists for a specific reason: `04-FINANCE-DNA.md` Section 4 scoped Version 1 to publicly traded companies only, which means most of a Company's real supply chain has no Finance DNA at all. Without this node type, a relationship like "depends on a private cocoa exporter" would have nothing real to point to — failing Section 2's second criterion outright. Supply Chain Entity is what lets that relationship exist honestly, even though the entity at the other end carries no Finance DNA of its own.

**Commodity** — a fungible physical or financial input: coffee, copper, crude oil.

**Geography** — a country or region. The anchor point most Macro Factors, supply chains, and currency relationships ultimately resolve to.

**Currency** — a unit of account whose movement is what makes Currency Exposure (`04-FINANCE-DNA.md`, Section 6) a real, traceable relationship rather than an abstract score.

**Macro Factor** — per `02-FOUNDATIONAL-CONCEPTS.md`: an external force affecting many Assets simultaneously (interest rates, inflation).

**Industry** — a classification grouping Companies that compete or operate similarly. This is also where a dimension that didn't quite fit inside Finance DNA finds a home: Market Concentration was flagged Needs Refinement on the Dimension Candidate Board specifically because it described the *industry*, not the company. As a property of an Industry node rather than a forced-fit Asset dimension, it stops being a refinement problem and becomes exactly what it always was.

**Regulation** — a specific regulatory regime or rule that a Company or Industry is subject to.

**Economic Event** — a discrete occurrence with a beginning: a drought, a rate hike, a supply shock. The node type that gives a Reasoning Path (Section 7) its sense of something *happening*, rather than just something *being*.

The node types above intentionally avoid introducing separate concepts that differ only in name — Company folded into Asset, and nothing invented just because it was on the original brainstorm list. If a future version introduces Exchange, or Country Bloc, or Shipping Route, that's a new node earning its place under this same test, not a contradiction of it. The philosophy is what's load-bearing here; the count is implementation detail.

---

## 4. What Kinds of Relationships Are Allowed?

Now that the nodes exist, the verbs connecting them have somewhere real to land. Every relationship type below has to pass Section 2 — particularly the first criterion, a real mechanism, not a coincidence — and every one declares which node types it's actually allowed to connect, the same way every Finance DNA dimension declared a Value Structure and a Temporal Behavior before it meant anything.

```
   Asset ──depends_on──▶ Commodity / Supply Chain Entity / Asset
   Asset ──competes_with──▶ Asset            (symmetric, same Industry)
   Asset ──sells_to──▶ Asset
   Asset ──exports_to──▶ Geography
   Asset / Supply Chain Entity / Commodity ──located_in──▶ Geography
   Asset ──exposed_to──▶ Macro Factor / Currency
   Asset ──affected_by──▶ Economic Event
   Asset / Industry ──regulated_by──▶ Regulation
   Asset ──belongs_to──▶ Industry
```

*One addition flagged honestly: `belongs_to` wasn't in the original pass. Industry was qualified as a node type in Section 3 with no relationship type ever connecting an Asset to it — a real gap, not a style choice, surfaced while drafting Section 6's patterns. Per the standing rule that frozen sections only reopen for genuine inconsistencies, this is one.*

A worked chain, the shape Section 7 will eventually formalize:

```
   Nestlé
      │ depends_on
      ▼
   Coffee
      │ located_in
      ▼
   Brazil
      │ affected_by
      ▼
   Drought (Economic Event)
```

Two things surfaced while drafting this list that turn out not to belong here at all. Section 4 answers *what relationships exist*; these two questions are about *what properties every relationship carries* — which makes them Section 5's job, not an open item to resolve before reaching it.

**Directionality.** `depends_on` and `supplies` are inverses of the same underlying fact — Nestlé depends on a coffee supplier; the supplier supplies Nestlé. Storing both as separate relationship types risks the exact duplication problem Section 1 built Atlas to prevent. This isn't a naming preference to settle now — it's a property of the relationship itself, and Section 5 is where that property gets defined.

**Persistent versus event-triggered.** `exposed_to` describes a standing sensitivity (an Asset is structurally exposed to a Macro Factor, indefinitely). `affected_by` describes something with a start and, usually, an end (a drought happened). That distinction echoes Finance DNA's Static / Time-varying axis from Section 3, but for relationships instead of dimensions — which is exactly why it belongs in Section 5 as a relationship characteristic, not folded into the relationship-type list above.

---

## 5. Relationship Characteristics

Section 4 answered what relationships exist. This section answers what every relationship, regardless of type, carries with it. Not because graphs conventionally have these properties — because Hyperion specifically needs them in order to reason consistently, the same way Finance DNA needed Value Structure and Temporal Behavior before a single dimension could be trusted.

Five characteristics. Every relationship type from Section 4 gets a value on each.

### Directionality

```
   Directed         A ──▶ B          meaning holds one way only
   Bidirectional    A ◀──▶ B         one fact, different label per direction
   Symmetric        A ──▶ B          same label, same meaning, either direction
                    A ◀── B
```

**Directed** — the relationship only means something traveling one way. `located_in` is Directed: a Commodity is located in a Geography, and reversing the arrow produces nonsense, not a different true statement.

**Bidirectional** — a single underlying fact, labeled differently depending on which end it's read from. This is the resolution to Section 4's open directionality question: `depends_on` and `supplies` are not two relationship types. They're one Bidirectional relationship, stored once, read as "depends_on" from the dependent Asset's side and "supplies" from the other side. One canonical edge, two labels — which is exactly what Section 1's founding principle requires.

**Symmetric** — the same label is true regardless of which node is named first. `competes_with` is Symmetric: if Coca-Cola competes_with Pepsi, that's one fact, not two.

### Temporality

```
   Persistent     ──────────────────────────────▶   holds until something changes it
   Temporal       ────[================]────────▶   holds for a known, bounded term
   Event-driven        ▲                            tied to a discrete occurrence
                      (event)
```

**Persistent** — holds indefinitely until a structural change overwrites it. `depends_on`, `located_in`, and `regulated_by` are typically Persistent.

**Temporal** — holds for a known, bounded duration that isn't a single instant: a five-year supply contract, a multi-year trade agreement. Distinct from Persistent (no defined end) and from Event-driven (no defined duration at all, just a moment something happened).

**Event-driven** — tied to a discrete occurrence with a start and, usually, an end. `affected_by` is Event-driven by definition; this is the formal version of the Section 4 observation that a drought is fundamentally different in kind from a standing dependency.

### Cardinality

```
   One-to-One      A ── B
   One-to-Many     A ──┬── B₁
                       ├── B₂
                       └── B₃
   Many-to-Many    A₁ ─┬─ B₁
                    A₂ ─┴─ B₂
```

How many edges of a given relationship type a single node can hold. `located_in` is typically One-to-Many from Geography's side (many Assets located in one Geography) and One-to-One from a given Asset's primary-headquarters perspective. `depends_on` is Many-to-Many: a Commodity is depended on by many Assets, and a single Asset typically depends on several Commodities at once. Cardinality doesn't change what a relationship type means — it changes what aggregation across it is allowed to assume.

### Evidence Source

Every relationship already had to clear Section 2's evidence-traceability criterion to exist at all. This characteristic records *what kind* of evidence it cleared that bar with — the same Primitive / Derived distinction Finance DNA's qualification round surfaced for dimensions, applied here to relationships:

- **Disclosed** — directly stated in a filing, segment report, or comparable primary source.
- **Public Record** — independently verifiable but not company-disclosed (a patent filing, a regulatory registry).
- **Derived** — inferred from a combination of other, already-qualified relationships, rather than read directly off one source.

A relationship's Evidence Source type isn't a judgment of how good the relationship is — `21. Interest Rate Sensitivity` in Finance DNA is Derived and still qualified cleanly. It's a record of how to verify the claim, and where to look if it ever needs re-checking.

### Confidence

The relationship-level instance of the Confidence Layer already defined in `02-FOUNDATIONAL-CONCEPTS.md`. A Disclosed relationship typically carries a high Confidence value by default; a Derived relationship's Confidence depends on the Confidence of everything it was derived from. This is what lets a Reasoning Path (Section 7) carry an honest, compounding Confidence Layer across multiple hops, rather than treating every edge in a five-step chain as equally certain — which is rarely true, and asserting otherwise would quietly violate the same Explainability standard the rest of Hyperion has been built around.

---

Every relationship type from Section 4, restated with its characteristics:

| Relationship | Directionality | Temporality | Cardinality | Evidence Source | Confidence |
|---|---|---|---|---|---|
| depends_on / supplies | Bidirectional | Persistent | Many-to-Many | Determined per instance | Derived per instance |
| competes_with | Symmetric | Persistent | Many-to-Many | Determined per instance | Derived per instance |
| sells_to | Directed | Temporal or Persistent | Many-to-Many | Determined per instance | Derived per instance |
| exports_to | Directed | Persistent | One-to-Many | Determined per instance | Derived per instance |
| located_in | Directed | Persistent | One-to-Many | Determined per instance | Derived per instance |
| exposed_to | Directed | Persistent | Many-to-Many | Determined per instance | Derived per instance |
| affected_by | Directed | Event-driven | One-to-Many | Determined per instance | Derived per instance |
| regulated_by | Directed | Persistent | Many-to-Many | Determined per instance | Derived per instance |
| belongs_to | Directed | Persistent | One-to-Many | Determined per instance | Derived per instance |

Note `sells_to` carries two possible Temporality values depending on the instance — a spot sale versus a multi-year supply contract are the same relationship type with different characteristics, not two relationship types. That's the same lesson Section 3 and Section 4 already taught, applied once more: the type stays singular; the variation lives in its characteristics, not in a proliferating list of near-duplicate names.

Evidence Source and Confidence are marked "per instance" rather than left out of the table entirely, even though they don't vary meaningfully at the type level today. This table is the contract between Atlas and Janus — every relationship Janus traverses carries all five characteristics, and a column that's easy to omit now is a column someone eventually forgets exists. Determined and Derived per instance is still a value, not an absence of one.

---

## 6. Canonical Relationship Patterns

Section 4 listed relationship *types*. This section is about something one level more abstract: recurring *structures* — combinations of node types and relationship types that show up again and again across unrelated companies, because the underlying economics are the same even when the names aren't.

The distinction matters. "Nestlé depends_on Coffee" is an example — one specific edge, between two specific nodes. The pattern underneath it is `Asset —depends_on→ Commodity` — a template with the types left in, the instances pulled out. The same pattern represents Starbucks → Coffee, Hershey → Cocoa, and Delta → Jet Fuel equally well. Atlas isn't storing four facts that happen to look similar. It's storing one structure, instantiated four times.

This section is closer to a grammar book than a dictionary: not "here are the relationships," but "here are the sentence structures Atlas understands." Six canonical patterns, each built entirely from node types (Section 3) and relationship types (Section 4) already established — nothing new is introduced here, only recombined.

**Pattern A — Commodity Dependency**
```
   Asset
     │ depends_on
     ▼
  Commodity
```
*Purpose:* represents reliance on a fungible input. *Instances:* Nestlé → Coffee, Hershey → Cocoa, Delta → Jet Fuel.

**Pattern B — Geographic Footprint**
```
   Asset
     │ located_in
     ▼
  Geography
```
*Purpose:* represents where an Asset is headquartered or operates. *Instances:* Nestlé → Switzerland (headquarters, One-to-One), Nestlé → dozens of manufacturing countries (operational footprint, One-to-Many). One relationship type, two Cardinality values — not two relationship types. (This pattern absorbs what might first look like a separate "operates_in" relationship: headquarters and operating footprint are the same fact, *located_in*, differing only in Cardinality, exactly the way `sells_to` already differs by Temporality in Section 5.)

**Pattern C — Regulatory Dependency**
```
   Asset
     │ regulated_by
     ▼
  Regulation
```
*Purpose:* represents formal oversight. *Instances:* a bank → capital adequacy requirements, a utility → rate-setting regulation. (The enforcing body — an SEC, an FDA — is metadata carried on the Regulation node itself, not a separate node type. Adding a parallel "Regulator" node would duplicate what Regulation already represents, the same mistake Section 3 avoided with Company/Asset.)

**Pattern D — Sector Membership**
```
   Asset
     │ belongs_to
     ▼
  Industry
```
*Purpose:* represents which competitive set an Asset participates in. The structural backbone `competes_with` depends on — two Assets that both `belong_to` the same Industry are the ones `competes_with` connects.

**Pattern E — Macro Exposure**
```
   Asset
     │ exposed_to
     ▼
  Macro Factor / Currency
```
*Purpose:* represents structural sensitivity to a force no single Asset controls.

**Pattern F — Event Impact**
```
  [any node]
     │ affected_by
     ▼
 Economic Event
```
*Purpose:* represents a discrete occurrence striking a node — the only pattern whose Temporality (Section 5) is Event-driven rather than Persistent, and the pattern that turns a static graph into one capable of representing something *happening*.

Six patterns, not a fixed ceiling — but six is also not an accident. Every relationship type from Section 4 appears in exactly one pattern above, with nothing left over and nothing repeated. That's the check this section was supposed to pass: if a relationship type didn't fit a pattern, either the pattern list was incomplete or the relationship type didn't actually belong in Section 4 to begin with.

Patterns rarely appear alone. Chained together — Pattern A into Pattern B into Pattern F — they produce exactly the kind of structure Section 7 is about to formalize.

---

## 7. Reasoning Paths

A relationship is not a conclusion.

```
   Asset
     │ depends_on
     ▼
  Commodity
```

On its own, this tells Hyperion almost nothing useful — a single fact, sitting alone. But chain several canonical patterns together:

```
   Nestlé
      │ depends_on
      ▼
   Coffee
      │ located_in
      ▼
   Brazil
      │ affected_by
      ▼
   Drought
      │ reduces supply
      ▼
   Higher Coffee Prices
      │
      ▼
   Margin Pressure
      │
      ▼
   Portfolio Blind Spot
```

That's no longer a relationship. It's a **Reasoning Path** — an ordered traversal across canonical edges, each one independently real, that together produce a conclusion none of them states alone.

### What makes a Reasoning Path valid

A traversal only counts as a Reasoning Path if it satisfies all four:

**Logical continuity.** Each step's endpoint is the next step's starting node. No skipping from Coffee directly to Margin Pressure without passing through Brazil and Drought — a path with a gap in it isn't a shorter path, it's a broken one.

**Evidence at every step.** Every edge in the traversal already independently cleared Section 2's qualification criteria before this path ever existed. A Reasoning Path doesn't grant evidence to an edge that lacked it — it only ever connects edges that already had it.

**No unsupported jumps.** Every step in the path has to be an actual edge that exists in Atlas, not a connection invented in the moment because it would make the explanation land better. A persuasive shortcut that isn't a canonical edge is not a Reasoning Path — it's a guess wearing one.

**Canonical traversal.** Where a relationship is Bidirectional (Section 5), the path has to traverse it consistent with that relationship's actual semantics in the direction it's being read — reading `depends_on` as `supplies` partway through a chain without acknowledging the direction flip would silently misstate what the edge means.

### Atlas stores possibilities. Janus chooses paths.

This is the boundary the rest of Hyperion's architecture depends on. Atlas, fully built, contains an enormous number of valid traversals — most of them irrelevant to any particular question. Atlas does not decide which one matters for a given Asset, a given Portfolio, a given moment. That selection — *which* Reasoning Path answers *this* question — belongs to Janus, not Atlas.

This is also the precise, formal version of something Section 1 already argued less precisely: Janus doesn't construct the Evidence Graph behind a Blind Spot. It traverses one that already exists. A Reasoning Path is what that traversal actually is, made concrete enough to test against four criteria rather than just asserted as a metaphor.

### Janus's contract

The four criteria above aren't just a definition — they're what Janus has to guarantee every time it presents a Reasoning Chain to a user. If a presented explanation can't be shown to satisfy all four against the live graph, it isn't a Reasoning Path yet. It's a claim about one.

---

## 8. Design Implications, Scope, and Open Questions

### What Atlas deliberately does not do

Atlas does not predict, rank, recommend, or infer. It represents. Every one of those four verbs requires choosing among possibilities — and choosing is Janus's job, established formally in Section 7. The moment Atlas starts ranking which relationships matter most for a given question, or inferring a connection that wasn't independently qualified through Section 2, it has quietly become Janus wearing Atlas's name, and the clean separation the rest of this document depends on collapses. This boundary is a Design Implication in the same sense Finance DNA's "detection and explanation stay separate" was: a rule for whoever builds this, not a passive observation about what Atlas happens to be.

### Version 1 Scope

Atlas Version 1 is built from exactly the node types qualified in Section 3: Companies (as Assets), Commodities, Geographies, Currencies, Macro Factors, Industries, Regulations, Economic Events, and Supply Chain Entities. Nothing in Sections 3–7 assumed anything beyond this set — the scope was set implicitly by which node types survived qualification, not declared separately here.

**Future Extensions**
- Shipping routes, as a node type connecting Geography to Geography directly rather than implying transit through Commodity Dependency alone.
- ESG-related node and relationship types, once Finance DNA's own Regulatory Transition Exposure dimension matures past its current data-maturity caveat.
- Supply chain tiers — distinguishing a direct Supply Chain Entity from one two or three hops removed, rather than treating all non-Asset suppliers as a single undifferentiated node type.
- Private markets, extending Supply Chain Entity's logic (a real node without Finance DNA) to private companies more generally, not just supply-chain participants.

### Open Questions

Recorded, not answered — exactly the discipline the Blind Spot Framework and Finance DNA both held to at this stage.

- Should relationships carry numeric weights, distinct from Confidence, to express magnitude (how *much* an Asset depends on a Commodity, not just whether it does)?
- Should Confidence be tracked at the node level as well as the edge level, or is edge-level Confidence sufficient to derive whatever node-level confidence Janus eventually needs?
- Can a single edge legitimately carry multiple Evidence Sources — for instance, a relationship that is both Disclosed and independently confirmed by Public Record — and if so, how should Confidence combine them?
- How should Temporal relationships (a contract with a defined term) be versioned as they near or pass their end date, rather than silently remaining in the graph as if still active?

---

## Revision History

| Version | Date | Summary |
|---|---|---|
| 1.0 | 28 June 2026 | Initial release. Sections 1–8 complete. |
