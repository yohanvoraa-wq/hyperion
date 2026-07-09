# Finance DNA — Scoring Rationale

**Version:** 0.1
**Status:** Active
**Applies to:** `backend/finance_dna/rules.py`

This document records the human reasoning behind every number in the V0.1
scoring tables. It exists so that six months from now, a contributor reading
`0.85` in a lookup table can understand *why it is 0.85*, not just that it is.

All V0.1 scores are **sector-level approximations**. They are informed
by publicly observable industry characteristics, not by company-specific
financial filings. Company-specific data (disclosed PP&E/Revenue, R&D spend,
geographic revenue breakdowns) will replace these approximations in future
milestones when Ingestion is extended to load financial statements.

Score range: 0.0 (negligible) → 1.0 (maximum exposure / intensity).

---

## Capital Intensity

*How much fixed capital the business requires relative to output.*

| Sector | Industry | Score | Rationale |
|---|---|---|---|
| Technology | Semiconductors | 0.85 | Fab construction and lithography equipment represent 20–35% of revenue in capex for leading foundries (TSMC, Intel). A single advanced fab costs $10–20B+. |
| Technology | Software | 0.20 | Software companies are almost entirely IP-based. PP&E/Revenue is typically 2–5%. Physical assets are data centres, leased. |
| Technology | Consumer Electronics | 0.55 | Apple-style companies outsource manufacturing (low owned capex) but carry significant IP infrastructure and R&D capital. Mid-range. |
| Technology | Internet Services | 0.35 | Data centres require meaningful capex, but the business model is software-driven. Google/Meta: capex/revenue ~12–18%. |
| Consumer Discretionary | E-Commerce & Cloud Services | 0.50 | Amazon's fulfilment network and AWS infrastructure are genuinely capital-heavy, offset by the software/marketplace segments. |
| Consumer Staples | Food & Beverages | 0.60 | Nestlé, Unilever: factories, processing equipment, cold chains. Capex/Revenue ~3–5% annually but accumulated asset base is large relative to software. |

**Fallbacks** (industry not matched):
- Technology: 0.45 (mid-range assumption for unmapped sub-industries)
- Consumer Discretionary: 0.45
- Consumer Staples: 0.58

---

## Commodity Input Exposure

*Degree to which costs are tied to commodity prices.*

| Sector | Industry | Score | Rationale |
|---|---|---|---|
| Technology | Semiconductors | 0.90 | Silicon wafers, specialty gases (NF₃, HCl, WF₆), copper interconnects, rare earth elements for photolithography chemicals. Among the highest commodity exposure of any industry. |
| Technology | Software | 0.05 | Near-zero direct commodity inputs. Energy for offices is the main exposure — minor relative to labour costs. |
| Technology | Consumer Electronics | 0.65 | Aluminium casings, copper, lithium (batteries), rare earths for magnets and displays, cobalt. Supply tied to Congo, Chile, China. |
| Technology | Internet Services | 0.15 | Energy (for data centres) and some hardware components. Primarily exposure through electricity prices. |
| Consumer Discretionary | E-Commerce & Cloud Services | 0.30 | Packaging (cardboard, plastic), energy (fulfilment centres, delivery). AWS insulates partially. |
| Consumer Staples | Food & Beverages | 0.85 | Coffee, cocoa, wheat, palm oil, dairy — direct agricultural commodity inputs form the primary cost structure. Weather, geography, and seasonality all directly affect margins. |

**Fallbacks:**
- Technology: 0.40
- Consumer Discretionary: 0.30
- Consumer Staples: 0.75

---

## Supply Chain Complexity

*Degree of multi-tier, global supply chain involvement.*

| Sector | Industry | Score | Rationale |
|---|---|---|---|
| Technology | Semiconductors | 0.95 | Arguably the most complex supply chain on earth. A single chip involves 50+ countries, 1,000+ suppliers across multiple tiers. TSMC itself is a critical single point of the global supply graph. |
| Technology | Software | 0.10 | Minimal physical supply chain. Cloud infrastructure is leased; the product is distributed digitally. |
| Technology | Consumer Electronics | 0.85 | Apple's supply chain spans 200+ suppliers across 43 countries. Assembly is concentrated in Asia with raw material sourcing globally distributed. |
| Technology | Internet Services | 0.30 | Server hardware procurement has moderate complexity; the product delivery chain is digital. |
| Consumer Discretionary | E-Commerce & Cloud Services | 0.70 | Amazon operates a vast physical logistics network with millions of suppliers. Third-party seller complexity adds further tiers. |
| Consumer Staples | Food & Beverages | 0.65 | Agricultural sourcing, processing, packaging, cold chain distribution. Global but somewhat more stable than electronics. |

