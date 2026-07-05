# 09 — Public Interface Specification

**Version:** 1.0
**Status:** Active
**Last Updated:** 28 June 2026
**Document Owner:** Hyperion Core

**Depends On:**
- `07-SYSTEM-ARCHITECTURE.md`
- All implemented engine modules (03–08)

**Used By:**
- `10-REST-API.md` (once written)
- `backend/api/` (all files)

---

## Purpose

This document freezes the boundary between the Hyperion engine and every external consumer — REST API, CLI, frontend, and any future integration. It answers exactly seven questions:

1. What is the input?
2. What is the output?
3. How does someone call it?
4. What does a successful response look like?
5. What does an error look like?
6. How do we version it?
7. Which objects are permanent public contracts?

Once these are frozen, implementing the API, CLI, and frontend becomes composition rather than design. Changing the engine never requires changing the contract.

---

## The Anti-Corruption Rule

**The engine never imports from `backend/api/`. The API never imports directly from the engine.**

```
Outside World
      ↓
backend/api/schemas.py   ← Pydantic models (JSON-serializable)
      ↓
backend/api/serializers.py ← DTO → Pydantic
      ↓
backend/api/dto.py       ← Python dataclasses (typed, not serializable)
      ↓
backend/api/mapper.py    ← THE ONLY PLACE that touches engine objects
      ↓
Engine (models, atlas, janus, titan, finance_dna, ingestion)
```

`mapper.py` is the firewall. If the engine changes, only `mapper.py` changes. Consumers never notice.

---

## Request Contract

```json
POST /v1/analyze
Content-Type: application/json

{
  "portfolio": ["Apple", "NVIDIA", "Microsoft"],
  "as_of": "2024-12-31"
}
```

**Fields:**
- `portfolio` — required, non-empty list of company identifiers (names, tickers, or aliases — same resolution as Ingestion)
- `as_of` — optional ISO-8601 date; defaults to today; with a fixed `as_of`, the same request always returns the same response

---

## Response Contract

```json
{
  "metadata": {
    "hyperion_version": "0.1",
    "finance_dna_schema": "0.1",
    "processed_at": "2024-12-31T14:23:01",
    "processing_time_ms": 63,
    "request_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
  },
  "portfolio": ["Apple Inc.", "NVIDIA Corporation", "Microsoft Corporation"],
  "blind_spots": [
    {
      "summary": {
        "company_id": "apple-inc",
        "company_name": "Apple Inc.",
        "confidence": 0.8075,
        "severity": "MEDIUM",
        "categories": ["dependency", "macroeconomic"]
      },
      "explanation": {
        "steps": [
          {
            "premise": "Apple Inc. → DEPENDS_ON_SUPPLIES → Taiwan Semiconductor Manufacturing Company",
            "inference": "Apple Inc. has a supply chain dependency on Taiwan Semiconductor Manufacturing Company.",
            "confidence": 0.95,
            "relationship_type": "depends_on_supplies",
            "source_id": "apple-inc",
            "target_id": "tsmc",
            "source_label": "Apple Inc.",
            "target_label": "Taiwan Semiconductor Manufacturing Company"
          }
        ]
      },
      "evidence": {
        "supporting_evidence": ["Apple 10-K: TSMC identified as sole-source supplier..."],
        "assumptions": ["Finance DNA dimensions are sector-level approximations (V0.1)."],
        "falsifiability_conditions": ["Evidence that Apple Inc. has materially reduced its supply chain exposure..."]
      }
    }
  ],
  "no_findings": [
    {
      "company_id": "microsoft",
      "company_name": "Microsoft Corporation",
      "reason": "NO_QUALIFYING_REASONING_PATH"
    }
  ],
  "errors": []
}
```

---

## Field Definitions

### `metadata`
Present in every response regardless of outcome.

| Field | Type | Description |
|---|---|---|
| `hyperion_version` | string | Hyperion engine version |
| `finance_dna_schema` | string | Finance DNA schema version used |
| `processed_at` | ISO-8601 datetime | When analysis was executed |
| `processing_time_ms` | integer | Wall-clock time for the full pipeline |
| `request_id` | UUID string | Unique per request; for tracing and debugging |

### `blind_spots[].summary`
| Field | Type | Description |
|---|---|---|
| `company_id` | string | Permanent, immutable internal identifier |
| `company_name` | string | Human-readable display name |
| `confidence` | float [0,1] | Product of all edge confidences in the reasoning chain |
| `severity` | string | "LOW" / "MEDIUM" / "HIGH" / "CRITICAL"; independent of confidence |
| `categories` | string[] | Lowercase Blind Spot taxonomy categories |

### `blind_spots[].explanation.steps[].`
| Field | Type | Description |
|---|---|---|
| `premise` | string | The factual starting point of this step |
| `inference` | string | What follows from the premise |
| `confidence` | float [0,1] | Confidence in this individual step |
| `relationship_type` | string | Lowercase Atlas relationship type (e.g. `"depends_on_supplies"`) |
| `source_id` | string | Permanent source node identifier |
| `target_id` | string | Permanent target node identifier |
| `source_label` | string | Human-readable source name |
| `target_label` | string | Human-readable target name |

### `no_findings[]`
Companies that were resolved but produced no Blind Spot.

| Field | Type | Description |
|---|---|---|
| `company_id` | string | Resolved company identifier |
| `company_name` | string | Human-readable name |
| `reason` | string | `"NO_QUALIFYING_REASONING_PATH"` — no path from this asset to a risk endpoint met the significance criteria |

### `errors[]`
Identifiers that could not be resolved at all.

| Field | Type | Description |
|---|---|---|
| `identifier` | string | The original identifier as submitted |
| `reason` | string | `"UNKNOWN_COMPANY"` — not found in the registry |

---

## Partial Success Semantics

Unknown companies go in `errors[]`, not HTTP 4xx. The pipeline runs for companies it can resolve and reports failures for those it cannot. A portfolio of ten companies should not fail completely because one name was misspelled.

---

## Error Responses

**HTTP 422 — Request validation failed:**
```json
{"error": "INVALID_REQUEST", "detail": "portfolio cannot be empty"}
```

**HTTP 500 — Internal pipeline failure:**
```json
{"error": "PIPELINE_ERROR", "detail": "internal error"}
```

---

## ID Immutability Guarantee

**Company IDs are permanent and never reused.**

`"apple-inc"` refers to Apple Inc. today and in all future versions. IDs are never renamed, recycled, or reassigned. Clients may safely store and reference them across versions.

---

## Versioning

- `metadata.hyperion_version` increments when the response schema changes in a breaking way
- `metadata.finance_dna_schema` increments when the set of evaluated dimensions changes materially
- The `/v1/` prefix in the URL is the contract version; breaking changes require `/v2/`

---

## Severity (V0.1 Note)

`severity` is frozen as a field but not yet meaningfully computed. V0.1 sets it to `"MEDIUM"` for all qualified Blind Spots. Future versions will compute severity independently from confidence — high confidence in a minor exposure may be LOW severity; low confidence in a critical supply chain dependency may be CRITICAL severity. The field is present now so that clients can begin building against it.
