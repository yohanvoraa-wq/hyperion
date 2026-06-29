"""Shared artifact types: the common language of the codebase.

Justified by: docs/02-FOUNDATIONAL-CONCEPTS.md (Asset, Portfolio, Financial
System) and every module-specific artifact named in its own document
(Dimension, Relationship, ReasoningArtifact, BlindSpot).

Per ED-005 (Data Ownership): these types are immutable. A module that does
not own a given artifact type cannot mutate an instance of it -- this is
enforced here, at the type level, not left to code review.

No logic lives here. Only the shapes every other module agrees on.
"""
