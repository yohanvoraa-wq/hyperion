# 07 — System Architecture

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
- `05-ATLAS.md`
- `06-JANUS.md`

**Used By:**
- Implementation (all engineering work from this point forward)

**Artifact:** System Interaction Contract

**Research Question:**
How should Hyperion's conceptual abstractions be wired into an executable system without violating the boundaries that define them?

---

## 1. Why Architecture Exists

A well-defined abstraction is not the same thing as a system that runs.

Every document so far has asked *what*. Finance DNA asked what an Asset is. Atlas asked how Assets connect. Janus asked what follows from those connections. None of those documents can be executed. They're correct, qualified, internally consistent — and entirely inert until something wires them together in an order, with a direction, and with rules about who is allowed to call whom. That wiring is what this document is.

### Why this can't be skipped

The honest objection here is different from the one every prior document had to answer. It's not "why not fold this into Janus" — it's "why not just start writing code." The six documents already say what's true. Isn't the rest just engineering?

It isn't, for the same reason every previous boundary in this repository mattered: the moment code gets written without first deciding how modules are allowed to talk to each other, the boundaries that took six documents to earn get eroded in an afternoon. A function that both selects a Reasoning Path *and* decides whether the resulting Blind Spot is worth surfacing has quietly merged Janus and Titan, even if no one intended that and even if the code works. Boundaries that exist only in documentation don't survive contact with a deadline. Architecture is what makes them survive it — by deciding, before any framework or language is chosen, exactly what is allowed to cross each seam.

### The founding principle

Every module so far has produced exactly one artifact, already named in its own document:

```
   Finance DNA  →  qualified Dimensions
   Atlas        →  qualified Reasoning Paths
   Janus        →  the Reasoning Artifact
   Titan        →  a qualified Blind Spot   (per 03-BLIND-SPOT-FRAMEWORK.md, Section 7)
```

Architecture's founding principle is narrower than it might look:

**No module may communicate with another except through the artifact that module's own specification already defined.**

Architecture does not invent new interfaces between Finance DNA, Atlas, Janus, and Titan. It wires together interfaces that already exist, in the order the conceptual documents already implied. If this document finds itself defining a new kind of object that needs to pass between two modules, that's a signal one of the earlier documents is incomplete — not a license to patch the gap here.

### Conceptual architecture versus engineering architecture

```
──────────────────────────────────────────
        CONCEPTUAL ARCHITECTURE
──────────────────────────────────────────
   Constitution → Vision → Foundational
   Concepts → Blind Spot Framework
              │
   Finance DNA → Atlas → Janus → Titan
   (Identity)  (Relationships) (Reasoning) (Qualification)
──────────────────────────────────────────
        ENGINEERING ARCHITECTURE
──────────────────────────────────────────
              │
      This document
              │
        Implementation
```

Everything above this document asked what Hyperion is and how it thinks. Everything below it asks how those decisions become running software. This document is the seam — and like every seam in this repository, the discipline is to make it as thin and as load-bearing as possible, not to let it sprawl into the layer beneath it.

---

## 2. Core Design Principles

Five principles, none of them new — each one is a synthesis of something already enforced separately in Finance DNA, Atlas, or Janus, now stated as a constraint on the system as a whole rather than on any single module's internals.

**Boundaries.** Every module's responsibility is singular, and every previous document fought to keep it that way — Atlas refusing to rank or recommend, Janus refusing to decide what matters. Architecture's first job is to make sure wiring the modules together doesn't quietly undo six documents' worth of restraint. A boundary that exists in a specification but not in how the system actually calls its functions isn't a boundary; it's a suggestion.

**Data Flow.** Not microservices, not APIs, not queues — not yet. What enters, what leaves, who owns it. Those three questions stay true regardless of what technology eventually implements them, which is exactly why they're the right level for this document and the wrong level for an implementation guide.

**Responsibility.** One module, one job, restated from Section 3's perspective: Finance DNA owns Identity. Atlas owns Relationships. Janus owns Reasoning. Titan owns Qualification. None of the four should ever need to know how another one does its job internally — only what artifact it produces and what artifact it expects.

**Explainability.** The chain of qualification has to survive the transition into a running system intact. A Dimension is qualified before Atlas can use it. A Reasoning Path is qualified before Janus can traverse it. A Reasoning Artifact is complete before Titan can evaluate it. If any hop in the running system allows an unqualified object through "just this once" — for performance, for a missing data source, for convenience — Explainability stops being something Hyperion guarantees and becomes something it usually does.

**Extensibility.** The test isn't whether this architecture handles Hyperion today. It's whether Hyperion Version 5 — with new modules nobody has designed yet — still fits inside the same shape without this document needing a rewrite. A new module should be addable the same way Atlas's `belongs_to` relationship type was added to an already-frozen section: because it satisfies the existing rules, not because the rules were bent to fit it.

---

## 3. Module Responsibilities

