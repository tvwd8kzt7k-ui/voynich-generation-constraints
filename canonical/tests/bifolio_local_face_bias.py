#!/usr/bin/env python3
"""Canonical bifolio-local concrete-face bias test.

This is a current explicit analysis, not a historical reconstruction.

Each clean bifolio has four physical pages in IVTFF P order.  Following the
existing cross-half diagnostics, pages [0,3] form half 0 and [1,2] half 1.
For every occupied slot whose family has >=2 concrete faces, predict the face.

Baseline:
  P(face | slot, family, context=I|L, hand=H), fit outside the target bifolio,
  Jeffreys alpha=0.5 over the family members.

Local adaptation:
  counts from the opposite half of one source bifolio are shrunk to the target
  baseline with equivalent sample size tau.

The tau grid is reported descriptively. tau=20 is the frozen focal setting
because it maximizes aggregate true-half likelihood on this exploratory grid.
A wrong-source control adapts the same target half with each of the other 41
bifolios and compares the true opposite half with their mean/rank.

This detects a bifolio-local shared state after conditioning on the named
context and hand fields. It does not identify a physical bag or inventory.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from canonical.core import ho, iter_clean42_records

ALPHA = 0.5
TAU_GRID = [5, 10, 20, 50, 100, 200]
FOCAL_TAU = 20


def add(store, key, face):
    z = store[key]
    z["n"] += 1
    z["c"][face] += 1


def subtract(a, b):
    if a is None:
        return {"n": 0, "c": Counter()}
    bc = b["c"] if b else Counter()
    return {
        "n": a["n"] - (b["n"] if b else 0),
        "c": Counter({f: n - bc.get(f, 0) for f, n in a["c"].items() if n - bc.get(f, 0) > 0}),
    }


def analyze(text: str):
    headers, _ = ho.parse_zl3b(text)
    pages_by_bif = defaultdict(list)
    for page, h in headers.items():
        if not ho.PAGE_RE.match(page) or not all(k in h for k in ("Q", "B", "P")):
            continue
        bif = h["Q"] + h["B"]
        if bif in ho.CLEAN42_SET:
            pages_by_bif[bif].append(page)
    for bif in pages_by_bif:
        pages_by_bif[bif].sort(key=lambda p: ho.POS_ORDER.get(headers[p].get("P", "Z"), 99))

    # Physical-half assignment.  With a complete four-page bifolio this is
    # exactly the same split as sorted IVTFF P positions [0,3] vs [1,2]:
    # lower-folio recto + higher-folio verso form half 0, while
    # lower-folio verso + higher-folio recto form half 1.
    #
    # Use physical page identity rather than list indices so the definition
    # remains valid when an alternate transcription omits one physical page
    # (IT2a omits f116v in clean42 bifolio T1).  No missing text is imputed.
    half_of_page = {}
    physical_page_re = re.compile(r"^f(\d+)([rv])$")
    for bif in ho.CLEAN42:
        pages = pages_by_bif[bif]
        parsed = []
        for p in pages:
            m = physical_page_re.match(p)
            if not m:
                raise RuntimeError(f"could not parse physical page id for {bif}: {p}")
            parsed.append((p, int(m.group(1)), m.group(2)))
        folios = sorted({n for _, n, _ in parsed})
        if len(folios) != 2 or len(parsed) < 3 or len(parsed) > 4:
            raise RuntimeError(
                f"expected 3-4 transcribed pages spanning two physical folios for {bif}, got {pages}"
            )
        low, high = folios
        for p, n, side in parsed:
            if n == low:
                half_of_page[p] = 0 if side == "r" else 1
            elif n == high:
                half_of_page[p] = 1 if side == "r" else 0

    events_by_bif = defaultdict(list)
    all_events = []
    for r in iter_clean42_records(text):
        half = half_of_page[r["page"]]
        for j, (face, fam) in enumerate(zip(r["exact"], r["family"])):
            if not face or not fam:
                continue
            members = ho.FAMILY_MEMBERS[j].get(fam, [face])
            if len(members) < 2:
                continue
            e = {
                "bifolio": r["bifolio"], "half": half, "slot": j,
                "family": fam, "face": face, "context": r["context"],
                "hand": r["hand"], "members": tuple(members),
            }
            events_by_bif[r["bifolio"]].append(e)
            all_events.append(e)

    empty = lambda: {"n": 0, "c": Counter()}
    total = defaultdict(empty)
    by_bif = defaultdict(empty)
    source = defaultdict(empty)
    for e in all_events:
        base_key = (e["slot"], e["family"], e["context"], e["hand"])
        add(total, base_key, e["face"])
        add(by_bif, (e["bifolio"], base_key), e["face"])
        add(source, (e["bifolio"], e["half"], e["slot"], e["family"]), e["face"])

    def base_prob(e, target):
        k = (e["slot"], e["family"], e["context"], e["hand"])
        z = subtract(total.get(k), by_bif.get((target, k)))
        K = len(e["members"])
        return (z["c"].get(e["face"], 0) + ALPHA) / (z["n"] + ALPHA * K)

    # Cache baseline p per target event: repeated across tau/wrong-source scans.
    cached = {}
    for bif in ho.CLEAN42:
        for i, e in enumerate(events_by_bif[bif]):
            cached[(bif, i)] = base_prob(e, bif)

    def score(target, target_half, source_bif, source_half, tau):
        ll0 = ll = 0.0
        n = 0
        for i, e in enumerate(events_by_bif[target]):
            if e["half"] != target_half:
                continue
            q = cached[(target, i)]
            s = source.get((source_bif, source_half, e["slot"], e["family"]))
            if s is None:
                sn = 0; sc = 0
            else:
                sn = s["n"]; sc = s["c"].get(e["face"], 0)
            p = (sc + tau * q) / (sn + tau)
            ll0 += math.log(q)
            ll += math.log(p)
            n += 1
        return {"ll0": ll0, "ll": ll, "n": n}

    tau_grid = {}
    for tau in TAU_GRID:
        base_ll = true_ll = wrong_mean_ll = 0.0
        n_total = 0
        better_mean_dirs = 0
        bif_acc = {b: {"wrong": 0.0, "n": 0} for b in ho.CLEAN42}
        for target in ho.CLEAN42:
            for source_half, target_half in ((0, 1), (1, 0)):
                tr = score(target, target_half, target, source_half, tau)
                wrong = [score(target, target_half, b, source_half, tau)["ll"] for b in ho.CLEAN42 if b != target]
                mean_wrong = sum(wrong) / len(wrong)
                base_ll += tr["ll0"]; true_ll += tr["ll"]; wrong_mean_ll += mean_wrong; n_total += tr["n"]
                better_mean_dirs += tr["ll"] > mean_wrong
                bif_acc[target]["wrong"] += tr["ll"] - mean_wrong
                bif_acc[target]["n"] += tr["n"]
        tau_grid[str(tau)] = {
            "true_gain_over_context_hand_baseline": (true_ll - base_ll) / n_total,
            "true_minus_wrong_source_mean": (true_ll - wrong_mean_ll) / n_total,
            "true_better_wrong_mean_directions": better_mean_dirs,
            "positive_bifolios_vs_wrong_mean": sum(z["wrong"] > 0 for z in bif_acc.values()),
        }

    # Detailed focal-tau output, including ranks against the 41 wrong sources.
    tau = FOCAL_TAU
    base_ll = true_ll = wrong_mean_ll = 0.0
    n_total = 0
    dirs = []
    for target in ho.CLEAN42:
        for source_half, target_half in ((0, 1), (1, 0)):
            tr = score(target, target_half, target, source_half, tau)
            wrong = [score(target, target_half, b, source_half, tau)["ll"] for b in ho.CLEAN42 if b != target]
            mean_wrong = sum(wrong) / len(wrong)
            rank = 1 + sum(x > tr["ll"] for x in wrong)
            dirs.append({
                "bifolio": target, "source_half": source_half, "target_half": target_half,
                "n_events": tr["n"], "true_gain": (tr["ll"] - tr["ll0"]) / tr["n"],
                "true_minus_wrong_mean": (tr["ll"] - mean_wrong) / tr["n"],
                "rank_of_42": rank,
            })
            base_ll += tr["ll0"]; true_ll += tr["ll"]; wrong_mean_ll += mean_wrong; n_total += tr["n"]

    per_bif = []
    for bif in ho.CLEAN42:
        ds = [d for d in dirs if d["bifolio"] == bif]
        n = sum(d["n_events"] for d in ds)
        per_bif.append({
            "bifolio": bif, "n_events": n,
            "true_gain": sum(d["true_gain"] * d["n_events"] for d in ds) / n,
            "true_minus_wrong_mean": sum(d["true_minus_wrong_mean"] * d["n_events"] for d in ds) / n,
        })

    return {
        "status": "canonical-current-analysis",
        "model": {
            "page_split": "physical bifolio halves: lower-folio recto + higher-folio verso vs lower-folio verso + higher-folio recto (equivalent to complete-page P-order [0,3] vs [1,2])",
            "event": "occupied slot-family concrete-face choice, only families with >=2 faces",
            "baseline": "P(face | slot, family, I|L, H), target bifolio excluded, Jeffreys alpha=0.5",
            "local_adaptation": "opposite-half slot-family counts shrunk to baseline with tau",
            "tau_grid": TAU_GRID,
            "focal_tau": FOCAL_TAU,
        },
        "n_events": n_total,
        "tau_grid": tau_grid,
        "focal": {
            "tau": tau,
            "base_ll_per_event": base_ll / n_total,
            "true_local_ll_per_event": true_ll / n_total,
            "true_gain": (true_ll - base_ll) / n_total,
            "true_minus_wrong_source_mean": (true_ll - wrong_mean_ll) / n_total,
            "true_better_wrong_mean_directions": sum(d["true_minus_wrong_mean"] > 0 for d in dirs),
            "top1_directions": sum(d["rank_of_42"] == 1 for d in dirs),
            "top5_directions": sum(d["rank_of_42"] <= 5 for d in dirs),
            "positive_bifolio_true_gain": sum(x["true_gain"] > 0 for x in per_bif),
            "positive_bifolio_vs_wrong_mean": sum(x["true_minus_wrong_mean"] > 0 for x in per_bif),
        },
        "per_bifolio": per_bif,
        "per_direction": dirs,
        "interpretation_ceiling": "The opposite half of the true bifolio carries residual predictive information about concrete face choice beyond a context+hand baseline and performs better than wrong-bifolio source halves. This supports a bifolio-local shared state but does not identify its historical implementation.",
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
    ap.add_argument("--output", type=Path, default=Path("canonical/results/bifolio_local_face_bias.json"))
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
    print(json.dumps({"n_events": result["n_events"], "tau_grid": result["tau_grid"], "focal": result["focal"], "interpretation_ceiling": result["interpretation_ceiling"]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
