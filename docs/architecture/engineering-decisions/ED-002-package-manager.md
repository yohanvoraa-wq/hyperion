# ED-002 — Package Manager

**Status:** Decided
**Date:** 28 June 2026

## Decision
How are Python dependencies managed and locked?

## Rationale
Reproducibility matters more than ecosystem maturity during the MVP phase — a lockfile that resolves identically across machines removes an entire category of "works on my machine" debugging that has nothing to do with Hyperion's actual architecture.

## Alternatives Considered
- **pip + requirements.txt** — no lockfile by default; dependency resolution can silently drift between environments.
- **Poetry** — mature, widely used, slightly slower, a more opinionated project layout. A reasonable choice if the team is more familiar with it.
- **Conda** — suited to heavier scientific-computing dependency chains than Hyperion currently needs; unnecessary overhead at this stage.

## Final Choice
**uv.** Fast, reproducible, handles both dependency locking and Python version pinning. Poetry remains an acceptable substitute — the requirement is reproducibility and a committed lockfile, not this specific tool.
