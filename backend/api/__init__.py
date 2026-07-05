"""Hyperion API layer — public interface.

Justified by: docs/09-PUBLIC-INTERFACE.md.

The API layer translates between the engine (backend/models/ and all engine
modules) and external consumers (REST API, CLI, frontend).

Architecture — one-way dependency:
    Outside World
        ↓
    schemas.py      (Pydantic — JSON-serializable wire format)
        ↓
    serializers.py  (DTO → Pydantic)
        ↓
    dto.py          (Python dataclasses — typed intermediate representation)
        ↓
    mapper.py       (THE ONLY FILE that imports engine objects)
        ↓
    Engine          (models, atlas, janus, titan, finance_dna, ingestion)

The engine NEVER imports from backend/api. This file exports only what
external callers need to invoke the full analysis pipeline.

Public exports
--------------
map_analyze_response    — engine objects → AnalyzeResponseDTO
serialize_response      — AnalyzeResponseDTO → AnalyzeResponseSchema (JSON)
AnalyzeRequestSchema    — validates incoming request body
AnalyzeResponseSchema   — the frozen wire-format response contract
"""

from backend.api.mapper import map_analyze_response
from backend.api.schemas import AnalyzeRequestSchema, AnalyzeResponseSchema
from backend.api.serializers import serialize_response

__all__ = [
    "map_analyze_response",
    "serialize_response",
    "AnalyzeRequestSchema",
    "AnalyzeResponseSchema",
]
