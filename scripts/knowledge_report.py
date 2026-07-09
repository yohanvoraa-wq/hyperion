#!/usr/bin/env python3
"""scripts/knowledge_report.py — Hyperion knowledge base dashboard.

Prints the current state of the knowledge base at a glance:
  - Finance DNA dimensions by approximation level
  - Atlas nodes and relationships
  - Benchmark coverage by state
  - Knowledge domain coverage
  - Atlas integrity summary

This is an internal engineering tool, not a user-facing feature.
It tells you whether the knowledge base is healthy and where
the remaining Version 0.2 work lies.

Usage:
    uv run python scripts/knowledge_report.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_assets() -> list[dict[str, str]]:
    with open(_ROOT / "datasets" / "assets.csv") as f:
        return list(csv.DictReader(f))


def load_context_nodes() -> list[dict[str, str]]:
    with open(_ROOT / "datasets" / "atlas" / "context_nodes.csv") as f:
        return list(csv.DictReader(f))


def load_relationships() -> list[dict[str, str]]:
    with open(_ROOT / "datasets" / "atlas" / "seed_relationships.csv") as f:
        return list(csv.DictReader(f))


def load_benchmark_cases() -> list[dict]:  # type: ignore[type-arg]
    cases = []
    cases_dir = _ROOT / "benchmarks" / "canonical_cases"
    for case_file in sorted(cases_dir.glob("*.json")):
        with open(case_file) as f:
            cases.append(json.load(f))
    return cases


def load_registry() -> tuple[int, int, int]:
    """Returns (level_a, level_b, level_c) dimension counts by reading the registry."""
    sys.path.insert(0, str(_ROOT))
    # Evaluate one asset to get approximation levels
    from backend.ingestion import load_portfolio
    from backend.models.enums import ApproximationLevel
    portfolio = load_portfolio(["Apple"])
    apple = portfolio.assets[0]

    from backend.finance_dna import evaluate
    dna = evaluate(apple, as_of="2024-12-31")

    counts = {ApproximationLevel.A: 0, ApproximationLevel.B: 0, ApproximationLevel.C: 0}
    for dim in dna.dimensions:
        level = dim.approximation_level
        if level in counts:
            counts[level] += 1
    return counts[ApproximationLevel.A], counts[ApproximationLevel.B], counts[ApproximationLevel.C]


# ---------------------------------------------------------------------------
# Atlas integrity (inline — no subprocess)
# ---------------------------------------------------------------------------


def run_integrity_checks(
    assets: list[dict[str, str]],
    nodes: list[dict[str, str]],
    rels: list[dict[str, str]],
) -> dict[str, bool]:
    asset_ids = {a["id"] for a in assets}
    node_ids = {n["id"] for n in nodes}
    all_ids = asset_ids | node_ids

    checks = {}

    # Duplicates
    seen_assets: set[str] = set()
    dup_assets = False
    for a in assets:
        if a["id"] in seen_assets:
            dup_assets = True
        seen_assets.add(a["id"])
    checks["No duplicate assets"] = not dup_assets

    seen_nodes: set[str] = set()
    dup_nodes = False
    for n in nodes:
        if n["id"] in seen_nodes:
            dup_nodes = True
        seen_nodes.add(n["id"])
    checks["No duplicate nodes"] = not dup_nodes

    seen_rels: set[tuple[str, str, str]] = set()
    dup_rels = False
    for r in rels:
        key = (r["source_id"], r["target_id"], r["relationship_type"])
        if key in seen_rels:
            dup_rels = True
        seen_rels.add(key)
    checks["No duplicate relationships"] = not dup_rels

    # Broken references
    broken = any(
        r["source_id"] not in all_ids or r["target_id"] not in all_ids
        for r in rels
    )
    checks["No broken references"] = not broken

    # Orphaned nodes
    referenced = {r["source_id"] for r in rels} | {r["target_id"] for r in rels}
    orphaned = any(n["id"] not in referenced for n in nodes)
    checks["No orphaned nodes"] = not orphaned

    # Missing evidence
    missing_ev = any(not r.get("evidence", "").strip() for r in rels)
    checks["All relationships have evidence"] = not missing_ev

    # Confidence range
    bad_conf = False
    for r in rels:
        try:
            c = float(r.get("confidence", "0"))
            if not (0.0 <= c <= 1.0):
                bad_conf = True
        except ValueError:
            bad_conf = True
    checks["Confidence values in range"] = not bad_conf

    return checks


# ---------------------------------------------------------------------------
# Domain coverage estimation
# ---------------------------------------------------------------------------

_DOMAIN_NODES: dict[str, list[str]] = {
    "Supply Chain": [
        "tsmc", "taiwan", "geopolitical-risk-taiwan",
    ],
    "Commodity": [
        "coffee", "brazil", "brazil-climate-risk",
    ],
    "Regulation": [
        "semiconductor-export-ban", "eu-digital-regulation",
    ],
    "Geopolitical": [
        "taiwan", "china", "geopolitical-risk-taiwan",
    ],
    "Currency": [
    ],
    "Energy": [
    ],
    "Labour": [
    ],
    "Interest Rate": [
        "us-fed-rate",
    ],
    "Customer": [
    ],
    "Supplier": [
    ],
}

_DOMAIN_MAX: dict[str, int] = {
    "Supply Chain": 5,
    "Commodity": 6,
    "Regulation": 5,
    "Geopolitical": 4,
    "Currency": 4,
    "Energy": 4,
    "Labour": 4,
    "Interest Rate": 4,
    "Customer": 4,
    "Supplier": 4,
}


def _bar(ratio: float, width: int = 16) -> str:
    filled = round(ratio * width)
    return "█" * filled + "░" * (width - filled)


# ---------------------------------------------------------------------------
# Main report
# ---------------------------------------------------------------------------


def main() -> None:
    assets = load_assets()
    nodes = load_context_nodes()
    rels = load_relationships()
    cases = load_benchmark_cases()

    level_a, level_b, level_c = load_registry()
    total_dims = level_a + level_b + level_c

    print()
    print("=" * 60)
    print("  Hyperion Knowledge Report")
    print("=" * 60)

    # Finance DNA
    print(f"""
  Finance DNA
  ──────────────────────────────────────
  {total_dims} dimensions registered

  Approximation breakdown:
    Level A (company-specific)  {level_a:>3}   {'█' * level_a if level_a else '░'}
    Level B (industry)          {level_b:>3}   {'█' * level_b}
    Level C (sector)            {level_c:>3}   {'█' * level_c}

  Level A target: 0 → 15 (Version 0.4 — automated SEC ingestion)""")

    # Atlas
    node_classes: dict[str, int] = {}
    for n in nodes:
        nc = n["node_class"]
        node_classes[nc] = node_classes.get(nc, 0) + 1

    print(f"""
  Atlas
  ──────────────────────────────────────
  {len(assets)} assets
  {len(nodes)} context nodes""")
    for nc, count in sorted(node_classes.items()):
        print(f"    {nc:<20} {count}")
    print(f"  {len(rels)} relationships")

    # Benchmarks
    by_state: dict[str, list[dict]] = {}  # type: ignore[type-arg]
    for case in cases:
        state = case.get("state", "Unknown")
        by_state.setdefault(state, []).append(case)

    implemented = by_state.get("Implemented", [])
    partial = by_state.get("Partial", [])
    planned = by_state.get("Planned", [])

    print(f"""
  Benchmarks
  ──────────────────────────────────────
  Implemented   {len(implemented):>3}""")
    for c in implemented:
        ci = c["expected"].get("confidence", {})
        cmin, cmax = ci.get("min", 0), ci.get("max", 0)
        print(f"    ✅ {c['id']:<35} conf={cmin:.4f}–{cmax:.4f}")

    if partial:
        print(f"  Partial       {len(partial):>3}")
        for c in partial:
            print(f"    🟡 {c['id']}")

    n_planned = len(planned) + (10 - len(implemented) - len(partial))
    print(f"  Planned       {n_planned:>3}")

    # Pattern coverage
    done = {c["pattern"] for c in cases if c["state"] == "Implemented"}
    all_patterns = [
        ("Supply Chain Risk", "Supply Chain Risk" in done),
        ("Commodity Shock", "Commodity Shock" in done),
        ("Regulatory Risk", "Regulatory Risk" in done),
        ("Geopolitical Risk", "Geopolitical Risk" in done),
        ("Currency Exposure", "Currency Exposure" in done),
        ("Interest Rate Sensitivity", "Interest Rate Sensitivity" in done),
        ("Customer Concentration", "Customer Concentration" in done),
        ("Supplier Concentration", "Supplier Concentration" in done),
        ("Energy Dependency", "Energy Dependency" in done),
        ("Labour Exposure", "Labour Exposure" in done),
    ]
    covered = sum(1 for _, done in all_patterns if done)
    print(f"\n  Pattern coverage: {covered}/10")
    for pattern, done in all_patterns:
        icon = "✅" if done else "🔲"
        print(f"    {icon} {pattern}")

    # Knowledge Domain Coverage
    existing_node_ids = {n["id"] for n in nodes}
    print("""
  Knowledge Domain Coverage
  ──────────────────────────────────────""")
    for domain, domain_nodes in _DOMAIN_NODES.items():
        present = sum(1 for n in domain_nodes if n in existing_node_ids)
        max_nodes = _DOMAIN_MAX[domain]
        ratio = present / max_nodes if max_nodes > 0 else 0
        pct = int(ratio * 100)
        bar = _bar(ratio)
        print(f"  {domain:<18} {bar}  {pct:>3}%")

    # Integrity
    checks = run_integrity_checks(assets, nodes, rels)
    all_clean = all(checks.values())
    print("""
  Atlas Integrity
  ──────────────────────────────────────""")
    for check_name, passed in checks.items():
        icon = "✅" if passed else "❌"
        print(f"  {icon} {check_name}")

    print()
    print("=" * 60)
    if all_clean:
        print(f"  Knowledge base healthy. {covered}/10 patterns. {total_dims} dimensions.")
    else:
        failed = sum(1 for p in checks.values() if not p)
        print(f"  ⚠️  {failed} integrity issue(s). Run scripts/lint_atlas.py for details.")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