**Fallbacks:**
- Technology: 0.50
- Consumer Discretionary: 0.65
- Consumer Staples: 0.60

---

## Innovation Intensity

*R&D spend as a proportion of revenue; forward-looking competitive posture.*

| Sector | Industry | Score | Rationale |
|---|---|---|---|
| Technology | Semiconductors | 0.85 | Process node advancement (3nm → 2nm → 1nm) requires sustained R&D investment. TSMC, NVIDIA, Qualcomm: R&D/Revenue ~15–25%. |
| Technology | Software | 0.80 | Continuous product development, security patching, AI integration. Microsoft: R&D/Revenue ~12–14%. |
| Technology | Consumer Electronics | 0.75 | Apple: R&D/Revenue ~6–8%, but absolute spend is enormous ($25B+). Device + software + silicon R&D. |
| Technology | Internet Services | 0.85 | AI infrastructure, search quality, advertising technology, hardware (Pixel, Quest). Alphabet: R&D/Revenue ~15%. |
| Consumer Discretionary | E-Commerce & Cloud Services | 0.70 | AWS service development, logistics robotics, Alexa, Project Kuiper. Amazon: R&D/Revenue ~14%. |
| Consumer Staples | Food & Beverages | 0.20 | Incremental product reformulation and packaging. R&D/Revenue typically 1–2%. Not a competitive differentiator. |

**Fallbacks:**
- Technology: 0.80
- Consumer Discretionary: 0.55
- Consumer Staples: 0.20

---

## Regulatory Exposure

*Degree and intensity of regulatory oversight affecting operations.*

| Sector | Industry | Score | Rationale |
|---|---|---|---|
| Technology | Semiconductors | 0.60 | Export control (CHIPS Act, BIS Entity List), ITAR, trade restrictions on advanced chip technology to China. Taiwan geopolitical risk adds regulatory uncertainty. |
| Technology | Software | 0.65 | GDPR, CCPA, AI Act (EU), antitrust scrutiny of platform dominance, cybersecurity disclosure rules (SEC). Rising trajectory. |
| Technology | Consumer Electronics | 0.55 | FCC approvals, product safety certifications, right-to-repair legislation, trade tariffs (Section 301). |
| Technology | Internet Services | 0.80 | Antitrust investigations (EU DMA, US DOJ), data privacy (GDPR), content moderation liability, AI regulation, digital markets regulation. Highest in the sector. |
| Consumer Discretionary | E-Commerce & Cloud Services | 0.65 | FTC antitrust scrutiny, EU Digital Markets Act, labour regulations for delivery/warehouse workers, consumer protection rules. |
| Consumer Staples | Food & Beverages | 0.70 | FDA, EFSA food safety, nutritional labelling, advertising restrictions (especially to children), environmental packaging rules, supply chain sustainability disclosures. |

**Fallbacks:**
- Technology: 0.60
- Consumer Discretionary: 0.60
- Consumer Staples: 0.65

---

## Geographic Revenue Concentration

*Degree of revenue concentration in one geography. Lower score = more diversified.*

| Sector | Industry | Score | Rationale |
|---|---|---|---|
| Technology | Semiconductors | 0.60 | Revenue is globally distributed (chip demand is global), but the supply chain is highly Taiwan-concentrated. The score reflects *systemic* geographic risk, not just revenue geography. |
| Technology | Software | 0.35 | Global distribution of software products. Microsoft: Americas ~50%, Europe ~25%, Asia ~25%. Reasonably diversified. |
| Technology | Consumer Electronics | 0.45 | Apple: Americas ~44%, Europe ~24%, Greater China ~19%, Rest ~13%. Some China concentration. |
| Technology | Internet Services | 0.35 | Alphabet/Meta: global ad markets. Revenue correlates with global internet penetration rather than any single geography. |
| Consumer Discretionary | E-Commerce & Cloud Services | 0.55 | Amazon: US-heavy (~60% of revenue). AWS is more globally distributed. Net: moderate concentration. |
| Consumer Staples | Food & Beverages | 0.45 | Nestlé: widely global with regional category variation. Some product categories are regionally concentrated. |

**Fallbacks:**
- Technology: 0.45
- Consumer Discretionary: 0.50
- Consumer Staples: 0.45

---

## Version History

| Version | Date | Change |
|---|---|---|
| 0.1 | 28 June 2026 | Initial six dimensions, sector-level approximations. |

---

*When company-specific financial data is available, these tables will be
superseded by per-company calculations. At that point, `evidence_source`
will change from `DERIVED` to `DISCLOSED` and `primitive` will be `True`
for direct calculations.*

---

---

# Finance DNA — Scoring Rationale Extension

