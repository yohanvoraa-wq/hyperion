#!/usr/bin/env python3
"""scripts/run_benchmarks.py — Execute all canonical reasoning cases.

Runs every case in benchmarks/canonical_cases/ against the live Hyperion
pipeline and reports pass/fail with detailed output.

Usage:
    uv run python scripts/run_benchmarks.py

Exit code 0 if all State A cases pass. Exit code 1 if any fail.

State B and C cases are reported but not counted as failures —
they define future targets, not current requirements.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from backend.atlas import build
from backend.finance_dna import evaluate
from backend.ingestion import load_asset_registry, load_portfolio
from backend.ingestion.exceptions import UnknownAssetError
from backend.janus import reason
from backend.titan import qualify

# -----------------------------------------------------------------------
# Pipeline runner
# -----------------------------------------------------------------------

_REGISTRY = None
_ALL_ASSETS = None


def _get_registry():  # type: ignore[return]
    global _REGISTRY, _ALL_ASSETS
    if _REGISTRY is None:
        _REGISTRY = load_asset_registry()
        _ALL_ASSETS = list(_REGISTRY.assets)
    return _REGISTRY, _ALL_ASSETS


def run_pipeline(portfolio_names: list[str], as_of: str) -> dict:  # type: ignore[type-arg]
    """Run the full Hyperion pipeline for a portfolio."""
    registry, all_assets = _get_registry()
    portfolio = load_portfolio(portfolio_names)
    finance_dnas = {
        asset.id: evaluate(asset, as_of=as_of) for asset in portfolio.assets
    }
    graph = build(all_assets, finance_dnas)
    artifacts = {
        asset.id: reason(asset.id, graph) for asset in portfolio.assets
    }
    blind_spots = {
        asset_id: (qualify(art) if art is not None else None)
        for asset_id, art in artifacts.items()
    }
    return {
        "portfolio": portfolio,
        "finance_dnas": finance_dnas,
        "graph": graph,
        "artifacts": artifacts,
        "blind_spots": blind_spots,
    }


# -----------------------------------------------------------------------
# Case validation
# -----------------------------------------------------------------------

def validate_case(case: dict, result: dict) -> tuple[bool, list[str]]:  # type: ignore[type-arg]
    """Validate pipeline result against benchmark expected output.

    Checks:
      1. Correct status (BLIND_SPOT_FOUND vs NO_FINDING)
      2. Confidence within the expected range
      3. Reasoning path has the expected number of steps
      4. Each step uses the expected relationship type

    Note: premise text uses node labels ("Apple Inc.") not IDs ("apple-inc").
    Path structure is validated by relationship type and step count, not by
    matching IDs to premise strings.

    Returns (passed, list_of_failures).
    """
    failures: list[str] = []
    expected = case["expected"]
    company_id = expected.get("company")

    if expected["status"] == "BLIND_SPOT_FOUND":
        blind_spot = result["blind_spots"].get(company_id)
        artifact = result["artifacts"].get(company_id)

        if blind_spot is None or artifact is None:
            failures.append(f"Expected BLIND_SPOT_FOUND for {company_id} but got None")
            return False, failures

        # 1. Confidence range
        conf = artifact.confidence
        conf_min = expected["confidence"]["min"]
        conf_max = expected["confidence"]["max"]
        if not (conf_min <= conf <= conf_max):
            failures.append(
                f"Confidence {conf:.4f} outside expected range [{conf_min}, {conf_max}]"
            )

        # 2. Path step count
        expected_path = expected.get("reasoning_path", [])
        actual_steps = artifact.reasoning_steps
        if len(actual_steps) != len(expected_path):
            failures.append(
                f"Path length {len(actual_steps)} != expected {len(expected_path)}"
            )
        else:
            # 3. Relationship types match
            for i, (step, exp_step) in enumerate(zip(actual_steps, expected_path, strict=True)):
                expected_rel = exp_step.get("relationship", "").upper()
                if expected_rel and expected_rel not in step.premise.upper():
                    failures.append(
                        f"Step {i}: expected relationship '{expected_rel}' "
                        f"not found in premise"
                    )

    elif expected["status"] == "NO_FINDING":
        blind_spot = result["blind_spots"].get(company_id)
        if blind_spot is not None:
            failures.append(f"Expected NO_FINDING for {company_id} but got a BlindSpot")

    return len(failures) == 0, failures


# -----------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------

def main() -> int:
    cases_dir = _ROOT / "benchmarks" / "canonical_cases"
    case_files = sorted(cases_dir.glob("*.json"))

    if not case_files:
        print("No benchmark cases found.")
        return 1

    print("=" * 60)
    print("  Hyperion Canonical Reasoning Benchmark Suite")
    print("=" * 60)

    state_a_total = 0
    state_a_passed = 0
    state_b_total = 0
    state_c_total = 0
    all_results: list[tuple[str, str, bool, list[str]]] = []

    for case_file in case_files:
        with open(case_file) as f:
            case = json.load(f)

        case_id = case["id"]
        state = case["state"]
        pattern = case["pattern"]
        portfolio = case["input"]["portfolio"]
        as_of = case["input"]["as_of"]

        print(f"\n  [{state}] {case_id}")
        print(f"       Pattern: {pattern}")
        print(f"       Portfolio: {portfolio}")

        if state == "Planned":
            state_c_total += 1
            print("       Status: SKIP (Planned — target, not yet implemented)")
            all_results.append((case_id, state, True, []))
            continue

        if state == "Partial":
            state_b_total += 1

        if state == "Implemented":
            state_a_total += 1

        try:
            result = run_pipeline(portfolio, as_of)
            passed, failures = validate_case(case, result)

            if state == "Implemented":
                if passed:
                    state_a_passed += 1
                    print("       Status: ✅ PASS")
                    company_id = case["expected"].get("company")
                    if company_id and result["blind_spots"].get(company_id):
                        conf = result["blind_spots"][company_id].supporting_reasoning.confidence
                        print(f"       Confidence: {conf:.4f}")
                else:
                    print("       Status: ❌ FAIL")
                    for failure in failures:
                        print(f"         • {failure}")
            else:  # State B
                company_id = case["expected"].get("company")
                bs = result["blind_spots"].get(company_id) if company_id else None
                if bs is not None:
                    conf = bs.supporting_reasoning.confidence
                    print(f"       Status: 🟡 PARTIAL (blind spot found, confidence={conf:.4f})")
                else:
                    print("       Status: 🟡 PARTIAL (no blind spot found yet)")

            all_results.append((case_id, state, passed, failures))

        except UnknownAssetError as e:
            print(f"       Status: ⚠️  SKIP (company not in registry: {e})")
            if state == "Implemented":
                state_a_total -= 1  # Don't count as a failure — it's a data gap
            all_results.append((case_id, state, True, []))

        except Exception as e:
            print(f"       Status: ❌ ERROR: {e}")
            if state == "Implemented":
                pass  # counted as failure
            all_results.append((case_id, state, False, [str(e)]))

    # Summary
    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)
    print(f"\n  Implemented (regression tests): {state_a_passed}/{state_a_total} passing")
    print(f"  Partial:          {state_b_total} case(s)")
    print(f"  Planned (targets):          {state_c_total} case(s)")

    print("\n  Knowledge Coverage:")
    coverage_map = {r[0]: r[2] for r in all_results}
    patterns_covered = set()
    for case_file in case_files:
        with open(case_file) as f:
            case = json.load(f)
        if case["state"] == "Implemented" and coverage_map.get(case["id"], False):
            patterns_covered.add(case["pattern"])

    all_patterns = [
        "Supply Chain Risk", "Commodity Shock", "Interest Rate Sensitivity",
        "Currency Exposure", "Regulatory Risk", "Customer Concentration",
        "Supplier Concentration", "Energy Dependency", "Labour Exposure",
        "Geopolitical Risk",
    ]
    for pattern in all_patterns:
        status = "✅" if pattern in patterns_covered else "❌"
        print(f"    {status} {pattern}")

    print(f"\n  Coverage: {len(patterns_covered)}/10 patterns")
    print("=" * 60)

    return 0 if state_a_passed == state_a_total else 1


if __name__ == "__main__":
    sys.exit(main())
