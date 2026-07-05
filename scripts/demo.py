#!/usr/bin/env python3
"""scripts/demo.py — Hyperion v0.1 Proof of Concept.

Executes the complete Hyperion pipeline deterministically:

    load_portfolio() → evaluate() → build() → reason() → qualify()

Run from the project root:

    uv run python scripts/demo.py

If this script produces a Blind Spot, the Constitution has become software.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — works whether run from project root or scripts/
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from backend.atlas import build
from backend.finance_dna import FINANCE_DNA_VERSION, evaluate
from backend.ingestion import load_asset_registry, load_portfolio
from backend.janus import reason
from backend.models import BlindSpot, FinanceDNA, ReasoningArtifact
from backend.titan import qualify

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEMO_PORTFOLIO: list[str] = ["Apple", "NVIDIA", "Microsoft"]
AS_OF: str = date.today().isoformat()

# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

_W = 50  # rule width — decorative, content may exceed


def _rule(char: str = "=") -> str:
    return char * _W


def _tick(label: str) -> str:
    return f"    \u2713  {label}"


def _skip(label: str) -> str:
    return f"    -  {label}"


def _bullet(text: str) -> str:
    return f"    \u2022  {text}"


def _chain_lines(artifact: ReasoningArtifact) -> list[str]:
    """Format a reasoning chain as a visual step-by-step descent.

    Turns:
        "Apple Inc. → DEPENDS_ON_SUPPLIES → TSMC"
        "TSMC → LOCATED_IN → Taiwan"
        "Taiwan → AFFECTED_BY → Taiwan Geopolitical Risk"

    Into:
        Apple Inc.
        → DEPENDS_ON_SUPPLIES → TSMC
        → LOCATED_IN → Taiwan
        → AFFECTED_BY → Taiwan Geopolitical Risk
    """
    steps = artifact.reasoning_steps
    if not steps:
        return []
    first_parts = steps[0].premise.split(" → ")
    lines: list[str] = [f"      {first_parts[0]}"]
    for step in steps:
        parts = step.premise.split(" → ")
        if len(parts) >= 3:
            lines.append(f"      \u2192 {parts[1]} \u2192 {parts[2]}")
    return lines


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def run() -> None:
    """Execute the full Hyperion pipeline and print the results."""

    # Header
    print(f"\n{_rule()}")
    print(f"  Hyperion v0.1  (Finance DNA schema {FINANCE_DNA_VERSION})")
    print(f"  Financial Reasoning Demonstration")
    print(_rule())

    # Portfolio display
    print(f"\n  Portfolio\n")
    for name in DEMO_PORTFOLIO:
        print(_bullet(name))

    # ------------------------------------------------------------------
    # Step 1 — Ingestion
    # ------------------------------------------------------------------
    print(f"\n{_rule('-')}\n  Loading Portfolio...\n")
    portfolio = load_portfolio(DEMO_PORTFOLIO)
    registry = load_asset_registry()
    all_assets = list(registry.assets)
    print(_tick(f"{len(portfolio.assets)} assets resolved from registry"))

    # ------------------------------------------------------------------
    # Step 2 — Finance DNA
    # ------------------------------------------------------------------
    print(f"\n{_rule('-')}\n  Building Finance DNA...\n")
    finance_dnas: dict[str, FinanceDNA] = {}
    for asset in portfolio.assets:
        dna = evaluate(asset, as_of=AS_OF)
        finance_dnas[asset.id] = dna
        print(_tick(asset.name))

    # ------------------------------------------------------------------
    # Step 3 — Atlas
    # ------------------------------------------------------------------
    print(f"\n{_rule('-')}\n  Building Knowledge Graph...\n")
    graph = build(all_assets, finance_dnas)
    print(_tick(f"{len(graph.nodes)} nodes"))
    print(_tick(f"{len(graph.relationships)} relationships"))

    # ------------------------------------------------------------------
    # Step 4 — Janus
    # ------------------------------------------------------------------
    print(f"\n{_rule('-')}\n  Running Janus...\n")
    artifacts: dict[str, ReasoningArtifact] = {}
    for asset in portfolio.assets:
        artifact = reason(asset.id, graph)
        if artifact is not None:
            artifacts[asset.id] = artifact
            print(_tick(asset.name))
        else:
            print(
                _skip(
                    f"No significant reasoning path found for {asset.name}."
                )
            )

    # ------------------------------------------------------------------
    # Step 5 — Titan
    # ------------------------------------------------------------------
    print(f"\n{_rule('-')}\n  Running Titan...\n")
    blind_spots: list[tuple[str, BlindSpot]] = []
    for asset in portfolio.assets:
        if asset.id not in artifacts:
            continue
        blind_spot = qualify(artifacts[asset.id])
        if blind_spot is not None:
            blind_spots.append((asset.name, blind_spot))
            print(_tick(f"{asset.name} — Blind Spot qualified"))
        else:
            print(
                _skip(f"{asset.name} — did not meet qualification criteria")
            )

    # ------------------------------------------------------------------
    # Step 6 — Output
    # ------------------------------------------------------------------
    if not blind_spots:
        print(f"\n{_rule('-')}")
        print("\n  No Blind Spots detected for this portfolio.")
    else:
        for i, (company_name, bs) in enumerate(blind_spots, 1):
            print(f"\n{_rule('-')}")
            _print_blind_spot(i, company_name, bs)

    # Footer
    print(f"\n{_rule()}")
    print(
        f"  Demonstration complete.  "
        f"{len(blind_spots)} Blind Spot(s) detected "
        f"for {len(DEMO_PORTFOLIO)} companies."
    )
    print(_rule())
    print()


def _print_blind_spot(n: int, company_name: str, bs: BlindSpot) -> None:
    """Print one fully-explained Blind Spot."""
    artifact = bs.supporting_reasoning

    print(f"\n  Blind Spot #{n}")

    print(f"\n  Company")
    print(f"    {company_name}")

    print(f"\n  Reasoning Chain")
    for line in _chain_lines(artifact):
        print(line)

    print(f"\n  Why it matters")
    for step in artifact.reasoning_steps:
        print(f"    {step.inference}")

    print(f"\n  Confidence")
    print(f"    {bs.confidence:.4f}")

    print(f"\n  Supporting Evidence")
    for ev in artifact.supporting_evidence:
        print(_bullet(ev))

    print(f"\n  Assumptions")
    for assumption in artifact.assumptions:
        print(_bullet(assumption))

    print(f"\n  What changes this conclusion")
    for condition in artifact.falsifiability_conditions:
        print(_bullet(condition))


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run()