**Version:** 0.2
**Extends:** V0.1 above
**Approximation Level:** All V0.2 scores are **Level B — Industry Approximation** unless noted.
**Confidence modifier applied at evaluation time:** Level B × 0.85

> **V0.1 retrospective note:** The six V0.1 dimensions were scored at Level C (sector approximation)
> by today's classification. They will be retroactively tagged Level C in the Dimension model
> during Session 3 implementation. This does not change any score values — only adds transparency.

> **Future work — Evidence Maturity:** Approximation Level measures *how* a score was derived
> (company data vs industry vs sector). A separate concept, Evidence Maturity, will eventually
> measure *how strong the supporting evidence is* (audited filing vs company presentation vs
> industry report vs expert estimate vs hypothesis). Evidence Maturity is a Version 0.3 concept.
> It is noted here so the distinction is not confused with Approximation Level.

**Rule:** Every score in this document must have a written rationale before it appears in
`rules.py`. This rule is permanent.

---

## Pricing Power

**Purpose:** Measures whether a company can raise prices without proportional loss of volume.
Critical for understanding how a company absorbs commodity shocks, energy price spikes,
and labour cost inflation. A HIGH pricing power company survives cost shocks that a LOW
company cannot — the excess cost either passes through to customers or compresses margins
by the full amount of the shock.

**Benchmark linkage:** Commodity Shock (nestle_coffee), Energy Dependency, Labour Exposure.
Pricing Power modulates the severity of any cost-side blind spot.

**Approximation Level:** B (Industry) — market structure characteristics are well-documented
at the industry level. Company-level pricing data (realised price increases vs volume impact)
requires Level A (company filings).

*Degree to which a company can raise prices without proportional loss of volume.*

| Sector | Industry | Score | Rationale |
|--------|----------|-------|-----------|
| Technology | Semiconductors | 0.85 | TSMC raised wafer prices 3–6% in 2022 with no meaningful customer defection — no alternative foundry exists for leading-edge nodes. NVIDIA priced H100 at $25,000–40,000 with 8+ month waitlists. Advanced semiconductor pricing is set by capability, not competition. |
| Technology | Software | 0.85 | Enterprise software has among the highest pricing power of any industry. Switching costs (data migration, workflow disruption, retraining) make customers highly price-inelastic. Microsoft raised Microsoft 365 prices 15–25% in 2022; churn was negligible. |
| Technology | Consumer Electronics | 0.60 | Apple raised iPhone prices consistently but faces substitution from Android at extreme price points. Brand and ecosystem lock-in provide strong but bounded pricing power. Average selling price has risen from ~$694 (2016) to ~$988 (2023). |
| Technology | Internet Services | 0.75 | Google Search and YouTube Ads command premium CPMs because advertisers have no comparable alternative for search intent targeting at scale. Some pricing power limits from advertiser budget constraints and social media competition. |
| Consumer Discretionary | E-Commerce & Cloud Services | 0.65 | AWS pricing power is high (cloud switching costs are substantial). Amazon Prime has been raised from $79 to $139 without meaningful churn. Retail marketplace is more competitive; blended score reflects the business mix. |
| Consumer Staples | Food & Beverages | 0.50 | Nestlé raised prices 9.8% in 2022; organic volume fell 2.2% — net revenue positive but with real volume loss. Brand provides partial pricing power but private label competition and retailer leverage create a ceiling. |

**Fallbacks:**
- Technology: 0.70 (technology businesses generally have above-average pricing power)
- Consumer Discretionary: 0.55
- Consumer Staples: 0.45 (branded goods: partial pricing power, consumer elasticity limits)

**Known limitations:** Industry-level scores mask significant intra-industry variation.
Qualcomm (semiconductor, fabless) has lower pricing power than NVIDIA because it faces
direct competition from MediaTek. A Level A score would distinguish these.

**Future Level A data:** Realised price increase vs volume impact from earnings calls and
annual reports. Gross margin trend over 5 years is a reliable proxy for pricing power.

---

## Customer Concentration

**Purpose:** Measures revenue dependence on a small number of customers. High concentration
creates binary risk: a single customer's decision to reduce orders, switch suppliers, or
in-source can impair revenue without warning. This is a demand-side fragility metric —
distinct from supply-side fragility (Supplier Concentration).

**Benchmark linkage:** Customer Concentration pattern. Required for planned case:
qualcomm_apple_concentration.

**Approximation Level:** B (Industry) — B2B vs B2C structure is well-documented and reliably
predicts concentration. Company-specific customer breakdowns require Level A (10-K disclosures).

*Degree to which revenue is concentrated in a small number of customers.*

