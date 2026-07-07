# Contributing to Hyperion

Thank you for your interest. Hyperion is a deterministic financial reasoning engine. Every contribution should make it more accurate, more knowledgeable, or easier to use — without compromising the architectural discipline that makes it trustworthy.

---

## The most valuable contributions (no engine knowledge required)

### Add a company to the registry

Edit `datasets/assets.csv`. Add one row following the existing format:

```
id,ticker,name,sector,industry,aliases
your-company,TICK,Full Legal Name,Sector,Industry,alias1;alias2
```

Rules:
- `id` must be a stable, lowercase slug (e.g. `samsung-electronics`). **IDs are permanent and never reused.**
- `ticker` must be the primary exchange ticker.
- `aliases` are semicolon-separated alternative names (common abbreviations, former names).
- `sector` and `industry` must match an existing Finance DNA scoring table entry or add a new fallback score — see `backend/finance_dna/rules.py` and `backend/finance_dna/SCORING-RATIONALE.md`.

### Add a context node to Atlas

Edit `datasets/atlas/context_nodes.csv`:

```
id,node_class,label
taiwan-strait-risk,MACRO_FACTOR,Taiwan Strait Military Risk
```

Valid `node_class` values: `GEOGRAPHY`, `MACRO_FACTOR`, `INDUSTRY`, `COMMODITY`, `CURRENCY`, `REGULATION`, `ECONOMIC_EVENT`.

### Add a relationship to Atlas

Edit `datasets/atlas/seed_relationships.csv`. Add one row:

```
source_id,target_id,relationship_type,directionality,temporality,cardinality,evidence_source,confidence,evidence
apple-inc,taiwan-strait-risk,EXPOSED_TO,DIRECTED,PERSISTENT,ONE_TO_MANY,PUBLIC_RECORD,0.80,Apple earns ~19% revenue from Greater China per 2024 10-K
```

Every relationship **must** have evidence. A relationship without a verifiable source does not belong in Atlas.

Valid `relationship_type` values: `DEPENDS_ON_SUPPLIES`, `COMPETES_WITH`, `SELLS_TO`, `EXPORTS_TO`, `LOCATED_IN`, `EXPOSED_TO`, `AFFECTED_BY`, `REGULATED_BY`, `BELONGS_TO`.

---

## Adding a Finance DNA dimension

This is a more involved contribution. Every new dimension must:

1. Earn its existence against the five criteria in `docs/04-FINANCE-DNA.md §2`
2. Have a `DimensionDefinition` added to `backend/finance_dna/dimensions.py`
3. Have scoring tables (sector/industry → score) added to `backend/finance_dna/rules.py`
4. Have a human rationale for every score added to `backend/finance_dna/SCORING-RATIONALE.md`
5. Be registered in `backend/finance_dna/registry.py`
6. Have unit tests covering all 7 fixture assets

---

## Quality gate (run before opening a PR)

```bash
uv run ruff check backend/   # must pass clean
uv run mypy backend           # must pass clean (--strict)
uv run pytest -q              # all tests must pass
```

The CI pipeline runs the same three commands automatically.

---

## What not to contribute (yet)

- Changes to the reasoning engine (Janus, Titan) — these are architecturally frozen. See `docs/ENGINE-STABILITY.md`.
- AI, LLM, or probabilistic components — these belong in Version 1.0.
- New API endpoints — the V0.1 API surface is frozen at `/v1/analyze` and `/v1/health`.
- Frontend code — out of scope until Milestone visualization work begins.

If you're unsure whether a contribution fits, open an issue first.

---

## Commit style

```
feat: add Samsung Electronics to asset registry
fix: correct TSMC sector fallback score
docs: add debt sensitivity to SCORING-RATIONALE
test: verify geographic concentration for Alphabet
```

One logical change per commit. Reference the relevant pillar (Knowledge, Interface, Developer Experience) in the PR description.
