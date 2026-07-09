# Knowledge Registry

**Version:** 0.2
**Status:** Active
**Updated:** July 2026

The single source of truth for Hyperion's knowledge state. Every Finance DNA
dimension, Atlas node, and benchmark case is registered here with its current
status, evidence level, and benchmark linkage.

Run `uv run python scripts/knowledge_report.py` to verify this registry
against the actual codebase.

---

## Finance DNA — 15 Dimensions

### Market Structure (V0.2)

| Dimension | Approximation | Primary Benchmark | Status |
|-----------|--------------|-------------------|--------|
| Pricing Power | B — Industry | Commodity Shock (`nestle_coffee`) | ✅ Implemented |
| Customer Concentration | B — Industry | Customer Concentration (planned) | ✅ Implemented |
| Supplier Concentration | B — Industry | Supplier Concentration (planned) | ✅ Implemented |

### Financial Structure (V0.2)

| Dimension | Approximation | Primary Benchmark | Status |
|-----------|--------------|-------------------|--------|
| Revenue Diversification | B — Industry | Multiple patterns (confidence modulator) | ✅ Implemented |
| Debt Sensitivity | B — Industry | Interest Rate Sensitivity (planned) | ✅ Implemented |
| Currency Exposure | B — Industry | Currency Exposure (planned) | ✅ Implemented |

### Operational Structure (V0.2)

| Dimension | Approximation | Primary Benchmark | Status |
|-----------|--------------|-------------------|--------|
| Energy Dependency | B — Industry | Energy Dependency (planned) | ✅ Implemented |
| Labour Intensity | B — Industry | Labour Exposure (planned) | ✅ Implemented |
| Regulatory Compliance Cost | B — Industry | Regulatory Risk (`nvidia_export_controls`) | ✅ Implemented |

### Business Structure (V0.1)

| Dimension | Approximation | Primary Benchmark | Status |
|-----------|--------------|-------------------|--------|
| Capital Intensity | C — Sector | Supply Chain Risk (`apple_taiwan`) | ✅ Implemented |
| Supply Chain Complexity | C — Sector | Supply Chain Risk (`apple_taiwan`) | ✅ Implemented |

### Revenue Structure (V0.1)

| Dimension | Approximation | Primary Benchmark | Status |
|-----------|--------------|-------------------|--------|
| Geographic Revenue Concentration | C — Sector | Geopolitical Risk (planned) | ✅ Implemented |

### Macroeconomic & Regulatory Sensitivity (V0.1)

| Dimension | Approximation | Primary Benchmark | Status |
|-----------|--------------|-------------------|--------|
| Commodity Input Exposure | C — Sector | Commodity Shock (`nestle_coffee`) | ✅ Implemented |
| Regulatory Exposure | C — Sector | Regulatory Risk (`nvidia_export_controls`) | ✅ Implemented |

### Innovation & Technology (V0.1)

| Dimension | Approximation | Primary Benchmark | Status |
|-----------|--------------|-------------------|--------|
| Innovation Intensity | C — Sector | (general intelligence dimension) | ✅ Implemented |

**Totals:** 15 dimensions — Level A: 0 | Level B: 9 | Level C: 6

---

## Atlas — Asset Registry

7 companies registered in `datasets/assets.csv`.

| Company | ID | Sector | Industry | Benchmarks |
|---------|-----|--------|----------|------------|
| Apple Inc. | `apple-inc` | Technology | Consumer Electronics | `apple_taiwan` |
| Microsoft Corporation | `microsoft` | Technology | Software | planned cases |
| NVIDIA Corporation | `nvidia` | Technology | Semiconductors | `nvidia_export_controls` |
| Taiwan Semiconductor Mfg. | `tsmc` | Technology | Semiconductors | `apple_taiwan` |
| Amazon.com Inc. | `amazon` | Consumer Discretionary | E-Commerce & Cloud Services | planned cases |
| Alphabet Inc. | `alphabet` | Technology | Internet Services | planned cases |
| Nestlé S.A. | `nestle` | Consumer Staples | Food & Beverages | `nestle_coffee` |