| Sector | Industry | Score | Rationale |
|--------|----------|-------|-----------|
| Technology | Semiconductors | 0.70 | TSMC: Apple (~26%), NVIDIA (~11%), AMD, Intel, Qualcomm are large customers. NVIDIA: hyperscalers (Microsoft, Google, Amazon, Meta) dominate data center revenue. High concentration is structural for foundry and GPU businesses. |
| Technology | Software | 0.25 | Microsoft serves hundreds of millions of consumers and hundreds of thousands of enterprise customers. No single customer is material. Azure's hyperscale customers are significant but Azure revenue is diversified. |
| Technology | Consumer Electronics | 0.15 | Apple sells to hundreds of millions of individual consumers globally. No single customer approaches materiality. Channel (carriers, retailers) concentration is present but manageable. |
| Technology | Internet Services | 0.20 | Alphabet's advertising revenue comes from millions of advertisers across millions of keywords. No single advertiser approaches 1% of revenue. Enterprise Google Cloud is more concentrated but remains a minority of revenue. |
| Consumer Discretionary | E-Commerce & Cloud Services | 0.30 | AWS: some hyperscale customer concentration (though no single customer is disclosed as >10%). Amazon marketplace revenue is highly distributed. Retail concentration through major sellers, not buyers. |
| Consumer Staples | Food & Beverages | 0.40 | Retail channel concentration is the primary risk. Walmart is estimated at 10–15% of Nestlé US revenue; other major retailers add further concentration. Global diversification moderates the overall score. |

**Fallbacks:**
- Technology: 0.40 (B2B technology has inherent customer concentration)
- Consumer Discretionary: 0.30
- Consumer Staples: 0.40 (retail channel concentration is systemic)

**Known limitations:** Industry scores cannot capture company-specific concentration.
Qualcomm (Semiconductors) has Apple at ~20–25% of revenue — far higher than the industry
average would suggest. Level A scores are critical for this dimension.

**Future Level A data:** 10-K customer concentration disclosures (required when >10% of
revenue from a single customer). Earnings call commentary on major customer dependency.

---

## Supplier Concentration

**Purpose:** Measures supply chain fragility through single-source or concentrated sourcing.
High concentration means a disruption at one supplier — natural disaster, geopolitical event,
labour action, or financial distress — can halt production entirely. Extends Supply Chain
Complexity (which measures breadth) with a directional fragility measure.

**Benchmark linkage:** Supplier Concentration pattern. Directly supports apple_taiwan
(TSMC as near-sole-source supplier for Apple Silicon) and nvidia_export_controls
(TSMC as sole advanced-node manufacturer for NVIDIA GPUs).

**Approximation Level:** B (Industry)

*Degree to which the supply chain depends on a small number of critical suppliers.*

| Sector | Industry | Score | Rationale |
|--------|----------|-------|-----------|
| Technology | Semiconductors | 0.90 | ASML is the sole supplier of EUV lithography equipment globally — no alternative exists. TSMC itself is the sole or primary source for leading-edge chips for Apple, NVIDIA, AMD, and Qualcomm. The semiconductor supply chain has among the highest supplier concentration of any industry. |
| Technology | Software | 0.10 | Cloud infrastructure has multiple providers (AWS, Azure, GCP). Open-source dependencies have many contributors. No physical supply chain creates meaningful concentration risk. |
| Technology | Consumer Electronics | 0.80 | Apple depends on TSMC for Apple Silicon (sole-source), LG/Samsung for OLED displays (concentrated), and specific camera sensor suppliers. 2022 TSMC Arizona announcement acknowledges the concentration risk explicitly. |
| Technology | Internet Services | 0.25 | Server hardware from multiple vendors (Dell, HPE, custom). Software dependencies are internal or open-source with many contributors. No single external supplier is critical. |
| Consumer Discretionary | E-Commerce & Cloud Services | 0.40 | Amazon's product supply base is highly distributed across millions of third-party sellers. AWS hardware is more concentrated (custom silicon from TSMC). Logistics fleet diversified. |
| Consumer Staples | Food & Beverages | 0.55 | Agricultural commodity sourcing is geographically concentrated (Brazilian coffee, West African cocoa, Indonesian palm oil). Within each commodity, multiple farmers/traders provide some supplier diversification. |

**Fallbacks:**
- Technology: 0.55 (technology businesses frequently have specialised supplier dependencies)
- Consumer Discretionary: 0.40
- Consumer Staples: 0.50 (commodity sourcing concentration is common)

**Known limitations:** The score cannot capture the severity of a specific single-source
dependency without Level A data. Knowing that Supplier Concentration is HIGH for
Semiconductors does not tell us that ASML has zero substitutes — that requires Atlas.

