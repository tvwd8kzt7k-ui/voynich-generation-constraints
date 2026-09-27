#!/usr/bin/env python3
"""Canonical clean42 context-vs-hand exact-choice comparison.

This is a NEW canonical analysis, not a historical reconstruction.  It answers
only what the pinned current data/parser say under an explicit model.

For every held-out bifolio:
  global:        P(exact | family), Jeffreys alpha=0.5 over theoretical support
  context:       P(exact | family, I|L), shrunk to global with tau=100
  hand:          P(exact | family, H),   shrunk to global with tau=100
  context+hand:  P(exact | family, I|L, H), shrunk to context with tau=100

The 42 bifolios were repeatedly inspected historically, so these are frozen
exploratory/descriptive predictive comparisons, not pristine confirmation.
"""
from __future__ import annotations

import argparse
import sys
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from canonical.core import ho, iter_clean42_records, support_for_family

ALPHA = 0.5
TAU = 100.0


def add(store, key, exact):
    z = store[key]
    z["n"] += 1
    z["c"][exact] += 1


def subtract(a, b):
    if a is None:
        return {"n": 0, "c": Counter()}
    bc = b["c"] if b else Counter()
    return {
        "n": a["n"] - (b["n"] if b else 0),
        "c": Counter({x: n - bc.get(x, 0) for x, n in a["c"].items() if n - bc.get(x, 0) > 0}),
    }


def analyze(text: str):
    records = list(iter_clean42_records(text))
    empty = lambda: {"n": 0, "c": Counter()}
    G = defaultdict(empty); C = defaultdict(empty); H = defaultdict(empty); CH = defaultdict(empty)
    bG = defaultdict(empty); bC = defaultdict(empty); bH = defaultdict(empty); bCH = defaultdict(empty)
    support_size = {}

    for r in records:
        fam = r["family"]; ex = r["exact"]; bif = r["bifolio"]
        ctx = r["context"]; hand = r["hand"]
        support_size.setdefault(fam, len(support_for_family(fam)))
        add(G, fam, ex); add(C, (ctx, fam), ex); add(H, (hand, fam), ex); add(CH, (ctx, hand, fam), ex)
        add(bG, (bif, fam), ex); add(bC, (bif, ctx, fam), ex); add(bH, (bif, hand, fam), ex); add(bCH, (bif, ctx, hand, fam), ex)

    def p_global(r, target):
        fam=r["family"]; ex=r["exact"]
        g=subtract(G.get(fam), bG.get((target, fam)))
        k=support_size[fam]
        return (g["c"].get(ex,0)+ALPHA)/(g["n"]+ALPHA*k)

    def p_hier(a, ba, akey, bakey, r, base):
        c=subtract(a.get(akey), ba.get(bakey))
        return (c["c"].get(r["exact"],0)+TAU*base)/(c["n"]+TAU)

    totals=Counter(); per=[]
    by_bif=defaultdict(list)
    for r in records: by_bif[r["bifolio"]].append(r)
    for target in ho.CLEAN42:
        z=Counter()
        for r in by_bif[target]:
            pg=p_global(r,target)
            pc=p_hier(C,bC,(r["context"],r["family"]),(target,r["context"],r["family"]),r,pg)
            ph=p_hier(H,bH,(r["hand"],r["family"]),(target,r["hand"],r["family"]),r,pg)
            pch=p_hier(CH,bCH,(r["context"],r["hand"],r["family"]),(target,r["context"],r["hand"],r["family"]),r,pc)
            z["global"] += math.log(pg); z["context"] += math.log(pc); z["hand"] += math.log(ph); z["context_hand"] += math.log(pch); z["n"] += 1
        totals.update(z)
        per.append({
            "bifolio": target, "n": z["n"],
            "global_ll_per_token": z["global"]/z["n"],
            "context_ll_per_token": z["context"]/z["n"],
            "hand_ll_per_token": z["hand"]/z["n"],
            "context_hand_ll_per_token": z["context_hand"]/z["n"],
            "context_gain": (z["context"]-z["global"])/z["n"],
            "hand_gain": (z["hand"]-z["global"])/z["n"],
            "context_minus_hand": (z["context"]-z["hand"])/z["n"],
            "hand_after_context_gain": (z["context_hand"]-z["context"])/z["n"],
        })
    n=totals["n"]
    diffs=sorted(x["context_minus_hand"] for x in per)
    return {
        "status":"canonical-current-analysis",
        "model":{"alpha":ALPHA,"tau":TAU,"context":"IVTFF I|L","hand":"IVTFF H","support":"all concrete variants licensed by each family"},
        "n_tokens":n,"n_bifolios":42,
        "global_ll_per_token":totals["global"]/n,
        "context_ll_per_token":totals["context"]/n,
        "hand_ll_per_token":totals["hand"]/n,
        "context_hand_ll_per_token":totals["context_hand"]/n,
        "context_gain_over_global":(totals["context"]-totals["global"])/n,
        "hand_gain_over_global":(totals["hand"]-totals["global"])/n,
        "aggregate_context_minus_hand":(totals["context"]-totals["hand"])/n,
        "hand_after_context_gain":(totals["context_hand"]-totals["context"])/n,
        "context_beats_global_bifolios":sum(x["context_gain"]>0 for x in per),
        "hand_beats_global_bifolios":sum(x["hand_gain"]>0 for x in per),
        "context_beats_hand_bifolios":sum(x["context_minus_hand"]>0 for x in per),
        "context_hand_beats_context_bifolios":sum(x["hand_after_context_gain"]>0 for x in per),
        "median_bifolio_context_minus_hand":diffs[len(diffs)//2],
        "per_bifolio":per,
        "interpretation_ceiling":"Both context and hand predict exact choice beyond the global family-conditioned model. Aggregate context LL is slightly better here, but context does not dominate hand across bifolios; no robust context>hand ordering is claimed.",
    }


def compare_subset(actual, expected, path="", tol=1e-10):
    errors=[]
    if isinstance(expected,dict):
        for k,v in expected.items():
            if k not in actual: errors.append(f"missing {path}/{k}")
            else: errors.extend(compare_subset(actual[k],v,f"{path}/{k}",tol))
    elif isinstance(expected,float):
        if not math.isclose(float(actual),expected,rel_tol=tol,abs_tol=tol): errors.append(f"mismatch {path}: {actual!r} != {expected!r}")
    else:
        if actual!=expected: errors.append(f"mismatch {path}: {actual!r} != {expected!r}")
    return errors


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input",type=Path,required=True); ap.add_argument("--output",type=Path,default=Path("canonical/results/context_hand.json")); ap.add_argument("--check",type=Path)
    a=ap.parse_args(); data=a.input.read_bytes()
    if ho.git_blob_sha1(data)!=ho.EXPECTED_GIT_BLOB_SHA1: raise SystemExit("input Git blob SHA-1 mismatch")
    result=analyze(data.decode("utf-8")); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    if a.check:
        errors=compare_subset(result,json.loads(a.check.read_text(encoding="utf-8")))
        if errors:
            print("CHECK FAILED"); print("\n".join(" - "+x for x in errors)); raise SystemExit(1)
        print("CHECK OK")
    print(json.dumps({k:v for k,v in result.items() if k!="per_bifolio"},indent=2,ensure_ascii=False))
if __name__=="__main__": main()