```
   Module        Owns            Produces                 Never
   ──────        ────            ────────                  ─────
   Finance DNA   Identity        Qualified Dimensions      Creates relationships
   Atlas         Relationships   Qualified Reasoning Paths  Creates Blind Spots
   Janus         Reasoning       The Reasoning Artifact     Creates Dimensions
   Titan         Qualification   A qualified Blind Spot     Changes Reasoning Chains
```

Each row is a complete restatement of a boundary a prior document already spent a full section defending — `04-FINANCE-DNA.md` Section 8, `05-ATLAS.md` Section 8, `06-JANUS.md` Section 6. Architecture adds nothing to these boundaries. It just insists they survive being wired into a system, which is what the "Never" column is actually for: not a description of current behavior, but a constraint on what's allowed to be built.

A useful test for any proposed engineering change, going forward: name which module owns the change, and check it against this table. If the change requires touching a module's "Never" column to work, the change is wrong — not the table.

---

## 4. System Flow

```
                              USER
                                │
                                ▼
              Upload Portfolio / Ask Question
                                │
                                ▼
                  Portfolio Ingestion Layer
                                │
                                ▼
                          Finance DNA
                   (Identity Representation)
                                │
                                ▼
                            Atlas
                  (Relationship Discovery)
                                │
                                ▼
                            Janus
                 (Evidence-Based Reasoning)
                                │
                                ▼
                            Titan
              (Blind Spot Qualification)
                                │
                                ▼
                  Explainable Output Layer
                                │
                                ▼
                              USER
```

Six hops, six already-defined crossings:

1. **User → Ingestion.** A raw Portfolio enters. Nothing about this hop is conceptually interesting yet — it becomes interesting the moment Ingestion has to resolve a raw holding into something Finance DNA recognizes as an Asset, which is Section 5's job.
2. **Ingestion → Finance DNA.** A resolved Asset is qualified against Finance DNA's dimensions (`04-FINANCE-DNA.md`, Section 2).
3. **Finance DNA → Atlas.** Qualified Dimensions become the Finance-DNA-side endpoint of Atlas relationships — Atlas's nodes are partly populated by Finance DNA's output, not invented separately.
4. **Atlas → Janus.** Qualified Reasoning Paths (`05-ATLAS.md`, Section 7) become the substrate Janus traverses, never the conclusion itself.
5. **Janus → Titan.** A completed Reasoning Artifact (`06-JANUS.md`, Section 6) is handed to Titan as a candidate — Janus's responsibility ends exactly where Titan's begins.
6. **Titan → Output → User.** A qualified Blind Spot, with its Reasoning Artifact still attached, is rendered for the user. Rendering is presentation, not reasoning — the same line `06-JANUS.md` already drew between producing the artifact and visualizing it.

Nothing in this diagram is new information. It's the order six already-written documents implied, made explicit in one place.

---

## 5. Data Lifecycle

Section 4 showed the shape. This section answers, for each hop, the three questions that actually matter: what enters, what leaves, who owns it.

**Entry: Portfolio → Normalization → Asset Resolution → Finance DNA**
*Enters:* a raw Portfolio, in whatever form the user provided it. *Leaves:* a set of resolved Assets, each one identified well enough to be qualified against Finance DNA's dimensions. *Owns it:* the Ingestion layer owns normalization and resolution; once an Asset is resolved, ownership of everything about *what it is* passes to Finance DNA and never returns to Ingestion.

**Finance DNA → Atlas**
*Enters:* a resolved Asset. *Leaves:* that Asset's qualified Dimensions, each one already typed and evidenced per `04-FINANCE-DNA.md` Sections 2–3. *Owns it:* Finance DNA owns the Dimensions themselves, permanently — Atlas only ever references them as one endpoint of a relationship. Atlas does not get to recompute or override a Dimension it disagrees with; disagreement is a signal to revisit Finance DNA's qualification, not a license for Atlas to quietly diverge from it.

**Atlas → Janus**
*Enters:* a question, implicitly defining which part of the graph is relevant. *Leaves:* one or more qualified Reasoning Paths, selected from everything Atlas could have offered. *Owns it:* Atlas owns the graph and every edge in it, indefinitely. Janus owns the *selection* of which paths matter for a given question — selection is Janus's responsibility, not something Atlas does on Janus's behalf, exactly as `05-ATLAS.md` Section 7 already insisted.

**Janus → Titan**
*Enters:* a qualified Reasoning Path. *Leaves:* a complete Reasoning Artifact — observation, evidence, inference, conclusion, confidence, assumptions, and falsifiability condition, per `06-JANUS.md` Section 6. *Owns it:* Janus owns the Reasoning Artifact's content permanently; once it's handed to Titan, Titan may evaluate it, accept it, or reject it, but it may not edit the reasoning inside it. A Titan that rewrites a Reasoning Chain to make a Blind Spot look stronger has stopped being Titan and started being a second Janus with worse incentives.

