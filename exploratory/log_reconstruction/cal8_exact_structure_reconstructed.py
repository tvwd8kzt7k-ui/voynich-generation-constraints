#!/usr/bin/env python3
"""Reconstruct two descriptive 2026-09-25/26 checkpoints from the research log.

Status: reconstructed-from-log, not recovered historical source.

This script deliberately reconstructs only checkpoints whose definitions can be
made explicit and whose logged numbers are matched exactly by the frozen 12-slot
parser:
  * CAL8 exact-form frequency spectrum;
  * high-frequency (count >= 21) within-family face-space neighborhood audit;
  * family-level variable-slot / weighted-coverage audit;
  * basic observed exact-form spectrum on clean42.

The variable-slot audit is reconstructed from the research log definition:
  * audit the 24 family forms containing at least one exact form with CAL8 count >= 21;
  * use all CAL8 tokens belonging to those family forms;
  * call a slot "effectively variable" when its modal face has <95% share and
    an alternative face occurs at least 5 times;
  * rank slots by 1 - modal-face share (ties: larger second-face count, then slot);
  * for top-k coverage, allow the k highest-ranked slots to vary freely and
    require every other slot to equal that family's modal face.

This reproduces the logged weighted top-1/top-2/top-3 coverages and family
threshold counts. It is reconstructed-from-log, not recovered historical source.

It does NOT reconstruct the old reuse simulations or context-vs-hand LOBO.
Those remain reference-only because the log record does not preserve enough
implementation detail to identify a unique historical procedure.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FROZEN = ROOT / "frozen" / "human_operation" / "run_freeze.py"

spec = importlib.util.spec_from_file_location("human_operation_freeze", FROZEN)
if spec is None or spec.loader is None:
    raise RuntimeError(f"could not import frozen parser: {FROZEN}")
ho = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ho)

CAL8 = {"C3", "F4", "M1", "A4", "M3", "B3", "T3", "C2"}
HIGH_FREQ_THRESHOLD = 21


def iter_records(text: str, allowed_bifolios: set[str]):
    headers, lines = ho.parse_zl3b(text)
    for page, h in headers.items():
        if not ho.PAGE_RE.match(page) or not all(k in h for k in ("Q", "B", "P")):
            continue
        bif = h["Q"] + h["B"]
        if bif not in allowed_bifolios:
            continue
        for code, body in lines.get(page, []):
            if not (len(code) >= 2 and code[1] == "P"):
                continue
            for word in ho.clean_tokens(body):
                eva = ho.normalize_eva(word)
                slots = ho.decode_slots(eva) if eva is not None else None
                if slots is None:
                    continue
                family = tuple(
                    ho.FAMILY_MAP[j].get(face, face) if face else ""
                    for j, face in enumerate(slots)
                )
                yield {
                    "bifolio": bif,
                    "exact": tuple(slots),
                    "family": family,
                    "skeleton": tuple(bool(face) for face in slots),
                }


def bins(counter: Counter[tuple[str, ...]]):
    out = {"1": 0, "2": 0, "3": 0, "4-5": 0, "6-10": 0, "11-20": 0, "21+": 0}
    for n in counter.values():
        if n == 1:
            out["1"] += 1
        elif n == 2:
            out["2"] += 1
        elif n == 3:
            out["3"] += 1
        elif n <= 5:
            out["4-5"] += 1
        elif n <= 10:
            out["6-10"] += 1
        elif n <= 20:
            out["11-20"] += 1
        else:
            out["21+"] += 1
    return out


def hamming(a: tuple[str, ...], b: tuple[str, ...]) -> int:
    return sum(x != y for x, y in zip(a, b))



def dominant_stats(forms: list[tuple[str, ...]], slot: int):
    c = Counter(form[slot] for form in forms)
    ranked = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))
    modal_face, modal_n = ranked[0]
    alt_n = ranked[1][1] if len(ranked) > 1 else 0
    n = len(forms)
    return {
        "modal_face": modal_face,
        "modal_count": modal_n,
        "modal_share": modal_n / n,
        "alternative_count": alt_n,
        "variability": 1.0 - modal_n / n,
    }


def family_variable_slot_audit(
    records: list[dict],
    high_families: set[tuple[str, ...]],
):
    by_family = defaultdict(list)
    for r in records:
        if r["family"] in high_families:
            by_family[r["family"]].append(r["exact"])

    total_tokens = sum(len(forms) for forms in by_family.values())
    covered = {1: 0, 2: 0, 3: 0}
    active_hist = Counter()
    top2_ge_90 = 0
    top2_ge_95 = 0
    per_family = []

    for family, forms in sorted(by_family.items()):
        stats = [dominant_stats(forms, j) for j in range(12)]
        active = sum(
            s["modal_share"] < 0.95 and s["alternative_count"] >= 5
            for s in stats
        )
        active_hist[active] += 1

        ranked_slots = sorted(
            range(12),
            key=lambda j: (
                -stats[j]["variability"],
                -stats[j]["alternative_count"],
                j,
            ),
        )

        cov = {}
        for k in (1, 2, 3):
            free = set(ranked_slots[:k])
            ok = 0
            for form in forms:
                if all(
                    j in free or form[j] == stats[j]["modal_face"]
                    for j in range(12)
                ):
                    ok += 1
            cov[k] = ok / len(forms)
            covered[k] += ok

        if cov[2] >= 0.90:
            top2_ge_90 += 1
        if cov[2] >= 0.95:
            top2_ge_95 += 1

        per_family.append({
            "family": list(family),
            "n_tokens": len(forms),
            "effectively_variable_slots": active,
            "top_slots_1indexed": [j + 1 for j in ranked_slots[:3]],
            "coverage_top1": cov[1],
            "coverage_top2": cov[2],
            "coverage_top3": cov[3],
        })

    return {
        "audited_families": len(by_family),
        "family_tokens": total_tokens,
        "active_variable_definition": {
            "modal_face_share_lt": 0.95,
            "alternative_face_count_ge": 5,
        },
        "families_with_at_most_2_effectively_variable_slots": sum(
            n for k, n in active_hist.items() if k <= 2
        ),
        "active_variable_slot_histogram": {str(k): active_hist[k] for k in sorted(active_hist)},
        "slot_ranking": "descending 1-modal_share; tie by alternative_count then slot index",
        "weighted_coverage": {
            "top1": covered[1] / total_tokens,
            "top2": covered[2] / total_tokens,
            "top3": covered[3] / total_tokens,
        },
        "families_top2_coverage_ge_90pct": top2_ge_90,
        "families_top2_coverage_ge_95pct": top2_ge_95,
        "per_family": per_family,
    }



def clean42_raw_cross_half_recurrence(text: str):
    """Raw Q3-style exact recurrence on strict line interiors.

    For each clean bifolio, sort its four pages by IVTFF $P, split pages
    [0,3] versus [1,2], and score both directions.  The source repertoire is
    the set of exact forms occurring at strict line-interior positions; target
    tokens are also strict line-interior positions.  Aggregate token-weighted.
    """
    headers, lines = ho.parse_zl3b(text)
    pages_by_bif = defaultdict(list)

    for page, h in headers.items():
        if not ho.PAGE_RE.match(page) or not all(k in h for k in ("Q", "B", "P")):
            continue
        bif = h["Q"] + h["B"]
        if bif not in set(ho.CLEAN42):
            continue

        strict = []
        for code, body in lines.get(page, []):
            if not (len(code) >= 2 and code[1] == "P"):
                continue
            line_forms = []
            for word in ho.clean_tokens(body):
                eva = ho.normalize_eva(word)
                slots = ho.decode_slots(eva) if eva is not None else None
                if slots is not None:
                    line_forms.append(tuple(slots))
            if len(line_forms) >= 3:
                strict.extend(line_forms[1:-1])

        pages_by_bif[bif].append({"P": h["P"], "strict": strict})

    hits = 0
    targets = 0
    per_bifolio = {}
    for bif in sorted(ho.CLEAN42):
        pages = sorted(pages_by_bif[bif], key=lambda x: x["P"])
        if len(pages) != 4:
            raise RuntimeError(f"expected four pages for {bif}, got {len(pages)}")
        b_hits = 0
        b_targets = 0
        for source_idx, target_idx in (((0, 3), (1, 2)), ((1, 2), (0, 3))):
            repertoire = set()
            for i in source_idx:
                repertoire.update(pages[i]["strict"])
            for i in target_idx:
                for form in pages[i]["strict"]:
                    b_targets += 1
                    if form in repertoire:
                        b_hits += 1
        hits += b_hits
        targets += b_targets
        per_bifolio[bif] = {
            "hits": b_hits,
            "targets": b_targets,
            "rate": b_hits / b_targets if b_targets else None,
        }

    return {
        "split": "pages [0,3] vs [1,2], both directions",
        "positions": "strict line interiors for both source repertoire and target",
        "hits": hits,
        "target_tokens": targets,
        "rate": hits / targets,
        "per_bifolio": per_bifolio,
    }


def analyze(text: str):
    cal_records = list(iter_records(text, CAL8))
    cal_counts = Counter(r["exact"] for r in cal_records)

    high = {exact: n for exact, n in cal_counts.items() if n >= HIGH_FREQ_THRESHOLD}
    exact_to_family = {}
    exact_to_skeleton = {}
    for r in cal_records:
        if r["exact"] in high:
            exact_to_family[r["exact"]] = r["family"]
            exact_to_skeleton[r["exact"]] = r["skeleton"]

    by_family = defaultdict(list)
    for exact in high:
        by_family[exact_to_family[exact]].append(exact)

    pair_dists = Counter()
    for forms in by_family.values():
        for i in range(len(forms)):
            for j in range(i + 1, len(forms)):
                pair_dists[hamming(forms[i], forms[j])] += 1

    variable_audit = family_variable_slot_audit(cal_records, set(by_family))

    clean_records = list(iter_records(text, set(ho.CLEAN42)))
    clean_counts = Counter(r["exact"] for r in clean_records)
    clean_n = len(clean_records)
    clean_recurrence = clean42_raw_cross_half_recurrence(text)

    return {
        "status": "reconstructed-from-log",
        "source": {
            "repository": "matthewdgreen/cipher_benchmark",
            "commit": ho.SOURCE_COMMIT,
            "path": ho.SOURCE_PATH,
            "expected_git_blob_sha1": ho.EXPECTED_GIT_BLOB_SHA1,
        },
        "cal8_exact_frequency": {
            "bifolios": sorted(CAL8),
            "n_tokens": len(cal_records),
            "unique_exact_types": len(cal_counts),
            "type_bins": bins(cal_counts),
        },
        "cal8_high_frequency_neighborhood": {
            "threshold_count_ge": HIGH_FREQ_THRESHOLD,
            "exact_forms": len(high),
            "distinct_family_forms": len(by_family),
            "distinct_skeletons": len(set(exact_to_skeleton.values())),
            "within_family_pairwise_face_hamming": {
                "pairs": sum(pair_dists.values()),
                "distance_1": pair_dists[1],
                "distance_2": pair_dists[2],
                "distance_ge_3": sum(n for d, n in pair_dists.items() if d >= 3),
            },
        },
        "cal8_family_variable_slot_audit": variable_audit,
        "clean42_observed_exact_spectrum": {
            "n_tokens": clean_n,
            "unique_exact_types": len(clean_counts),
            "ttr": len(clean_counts) / clean_n,
            "hapax": sum(n == 1 for n in clean_counts.values()),
            "count_ge_21": sum(n >= 21 for n in clean_counts.values()),
            "count_ge_50": sum(n >= 50 for n in clean_counts.values()),
            "raw_cross_half_exact_recurrence": clean_recurrence,
        },
        "not_reconstructed_here": [
            "CAL8 reuse simulations and their random/sampling implementation",
            "context-vs-hand LOBO preprocessing/model formula",
            "conditional global/context simulation layer",
        ],
    }


def compare_subset(actual, expected, path="", tol=1e-10):
    errors = []
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [f"{path}: expected object"]
        for k, v in expected.items():
            if k not in actual:
                errors.append(f"{path}/{k}: missing")
            else:
                errors.extend(compare_subset(actual[k], v, f"{path}/{k}", tol))
    elif isinstance(expected, list):
        if actual != expected:
            errors.append(f"{path}: {actual!r} != {expected!r}")
    elif isinstance(expected, float):
        if not isinstance(actual, (int, float)) or abs(float(actual) - expected) > tol:
            errors.append(f"{path}: {actual!r} != {expected!r}")
    elif actual != expected:
        errors.append(f"{path}: {actual!r} != {expected!r}")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--check", type=Path)
    ap.add_argument("--allow-source-mismatch", action="store_true")
    args = ap.parse_args()

    data = args.input.read_bytes()
    got = ho.git_blob_sha1(data)
    if got != ho.EXPECTED_GIT_BLOB_SHA1 and not args.allow_source_mismatch:
        raise SystemExit(f"input blob mismatch: got {got}, expected {ho.EXPECTED_GIT_BLOB_SHA1}")
    result = analyze(data.decode("utf-8"))
    result["source"]["actual_git_blob_sha1"] = got

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))

    if args.check:
        expected = json.loads(args.check.read_text(encoding="utf-8"))
        errors = compare_subset(result, expected)
        if errors:
            print("CHECK FAILED")
            for e in errors:
                print(" -", e)
            return 1
        print("CHECK PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
