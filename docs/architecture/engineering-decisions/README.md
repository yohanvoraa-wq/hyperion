# Engineering Decisions — Index

Lightweight Architecture Decision Records (ADRs). Each one answers exactly: Decision, Rationale, Alternatives Considered, Final Choice. These are not specifications — the conceptual documents (`docs/00`–`07`) remain the source of truth for *what* Hyperion is. These records exist to document *why* a specific engineering choice was made, so the reasoning isn't lost the way an undocumented choice would be.

| ID | Title | Status |
|---|---|---|
| [ED-001](./ED-001-python.md) | Programming Language | Decided — Python 3.12+ |
| [ED-002](./ED-002-package-manager.md) | Package Manager | Decided — uv |
| [ED-003](./ED-003-repository-structure.md) | Repository Structure | Decided |
| [ED-004](./ED-004-engineering-principles.md) | Engineering Principles | Decided |
| [ED-005](./ED-005-data-ownership.md) | Data Ownership | Decided (inherits `07-SYSTEM-ARCHITECTURE.md`) |
| [ED-006](./ED-006-development-workflow.md) | Development Workflow | Decided |
| [ED-007](./ED-007-testing-philosophy.md) | Testing Philosophy | Decided |
| [ED-008](./ED-008-graph-requirements.md) | Graph Representation Requirements | Decided — properties only, no library |
| [ED-009](./ED-009-mvp-scope.md) | MVP Scope (Version 0.1) | Decided |
| ED-010 | Technology Choices | **Not started — Session 2** |

ED-010 is deliberately absent. Per the agreed sequencing, technology choices (graph library, database, frontend, API framework) are made in Session 2, against the requirements ED-008 already locked — not in this session.
