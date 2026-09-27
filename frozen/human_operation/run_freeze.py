#!/usr/bin/env python3
"""Reproduce the 2026-09-26 'human-operation' diagnostics for ZL3b.

Scope: post-v1 exploratory/frozen diagnostics only. This does NOT reproduce the
published v1.0 report end-to-end.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

SOURCE_COMMIT = "729aad62d12483c549e64a2541d4f9255538c8cf"
SOURCE_PATH = "benchmark/unsolved/sources/voynich/transcriptions/ZL3b-n.txt"
SOURCE_URL = f"https://raw.githubusercontent.com/matthewdgreen/cipher_benchmark/{SOURCE_COMMIT}/{SOURCE_PATH}"
EXPECTED_GIT_BLOB_SHA1 = "2a4533ab9bdfa85db9bad602d590978953055df1"

HERE = Path(__file__).resolve().parent
CLEAN42 = [x.strip() for x in (HERE / "clean42.txt").read_text(encoding="utf-8").splitlines() if x.strip()]
if len(CLEAN42) != 42 or len(set(CLEAN42)) != 42:
    raise RuntimeError("clean42.txt must contain exactly 42 unique bifolio keys")
CLEAN42_SET = set(CLEAN42)

SLOTS = [
    ["q","s","d"], ["o","y"], ["l","r"], ["k","p","t","f"],
    ["S","C"], ["K","P","T","F"], ["e","E","B"], ["s","d"],
    ["o","a"], ["i","J","U"], ["d","l","r","m","n"], ["y"],
]
FAMILY_MAP = [
    {"q":"Q","s":"SD","d":"SD"}, {"o":"OY","y":"OY"},
    {"l":"LR","r":"LR"}, {"k":"GAL","p":"GAL","t":"GAL","f":"GAL"},
    {"S":"BENCH","C":"BENCH"}, {"K":"PED","P":"PED","T":"PED","F":"PED"},
    {"e":"ERUN","E":"ERUN","B":"ERUN"}, {"s":"SD","d":"SD"},
    {"o":"OA","a":"OA"}, {"i":"IRUN","J":"IRUN","U":"IRUN"},
    {"d":"D","l":"END","r":"END","m":"END","n":"END"}, {"y":"Y"},
]
FAMILY_MEMBERS: List[Dict[str, List[str]]] = []
for mapping in FAMILY_MAP:
    out: Dict[str, List[str]] = defaultdict(list)
    for concrete, fam in mapping.items():
        out[fam].append(concrete)
    FAMILY_MEMBERS.append(dict(out))

ALLOWED = set(x for slot in SLOTS for x in slot)
POS_ORDER = {c: i for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
VAR_RE = re.compile(r"\$([A-Z])=([A-Za-z0-9@])")
HEADER_RE = re.compile(r"^<([^>]+)>\s+(.*)$")
PAGE_RE = re.compile(r"^f\d+[rv]$")
BAD_TOKEN_RE = re.compile(r"[\[\]\{\}\?@<>:0-9'\"=_/\\\-]")

GRID = [0.5,0.7,0.85,1.0,1.1,1.25,1.5,1.75,2.0,2.5,3.0]
TAU = 100.0


def git_blob_sha1(data: bytes) -> str:
    h = hashlib.sha1()
    h.update(f"blob {len(data)}\0".encode("ascii"))
    h.update(data)
    return h.hexdigest()


def fetch_input(path: Path) -> None:
    data = urllib.request.urlopen(SOURCE_URL, timeout=60).read()
    got = git_blob_sha1(data)
    if got != EXPECTED_GIT_BLOB_SHA1:
        raise RuntimeError(f"input blob mismatch: got {got}, expected {EXPECTED_GIT_BLOB_SHA1}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def normalize_eva(word: str) -> str | None:
    s = word
    for a, b in [
        ("ckh","K"),("cfh","F"),("cth","T"),("cph","P"),
        ("ch","C"),("sh","S"),("eee","B"),("ee","E"),
        ("iii","U"),("ii","J"),
    ]:
        s = s.replace(a, b)
    if re.search(r"[gvxujbz']", s) or "c" in s or "h" in s:
        return None
    if any(ch not in ALLOWED for ch in s):
        return None
    return s


def _promote(a: List[str], c: str, begin: int, end: int) -> None:
    if a[begin] == c and all(x == "" for x in a[begin+1:end+1]):
        a[begin] = ""
        a[end] = c


def decode_slots(s: str) -> List[str] | None:
    a = [""] * 12
    rest = s
    for i, options in enumerate(SLOTS):
        for o in options:
            if rest.startswith(o):
                a[i] = o
                rest = rest[len(o):]
                break
    if rest:
        return None
    _promote(a, "y", 1, 11)
    _promote(a, "d", 0, 10)
    _promote(a, "d", 7, 10)
    _promote(a, "r", 2, 10)
    _promote(a, "l", 2, 10)
    _promote(a, "o", 1, 8)
    _promote(a, "d", 0, 7)
    _promote(a, "s", 0, 7)
    return a


def clean_tokens(body: str) -> List[str]:
    body = re.sub(r"<!.*?>", "", body)
    body = body.replace("<->", ".").replace("<$>", ".").replace("<%>", ".")
    toks = re.split(r"[\s\.,]+", body)
    return [
        t for t in toks
        if t and not BAD_TOKEN_RE.search(t) and re.fullmatch(r"[a-z]+", t)
    ]


def parse_zl3b(text: str):
    headers: Dict[str, Dict[str, str]] = {}
    lines: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    for raw in text.splitlines():
        m = HEADER_RE.match(raw)
        if not m:
            continue
        tag, body = m.group(1), m.group(2)
        if "." not in tag and body.lstrip().startswith("<!"):
            headers[tag] = {k: v for k, v in VAR_RE.findall(body)}
        elif "." in tag:
            page = tag.split(".", 1)[0]
            code = tag.split(",", 1)[1] if "," in tag else ""
            lines[page].append((code, body))
    return headers, lines


def add_count(store, key, face, n=1):
    z = store.setdefault(key, {"n": 0, "c": Counter()})
    z["n"] += n
    z["c"][face] += n


def subtract_counts(a, b):
    if a is None:
        return None
    z = {"n": a["n"] - (b["n"] if b else 0), "c": Counter()}
    for f, n in a["c"].items():
        v = n - (b["c"].get(f, 0) if b else 0)
        if v > 0:
            z["c"][f] = v
    return z


def build_data(headers, lines):
    bif_pages: Dict[str, List[str]] = defaultdict(list)
    for page, h in headers.items():
        if not PAGE_RE.match(page) or not all(k in h for k in ("Q","B","P")):
            continue
        bif = h["Q"] + h["B"]
        if bif in CLEAN42_SET:
            bif_pages[bif].append(page)
    for bif in bif_pages:
        bif_pages[bif].sort(key=lambda p: POS_ORDER.get(headers[p].get("P", "Z"), 99))

    tot, ctot, btot, bctot = {}, {}, {}, {}
    keyfaces: Dict[str, List[str]] = {}
    events = []
    linecounts = {}
    all_face_events = 0

    for bif in CLEAN42:
        for page in bif_pages.get(bif, []):
            h = headers[page]
            ctx = f"{h.get('I','?')}|{h.get('L','?')}"
            word_pos = 0
            histories = defaultdict(list)
            line_idx = 0
            for code, body in lines.get(page, []):
                if not (len(code) >= 2 and code[1] == "P"):
                    continue
                for word in clean_tokens(body):
                    word_pos += 1
                    e = normalize_eva(word)
                    d = decode_slots(e) if e is not None else None
                    if d is None:
                        continue
                    for j, face in enumerate(d):
                        if not face:
                            continue
                        fam = FAMILY_MAP[j].get(face, face)
                        faces = FAMILY_MEMBERS[j].get(fam, [])
                        if len(faces) < 3:
                            continue
                        key = f"{j+1}|{fam}"
                        keyfaces[key] = list(faces)
                        all_face_events += 1
                        add_count(tot, key, face)
                        add_count(ctot, f"{ctx}||{key}", face)
                        add_count(btot, f"{bif}||{key}", face)
                        add_count(bctot, f"{bif}||{ctx}||{key}", face)
                        add_count(linecounts, f"{page}|{line_idx}|{key}", face)

                        hist = histories[key]
                        if hist:
                            prev1 = hist[-1]
                            prev2 = hist[-2] if len(hist) >= 2 else None
                            gap1 = word_pos - prev1["pos"]
                            events.append({
                                "bif": bif, "page": page, "ctx": ctx, "key": key,
                                "face": face, "prev1": prev1["face"],
                                "prev_line": prev1["line"], "line": line_idx,
                                "cross": prev1["line"] != line_idx,
                                "gap1": gap1, "bin": gap_bin(gap1),
                                "prev2": prev2["face"] if prev2 else None,
                            })
                        hist.append({"face": face, "pos": word_pos, "line": line_idx})
                line_idx += 1

    return {
        "bif_pages": bif_pages, "tot": tot, "ctot": ctot, "btot": btot,
        "bctot": bctot, "keyfaces": keyfaces, "events": events,
        "linecounts": linecounts, "all_face_events": all_face_events,
    }


def gap_bin(g: int) -> str:
    if g <= 2: return "1-2"
    if g <= 5: return "3-5"
    if g <= 10: return "6-10"
    if g <= 20: return "11-20"
    return "21+"


def base_dist(data, key, ctx, target, tau=TAU):
    g = subtract_counts(data["tot"].get(key), data["btot"].get(f"{target}||{key}"))
    if not g or not g["n"]:
        return None
    faces = data["keyfaces"][key]
    K = len(faces)
    c = subtract_counts(data["ctot"].get(f"{ctx}||{key}"), data["bctot"].get(f"{target}||{ctx}||{key}"))
    pg = {f: (g["c"].get(f, 0) + 0.5) / (g["n"] + 0.5*K) for f in faces}
    if c and c["n"]:
        return {f: (c["c"].get(f, 0) + tau*pg[f]) / (c["n"] + tau) for f in faces}
    return pg


def boosted_prob(base, face, promotions):
    den = 0.0
    num = 0.0
    for f, p in base.items():
        w = 1.0
        for pr_face, pr_w in promotions:
            if f == pr_face:
                w *= pr_w
        v = p * w
        den += v
        if f == face:
            num = v
    return num / den


def fit_w(data, target, selector, extra_promotions=None):
    best_w, best_ll = 1.0, -math.inf
    for w in GRID:
        ll = 0.0
        n = 0
        for e in data["events"]:
            if e["bif"] == target or not selector(e):
                continue
            base = base_dist(data, e["key"], e["ctx"], target)
            if not base:
                continue
            promos = [(e["prev1"], w)]
            if extra_promotions:
                promos.extend(extra_promotions(e))
            p = boosted_prob(base, e["face"], promos)
            ll += math.log(max(p, 1e-15)); n += 1
        if n and ll > best_ll:
            best_ll, best_w = ll, w
    return best_w


def summarize(values):
    a = sorted(values)
    counts = Counter(str(v).rstrip("0").rstrip(".") if isinstance(v, float) else str(v) for v in a)
    return {
        "median": a[len(a)//2], "min": a[0], "max": a[-1],
        "counts": dict(counts),
    }


def recency_lobo(data):
    ll0 = ll1 = 0.0; N = 0; positive = 0
    by_key_fits = defaultdict(list)
    for target in CLEAN42:
        w_key = {}
        for key in data["keyfaces"]:
            best_w, best_ll = 1.0, -math.inf
            for w in GRID:
                ll = 0.0; n = 0
                for e in data["events"]:
                    if e["bif"] == target or e["key"] != key:
                        continue
                    base = base_dist(data, key, e["ctx"], target)
                    if not base: continue
                    ll += math.log(max(boosted_prob(base, e["face"], [(e["prev1"], w)]), 1e-15)); n += 1
                if n and ll > best_ll:
                    best_ll, best_w = ll, w
            w_key[key] = best_w
            by_key_fits[key].append(best_w)
        b0 = b1 = 0.0; bn = 0
        for e in data["events"]:
            if e["bif"] != target: continue
            base = base_dist(data, e["key"], e["ctx"], target)
            if not base: continue
            b0 += math.log(max(base[e["face"]], 1e-15))
            b1 += math.log(max(boosted_prob(base, e["face"], [(e["prev1"], w_key[e["key"]])]), 1e-15))
            bn += 1
        ll0 += b0; ll1 += b1; N += bn
        if b1 > b0: positive += 1
    return {
        "transitions": len(data["events"]),
        "baseline_ll_per_token": ll0/N,
        "recency_ll_per_token": ll1/N,
        "gain_per_token": (ll1-ll0)/N,
        "positive_bifolio": positive,
        "fit_w_by_key": {k: summarize(v) for k, v in sorted(by_key_fits.items())},
    }


def distance_lobo(data):
    bins = ["1-2","3-5","6-10","11-20","21+"]
    ll0 = ll_gap = ll_lag2 = 0.0; N = 0; pos_gap = pos_lag2 = 0
    fits = defaultdict(list); lag2_fits = []
    for target in CLEAN42:
        wb = {}
        for b in bins:
            w = fit_w(data, target, lambda e, b=b: e["bin"] == b)
            wb[b] = w; fits[b].append(w)
        best2, best_ll2 = 1.0, -math.inf
        for w2 in GRID:
            ll = 0.0; n = 0
            for e in data["events"]:
                if e["bif"] == target or e["prev2"] is None: continue
                base = base_dist(data, e["key"], e["ctx"], target)
                if not base: continue
                p = boosted_prob(base, e["face"], [(e["prev1"], wb[e["bin"]]), (e["prev2"], w2)])
                ll += math.log(max(p, 1e-15)); n += 1
            if n and ll > best_ll2:
                best_ll2, best2 = ll, w2
        lag2_fits.append(best2)
        b0 = b1 = b2 = 0.0; bn = 0
        for e in data["events"]:
            if e["bif"] != target: continue
            base = base_dist(data, e["key"], e["ctx"], target)
            if not base: continue
            p0 = base[e["face"]]
            p1 = boosted_prob(base, e["face"], [(e["prev1"], wb[e["bin"]])])
            promos = [(e["prev1"], wb[e["bin"]])]
            if e["prev2"] is not None: promos.append((e["prev2"], best2))
            p2 = boosted_prob(base, e["face"], promos)
            b0 += math.log(max(p0, 1e-15)); b1 += math.log(max(p1, 1e-15)); b2 += math.log(max(p2, 1e-15)); bn += 1
        ll0 += b0; ll_gap += b1; ll_lag2 += b2; N += bn
        if b1 > b0: pos_gap += 1
        if b2 > b1: pos_lag2 += 1
    return {
        "by_gap_n": {b: sum(e["bin"] == b for e in data["events"]) for b in bins},
        "baseline_ll_per_token": ll0/N,
        "gap_model_ll_per_token": ll_gap/N,
        "gap_gain_per_token": (ll_gap-ll0)/N,
        "positive_bifolio_gap": pos_gap,
        "lag2_model_ll_per_token": ll_lag2/N,
        "lag2_increment_per_token": (ll_lag2-ll_gap)/N,
        "positive_bifolio_lag2": pos_lag2,
        "fitted_w_by_gap": {b: summarize(fits[b]) for b in bins},
        "fitted_lag2_weight": summarize(lag2_fits),
    }


def line_reset_lobo(data):
    ll0 = ll1 = 0.0; N = 0; positive = 0
    win, wcross = [], []
    lobo_per_bifolio = []
    for target in CLEAN42:
        wi = fit_w(data, target, lambda e: not e["cross"])
        wc = fit_w(data, target, lambda e: e["cross"])
        win.append(wi); wcross.append(wc)
        b0 = b1 = 0.0; bn = 0
        for e in data["events"]:
            if e["bif"] != target: continue
            base = base_dist(data, e["key"], e["ctx"], target)
            if not base: continue
            b0 += math.log(max(base[e["face"]], 1e-15))
            b1 += math.log(max(boosted_prob(base, e["face"], [(e["prev1"], wc if e["cross"] else wi)]), 1e-15)); bn += 1
        ll0 += b0; ll1 += b1; N += bn
        if b1 > b0: positive += 1
        lobo_per_bifolio.append({
            "bifolio": target, "n": bn,
            "within_weight": wi, "cross_weight": wc,
            "gain_per_token": (b1-b0)/bn if bn else None,
        })

    perm = {
        "within": {"obs":0.0,"exp":0.0,"n":0},
        "cross": {"obs":0.0,"exp":0.0,"n":0},
    }
    per_bif = {b:{"within":{"obs":0.0,"exp":0.0,"n":0},"cross":{"obs":0.0,"exp":0.0,"n":0}} for b in CLEAN42}
    per_family = defaultdict(lambda:{"within":{"obs":0.0,"exp":0.0,"n":0},"cross":{"obs":0.0,"exp":0.0,"n":0}})

    for e in data["events"]:
        cur = data["linecounts"].get(f"{e['page']}|{e['line']}|{e['key']}")
        prv = data["linecounts"].get(f"{e['page']}|{e['prev_line']}|{e['key']}")
        same = 1.0 if e["face"] == e["prev1"] else 0.0
        side = "cross" if e["cross"] else "within"
        if not e["cross"]:
            if not cur or cur["n"] < 2: continue
            ex = sum(n*(n-1) for n in cur["c"].values()) / (cur["n"]*(cur["n"]-1))
        else:
            if not cur or not prv: continue
            faces = set(cur["c"]) | set(prv["c"])
            ex = sum((cur["c"].get(f,0)/cur["n"]) * (prv["c"].get(f,0)/prv["n"]) for f in faces)
        for z in (perm[side], per_bif[e["bif"]][side], per_family[e["key"]][side]):
            z["obs"] += same; z["exp"] += ex; z["n"] += 1

    def finalize(z):
        if not z["n"]:
            return {"n":0,"observed_same":None,"line_shuffle_expected":None,"excess":None}
        return {
            "n": z["n"],
            "observed_same": z["obs"]/z["n"],
            "line_shuffle_expected": z["exp"]/z["n"],
            "excess": (z["obs"]-z["exp"])/z["n"],
        }

    perm_out = {k:finalize(z) for k,z in perm.items()}
    per_bif_out = {b:{side:finalize(z) for side,z in sides.items()} for b,sides in per_bif.items()}
    per_family_out = {k:{side:finalize(z) for side,z in sides.items()} for k,sides in sorted(per_family.items())}

    return {
        "transitions": len(data["events"]),
        "within_events": sum(not e["cross"] for e in data["events"]),
        "cross_line_events": sum(e["cross"] for e in data["events"]),
        "baseline_ll_per_token": ll0/N,
        "separate_weights_ll_per_token": ll1/N,
        "gain_per_token": (ll1-ll0)/N,
        "positive_bifolio": positive,
        "fitted_within_line_weight": summarize(win),
        "fitted_cross_line_weight": summarize(wcross),
        "line_preserving_permutation": perm_out,
        "per_bifolio_lobo": lobo_per_bifolio,
        "per_bifolio_line_null": per_bif_out,
        "per_family_line_null": per_family_out,
        "within_positive_bifolios": sum(v["within"]["excess"] is not None and v["within"]["excess"] > 0 for v in per_bif_out.values()),
        "cross_positive_bifolios": sum(v["cross"]["excess"] is not None and v["cross"]["excess"] > 0 for v in per_bif_out.values()),
    }

def page_permutation_distance(data):
    # Analytic page/key multiset-preserving null for same-face transitions by gap.
    bins = ["1-2","3-5","6-10","11-20","21+"]
    seqs = defaultdict(list)
    # Reconstruct occurrence sequence from transition events: first prev plus each current.
    # Unique page/key sequences are obtained by sorting transitions in their original append order.
    # Since events retain append order, group in encounter order.
    grouped = defaultdict(list)
    for e in data["events"]:
        grouped[(e["bif"],e["page"],e["key"])].append(e)
    agg = {b:{"obs":0.0,"exp":0.0,"n":0} for b in bins}
    lag2 = {"obs":0.0,"exp":0.0,"n":0}
    per_bif = {b:{"obs":0.0,"exp":0.0,"n":0} for b in CLEAN42}
    for (bif,page,key), es in grouped.items():
        faces = [es[0]["prev1"]] + [e["face"] for e in es]
        counts = Counter(faces); nseq = len(faces)
        p_same = sum(n*(n-1) for n in counts.values())/(nseq*(nseq-1))
        for e in es:
            same = 1.0 if e["face"] == e["prev1"] else 0.0
            z = agg[e["bin"]]; z["obs"] += same; z["exp"] += p_same; z["n"] += 1
            q = per_bif[bif]; q["obs"] += same; q["exp"] += p_same; q["n"] += 1
        for i in range(2, len(faces)):
            lag2["obs"] += 1.0 if faces[i] == faces[i-2] else 0.0
            lag2["exp"] += p_same; lag2["n"] += 1
    by_gap = {b:{
        "n":z["n"], "observed_same":z["obs"]/z["n"],
        "shuffle_expected_same":z["exp"]/z["n"], "excess":(z["obs"]-z["exp"])/z["n"]
    } for b,z in agg.items()}
    total_n = sum(z["n"] for z in agg.values())
    total_obs = sum(z["obs"] for z in agg.values())
    total_exp = sum(z["exp"] for z in agg.values())
    return {
        "by_gap": by_gap,
        "overall": {
            "n": total_n, "observed_same": total_obs/total_n,
            "shuffle_expected_same": total_exp/total_n,
            "positive_bifolio": sum(q["n"] and q["obs"]/q["n"] > q["exp"]/q["n"] for q in per_bif.values()),
        },
        "lag2": {
            "n": lag2["n"], "observed_same":lag2["obs"]/lag2["n"],
            "shuffle_expected_same":lag2["exp"]/lag2["n"], "excess":(lag2["obs"]-lag2["exp"])/lag2["n"],
        },
    }


def compare_subset(actual, expected, path="", tol=1e-10):
    errors = []
    if isinstance(expected, dict):
        for k, v in expected.items():
            if k not in actual:
                errors.append(f"missing {path}/{k}")
            else:
                errors.extend(compare_subset(actual[k], v, f"{path}/{k}", tol))
    elif isinstance(expected, list):
        if actual != expected: errors.append(f"mismatch {path}: {actual!r} != {expected!r}")
    elif isinstance(expected, float):
        if not math.isclose(float(actual), expected, rel_tol=tol, abs_tol=tol):
            errors.append(f"mismatch {path}: {actual!r} != {expected!r}")
    else:
        if actual != expected: errors.append(f"mismatch {path}: {actual!r} != {expected!r}")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, default=Path("data/ZL3b-n.txt"))
    ap.add_argument("--fetch", action="store_true", help="download the pinned mirror snapshot if input is missing")
    ap.add_argument("--output", type=Path, default=Path("results/human_operation_freeze.json"))
    ap.add_argument("--check", type=Path, default=None, help="compare result against expected-results JSON subset")
    args = ap.parse_args()
    if not args.input.exists():
        if not args.fetch:
            raise SystemExit(f"missing input: {args.input}; use --fetch or supply --input")
        fetch_input(args.input)
    data_bytes = args.input.read_bytes()
    got_blob = git_blob_sha1(data_bytes)
    if got_blob != EXPECTED_GIT_BLOB_SHA1:
        raise SystemExit(f"input Git blob SHA-1 mismatch: {got_blob} != {EXPECTED_GIT_BLOB_SHA1}")

    headers, lines = parse_zl3b(data_bytes.decode("utf-8"))
    data = build_data(headers, lines)
    result = {
        "metadata": {
            "scope": "post-v1 human-operation diagnostics frozen 2026-09-26",
            "source_commit": SOURCE_COMMIT,
            "source_path": SOURCE_PATH,
            "source_git_blob_sha1": got_blob,
            "clean42": CLEAN42,
            "tau": TAU,
            "weight_grid": GRID,
            "all_multiface_events": data["all_face_events"],
        },
        "recency_lobo": recency_lobo(data),
        "distance_lobo": distance_lobo(data),
        "page_multiset_permutation": page_permutation_distance(data),
        "line_reset_lobo": line_reset_lobo(data),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if args.check:
        expected = json.loads(args.check.read_text(encoding="utf-8"))
        errors = compare_subset(result, expected)
        if errors:
            print("CHECK FAILED")
            for e in errors: print(" -", e)
            raise SystemExit(1)
        print("CHECK OK")

if __name__ == "__main__":
    main()
