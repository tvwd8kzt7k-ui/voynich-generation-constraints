#!/usr/bin/env python3
"""Canonical low-dimensional within-family audit.

This is a current deterministic analysis, not a historical reconstruction.
It uses the pinned parser and the CAL8 subset.  First select every family that
contains at least one exact form occurring >=21 times in CAL8.  Then, using ALL
tokens from those selected families, rank slots by within-family variability.

Box-k means: keep the k most variable slots free and fix every other slot to
its family-specific modal concrete face.  Coverage is the token fraction that
falls inside that box.  No historical physical box or rule table is implied.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from canonical.core import ho, iter_clean42_records

CAL8 = {"C3", "F4", "M1", "A4", "M3", "B3", "T3", "C2"}
HIGH_COUNT = 21


def modal_stats(rows, j):
    c = Counter(r["exact"][j] for r in rows)
    # deterministic tie-break by face string
    mode, modal_n = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0]
    alt_n = sorted(c.values(), reverse=True)[1] if len(c) > 1 else 0
    n = len(rows)
    return {
        "slot": j,
        "mode": mode,
        "modal_n": modal_n,
        "modal_share": modal_n / n,
        "alternative_n": alt_n,
        "variability": 1.0 - modal_n / n,
    }


def coverage(rows, stats, ranked_slots, k):
    free = set(ranked_slots[:k])
    ok = 0
    for r in rows:
        if all(j in free or r["exact"][j] == stats[j]["mode"] for j in range(12)):
            ok += 1
    return ok, ok / len(rows)


def analyze(text: str):
    cal = [r for r in iter_clean42_records(text) if r["bifolio"] in CAL8]
    exact_counts = Counter(r["exact"] for r in cal)
    high_exact = {x for x, n in exact_counts.items() if n >= HIGH_COUNT}
    selected_families = {r["family"] for r in cal if r["exact"] in high_exact}

    by_family = defaultdict(list)
    for r in cal:
        if r["family"] in selected_families:
            by_family[r["family"]].append(r)

    per_family = []
    weighted_hits = [0, 0, 0, 0]
    total = 0
    effectively_variable_le2 = 0
    top2_ge90 = 0
    top2_ge95 = 0

    for fam in sorted(by_family):
        rows = by_family[fam]
        stats = [modal_stats(rows, j) for j in range(12)]
        ranked = [
            z["slot"]
            for z in sorted(stats, key=lambda z: (-z["variability"], -z["alternative_n"], z["slot"]))
        ]
        cov = []
        hits = []
        for k in range(4):
            h, c = coverage(rows, stats, ranked, k)
            hits.append(h)
            cov.append(c)
            weighted_hits[k] += h

        # explicit audit rule preserved from the recovered descriptive branch
        active = sum(z["modal_share"] < 0.95 and z["alternative_n"] >= 5 for z in stats)
        effectively_variable_le2 += active <= 2
        top2_ge90 += cov[2] >= 0.90
        top2_ge95 += cov[2] >= 0.95
        total += len(rows)

        per_family.append({
            "family": list(fam),
            "n_tokens": len(rows),
            "effective_variable_slots": active,
            "top_variable_slots_1based": [j + 1 for j in ranked[:3]],
            "box_coverage": {f"box{k}": cov[k] for k in range(4)},
        })

    return {
        "status": "canonical-current-analysis",
        "population": {
            "subset": "CAL8",
            "cal8_bifolios": sorted(CAL8),
            "cal8_valid_tokens": len(cal),
            "exact_high_count_threshold": HIGH_COUNT,
            "high_frequency_exact_forms": len(high_exact),
            "selected_families": len(selected_families),
            "selected_family_tokens": total,
        },
        "box_definition": "Within each selected family, rank slots by 1-modal-share (ties: alternative count, then slot). Box-k leaves top k slots free and fixes all remaining slots to their family modal face.",
        "weighted_box_coverage": {f"box{k}": weighted_hits[k] / total for k in range(4)},
        "families_with_at_most_2_effectively_variable_slots": effectively_variable_le2,
        "families_box2_coverage_ge_90pct": top2_ge90,
        "families_box2_coverage_ge_95pct": top2_ge95,
        "per_family": per_family,
        "interpretation_ceiling": "High-frequency CAL8 families occupy a low-dimensional subset of their theoretical concrete-face space. This is a structural description, not evidence for a literal box, table, or conscious slot rule.",
    }


def compare_subset(actual, expected, path="", tol=1e-12):
    errors = []
    if isinstance(expected, dict):
        for k, v in expected.items():
            if k not in actual:
                errors.append(f"missing {path}/{k}")
            else:
                errors.extend(compare_subset(actual[k], v, f"{path}/{k}", tol))
    elif isinstance(expected, float):
        if not math.isclose(float(actual), expected, rel_tol=tol, abs_tol=tol):
            errors.append(f"mismatch {path}: {actual!r} != {expected!r}")
    else:
        if actual != expected:
            errors.append(f"mismatch {path}: {actual!r} != {expected!r}")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=Path("canonical/results/low_dimensional_family.json"))
    ap.add_argument("--check", type=Path)
    a = ap.parse_args()
    data = a.input.read_bytes()
    if ho.git_blob_sha1(data) != ho.EXPECTED_GIT_BLOB_SHA1:
        raise SystemExit("input Git blob SHA-1 mismatch")
    result = analyze(data.decode("utf-8"))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if a.check:
        errors = compare_subset(result, json.loads(a.check.read_text(encoding="utf-8")))
        if errors:
            print("CHECK FAILED")
            print("\n".join(" - " + x for x in errors))
            raise SystemExit(1)
        print("CHECK OK")
    print(json.dumps({k: v for k, v in result.items() if k != "per_family"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