---

## Atlas — Context Node Registry

14 context nodes registered in `datasets/atlas/context_nodes.csv`.

### Geography Nodes

| Node ID | Label | Relationships | Benchmark |
|---------|-------|---------------|-----------|
| `taiwan` | Taiwan | LOCATED_IN (from TSMC) | `apple_taiwan` |
| `brazil` | Brazil | LOCATED_IN (from coffee) | `nestle_coffee` |
| `china` | China | SELLS_TO (from NVIDIA) | `nvidia_export_controls` |

### Commodity Nodes

| Node ID | Label | Relationships | Benchmark |
|---------|-------|---------------|-----------|
| `coffee` | Coffee (Arabica & Robusta) | EXPOSED_TO (from Nestlé), LOCATED_IN (to Brazil) | `nestle_coffee` |

### Macro Factor Nodes

| Node ID | Label | Relationships | Benchmark |
|---------|-------|---------------|-----------|
| `geopolitical-risk-taiwan` | Taiwan Geopolitical Risk | AFFECTED_BY (from Taiwan) | `apple_taiwan` |
| `semiconductor-export-ban` | US-China Semiconductor Export Controls | AFFECTED_BY (from China) | `nvidia_export_controls` |
| `brazil-climate-risk` | Brazil Agricultural Climate Risk | AFFECTED_BY (from Brazil) | `nestle_coffee` |
| `us-fed-rate` | US Federal Reserve Interest Rate Policy | AFFECTED_BY (from Microsoft — low confidence) | planned |
| `eu-digital-regulation` | EU Digital Markets Act & AI Act | AFFECTED_BY (from Alphabet) | planned |

### Industry Nodes

| Node ID | Label | Relationships | Benchmark |
|---------|-------|---------------|-----------|
| `semiconductor-industry` | Semiconductors | BELONGS_TO (from Apple, NVIDIA, TSMC) | — |
| `software-industry` | Software | BELONGS_TO (from Microsoft) | — |
| `internet-services-industry` | Internet Services | BELONGS_TO (from Alphabet) | — |
| `ecommerce-cloud-industry` | E-Commerce & Cloud Services | BELONGS_TO (from Amazon) | — |
| `food-beverages-industry` | Food & Beverages | BELONGS_TO (from Nestlé) | — |

**Total: 14 context nodes — 3 Geography | 1 Commodity | 5 Macro Factor | 5 Industry**

---

## Atlas — Relationship Registry

19 relationships in `datasets/atlas/seed_relationships.csv`.

### Supply Chain Relationships

| Source | Type | Target | Confidence | Evidence Level | Benchmark |
|--------|------|--------|------------|----------------|-----------|
| `apple-inc` | DEPENDS_ON_SUPPLIES | `tsmc` | 0.95 | DISCLOSED | `apple_taiwan` |
| `nvidia` | DEPENDS_ON_SUPPLIES | `tsmc` | 0.90 | DISCLOSED | — |
| `tsmc` | LOCATED_IN | `taiwan` | 1.00 | PUBLIC_RECORD | `apple_taiwan` |
| `taiwan` | AFFECTED_BY | `geopolitical-risk-taiwan` | 0.85 | PUBLIC_RECORD | `apple_taiwan` |

### Commodity Relationships

| Source | Type | Target | Confidence | Evidence Level | Benchmark |
|--------|------|--------|------------|----------------|-----------|
| `nestle` | EXPOSED_TO | `coffee` | 0.95 | PUBLIC_RECORD | `nestle_coffee` |
| `coffee` | LOCATED_IN | `brazil` | 0.90 | PUBLIC_RECORD | `nestle_coffee` |
| `brazil` | AFFECTED_BY | `brazil-climate-risk` | 0.85 | PUBLIC_RECORD | `nestle_coffee` |

