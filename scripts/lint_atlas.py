#!/usr/bin/env python3
"""scripts/lint_atlas.py — Knowledge graph integrity checks.

Runs six categories of checks against the Atlas dataset files:

  1. Duplicate nodes         — same ID appears twice in context_nodes.csv
  2. Duplicate relationships — same source/target/type triplet appears twice
  3. Orphaned nodes          — context nodes with no relationships
  4. Broken references       — relationships referencing unknown node IDs
  5. Missing evidence        — relationships with empty evidence field
  6. Confidence range        — relationship confidence outside [0.0, 1.0]

Exit code 0 if all checks pass. Exit code 1 if any issue is found.

Usage:
    uv run python scripts/lint_atlas.py

Run this after every Atlas addition to catch data quality issues early.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_ASSETS_CSV = _ROOT / "datasets" / "assets.csv"
_NODES_CSV = _ROOT / "datasets" / "atlas" / "context_nodes.csv"
_RELATIONSHIPS_CSV = _ROOT / "datasets" / "atlas" / "seed_relationships.csv"


def load_assets() -> dict[str, str]:
    """Load asset IDs and names. Returns {id: name}."""
    assets: dict[str, str] = {}
    with open(_ASSETS_CSV) as f:
        for row in csv.DictReader(f):
            assets[row["id"]] = row["name"]
    return assets


def load_context_nodes() -> dict[str, str]:
    """Load context node IDs and classes. Returns {id: node_class}."""
    nodes: dict[str, str] = {}
    with open(_NODES_CSV) as f:
        for row in csv.DictReader(f):
            nodes[row["id"]] = row["node_class"]
    return nodes


def load_relationships() -> list[dict[str, str]]:
    """Load all seed relationships."""
    rels: list[dict[str, str]] = []
    with open(_RELATIONSHIPS_CSV) as f:
        for row in csv.DictReader(f):
            rels.append(dict(row))
    return rels


def check_duplicate_nodes(nodes: dict[str, str]) -> list[str]:
    """Check for duplicate node IDs in context_nodes.csv."""
    issues: list[str] = []
    seen: set[str] = set()
    with open(_NODES_CSV) as f:
        for row in csv.DictReader(f):
            node_id = row["id"]
            if node_id in seen:
                issues.append(f"Duplicate context node ID: '{node_id}'")
            seen.add(node_id)
    return issues


def check_duplicate_assets(assets: dict[str, str]) -> list[str]:
    """Check for duplicate asset IDs in assets.csv."""
    issues: list[str] = []
    seen: set[str] = set()
    with open(_ASSETS_CSV) as f:
        for row in csv.DictReader(f):
            asset_id = row["id"]
            if asset_id in seen:
                issues.append(f"Duplicate asset ID: '{asset_id}'")
            seen.add(asset_id)
    return issues


def check_duplicate_relationships(rels: list[dict[str, str]]) -> list[str]:
    """Check for duplicate source/target/relationship_type triplets."""
    issues: list[str] = []
    seen: set[tuple[str, str, str]] = set()
    for rel in rels:
        key = (rel["source_id"], rel["target_id"], rel["relationship_type"])
        if key in seen:
            issues.append(
                f"Duplicate relationship: {rel['source_id']} → "
                f"{rel['relationship_type']} → {rel['target_id']}"
            )
        seen.add(key)
    return issues


def check_broken_references(
    assets: dict[str, str],
    nodes: dict[str, str],
    rels: list[dict[str, str]],
) -> list[str]:
    """Check for relationships referencing unknown node IDs."""
    issues: list[str] = []
    all_known = set(assets.keys()) | set(nodes.keys())
    for rel in rels:
        src = rel["source_id"]
        tgt = rel["target_id"]
        if src not in all_known:
            issues.append(
                f"Relationship source '{src}' not found in assets or context nodes"
            )
        if tgt not in all_known:
            issues.append(
                f"Relationship target '{tgt}' not found in assets or context nodes"
            )
    return issues


def check_orphaned_nodes(
    nodes: dict[str, str],
    rels: list[dict[str, str]],
) -> list[str]:
    """Check for context nodes that appear in no relationships."""
    issues: list[str] = []
    referenced: set[str] = set()
    for rel in rels:
        referenced.add(rel["source_id"])
        referenced.add(rel["target_id"])
    for node_id in nodes:
        if node_id not in referenced:
            issues.append(
                f"Orphaned context node '{node_id}' — appears in no relationships"
            )
    return issues


def check_missing_evidence(rels: list[dict[str, str]]) -> list[str]:
    """Check for relationships with empty or missing evidence fields."""
    issues: list[str] = []
    for rel in rels:
        evidence = rel.get("evidence", "").strip()
        if not evidence:
            issues.append(
                f"Missing evidence: {rel['source_id']} → "
                f"{rel['relationship_type']} → {rel['target_id']}"
            )
    return issues


def check_confidence_range(rels: list[dict[str, str]]) -> list[str]:
    """Check that all relationship confidence values are in [0.0, 1.0]."""
    issues: list[str] = []
    for rel in rels:
        try:
            conf = float(rel.get("confidence", "0"))
        except ValueError:
            issues.append(
                f"Invalid confidence value '{rel.get('confidence')}' for: "
                f"{rel['source_id']} → {rel['relationship_type']} → {rel['target_id']}"
            )
            continue
        if not (0.0 <= conf <= 1.0):
            issues.append(
                f"Confidence {conf} out of range [0.0, 1.0]: "
                f"{rel['source_id']} → {rel['relationship_type']} → {rel['target_id']}"
            )
    return issues


def main() -> int:
    print("=" * 60)
    print("  Hyperion Atlas Integrity Linter")
    print("=" * 60)

    assets = load_assets()
    nodes = load_context_nodes()
    rels = load_relationships()

    print(f"\n  Loaded: {len(assets)} assets, {len(nodes)} context nodes, "
          f"{len(rels)} relationships")

    checks = [
        ("Duplicate assets", check_duplicate_assets(assets)),
        ("Duplicate context nodes", check_duplicate_nodes(nodes)),
        ("Duplicate relationships", check_duplicate_relationships(rels)),
        ("Broken references", check_broken_references(assets, nodes, rels)),
        ("Orphaned context nodes", check_orphaned_nodes(nodes, rels)),
        ("Missing evidence", check_missing_evidence(rels)),
        ("Confidence range", check_confidence_range(rels)),
    ]

    total_issues = 0
    print()
    for check_name, issues in checks:
        if issues:
            print(f"  ❌ {check_name}: {len(issues)} issue(s)")
            for issue in issues:
                print(f"     • {issue}")
            total_issues += len(issues)
        else:
            print(f"  ✅ {check_name}: clean")

    print("\n" + "=" * 60)
    if total_issues == 0:
        print("  Atlas is clean. 0 issues found.")
    else:
        print(f"  {total_issues} issue(s) found. Fix before committing.")
    print("=" * 60)

    return 0 if total_issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