**Titan → Output**
*Enters:* a Reasoning Artifact, evaluated against Titan's qualification criteria (`03-BLIND-SPOT-FRAMEWORK.md`, Section 7 — Titan is the operational execution of that section, not a new qualification framework invented here). *Leaves:* a qualified Blind Spot, with its full Reasoning Artifact still attached for the Output layer to render. *Owns it:* Titan owns the decision of whether something is worth surfacing. The Output layer owns presentation only — it may format, visualize, or summarize, but the artifact it's presenting is not its own to alter.

One property holds across every hop above, deliberately: ownership of an artifact's *content* never transfers backward. Atlas can be wrong and need correction, but Janus correcting it directly rather than flagging it back would be ownership creep, the same failure mode each prior document spent a full section preventing within its own walls.

---

## 6. Module Boundaries

Four rules, stated as invariants rather than qualification criteria — these aren't tested per-instance the way a Dimension or a Relationship is. They're constraints the system must never violate, full stop.

**Finance DNA never modifies Atlas.** Finance DNA may be *read* by Atlas, as the source of one endpoint's Dimensions. It never writes to the graph, adds a node, or asserts a relationship — doing so would let Identity quietly decide Relationships, collapsing the distinction Atlas's entire existence depends on.

**Atlas never creates Blind Spots.** This is restated directly from `05-ATLAS.md` Section 8 — Atlas does not predict, rank, recommend, or infer. A Blind Spot requires qualification (Titan's job) built on reasoning (Janus's job). Atlas producing one directly would mean Atlas silently absorbed two other modules' responsibilities at once.

**Janus never creates Dimensions.** Janus consumes Finance DNA's qualified Dimensions and Atlas's qualified Reasoning Paths; it does not invent a new Dimension mid-reasoning because the existing ones don't quite support the conclusion it's reaching for. An inference that needs a Dimension that doesn't exist is a sign the inference isn't valid yet — not a justification for Janus quietly extending Finance DNA's vocabulary on the fly.

**Titan never changes Reasoning Chains.** Titan qualifies or rejects the Reasoning Artifact it receives. It does not edit the chain to strengthen a borderline case, and it does not silently drop a weak step to make the Confidence Layer look better. Titan's qualification decision has to be a judgment about what Janus actually produced, not about an edited version of it.

These four rules share a shape: each one names a specific temptation — the shortcut that would make the system "work better" in some narrow sense by quietly letting one module reach into another's responsibility. Every one of them is a temptation that gets stronger, not weaker, once real code and real deadlines exist. That's exactly why they're written down here, before either does.

---

## 7. Future Architecture

The test for this document was never "does this describe Hyperion today." It's whether Hyperion Version 5 — with modules that don't exist yet — still fits inside this same shape.

A new module earns a place in the pipeline the same way `belongs_to` earned a place in an already-frozen section of Atlas: by satisfying the existing rules, not by getting the rules bent around it. Concretely, any future module must:

- Own exactly one responsibility, statable in one sentence, the way Finance DNA owns Identity and Titan owns Qualification.
- Produce exactly one named artifact, the way every module in Section 3 already does, and accept only already-named artifacts from the modules before it.
- Be insertable into the System Flow diagram in Section 4 as a single new hop, without requiring an existing hop to be rewired around it.
- Come with its own "Never" column before it's allowed to ship — the same restraint every module before it had to commit to in writing first.

This is also where the Conceptual/Engineering split from Section 1 pays for itself: a future module's conceptual responsibility gets defined the way Finance DNA, Atlas, Janus, and Titan were — in a document like this one's predecessors, asking *what* before *how*. Architecture only ever adds the *how*, after that conceptual work is already done. A module that skips straight to an engineering design, without first being qualified the way every existing module was, hasn't earned a place in this diagram yet, regardless of how useful it looks.

---

## 8. Open Questions

Recorded, not answered — the same discipline every prior document held to at this stage.

- Should Titan be allowed to request an additional Reasoning Path from Janus when the first one it receives doesn't meet qualification, or does the pipeline stay strictly one-directional, with a rejected candidate simply ending there?
- How should a partial failure propagate — for instance, an Asset that Ingestion resolves but that Finance DNA cannot fully qualify? Does it enter Atlas with incomplete Dimensions, or does it wait?
- Should each artifact crossing a module boundary (Section 5) eventually carry an explicit version number, so that a Reasoning Artifact built against an older Atlas graph can be distinguished from one built against a newer one?
- When a future module is added per Section 7, who decides whether it's genuinely a new responsibility or a responsibility that already belongs to an existing module — is that judgment call governed by anything more specific than "one sentence, one artifact"?
- Does Explainability's guarantee (Section 2) need to extend to the Ingestion and Output layers as formally as it applies to the four reasoning modules, or are those two layers held to a different standard since they don't themselves reason about anything?

---

## Revision History

| Version | Date | Summary |
|---|---|---|
| 1.0 | 28 June 2026 | Initial release. Sections 1–8 complete. |
