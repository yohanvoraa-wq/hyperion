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