**Future Level A data:** Supplier risk disclosures in 10-K filings. Apple explicitly names
TSMC and other critical suppliers in its risk factors section.

---

## Revenue Diversification

**Purpose:** Measures the degree to which revenue is distributed across multiple products,
geographies, and customer segments. Low diversification means financial performance is
highly correlated with a single market, product cycle, or demand shock. Acts as a
confidence modulator: a LOW revenue diversification score amplifies the severity of
any single-pattern blind spot.

**Benchmark linkage:** Modulates confidence across all patterns. A company with LOW
revenue diversification has less ability to absorb a blind spot in any single area.

**Approximation Level:** B (Industry) — business model structure is well-documented.
Geographic revenue breakdown requires Level A.

*Degree to which revenue is distributed across products, geographies, and customer segments.*

| Sector | Industry | Score | Rationale |
|--------|----------|-------|-----------|
| Technology | Semiconductors | 0.30 | NVIDIA: Data Center (~87% of revenue in FY2024) is highly concentrated in AI infrastructure. TSMC: concentrated in leading-edge foundry services. Single-segment dominance is structural for specialists. |
| Technology | Software | 0.65 | Microsoft: Intelligent Cloud (Azure), Productivity & Business (Office 365, LinkedIn), More Personal Computing (Windows, Xbox, Surface). Three large segments, each substantial. Geographic revenue split across Americas, Europe, Asia. Well-diversified. |
| Technology | Consumer Electronics | 0.45 | Apple: iPhone (~52% revenue), Services (~22%), Mac (~8%), iPad (~7%), Wearables (~10%). iPhone dominance creates concentration but Services growth is diversifying. Better than it was in 2015 when iPhone was ~63%. |
| Technology | Internet Services | 0.55 | Alphabet: Google Search & Other (~57%), YouTube (~11%), Google Network (~9%), Google Cloud (~11%), Other Bets (~<1%). Search dominant but cloud and YouTube growing. |
| Consumer Discretionary | E-Commerce & Cloud Services | 0.60 | Amazon: Online stores, Third-party seller services, AWS, Advertising, Subscriptions (Prime). AWS (~62% of operating income) masks retail's thin margins. Revenue base across retail, cloud, and advertising is genuinely diverse. |
| Consumer Staples | Food & Beverages | 0.75 | Nestlé: Powdered & Liquid Beverages, PetCare, Nutrition & Health Science, Prepared Dishes, Confectionery, Water — six major categories across 190+ countries. Arguably the most diversified food company globally. |

**Fallbacks:**
- Technology: 0.50 (technology businesses tend toward segment concentration)
- Consumer Discretionary: 0.55
- Consumer Staples: 0.70 (large consumer staples companies are inherently diversified)

**Known limitations:** Revenue diversification at the industry level misses specialist vs
generalist distinctions within sectors. A Level A score would use actual segment revenue
percentages from annual reports.

**Future Level A data:** Business segment revenue breakdown from annual reports.
Herfindahl-Hirschman Index of revenue concentration is a reliable quantitative measure.

---

## Debt Sensitivity

**Purpose:** Measures the degree to which financial performance is sensitive to interest
rate changes through the cost of debt financing. Capital-intensive businesses with high
leverage face margin compression when rates rise. Asset-light businesses with net cash
benefit from rising rates. Directly drives the Interest Rate Sensitivity reasoning pattern.

**Benchmark linkage:** Interest Rate Sensitivity pattern. Required for planned case:
microsoft_interest_rate (Microsoft is net cash positive — expected NO_FINDING, making it
a useful test of the negative case).

**Approximation Level:** B (Industry) for most. Level C (Sector) as fallback where industry
leverage profiles are less uniform.

*Degree to which financial performance is sensitive to interest rate changes through leverage.*

| Sector | Industry | Score | Rationale |
|--------|----------|-------|-----------|
| Technology | Semiconductors | 0.35 | TSMC carries meaningful debt for fab construction but generates strong operating cash flow (~35% FCF margin) that services it comfortably. NVIDIA is effectively net cash positive. Rate sensitivity is moderate — capex-driven but cash-generative. |
| Technology | Software | 0.15 | Microsoft: net cash ~$50bn+. Rising rates increase return on cash holdings — Microsoft is a rate beneficiary, not a victim. Minimal floating-rate debt. Among the least rate-sensitive large companies. |
| Technology | Consumer Electronics | 0.15 | Apple: net cash ~$60bn+. Same dynamic as Microsoft — benefits from higher short-term rates on its enormous cash and securities portfolio. Rates are essentially a tailwind. |
| Technology | Internet Services | 0.20 | Alphabet: net cash ~$100bn+. Extremely low debt sensitivity. Google has used debt opportunistically at low rates but is not dependent on leverage. |
| Consumer Discretionary | E-Commerce & Cloud Services | 0.45 | Amazon carries meaningful debt (fulfilment network expansion, MGM acquisition). Operating leverage in AWS provides cash generation, but the retail segment operates on thin margins. More rate-sensitive than pure-software peers. |
| Consumer Staples | Food & Beverages | 0.50 | Nestlé has historically carried moderate leverage (~2x EBITDA). M&A strategy has periodically increased debt (Vitafon acquisition). Rate sensitivity is real but manageable given defensive cash flows. |

