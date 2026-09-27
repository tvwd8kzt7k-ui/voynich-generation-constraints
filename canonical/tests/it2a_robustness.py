#!/usr/bin/env python3
"""Cross-transcription robustness pass on pinned IT2a.

This is NOT a new model fit and does not claim that all transcriptions have
been tested.  It applies the current canonical analyses, unchanged in their
scientific definitions, to one alternate EVA transcription: IT2a.

The raw transcription is not redistributed.  Input identity is pinned by Git
blob SHA-1.  The parser is the same shared canonical parser used for ZL3b.
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
from canonical.tests import low_dimensional_family as lowdim
from canonical.tests import context_hand
from canonical.tests import uniform_reuse
from canonical.tests import bifolio_local_face_bias as biflocal

IT2A_REPOSITORY = "oklo/voynich_gpt"
IT2A_COMMIT = "2d7c61c387ad6962de730caf73c48612bc8f6957"
IT2A_PATH = "IT2a-n.txt"
IT2A_GIT_BLOB_SHA1 = "7f491b574b65e5fba6b553e57372c3fa50e10fec"


def finalize(z):
    if not z["n"]:
        return {"n": 0, "observed_same": None, "line_shuffle_expected": None, "excess": None}
    return {
        "n": z["n"],
        "observed_same": z["obs"] / z["n"],
        "line_shuffle_expected": z["exp"] / z["n"],
        "excess": (z["obs"] - z["exp"]) / z["n"],
    }


def line_composition_null(text: str):
    """Same line-composition-preserving ordering statistic as frozen ZL3b branch.

    Uses only multi-face slot families with >=3 members, matching the frozen
    human-operation branch.  No historical production mechanism is assumed.
    """
    records = list(iter_clean42_records(text))
    linecounts = defaultdict(lambda: {"n": 0, "c": Counter()})
    histories = defaultdict(list)  # (page,key) -> ordered occurrences
    events = []
    all_multiface_events = 0

    for r in records:
        for j, face in enumerate(r["exact"]):
            if not face:
                continue
            fam = r["family"][j]
            members = ho.FAMILY_MEMBERS[j].get(fam, [])
            if len(members) < 3:
                continue
            key = f"{j+1}|{fam}"
            lk = (r["page"], r["line"], key)
            linecounts[lk]["n"] += 1
            linecounts[lk]["c"][face] += 1
            all_multiface_events += 1

            hk = (r["page"], key)
            hist = histories[hk]
            if hist:
                prev = hist[-1]
                events.append({
                    "bifolio": r["bifolio"],
                    "page": r["page"],
                    "key": key,
                    "face": face,
                    "prev_face": prev["face"],
                    "line": r["line"],
                    "prev_line": prev["line"],
                    "cross": prev["line"] != r["line"],
                })
            hist.append({"face": face, "line": r["line"]})

    agg = {"within": {"obs": 0.0, "exp": 0.0, "n": 0}, "cross": {"obs": 0.0, "exp": 0.0, "n": 0}}
    per_bif = {
        b: {"within": {"obs": 0.0, "exp": 0.0, "n": 0}, "cross": {"obs": 0.0, "exp": 0.0, "n": 0}}
        for b in ho.CLEAN42
    }
    per_family = defaultdict(lambda: {
        "within": {"obs": 0.0, "exp": 0.0, "n": 0},
        "cross": {"obs": 0.0, "exp": 0.0, "n": 0},
    })

    for e in events:
        cur = linecounts.get((e["page"], e["line"], e["key"]))
        prv = linecounts.get((e["page"], e["prev_line"], e["key"]))
        same = 1.0 if e["face"] == e["prev_face"] else 0.0
        side = "cross" if e["cross"] else "within"
        if not e["cross"]:
            if not cur or cur["n"] < 2:
                continue
            ex = sum(n * (n - 1) for n in cur["c"].values()) / (cur["n"] * (cur["n"] - 1))
        else:
            if not cur or not prv:
                continue
            faces = set(cur["c"]) | set(prv["c"])
            ex = sum((cur["c"].get(f, 0) / cur["n"]) * (prv["c"].get(f, 0) / prv["n"]) for f in faces)
        for z in (agg[side], per_bif[e["bifolio"]][side], per_family[e["key"]][side]):
            z["obs"] += same
            z["exp"] += ex
            z["n"] += 1

    within = finalize(agg["within"])
    cross = finalize(agg["cross"])
    return {
        "all_multiface_events": all_multiface_events,
        "transitions": len(events),
        "within": within,
        "cross": cross,
        "within_positive_bifolios": sum(finalize(v["within"])["excess"] > 0 for v in per_bif.values()),
        "cross_positive_bifolios": sum(finalize(v["cross"])["excess"] > 0 for v in per_bif.values()),
        "per_family": {
            k: {"within": finalize(v["within"]), "cross": finalize(v["cross"])}
            for k, v in sorted(per_family.items())
        },
        "interpretation_ceiling": "The line-composition-preserving ordering pattern is tested in IT2a as a transcription-robustness check only; it does not identify a historical mechanism.",
    }


def compact_uniform(result):
    return {
        "conditional_lobo": {k: v for k, v in result["conditional_lobo"].items() if k != "per_bifolio"},
        "spectrum_simulation": {
            "observed": result["spectrum_simulation"]["observed"],
            "weights": {w: z["summary"] for w, z in result["spectrum_simulation"]["weights"].items()},
            "n_replicates": result["spectrum_simulation"]["n_replicates"],
        },
    }


def analyze(text: str):
    ld = lowdim.analyze(text)
    ch = context_hand.analyze(text)
    ur = uniform_reuse.analyze(text)
    bl = biflocal.analyze(text)
    ln = line_composition_null(text)

    return {
        "status": "canonical-cross-transcription-robustness",
        "source": {
            "transcription": "IT2a",
            "repository": IT2A_REPOSITORY,
            "commit": IT2A_COMMIT,
            "path": IT2A_PATH,
            "git_blob_sha1": IT2A_GIT_BLOB_SHA1,
            "redistributed": False,
        },
        "scope": "One alternate EVA transcription only. This is evidence against ZL3b-specific transcription artifacts, not a claim of robustness across all transcriptions.",
        "low_dimensional_family": {
            "population": ld["population"],
            "weighted_box_coverage": ld["weighted_box_coverage"],
            "families_with_at_most_2_effectively_variable_slots": ld["families_with_at_most_2_effectively_variable_slots"],
            "families_box2_coverage_ge_90pct": ld["families_box2_coverage_ge_90pct"],
            "families_box2_coverage_ge_95pct": ld["families_box2_coverage_ge_95pct"],
        },
        "context_hand": {k: v for k, v in ch.items() if k not in ("per_bifolio", "model", "interpretation_ceiling", "status")},
        "uniform_reuse": compact_uniform(ur),
        "bifolio_local_face_bias": {
            "n_events": bl["n_events"],
            "focal": {
                k: v for k, v in bl["focal"].items()
                if k in (
                    "tau", "base_ll_per_event", "true_local_ll_per_event", "true_gain",
                    "true_minus_wrong_source_mean", "true_better_wrong_mean_directions",
                    "positive_bifolio_true_gain", "positive_bifolio_vs_wrong_mean",
                )
            },
        },
        "line_local_ordering": ln,
        "interpretation_ceiling": "The main current structural/predictive patterns survive this IT2a pass. This narrows transcription-specific-artifact explanations but does not establish mechanical historical production, semantic absence, or universality across transcriptions.",
    }


def compare_subset(actual, expected, path="", tol=1e-10):
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
    ap.add_argument("--output", type=Path, default=Path("canonical/results/it2a_robustness.json"))
    ap.add_argument("--check", type=Path)
    a = ap.parse_args()
    data = a.input.read_bytes()
    got = ho.git_blob_sha1(data)
    if got != IT2A_GIT_BLOB_SHA1:
        raise SystemExit(f"IT2a input Git blob SHA-1 mismatch: {got} != {IT2A_GIT_BLOB_SHA1}")
    result = analyze(data.decode("utf-8"))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if a.check:
        expected = json.loads(a.check.read_text(encoding="utf-8"))
        errors = compare_subset(result, expected)
        if errors:
            print("CHECK FAILED")
            print("\n".join(" - " + x for x in errors))
            raise SystemExit(1)
        print("CHECK OK")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