### Regulatory / Geopolitical Relationships

| Source | Type | Target | Confidence | Evidence Level | Benchmark |
|--------|------|--------|------------|----------------|-----------|
| `nvidia` | SELLS_TO | `china` | 0.90 | DISCLOSED | `nvidia_export_controls` |
| `china` | AFFECTED_BY | `semiconductor-export-ban` | 0.90 | PUBLIC_RECORD | `nvidia_export_controls` |
| `alphabet` | AFFECTED_BY | `eu-digital-regulation` | 0.90 | PUBLIC_RECORD | planned |
| `microsoft` | AFFECTED_BY | `us-fed-rate` | 0.35 | DERIVED | planned |
| `amazon` | SELLS_TO | `china` | 0.65 | PUBLIC_RECORD | — |

### Industry Classification Relationships

| Source | Type | Target | Confidence | Benchmark |
|--------|------|--------|------------|-----------|
| `apple-inc` | BELONGS_TO | `semiconductor-industry` | 0.90 | — |
| `nvidia` | BELONGS_TO | `semiconductor-industry` | 1.00 | — |
| `tsmc` | BELONGS_TO | `semiconductor-industry` | 1.00 | — |
| `microsoft` | BELONGS_TO | `software-industry` | 1.00 | — |
| `alphabet` | BELONGS_TO | `internet-services-industry` | 1.00 | — |
| `amazon` | BELONGS_TO | `ecommerce-cloud-industry` | 1.00 | — |
| `nestle` | BELONGS_TO | `food-beverages-industry` | 1.00 | — |

---

## Benchmark Registry

3 cases in `benchmarks/canonical_cases/`.

| Case ID | Pattern | State | Company | Confidence | Path Length |
|---------|---------|-------|---------|------------|-------------|
| `apple_taiwan` | Supply Chain Risk | ✅ Implemented | Apple | 0.8075 | 3 steps |
| `nvidia_export_controls` | Regulatory Risk | ✅ Implemented | NVIDIA | 0.8100 | 2 steps |
| `nestle_coffee` | Commodity Shock | ✅ Implemented | Nestlé | 0.7268 | 3 steps |

**Pattern coverage: 3 / 10**

Planned cases (not yet in `canonical_cases/`):
- `apple_china_revenue` — Currency Exposure
- `alphabet_eu_regulation` — Geopolitical Risk
- `amazon_energy` — Energy Dependency
- `qualcomm_apple_concentration` — Customer Concentration
- `microsoft_interest_rate` — Interest Rate Sensitivity

---

## Integrity Status

Last verified by `scripts/lint_atlas.py`:

| Check | Status |
|-------|--------|
| Duplicate assets | ✅ Clean |
| Duplicate context nodes | ✅ Clean |
| Duplicate relationships | ✅ Clean |
| Broken references | ✅ Clean |
| Orphaned context nodes | ✅ Clean |
| Missing evidence | ✅ Clean |
| Confidence range | ✅ Clean |

---

## What is missing

The honest answer to "what does Hyperion not yet know?"

**Finance DNA:** All 15 dimensions are implemented but at Level B or C approximation. No Level A (company-specific) scores exist yet. Level A requires automated SEC filing ingestion (Version 0.4).

**Atlas nodes not yet added:**
- ASML (EUV lithography sole-source supplier)
- Foxconn (Apple contract manufacturing)
- Samsung Electronics, SK Hynix (memory suppliers)
- CNY/USD currency risk macro factor
- Grid instability macro factor
- Minimum wage regulation nodes

**Patterns with no current benchmark:**
- Geopolitical Risk (distinct from Supply Chain — direct political event)
- Currency Exposure
- Interest Rate Sensitivity
- Customer Concentration
- Supplier Concentration
- Energy Dependency
- Labour Exposure

These define the Version 0.2 remaining roadmap.
