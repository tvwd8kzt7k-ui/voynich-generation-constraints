#!/usr/bin/env python3
"""Reproduce external checks against Torsten Timm's fixed self-citation output.

This module is an external-model audit, not a manuscript decipherment and not a
rejection/confirmation of the broader self-citation hypothesis.  It compares a
pinned generated text against the repository's frozen 12-slot representation.

The generated text has page/line structure but no Voynich bifolio, hand, or
context metadata.  Those fields are therefore never invented.  Tests that need
such metadata are replaced only by explicitly labelled page-level analogs.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from canonical.core import ho, iter_clean42_records, support_for_family
from canonical.tests.low_dimensional_family import modal_stats, coverage

TIMM_COMMIT = "a6ede2202dd7ad6285ce2c007bf22c2a0e7709b7"
TIMM_PATH = "executable/generate/generated_text.txt"
TIMM_URL = f"https://raw.githubusercontent.com/TorstenTimm/SelfCitationTextgenerator/{TIMM_COMMIT}/{TIMM_PATH}"
TIMM_BLOB_SHA1 = "31b5f847097d6c31e210d1ebc23ea9878f456607"
DICTIONARY_ROOT = "source/src/main/java/de/voynich/text/canfollow/vms/"
DICTIONARY_BLOBS = {
    "VoynichGroups.java": "a06a1a57bd92a6087126109c5f275547b0d47e04",
    "VoynichGroupsTwo.java": "95883bd8472db6b8ef386e81b13e86814ab624df",
    "VoynichGroupsThree.java": "86b8bf5c6ce22964ea1e30a851f37a4a97d84741",
}

PAGE_LINES = 29
PAGE_HALF_CUT = 14
HIGH_COUNT = 21
ALPHA = 0.5
TAU_GRID = [5, 10, 20, 50, 100, 200]
FOCAL_TAU = 20
FIT_GRID = [1.0, 1.1, 1.25, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0]
LENGTH_REPS = 1000
LOWDIM_REPS = 250
SEED_LENGTH_BASE = 20260928
SEED_LOWDIM_BASE = 2026092800


class XorShift32:
    def __init__(self, seed: int):
        self.x = seed & 0xFFFFFFFF

    def random(self) -> float:
        x = self.x
        x ^= (x << 13) & 0xFFFFFFFF
        x ^= x >> 17
        x ^= (x << 5) & 0xFFFFFFFF
        self.x = x & 0xFFFFFFFF
        return self.x / 4294967296.0


def fetch_verified(url: str, path: Path, expected_blob: str, fetch=True) -> bytes:
    if path.exists():
        data = path.read_bytes()
    else:
        if not fetch:
            raise RuntimeError(f"missing input: {path}; use --fetch")
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read()
    got = ho.git_blob_sha1(data)
    if got != expected_blob:
        raise RuntimeError(f"input Git blob SHA-1 mismatch for {path}: {got} != {expected_blob}")
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return data


def generated_lines(text: str) -> list[str]:
    # This is a strict adapter for the pinned output format, not a generic EVA
    # reader. In particular, never silently drop malformed/empty body lines.
    lines = []
    for line in text.splitlines():
        if line.startswith("#") and not lines:
            continue
        if not re.fullmatch(r"[a-z]+(?: [a-z]+)* *", line):
            raise ValueError(f"malformed generator output at body line {len(lines) + 1}")
        lines.append(line)
    header = generator_header(text)
    if len(lines) != header["line_count"]:
        raise ValueError("malformed generator output: header/body line count mismatch")
    if header["lines_per_page"] != PAGE_LINES or len(lines) != 1200:
        raise ValueError("malformed generator output: unexpected page/line structure")
    return lines


def generator_header(text):
    patterns = {
        "line_count": r"#Line count: (\d+)",
        "lines_per_page": r"#text.lines_per_page=(\d+)",
        "in_dictionary": r"#VMS tokens count: (\d+) \(\d+ %\)",
        "out_of_dictionary": r"#None VMS token count: (\d+) \(\d+ %\)",
    }
    result = {}
    for key, pattern in patterns.items():
        values = re.findall("^" + pattern + "$", text, re.MULTILINE)
        if len(values) != 1:
            raise ValueError(f"malformed generator output: missing/duplicate {key}")
        result[key] = int(values[0])
    result["tokens"] = result["in_dictionary"] + result["out_of_dictionary"]
    return result


def load_dictionary(directory, fetch):
    words = set()
    for name, blob in DICTIONARY_BLOBS.items():
        url = f"https://raw.githubusercontent.com/TorstenTimm/SelfCitationTextgenerator/{TIMM_COMMIT}/{DICTIONARY_ROOT}{name}"
        source = fetch_verified(url, directory / name, blob, fetch).decode("utf-8")
        match = re.search(r"static final String\[\]\[\] GROUPS\s*=\s*\{(.*?)\};", source, re.DOTALL)
        if match is None:
            raise ValueError(f"malformed dictionary array: {name}")
        entries = re.findall(r'\{\s*"([^"\\]+)"\s*,\s*"\d+"\s*\}', match[1])
        remainder = re.sub(r'\{\s*"([^"\\]+)"\s*,\s*"\d+"\s*\}\s*,?', "", match[1])
        if not entries or remainder.strip():
            raise ValueError(f"unparsed dictionary entry: {name}")
        words.update(entries)
    return words


def dictionary_audit(text, lines, dictionary):
    counts = Counter((word in dictionary, decode_word(word) is not None)
                     for line in lines for word in line.split())
    header = generator_header(text)
    body_in = counts[True, True] + counts[True, False]
    body_out = counts[False, True] + counts[False, False]
    return {
        "definition": "VMS token = exact membership in the union of the three pinned VoynichGroups arrays; distinct from frozen 12-slot validity.",
        "dictionary_types": len(dictionary),
        "cross_classification": {
            "dictionary_and_valid": counts[True, True],
            "dictionary_and_invalid": counts[True, False],
            "not_dictionary_but_valid": counts[False, True],
            "neither": counts[False, False],
        },
        "header": header,
        "body": {"in_dictionary": body_in, "out_of_dictionary": body_out, "tokens": body_in + body_out},
        "header_minus_body": {
            "in_dictionary": header["in_dictionary"] - body_in,
            "out_of_dictionary": header["out_of_dictionary"] - body_out,
            "tokens": header["tokens"] - body_in - body_out,
        },
        "analysis_population": "Written body only; the header's extra two tokens are not inserted.",
    }


def decode_word(word: str):
    e = ho.normalize_eva(word)
    return ho.decode_slots(e) if e is not None else None


def family_of(exact: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        ho.FAMILY_MAP[j].get(face, face) if face else ""
        for j, face in enumerate(exact)
    )


def parse_timm(text: str):
    lines = generated_lines(text)
    rows = []
    rows_by_line = []
    raw_tokens = 0
    for line_idx, line in enumerate(lines):
        line_rows = []
        for word in line.split():
            raw_tokens += 1
            d = decode_word(word)
            if d is None:
                continue
            exact = tuple(d)
            row = {
                "line_global": line_idx,
                "page": line_idx // PAGE_LINES,
                "line": line_idx % PAGE_LINES,
                "exact": exact,
                "family": family_of(exact),
            }
            rows.append(row)
            line_rows.append(row)
        rows_by_line.append(line_rows)
    return lines, rows, rows_by_line, raw_tokens


def spectrum(exacts):
    counts = Counter(exacts)
    bins = {"1": 0, "2": 0, "3": 0, "4-5": 0, "6-10": 0, "11-20": 0, "21+": 0}
    for n in counts.values():
        if n == 1:
            bins["1"] += 1
        elif n == 2:
            bins["2"] += 1
        elif n == 3:
            bins["3"] += 1
        elif n <= 5:
            bins["4-5"] += 1
        elif n <= 10:
            bins["6-10"] += 1
        elif n <= 20:
            bins["11-20"] += 1
        else:
            bins["21+"] += 1
    types = len(counts)
    hapax = bins["1"]
    high = bins["21+"]
    return {
        "tokens": sum(counts.values()),
        "types": types,
        "hapax": hapax,
        "mid_2_to_20": sum(bins[k] for k in ("2", "3", "4-5", "6-10", "11-20")),
        "high_21_plus": high,
        "bins": bins,
        "type_token_ratio": types / sum(counts.values()),
        "hapax_type_share": hapax / types,
        "high_type_share": high / types,
    }


def quantiles(values):
    a = sorted(values)

    def q(p):
        h = (len(a) - 1) * p
        lo = math.floor(h)
        hi = math.ceil(h)
        if lo == hi:
            return a[lo]
        return a[lo] + (a[hi] - a[lo]) * (h - lo)

    return {"min": a[0], "p025": q(0.025), "p25": q(0.25), "median": q(0.5), "p75": q(0.75), "p975": q(0.975), "max": a[-1]}


def sample_without_replacement(rows, n: int, seed: int):
    if not 0 <= n <= len(rows):
        raise ValueError("sample size must be between zero and population size")
    rng = XorShift32(seed)
    idx = list(range(len(rows)))
    for i in range(n):
        j = i + int(rng.random() * (len(idx) - i))
        idx[i], idx[j] = idx[j], idx[i]
    return [rows[i] for i in idx[:n]]


def lowdim(rows):
    exact_counts = Counter(r["exact"] for r in rows)
    high_exact = {x for x, n in exact_counts.items() if n >= HIGH_COUNT}
    selected_families = {r["family"] for r in rows if r["exact"] in high_exact}
    by_family = defaultdict(list)
    for r in rows:
        if r["family"] in selected_families:
            by_family[r["family"]].append(r)

    weighted_hits = [0, 0, 0, 0]
    total = 0
    effectively_variable_le2 = 0
    top2_ge90 = 0
    top2_ge95 = 0
    lowercase_tie_hits = 0
    for fam in sorted(by_family):
        rs = by_family[fam]
        stats = [modal_stats(rs, j) for j in range(12)]
        # Sensitivity diagnostic ONLY. The primary modes above are imported
        # unchanged from canonical code (Python string ordering for ties).
        # This explicit alternative reproduces the supplied historical Box-0
        # median; its agreement does not identify the historical implementation.
        alternative_mode = []
        for j, st in enumerate(stats):
            counts = Counter(r["exact"][j] for r in rs)
            tied = [face for face, count in counts.items() if count == st["modal_n"]]
            alternative_mode.append(min(tied, key=lambda face: (face.lower(), face.isupper())))
        lowercase_tie_hits += exact_counts.get(tuple(alternative_mode), 0)
        ranked = [z["slot"] for z in sorted(stats, key=lambda z: (-z["variability"], -z["alternative_n"], z["slot"]))]
        cov = []
        for k in range(4):
            h, _ = coverage(rs, stats, ranked, k)
            weighted_hits[k] += h
            cov.append(h / len(rs))
        active = sum(z["modal_share"] < 0.95 and z["alternative_n"] >= 5 for z in stats)
        effectively_variable_le2 += active <= 2
        top2_ge90 += cov[2] >= 0.90
        top2_ge95 += cov[2] >= 0.95
        total += len(rs)

    return {
        "n_tokens": len(rows),
        "high_frequency_exact_forms": len(high_exact),
        "selected_families": len(selected_families),
        "selected_family_tokens": total,
        "weighted_box_coverage": {f"box{k}": weighted_hits[k] / total for k in range(4)},
        "families_with_at_most_2_effectively_variable_slots": effectively_variable_le2,
        "families_box2_ge_90": top2_ge90,
        "families_box2_ge_95": top2_ge95,
        "lowercase_first_tie_box0_sensitivity": lowercase_tie_hits / total,
    }


def line_local(rows_by_line, n_lines):
    n_pages = math.ceil(n_lines / PAGE_LINES)
    events = []
    linecounts = {}
    all_face_events = 0

    def add_count(key, face):
        z = linecounts.setdefault(key, {"n": 0, "c": Counter()})
        z["n"] += 1
        z["c"][face] += 1

    for page in range(n_pages):
        histories = defaultdict(list)
        for global_line in range(page * PAGE_LINES, min(n_lines, (page + 1) * PAGE_LINES)):
            local_line = global_line - page * PAGE_LINES
            word_pos = 0
            for r in rows_by_line[global_line]:
                word_pos += 1
                for j, face in enumerate(r["exact"]):
                    if not face:
                        continue
                    fam = ho.FAMILY_MAP[j].get(face, face)
                    faces = ho.FAMILY_MEMBERS[j].get(fam, [])
                    if len(faces) < 3:
                        continue
                    key = (j, fam)
                    all_face_events += 1
                    add_count((page, local_line, key), face)
                    hist = histories[key]
                    if hist:
                        prev = hist[-1]
                        events.append({"page": page, "line": local_line, "prev_line": prev["line"], "key": key, "face": face, "prev1": prev["face"], "cross": prev["line"] != local_line})
                    hist.append({"face": face, "line": local_line, "pos": word_pos})

    agg = {"within": {"obs": 0.0, "exp": 0.0, "n": 0}, "cross": {"obs": 0.0, "exp": 0.0, "n": 0}}
    for e in events:
        cur = linecounts.get((e["page"], e["line"], e["key"]))
        prv = linecounts.get((e["page"], e["prev_line"], e["key"]))
        side = "cross" if e["cross"] else "within"
        same = 1.0 if e["face"] == e["prev1"] else 0.0
        if not e["cross"]:
            if not cur or cur["n"] < 2:
                continue
            expected = sum(n * (n - 1) for n in cur["c"].values()) / (cur["n"] * (cur["n"] - 1))
        else:
            if not cur or not prv:
                continue
            faces = sorted(set(cur["c"]) | set(prv["c"]))
            expected = sum((cur["c"].get(f, 0) / cur["n"]) * (prv["c"].get(f, 0) / prv["n"]) for f in faces)
        z = agg[side]
        z["obs"] += same
        z["exp"] += expected
        z["n"] += 1

    def finish(z):
        return {"n": z["n"], "observed_same": z["obs"] / z["n"], "line_shuffle_expected": z["exp"] / z["n"], "excess": (z["obs"] - z["exp"]) / z["n"]}

    return {"within": finish(agg["within"]), "cross": finish(agg["cross"]), "all_multiface_events": all_face_events, "transitions": len(events)}


def length_control(timm_rows, z_rows):
    n = len(timm_rows)
    t = spectrum(r["exact"] for r in timm_rows)
    metrics = {k: [] for k in ("types", "hapax", "mid_2_to_20", "high_21_plus", "type_token_ratio", "hapax_type_share", "high_type_share")}
    for rep in range(LENGTH_REPS):
        s = spectrum(r["exact"] for r in sample_without_replacement(z_rows, n, SEED_LENGTH_BASE + rep))
        for k in metrics:
            metrics[k].append(s[k])
    dist = {k: quantiles(v) for k, v in metrics.items()}
    percentile = {k: sum(y <= t[k] for y in v) / LENGTH_REPS for k, v in metrics.items()}
    chunks = []
    for start in range(0, len(z_rows) - n + 1, n):
        chunks.append(spectrum(r["exact"] for r in z_rows[start:start+n]))
    return {"timm": t, "zl3b_uniform_subsample_n": n, "zl3b_uniform_subsample_reps": LENGTH_REPS, "zl3b_uniform_subsample_distribution": dist, "timm_empirical_percentile_among_zl3b_subsamples": percentile, "zl3b_nonoverlap_contiguous_chunks": chunks}


def lowdim_length_control(timm_rows, z_rows):
    t = lowdim(timm_rows)
    n = len(timm_rows)
    metric_names = ["selected_families", "selected_family_tokens"]
    box_names = ["box0", "box1", "box2", "box3"]
    vals = {k: [] for k in metric_names + box_names}
    tie_values = []
    changed_replicates = []
    for rep in range(LOWDIM_REPS):
        s = lowdim(sample_without_replacement(z_rows, n, SEED_LOWDIM_BASE + rep))
        for k in metric_names:
            vals[k].append(s[k])
        for k in box_names:
            vals[k].append(s["weighted_box_coverage"][k])
        tie_values.append(s["lowercase_first_tie_box0_sensitivity"])
        if tie_values[-1] != vals["box0"][-1]:
            changed_replicates.append({"replicate_index": rep, "canonical_box0": vals["box0"][-1], "lowercase_first_box0": tie_values[-1]})
    dist = {k: quantiles(v) for k, v in vals.items()}
    chunks = []
    for start in range(0, len(z_rows) - n + 1, n):
        chunks.append(lowdim(z_rows[start:start+n]))
    return {
        "definition": "Length-matched whole-population Box-k analog; exact count >=21 selects families within each sample. Not the published CAL8 statistic. Primary modal ties use unchanged canonical Python string ordering.",
        "timm": t,
        "zl3b_uniform_without_replacement": {"repetitions": LOWDIM_REPS, "n": n, "distribution": dist},
        "zl3b_nonoverlap_contiguous_chunks": chunks,
        "box0_modal_tie_sensitivity": {
            "definition": "Separate compatibility/sensitivity diagnostic: among equally frequent modal faces, minimize (face.lower(), face.isupper()). All other inputs and sampling are unchanged. Not the canonical tie rule; historical provenance of supplied median is unknown.",
            "canonical_median": dist["box0"]["median"],
            "lowercase_first_median": quantiles(tie_values)["median"],
            "changed_replicates_count": len(changed_replicates),
            "changed_replicates": changed_replicates,
        },
    }


def add_counter(store, key, face):
    z = store[key]
    z["n"] += 1
    z["c"][face] += 1


def subtract_counter(a, b):
    if a is None:
        return {"n": 0, "c": Counter()}
    bc = b["c"] if b else Counter()
    return {"n": a["n"] - (b["n"] if b else 0), "c": Counter({f: n - bc.get(f, 0) for f, n in a["c"].items() if n - bc.get(f, 0) > 0})}


def complete_page_rows(rows, n_lines):
    # Determine completeness from raw lines, not the location of valid tokens.
    n_full_pages = n_lines // PAGE_LINES
    out = [[] for _ in range(n_full_pages)]
    for r in rows:
        if r["page"] < n_full_pages:
            out[r["page"]].append(r)
    return out


def page_local(rows, n_lines):
    by_page = complete_page_rows(rows, n_lines)
    n_pages = len(by_page)
    events_by_page = defaultdict(list)
    all_events = []
    for page, rs in enumerate(by_page):
        for r in rs:
            half = 0 if r["line"] < PAGE_HALF_CUT else 1
            for j, (face, fam) in enumerate(zip(r["exact"], r["family"])):
                if not face or not fam:
                    continue
                members = ho.FAMILY_MEMBERS[j].get(fam, [face])
                if len(members) < 2:
                    continue
                e = {"page": page, "half": half, "slot": j, "family": fam, "face": face, "members": tuple(members)}
                events_by_page[page].append(e)
                all_events.append(e)

    empty = lambda: {"n": 0, "c": Counter()}
    total = defaultdict(empty)
    byp = defaultdict(empty)
    source = defaultdict(empty)
    for e in all_events:
        k = (e["slot"], e["family"])
        add_counter(total, k, e["face"])
        add_counter(byp, (e["page"], k), e["face"])
        add_counter(source, (e["page"], e["half"], e["slot"], e["family"]), e["face"])

    base_cache = {}

    def base_prob(e, target):
        k = (e["slot"], e["family"])
        ck = (target, k, e["face"])
        if ck in base_cache:
            return base_cache[ck]
        z = subtract_counter(total.get(k), byp.get((target, k)))
        q = (z["c"].get(e["face"], 0) + ALPHA) / (z["n"] + ALPHA * len(e["members"]))
        base_cache[ck] = q
        return q

    def score(target, target_half, source_page, source_half, tau):
        ll0 = ll = 0.0
        n = 0
        for e in events_by_page[target]:
            if e["half"] != target_half:
                continue
            q = base_prob(e, target)
            s = source.get((source_page, source_half, e["slot"], e["family"]))
            sn = s["n"] if s else 0
            sc = s["c"].get(e["face"], 0) if s else 0
            p = (sc + tau * q) / (sn + tau)
            ll0 += math.log(q)
            ll += math.log(p)
            n += 1
        return ll0, ll, n

    tau_grid = {}
    for tau in TAU_GRID:
        base_ll = true_ll = wrong_ll = 0.0
        n_total = better = 0
        page_delta = [0.0] * n_pages
        for target in range(n_pages):
            for source_half, target_half in ((0, 1), (1, 0)):
                ll0, ll, n = score(target, target_half, target, source_half, tau)
                wrong = [score(target, target_half, p, source_half, tau)[1] for p in range(n_pages) if p != target]
                mean_wrong = sum(wrong) / len(wrong)
                base_ll += ll0
                true_ll += ll
                wrong_ll += mean_wrong
                n_total += n
                better += ll > mean_wrong
                page_delta[target] += ll - mean_wrong
        tau_grid[str(tau)] = {"true_gain_over_global_baseline": (true_ll - base_ll) / n_total, "true_minus_wrong_page_mean": (true_ll - wrong_ll) / n_total, "true_better_wrong_mean_directions": better, "positive_pages_vs_wrong_mean": sum(x > 0 for x in page_delta), "n_events": n_total}

    tau = FOCAL_TAU
    base_ll = true_ll = wrong_ll = 0.0
    n_total = 0
    dirs = []
    page_gain = [0.0] * n_pages
    page_wrong = [0.0] * n_pages
    page_n = [0] * n_pages
    for target in range(n_pages):
        for source_half, target_half in ((0, 1), (1, 0)):
            ll0, ll, n = score(target, target_half, target, source_half, tau)
            wrong = [score(target, target_half, p, source_half, tau)[1] for p in range(n_pages) if p != target]
            mean_wrong = sum(wrong) / len(wrong)
            rank = 1 + sum(x > ll for x in wrong)
            dirs.append({"page": target + 1, "source_half": source_half, "target_half": target_half, "n_events": n, "true_gain": (ll - ll0) / n, "true_minus_wrong_mean": (ll - mean_wrong) / n, "rank_of_41": rank})
            base_ll += ll0
            true_ll += ll
            wrong_ll += mean_wrong
            n_total += n
            page_gain[target] += ll - ll0
            page_wrong[target] += ll - mean_wrong
            page_n[target] += n

    return {
        "definition": {"complete_pages": n_pages, "excluded_partial_lines": n_lines - n_pages * PAGE_LINES, "split": "half0 lines 1-14; half1 lines 15-29", "baseline": "P(face|slot,family), target page excluded, Jeffreys alpha=0.5", "local": "opposite-half counts shrunk to baseline", "tau_grid": TAU_GRID, "focal_tau": FOCAL_TAU, "wrong_source": "same source-half index from each of the other 40 complete pages"},
        "tau_grid": tau_grid,
        "directions": dirs,
        "per_page": [{"page": i + 1, "n_events": page_n[i], "true_gain": page_gain[i] / page_n[i], "true_minus_wrong_mean": page_wrong[i] / page_n[i]} for i in range(n_pages)],
        "focal": {"n_events": n_total, "base_ll_per_event": base_ll / n_total, "true_local_ll_per_event": true_ll / n_total, "true_gain": (true_ll - base_ll) / n_total, "true_minus_wrong_page_mean": (true_ll - wrong_ll) / n_total, "true_better_wrong_mean_directions": sum(d["true_minus_wrong_mean"] > 0 for d in dirs), "top1_directions": sum(d["rank_of_41"] == 1 for d in dirs), "top5_directions": sum(d["rank_of_41"] <= 5 for d in dirs), "positive_pages_true_gain": sum(page_gain[i] / page_n[i] > 0 for i in range(n_pages)), "positive_pages_vs_wrong_mean": sum(page_wrong[i] / page_n[i] > 0 for i in range(n_pages))},
    }


def subtract_two(a, b, c):
    if a is None:
        return {"n": 0, "c": Counter()}
    bc = b["c"] if b else Counter()
    cc = c["c"] if c else Counter()
    return {"n": a["n"] - (b["n"] if b else 0) - (c["n"] if c else 0), "c": Counter({x: n - bc.get(x, 0) - cc.get(x, 0) for x, n in a["c"].items() if n - bc.get(x, 0) - cc.get(x, 0) > 0})}


def page_reuse(rows, n_lines):
    by_page = complete_page_rows(rows, n_lines)
    n_pages = len(by_page)
    empty = lambda: {"n": 0, "c": Counter()}
    G = defaultdict(empty)
    PG = defaultdict(empty)
    supports = {}
    for page, rs in enumerate(by_page):
        for r in rs:
            fam, ex = r["family"], r["exact"]
            if fam not in supports:
                supports[fam] = support_for_family(fam)
            add_counter(G, fam, ex)
            add_counter(PG, (page, fam), ex)

    cache = {}

    def distribution(exclude1, exclude2, r):
        key = (exclude1, exclude2, r["family"])
        if key in cache:
            return cache[key]
        fam = r["family"]
        sup = supports[fam]
        g = subtract_two(G.get(fam), PG.get((exclude1, fam)), PG.get((exclude2, fam)) if exclude2 is not None else None)
        den = g["n"] + ALPHA * len(sup)
        probs = {ex: (g["c"].get(ex, 0) + ALPHA) / den for ex in sup}
        cache[key] = probs
        return probs

    def sequence_terms(seq_page, exclude1, exclude2=None):
        seen = defaultdict(dict)  # insertion order makes mass summation stable
        ll0 = 0.0
        terms = []
        for r in by_page[seq_page]:
            d = distribution(exclude1, exclude2, r)
            p0 = d[r["exact"]]
            ss = seen[r["family"]]
            mass = sum(d.get(x, 0.0) for x in ss)
            terms.append((r["exact"] in ss, mass))
            ll0 += math.log(p0)
            ss[r["exact"]] = None
        return ll0, terms

    def score(z, w):
        ll0, terms = z
        ll = ll0
        for hit, mass in terms:
            ll += (math.log(w) if hit else 0.0) - math.log(1 + (w - 1) * mass)
        return ll

    total0 = total1 = 0.0
    N = positive = 0
    fits = []
    per_page = []
    for target in range(n_pages):
        training = [sequence_terms(train, target, train) for train in range(n_pages) if train != target]
        bestw, bestll = 1.0, -math.inf
        for w in FIT_GRID:
            s = sum(score(z, w) for z in training)
            if s > bestll:
                bestll, bestw = s, w
        z = sequence_terms(target, target, None)
        l1 = score(z, bestw)
        n = len(z[1])
        total0 += z[0]
        total1 += l1
        N += n
        positive += l1 > z[0]
        fits.append(bestw)
        per_page.append({"page": target + 1, "n_tokens": n, "fitted_weight": bestw, "gain_per_token": (l1 - z[0]) / n})
        cache.clear()
    sf = sorted(fits)
    return {"definition": {"pages": n_pages, "baseline": "P(exact|family), Jeffreys alpha=.5 over theoretical frozen 12-slot support, target page excluded", "reuse": "within target page, every previously seen exact form in same family receives same multiplicative weight", "fit": "nested leave-one-page-out across the other 40 pages; fixed grid", "weight_grid": FIT_GRID}, "per_page": per_page, "result": {"n_tokens": N, "baseline_ll_per_token": total0 / N, "reuse_ll_per_token": total1 / N, "gain_per_token": (total1 - total0) / N, "positive_pages": positive, "fitted_weight": {"median": sf[len(sf)//2], "min": sf[0], "max": sf[-1], "counts": dict(Counter(str(x).rstrip("0").rstrip(".") for x in fits))}}}


def compare_subset(actual, expected, path="", tol=1e-10):
    errors = []
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [f"type mismatch {path}: expected object"]
        for k, v in expected.items():
            if k not in actual:
                errors.append(f"missing {path}/{k}")
            else:
                errors.extend(compare_subset(actual[k], v, f"{path}/{k}", tol))
    elif isinstance(expected, list):
        if not isinstance(actual, list):
            return [f"type mismatch {path}: expected array"]
        if len(actual) != len(expected):
            errors.append(f"length mismatch {path}: {len(actual)} != {len(expected)}")
        else:
            for i, v in enumerate(expected):
                errors.extend(compare_subset(actual[i], v, f"{path}/{i}", tol))
    elif isinstance(expected, float):
        if not isinstance(actual, (int, float)) or not math.isfinite(actual) or not math.isclose(actual, expected, rel_tol=tol, abs_tol=tol):
            errors.append(f"mismatch {path}: {actual!r} != {expected!r}")
    elif actual != expected:
        errors.append(f"mismatch {path}: {actual!r} != {expected!r}")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timm-input", type=Path, default=HERE / "data" / "generated_text.txt")
    ap.add_argument("--zl3b-input", type=Path, default=Path("data/ZL3b-n.txt"))
    ap.add_argument("--dictionary-dir", type=Path, default=HERE / "data")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--output", type=Path, default=HERE / "results.json")
    ap.add_argument("--check", type=Path)
    args = ap.parse_args()
    try:
        run(args)
    except (OSError, ValueError, RuntimeError) as exc:
        failure = {"status": "external-generator-reproducibility-audit", "verification": {"status": "failed", "errors": [str(exc)]}}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(failure, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raise SystemExit(f"AUDIT FAILED: {exc}") from exc


def run(args):

    timm_bytes = fetch_verified(TIMM_URL, args.timm_input, TIMM_BLOB_SHA1, args.fetch)
    zl_bytes = fetch_verified(ho.SOURCE_URL, args.zl3b_input, ho.EXPECTED_GIT_BLOB_SHA1, args.fetch)
    dictionary = load_dictionary(args.dictionary_dir, args.fetch)

    timm_text = timm_bytes.decode("utf-8")
    zl_text = zl_bytes.decode("utf-8")
    lines, timm_rows, rows_by_line, raw_tokens = parse_timm(timm_text)
    z_rows = list(iter_clean42_records(zl_text))

    result = {
        "status": "external-generator-reproducibility-audit",
        "source": {"timm_repository": "TorstenTimm/SelfCitationTextgenerator", "timm_commit": TIMM_COMMIT, "timm_path": TIMM_PATH, "timm_git_blob_sha1": TIMM_BLOB_SHA1, "dictionary_git_blobs": {DICTIONARY_ROOT + name: sha for name, sha in DICTIONARY_BLOBS.items()}, "zl3b_commit": ho.SOURCE_COMMIT, "zl3b_path": ho.SOURCE_PATH, "zl3b_git_blob_sha1": ho.EXPECTED_GIT_BLOB_SHA1},
        "adapter": {"raw_generated_lines": len(lines), "raw_whitespace_tokens": raw_tokens, "valid_12slot_tokens": len(timm_rows), "invalid_12slot_tokens": raw_tokens - len(timm_rows), "zl3b_clean42_valid_tokens": len(z_rows), "note": "Frozen EVA normalization and 12-slot decoder reused. No bifolio, hand, or context labels invented."},
        "dictionary_audit": dictionary_audit(timm_text, lines, dictionary),
        "sampling": {"algorithm": "xorshift32; forward partial Fisher-Yates; j = i + floor(U * (N-i)); replicate index starts at 0", "length_seed_base": SEED_LENGTH_BASE, "lowdim_seed_base": SEED_LOWDIM_BASE, "quantiles": "linear interpolation at (N-1)*p", "order": "canonical.core.iter_clean42_records"},
        "exact_form_spectrum": spectrum(r["exact"] for r in timm_rows),
        "line_preserving_null": line_local(rows_by_line, len(lines)),
        "length_controlled_spectrum": length_control(timm_rows, z_rows),
        "low_dimensional_family_analog": lowdim_length_control(timm_rows, z_rows),
        "page_local_opposite_half_analog": page_local(timm_rows, len(lines)),
        "page_scope_uniform_reuse_analog": page_reuse(timm_rows, len(lines)),
        "not_applicable": {
            "canonical_context_hand": "Generator output has no manuscript context or hand labels.",
            "canonical_bifolio_local": "No bifolio metadata; page-local result is an analog/positive control only.",
            "canonical_bifolio_context_reuse": "No bifolio/context baseline; page-scope effect magnitudes are not directly comparable.",
            "published_CAL8": "No manuscript CAL8 membership; whole-population length-matched Box-k analog only.",
        },
        "interpretation_ceiling": "This external-model audit characterizes one fixed published generator. It is not a decipherment, does not show that the VMS was generated by Timm's mechanism, does not prove self-citation or absence of semantics, and does not reject the broader self-citation/dynamic-production hypothesis.",
    }
    result["constraint_assessment"] = {
        "line_ordering_sign_pattern": "reproduced" if result["line_preserving_null"]["within"]["excess"] > 0 > result["line_preserving_null"]["cross"]["excess"] else "not_reproduced",
        "exact_types_and_hapax": {
            k: "below_length_matched_95pct_range" if result["exact_form_spectrum"][k] < result["length_controlled_spectrum"]["zl3b_uniform_subsample_distribution"][k]["p025"] else "not_below_range"
            for k in ("types", "hapax")
        },
        "box0_to_box2": {
            k: "below_length_matched_median" if result["low_dimensional_family_analog"]["timm"]["weighted_box_coverage"][k] < result["low_dimensional_family_analog"]["zl3b_uniform_without_replacement"]["distribution"][k]["median"] else "not_below_median"
            for k in ("box0", "box1", "box2")
        },
        "page_local": "positive_control_analog_only",
        "page_reuse": "analog_only_no_direct_manuscript_effect_size_comparison",
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    errors = []
    if args.check:
        expected = json.loads(args.check.read_text(encoding="utf-8"))
        if not isinstance(expected, dict) or not expected:
            raise ValueError("expected checkpoint must be a nonempty JSON object")
        errors = compare_subset(result, expected)
    result["verification"] = {"status": "failed" if errors else ("passed" if args.check else "not_requested"), "errors": errors, "tolerance": 1e-10}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "exact_form_spectrum": result["exact_form_spectrum"],
        "line_preserving_null": result["line_preserving_null"],
        "length_controlled_spectrum": {"timm": result["length_controlled_spectrum"]["timm"], "zl3b_distribution": result["length_controlled_spectrum"]["zl3b_uniform_subsample_distribution"]},
        "low_dimensional_family_analog": {"timm": result["low_dimensional_family_analog"]["timm"], "zl3b_distribution": result["low_dimensional_family_analog"]["zl3b_uniform_without_replacement"]["distribution"]},
        "page_local_focal": result["page_local_opposite_half_analog"]["focal"],
        "page_reuse": result["page_scope_uniform_reuse_analog"]["result"],
    }, ensure_ascii=False, indent=2))

    if args.check:
        if errors:
            print("CHECK FAILED")
            for e in errors:
                print(" -", e)
            raise SystemExit(1)
        print("CHECK OK")


if __name__ == "__main__":
    main()
