"""Portfolio Ingestion Layer.

Justified by: docs/07-SYSTEM-ARCHITECTURE.md, Section 4 (hop 1) and Section 5
(Entry: Portfolio -> Normalization -> Asset Resolution -> Finance DNA).

Owns: turning a raw Portfolio into resolved Assets that backend.finance_dna
can qualify. Owns nothing once an Asset is resolved and handed off.
"""