**Fallbacks:**
- Technology: 0.25 (technology companies tend to be cash-generative and under-leveraged)
- Consumer Discretionary: 0.45
- Consumer Staples: 0.50

**Known limitations:** Industry-level scores are particularly misleading for this dimension.
Net debt/EBITDA varies enormously within industries. A semiconductor startup and TSMC
have very different debt profiles. Level A data is especially important here.

**Future Level A data:** Net debt/EBITDA from balance sheet. Interest coverage ratio.
Proportion of floating vs fixed rate debt from notes to financial statements.

---

## Currency Exposure

**Purpose:** Measures the degree to which revenue and cost structure spans multiple currencies,
creating exposure to foreign exchange movements. Companies with significant foreign currency
revenue and domestic currency costs face margin pressure when the domestic currency strengthens.
Directly drives the Currency Exposure reasoning pattern.

**Benchmark linkage:** Currency Exposure pattern. Required for planned case:
apple_china_revenue (Apple's CNY revenue exposure when USD strengthens).

**Approximation Level:** B (Industry)

*Degree to which revenue and cost structure creates foreign exchange exposure.*

| Sector | Industry | Score | Rationale |
|--------|----------|-------|-----------|
| Technology | Semiconductors | 0.80 | TSMC: revenues predominantly in USD, costs in TWD — TWD appreciation directly compresses margins. NVIDIA: USD revenue globally, but supply chain costs in TWD, KRW, JPY. FX is a material P&L factor for both. |
| Technology | Software | 0.50 | Microsoft: ~50% international revenue. Active hedging program moderates but does not eliminate exposure. EUR/USD and JPY/USD are primary risks. FX impact is disclosed quarterly in earnings. |
| Technology | Consumer Electronics | 0.65 | Apple: ~56% international revenue. Greater China (~19%) creates CNY exposure. Japan creates JPY exposure. Apple discloses that a 10% dollar strengthening would reduce revenue by ~4–5%. |
| Technology | Internet Services | 0.55 | Alphabet: global advertising revenue, much invoiced in USD internationally. But local currency ad markets (EUR, JPY, BRL) create real exposure. Google Cloud international pricing adds further complexity. |
| Consumer Discretionary | E-Commerce & Cloud Services | 0.45 | Amazon: US-heavy (~60% of revenue). International consumer segments (EU, JP, IN) carry FX exposure. AWS pricing often in USD even for international customers. Net: moderate exposure. |
| Consumer Staples | Food & Beverages | 0.80 | Nestlé: operates in 190+ countries with revenue in local currencies. CHF reporting currency means virtually all revenue is technically foreign. FX is one of the most material factors in Nestlé's annual results — management explicitly guides for FX impact. |

**Fallbacks:**
- Technology: 0.55 (technology products are globally distributed)
- Consumer Discretionary: 0.45
- Consumer Staples: 0.75 (large multinationals have pervasive currency exposure)

**Known limitations:** Industry-level scores cannot capture the specific currency pairs
or hedging programs of individual companies. A hedged company and an unhedged company
in the same industry have fundamentally different effective exposures.

**Future Level A data:** Geographic revenue breakdown from annual reports. Hedging
program disclosures in notes to financial statements. Management commentary on FX
sensitivity (e.g. "10% USD strengthening = X% revenue impact").

---

## Energy Dependency

**Purpose:** Measures the degree to which energy is a primary input to operations. High energy
dependency means operating costs are directly correlated with energy prices, and that supply
disruptions or carbon pricing policies create material financial risk. Distinct from Commodity
Input Exposure (which focuses on raw material inputs); energy has distinct price dynamics,
policy risk (carbon taxes, renewable mandates), and reliability risk (grid instability).

**Benchmark linkage:** Energy Dependency pattern. Required for planned case: amazon_energy
(Amazon AWS data center electricity consumption and carbon commitment).

**Approximation Level:** B (Industry) — energy intensity is one of the best-documented
industry characteristics. Industrial energy benchmarks are published by IEA, EPA, and
sector trade associations.

*Degree to which energy is a primary operational input and cost driver.*

| Sector | Industry | Score | Rationale |
|--------|----------|-------|-----------|
| Technology | Semiconductors | 0.85 | Semiconductor fabs are among the most energy-intensive industrial facilities globally. TSMC's fabs consume ~7–9% of Taiwan's total electricity supply. Energy represents an estimated 10–15% of fab operating expenditure. Power quality (stable frequency, minimal outages) is as critical as price — a power flicker can destroy a wafer batch. |
| Technology | Software | 0.15 | A software company's energy footprint is primarily office buildings and, to a lesser extent, cloud computing costs paid to infrastructure providers. For companies like Microsoft or Salesforce, direct energy is not a material operating cost. Indirect exposure exists through cloud provider pricing. |
| Technology | Consumer Electronics | 0.30 | Apple's direct operations (offices, retail stores, data centres) have a meaningful but not dominant energy footprint. Apple has achieved carbon neutrality in operations. Manufacturing energy is the supplier's cost (Foxconn, TSMC), not Apple's direct exposure. Supply chain energy exposure is real but indirect. |
| Technology | Internet Services | 0.70 | Data centres are primary infrastructure. Alphabet consumed 14.3 TWh of electricity in 2022 — equivalent to a small country. Committed to 24/7 carbon-free energy by 2030. Electricity is the largest operating cost for search and cloud infrastructure. |
| Consumer Discretionary | E-Commerce & Cloud Services | 0.75 | Amazon combines AWS data center energy (high) with fulfilment center energy (significant) and delivery fleet energy (diesel and electricity). Amazon has committed to 80,000 electric delivery vehicles. Energy is one of the largest and most visible operating cost exposures. |
| Consumer Staples | Food & Beverages | 0.50 | Manufacturing (factories, processing equipment) and cold chain distribution require significant energy. Nestlé has committed to net-zero emissions — acknowledging energy as a material operational factor. Moderate: energy is significant but not the dominant cost versus raw materials and labour. |

**Fallbacks:**
- Technology: 0.45 (varies widely between hardware-intensive and software sub-sectors)
- Consumer Discretionary: 0.55
- Consumer Staples: 0.50

**Known limitations:** Cloud infrastructure companies (Alphabet, Amazon) face indirect energy
exposure through their own data centers AND create energy exposure for their customers. The
score captures the company's direct exposure only.

**Future Level A data:** Annual energy consumption disclosures (GWh). Carbon/energy intensity
metrics from sustainability reports. Electricity as % of total operating costs from segment
disclosures.

---

## Labour Intensity

**Purpose:** Measures the degree to which human labour is a primary operational input and cost,
and the degree to which that workforce is large, concentrated, or exposed to regulatory change.
High labour intensity creates exposure to wage inflation, minimum wage legislation, unionisation,
geographic concentration of workers, and labour disruption (strikes, pandemic closures).

**Benchmark linkage:** Labour Exposure pattern. Supports future expansion of nestle_coffee
to include Foxconn/China assembly as a Labour Exposure case for Apple.

**Approximation Level:** B (Industry)

*Degree to which labour is a primary operational input relative to capital and technology.*

| Sector | Industry | Score | Rationale |
|--------|----------|-------|-----------|
| Technology | Semiconductors | 0.45 | Fab operations require skilled technicians and engineers but are increasingly automated. TSMC employs ~73,000 people generating ~$70bn revenue — high revenue per employee. However, the specialised skill requirements mean labour market tightness (e.g. US fab staffing challenges) is a genuine operational risk. |
| Technology | Software | 0.25 | Software companies are human-intensive in a different sense: engineers are the primary asset. But headcount is small relative to revenue (Microsoft: ~230,000 employees, ~$211bn revenue). Geographic concentration in a few talent markets (Seattle, Bay Area) creates some risk. Not a primary cost concern. |
| Technology | Consumer Electronics | 0.30 | Apple's own workforce is engineering and retail-focused — not labour-intensive. The labour intensity risk is in the supply chain: Foxconn employs 1M+ workers to assemble Apple products. Apple's own direct labour intensity is low; indirect exposure is high but captured in Supply Chain Complexity. |
| Technology | Internet Services | 0.30 | Alphabet employs ~180,000 people but generates ~$300bn revenue. High-skill, high-compensation workforce. Labour disruption risk is primarily skilled worker strikes or attrition, not wage floor legislation. |
| Consumer Discretionary | E-Commerce & Cloud Services | 0.80 | Amazon directly employs 1.5M+ workers, making it the second-largest private employer in the US. Fulfilment centers and delivery operations are labour-intensive. Amazon faces sustained minimum wage pressure, unionisation (JFK8), and turnover costs estimated at ~$8bn annually. Labour is a primary P&L risk. |
| Consumer Staples | Food & Beverages | 0.65 | Nestlé employs ~275,000 people across manufacturing, distribution, and agricultural supply chain. Factory operations are moderately automated but still labour-intensive. Agricultural sourcing creates additional exposure to seasonal and contract labour conditions in developing markets. |

**Fallbacks:**
- Technology: 0.35 (technology tends toward capital/IP intensity over labour intensity)
- Consumer Discretionary: 0.65 (retail, logistics, and manufacturing sub-sectors are labour-intensive)
- Consumer Staples: 0.60

**Known limitations:** The score does not distinguish between direct and indirect labour
exposure. Apple's score of 0.30 understates total system labour intensity when Foxconn's
million-worker workforce is considered. Atlas relationships (DEPENDS_ON_SUPPLIES → Foxconn)
capture this indirect exposure; the Finance DNA score captures direct exposure only.

**Future Level A data:** Total headcount from annual reports. Labour cost as % of revenue
from segment disclosures. Union coverage rates. Turnover rates where disclosed.

---

## Regulatory Compliance Cost

**Purpose:** Measures the degree to which regulatory compliance represents a material
operational burden — not just in financial cost but in management time, speed to market,
and flexibility constraints. Extends Regulatory Exposure (which measures how exposed a
company is to regulatory risk) with the cost and operational burden dimension.

**Benchmark linkage:** Regulatory Risk pattern. Required for planned case:
alphabet_eu_regulation (EU Digital Markets Act compliance cost and operational constraint).

**Approximation Level:** B (Industry) — compliance cost burden is well-documented by
industry and relatively consistent within sectors.

*Degree to which regulatory compliance is a material operational cost and constraint.*

| Sector | Industry | Score | Rationale |
|--------|----------|-------|-----------|
| Technology | Semiconductors | 0.50 | Export control compliance (BIS, ITAR, CHIPS Act) requires dedicated legal and compliance infrastructure. Environmental compliance for fab chemicals (process gases, wastewater) is significant. TSMC's US fab construction involves complex regulatory interactions. Moderate-high burden. |
| Technology | Software | 0.45 | GDPR compliance requires substantial engineering investment (data residency, consent management, deletion pipelines). EU AI Act introduces product classification and conformity assessment obligations. Antitrust monitoring is ongoing. Rising trajectory as digital regulation expands. |
| Technology | Consumer Electronics | 0.45 | FCC equipment authorisation, CE marking, RoHS compliance, right-to-repair legislation (multiple jurisdictions), product safety certifications. Each new product requires multi-jurisdiction regulatory clearance before sale. |
| Technology | Internet Services | 0.75 | Alphabet faces the highest regulatory burden in the technology sector. EU Digital Markets Act (Designated Gatekeeper), DSA content moderation obligations, GDPR (€50M fine in 2019, €150M in 2022), DOJ antitrust trial (2023). Dedicated regulatory compliance is a significant operational cost and constrains product design. |
| Consumer Discretionary | E-Commerce & Cloud Services | 0.60 | FTC antitrust scrutiny of Amazon marketplace practices. Worker safety and labour regulation for fulfilment centers (OSHA citations). Consumer protection rules. AWS: FedRAMP compliance for government contracts. EU Digital Markets Act as Designated Gatekeeper. |
| Consumer Staples | Food & Beverages | 0.65 | FDA and EFSA food safety requirements apply to all products. Nutritional labeling across 190+ countries with varying requirements. Advertising restrictions (especially targeting children). Palm oil and cocoa supply chain sustainability disclosures (EU deforestation regulation). Health claims require pre-approval in many markets. |

**Fallbacks:**
- Technology: 0.50 (digital regulation is expanding rapidly across all sub-sectors)
- Consumer Discretionary: 0.55
- Consumer Staples: 0.60 (food and beverage regulation is pervasive globally)

**Known limitations:** The score cannot capture company-specific compliance investment or
the trajectory of regulatory change. Internet Services is explicitly rising as the EU DMA
and AI Act enforcement ramps up. Annual reassessment is recommended for this dimension.

**Future Level A data:** Regulatory affairs headcount and cost disclosures where available.
Disclosed fines and regulatory remediation costs. Management commentary on regulatory
impact in MD&A sections of annual reports.

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 28 June 2026 | Initial six dimensions. Sector-level approximations (retroactively classified as Level C). |
| 0.2 | 09 July 2026 | Nine new dimensions added. Approximation Level framework introduced. All V0.2 scores are Level B (Industry). |

---

*V0.1 scores will be retroactively tagged Level C during Session 3 implementation.
No score values change — only the approximation_level field is added to the Dimension model.*
