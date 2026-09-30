#!/usr/bin/env python3
"""Voynich Generative Diagnostic Toolkit (VGDT) v0.1.

A mechanism-oriented diagnostic panel for EVA-like Voynich text and candidate
Voynich-like generators.  It does NOT compute a scalar "Voynich similarity"
score.  Each corpus is profiled against nulls constructed from that corpus.

Frozen v0.1 panel:
  * 12-slot FAMILY normalization
  * FAMILY spectrum: types / hapax / 2-20 / 21+ / Top-10 share
  * cue-conditioned exact-FAMILY lag spectrum
  * OUTER+CUE and LINE+CUE composition-preserving nulls
  * consecutive-return gaps
  * 21-50 same-cue decomposition into direct / chained returns

Standard-library only. Python 3.10+.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

VERSION = "0.1.0"
PROTOCOL_ID = "VGDT-FAMILY-NULLS-2026-09-30-v0.1"

# ---------------------------------------------------------------------------
# Frozen 12-slot representation
# ---------------------------------------------------------------------------
SLOTS = [
    ["q", "s", "d"], ["o", "y"], ["l", "r"], ["k", "p", "t", "f"],
    ["S", "C"], ["K", "P", "T", "F"], ["e", "E", "B"], ["s", "d"],
    ["o", "a"], ["i", "J", "U"], ["d", "l", "r", "m", "n"], ["y"],
]
FAMILY_MAP = [
    {"q": "Q", "s": "SD", "d": "SD"}, {"o": "OY", "y": "OY"},
    {"l": "LR", "r": "LR"}, {"k": "GAL", "p": "GAL", "t": "GAL", "f": "GAL"},
    {"S": "BENCH", "C": "BENCH"}, {"K": "PED", "P": "PED", "T": "PED", "F": "PED"},
    {"e": "ERUN", "E": "ERUN", "B": "ERUN"}, {"s": "SD", "d": "SD"},
    {"o": "OA", "a": "OA"}, {"i": "IRUN", "J": "IRUN", "U": "IRUN"},
    {"d": "D", "l": "END", "r": "END", "m": "END", "n": "END"}, {"y": "Y"},
]
ALLOWED = {x for slot in SLOTS for x in slot}
BAD_TOKEN_RE = re.compile(r"[\[\]\{\}\?@<>:0-9'\"=_/\\\-]")

CLEAN42 = [
    "A1","A2","A3","A4","B1","B2","B3","C1","C2","C3","C4",
    "D1","D2","D3","D4","E1","E2","E3","E4","F1","F2","F3","F4",
    "G1","G2","G3","G4","H1","H2","M1","M2","M3","M4","M5","Q1",
    "S2","T1","T2","T3","T4","T5","T6",
]
CLEAN42_SET = set(CLEAN42)
PAGE_RE = re.compile(r"^f\d+[rv]$")
HEADER_RE = re.compile(r"^<([^>]+)>\s+(.*)$")
VAR_RE = re.compile(r"\$([A-Z])=([A-Za-z0-9@])")

LAG_BINS = [(1,1),(2,5),(6,10),(11,20),(21,50),(51,100)]
LAG_LABELS = ["1","2-5","6-10","11-20","21-50","51-100"]
RETURN_BINS = [(1,1),(2,5),(6,10),(11,20),(21,50),(51,100),(101,None)]
RETURN_LABELS = ["1","2-5","6-10","11-20","21-50","51-100","101+"]
DEFAULT_PERMUTATIONS = 400
DEFAULT_SPECTRUM_REPS = 500

# Pinned external sources used by the reference-suite command.
SOURCES = {
    "zl3b": {
        "url": "https://raw.githubusercontent.com/matthewdgreen/cipher_benchmark/729aad62d12483c549e64a2541d4f9255538c8cf/benchmark/unsolved/sources/voynich/transcriptions/ZL3b-n.txt",
        "blob": "2a4533ab9bdfa85db9bad602d590978953055df1",
        "filename": "ZL3b-n.txt",
    },
    "timm": {
        "url": "https://raw.githubusercontent.com/TorstenTimm/SelfCitationTextgenerator/a6ede2202dd7ad6285ce2c007bf22c2a0e7709b7/executable/generate/generated_text.txt",
        "blob": "31b5f847097d6c31e210d1ebc23ea9878f456607",
        "filename": "timm_generated_text.txt",
    },
    "naibbe": {
        "url": "https://raw.githubusercontent.com/greshko/naibbe-cipher/f2675ec5dd275268bc64dd48ea64fc0e0e9827a2/encrypted/nathist_output_ciphertext_respaced.txt",
        "blob": "c95b95507e603ca9a7b0dadba2d13eb314e9b7ea",
        "filename": "naibbe_nathist_respaced.txt",
    },
}


def git_blob_sha1(data: bytes) -> str:
    h = hashlib.sha1()
    h.update(f"blob {len(data)}\0".encode("ascii"))
    h.update(data)
    return h.hexdigest()


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


def _promote(a: list[str], c: str, begin: int, end: int) -> None:
    if a[begin] == c and all(x == "" for x in a[begin+1:end+1]):
        a[begin] = ""
        a[end] = c


def decode_slots(s: str) -> list[str] | None:
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


def family_of(slots: list[str]) -> tuple[str, ...]:
    return tuple(FAMILY_MAP[i].get(x, x) if x else "" for i, x in enumerate(slots))


def cue_of(family: tuple[str, ...]) -> tuple[tuple[int,str], ...]:
    out = []
    for i, x in enumerate(family):
        if x:
            out.append((i, x))
            if len(out) == 2:
                break
    return tuple(out)


def decode_word(word: str):
    if not re.fullmatch(r"[a-z]+", word):
        return None
    e = normalize_eva(word)
    if e is None:
        return None
    slots = decode_slots(e)
    if slots is None:
        return None
    fam = family_of(slots)
    return {"word": word, "family": fam, "cue": cue_of(fam)}


def clean_zl3b_tokens(body: str) -> list[str]:
    body = re.sub(r"<!.*?>", "", body)
    body = body.replace("<->", ".").replace("<$>", ".").replace("<%>", ".")
    toks = re.split(r"[\s\.,]+", body)
    return [t for t in toks if t and not BAD_TOKEN_RE.search(t) and re.fullmatch(r"[a-z]+", t)]


@dataclass
class Corpus:
    name: str
    # all_units includes even one-line units for spectrum; analysis_units is the
    # population used for lag/null/return diagnostics.
    all_units: list[list[list[dict]]]
    analysis_units: list[list[list[dict]]]
    raw_tokens: int
    valid_tokens: int
    metadata: dict


def parse_blocks(text: str, name: str = "corpus", exclude_single_line_units: bool = True) -> Corpus:
    all_units: list[list[list[dict]]] = []
    cur: list[list[dict]] = []
    raw_tokens = valid_tokens = 0
    for raw in text.splitlines():
        if raw.strip() == "":
            if cur:
                all_units.append(cur)
                cur = []
            continue
        line = []
        for w in raw.strip().split():
            raw_tokens += 1
            r = decode_word(w)
            if r is not None:
                line.append(r)
                valid_tokens += 1
        # Preserve physical line even if no valid token survives.
        cur.append(line)
    if cur:
        all_units.append(cur)
    analysis_units = [u for u in all_units if (len(u) >= 2 or not exclude_single_line_units)]
    return Corpus(name, all_units, analysis_units, raw_tokens, valid_tokens, {
        "adapter": "blank-delimited blocks",
        "exclude_single_line_units_from_nulls": exclude_single_line_units,
        "all_units": len(all_units),
        "analysis_units": len(analysis_units),
        "lines": sum(len(u) for u in all_units),
    })


def parse_timm(text: str, name: str = "Timm fixed generator", lines_per_page: int = 29) -> Corpus:
    body = []
    started = False
    for raw in text.splitlines():
        if raw.startswith("#") and not started:
            continue
        started = True
        if raw.strip() == "":
            # Pinned output has no blank body lines; preserve a blank as a line
            # rather than silently deleting it.
            body.append("")
        else:
            body.append(raw.strip())
    all_units = []
    raw_tokens = valid_tokens = 0
    for start in range(0, len(body), lines_per_page):
        page = []
        for raw in body[start:start+lines_per_page]:
            line = []
            for w in raw.split():
                raw_tokens += 1
                r = decode_word(w)
                if r is not None:
                    line.append(r)
                    valid_tokens += 1
            page.append(line)
        all_units.append(page)
    return Corpus(name, all_units, all_units[:], raw_tokens, valid_tokens, {
        "adapter": "fixed lines per outer unit",
        "lines_per_unit": lines_per_page,
        "outer_units": len(all_units),
        "partial_final_unit_lines": len(all_units[-1]) if all_units and len(all_units[-1]) != lines_per_page else 0,
        "lines": len(body),
    })


def parse_zl3b(text: str, name: str = "ZL3b clean42 P") -> Corpus:
    headers: dict[str,dict[str,str]] = {}
    lines: dict[str,list[tuple[str,str]]] = defaultdict(list)
    for raw in text.splitlines():
        m = HEADER_RE.match(raw)
        if not m:
            continue
        tag, body = m.group(1), m.group(2)
        if "." not in tag and body.lstrip().startswith("<!"):
            headers[tag] = {k:v for k,v in VAR_RE.findall(body)}
        elif "." in tag:
            page = tag.split(".",1)[0]
            code = tag.split(",",1)[1] if "," in tag else ""
            lines[page].append((code, body))

    pages = []
    raw_tokens = valid_tokens = 0
    # Physical page order from transcription insertion order.
    for page, h in headers.items():
        if not PAGE_RE.match(page) or not all(k in h for k in ("Q","B","P")):
            continue
        if h["Q"] + h["B"] not in CLEAN42_SET:
            continue
        out_lines = []
        for code, body in lines.get(page, []):
            if not (len(code) >= 2 and code[1] == "P"):
                continue
            line = []
            for w in clean_zl3b_tokens(body):
                raw_tokens += 1
                r = decode_word(w)
                if r is not None:
                    line.append(r)
                    valid_tokens += 1
            out_lines.append(line)
        if out_lines:
            pages.append(out_lines)
    return Corpus(name, pages, pages[:], raw_tokens, valid_tokens, {
        "adapter": "ZL3b clean42, locus P only",
        "clean42_bifolios": 42,
        "pages": len(pages),
        "lines": sum(len(p) for p in pages),
    })


# ---------------------------------------------------------------------------
# Deterministic RNG matching the v0.1 freeze implementation (Mulberry32)
# ---------------------------------------------------------------------------
def _imul(a: int, b: int) -> int:
    return ((a & 0xFFFFFFFF) * (b & 0xFFFFFFFF)) & 0xFFFFFFFF


class Mulberry32:
    def __init__(self, seed: int):
        self.a = seed & 0xFFFFFFFF
    def random(self) -> float:
        self.a = (self.a + 0x6D2B79F5) & 0xFFFFFFFF
        t = _imul(self.a ^ (self.a >> 15), 1 | self.a)
        t = (t + _imul(t ^ (t >> 7), 61 | t)) & 0xFFFFFFFF
        t ^= t >> 14
        return (t & 0xFFFFFFFF) / 4294967296.0


def shuffle_in_place(a: list, rng: Mulberry32) -> None:
    for i in range(len(a)-1, 0, -1):
        j = int(rng.random() * (i+1))
        a[i], a[j] = a[j], a[i]


def _bin_index(distance: int) -> int | None:
    for i,(lo,hi) in enumerate(LAG_BINS):
        if lo <= distance <= hi:
            return i
    return None


def _return_bin_index(distance: int) -> int:
    for i,(lo,hi) in enumerate(RETURN_BINS):
        if distance >= lo and (hi is None or distance <= hi):
            return i
    raise AssertionError(distance)


def family_spectrum(corpus: Corpus) -> dict:
    fams = [r["family"] for u in corpus.all_units for line in u for r in line]
    c = Counter(fams)
    vals = sorted(c.values(), reverse=True)
    return {
        "tokens": len(fams),
        "types": len(c),
        "hapax": sum(n == 1 for n in vals),
        "mid_2_to_20": sum(2 <= n <= 20 for n in vals),
        "high_21_plus": sum(n >= 21 for n in vals),
        "top10_share": sum(vals[:10]) / len(fams) if fams else None,
        "type_token_ratio": len(c) / len(fams) if fams else None,
        "hapax_type_share": (sum(n == 1 for n in vals) / len(c)) if c else None,
    }


def _family_list(corpus: Corpus) -> list[tuple[str, ...]]:
    return [r["family"] for u in corpus.all_units for line in u for r in line]


def _spectrum_from_families(fams: list[tuple[str, ...]]) -> dict:
    c=Counter(fams); vals=sorted(c.values(), reverse=True)
    return {
        "tokens":len(fams),"types":len(c),
        "hapax":sum(n==1 for n in vals),
        "mid_2_to_20":sum(2<=n<=20 for n in vals),
        "high_21_plus":sum(n>=21 for n in vals),
        "top10_share":sum(vals[:10])/len(fams) if fams else None,
        "type_token_ratio":len(c)/len(fams) if fams else None,
        "hapax_type_share":sum(n==1 for n in vals)/len(c) if c else None,
    }


def _sample_without_replacement(items: list, n: int, rng: Mulberry32) -> list:
    if n>len(items): raise ValueError("sample larger than population")
    idx=list(range(len(items)))
    # Forward partial Fisher-Yates: only first n positions are selected.
    for i in range(n):
        j=i+int(rng.random()*(len(idx)-i))
        idx[i],idx[j]=idx[j],idx[i]
    return [items[idx[i]] for i in range(n)]


def _quantile_linear(values: list[float], p: float) -> float:
    a=sorted(values)
    if not a: return float("nan")
    if len(a)==1: return a[0]
    x=(len(a)-1)*p; lo=int(math.floor(x)); hi=int(math.ceil(x))
    if lo==hi: return a[lo]
    w=x-lo; return a[lo]*(1-w)+a[hi]*w


def length_matched_spectrum(a: Corpus, b: Corpus, reps: int = DEFAULT_SPECTRUM_REPS) -> dict:
    af=_family_list(a); bf=_family_list(b); n=min(len(af),len(bf))
    keys=["types","hapax","mid_2_to_20","high_21_plus","top10_share","type_token_ratio","hapax_type_share"]
    stores={"a":{k:[] for k in keys},"b":{k:[] for k in keys}}
    for r in range(reps):
        aa=af if len(af)==n else _sample_without_replacement(af,n,Mulberry32(0xA1B2C3D4+r*65537))
        bb=bf if len(bf)==n else _sample_without_replacement(bf,n,Mulberry32(0x1A2B3C4D+r*104729))
        sa=_spectrum_from_families(aa); sb=_spectrum_from_families(bb)
        for k in keys: stores["a"][k].append(sa[k]); stores["b"][k].append(sb[k])
    def summarize(store):
        return {k:{"median":_quantile_linear(v,.5),"p025":_quantile_linear(v,.025),"p975":_quantile_linear(v,.975)} for k,v in store.items()}
    return {"n":n,"repetitions":reps,"a_name":a.name,"b_name":b.name,"a":summarize(stores["a"]),"b":summarize(stores["b"])}


def encode_units(corpus: Corpus):
    fam_ids, cue_ids = {}, {}
    next_f = next_c = 0
    out = []
    for unit in corpus.analysis_units:
        F=[]; C=[]; line_of=[]; line_ranges=[]
        for li,line in enumerate(unit):
            start=len(F)
            for r in line:
                fam=r["family"]; cue=r["cue"]
                if fam not in fam_ids:
                    fam_ids[fam]=next_f; next_f+=1
                if cue not in cue_ids:
                    cue_ids[cue]=next_c; next_c+=1
                F.append(fam_ids[fam]); C.append(cue_ids[cue]); line_of.append(li)
            line_ranges.append((start,len(F)))
        pairs=[[] for _ in LAG_BINS]
        N=len(F)
        for d in range(1,101):
            bi=_bin_index(d)
            if bi is None: continue
            for i in range(0,N-d):
                j=i+d
                if C[i]==C[j]: pairs[bi].append((i,j))
        outer_groups=defaultdict(list)
        for i,c in enumerate(C): outer_groups[c].append(i)
        line_groups=[]
        for start,end in line_ranges:
            g=defaultdict(list)
            for i in range(start,end): g[C[i]].append(i)
            line_groups.append(g)
        out.append({"F":F,"C":C,"pairs":pairs,"outer_groups":outer_groups,"line_groups":line_groups})
    return out


def permute_families(unit: dict, rng: Mulberry32, mode: str) -> list[int]:
    out=unit["F"][:]
    groups=[unit["outer_groups"]] if mode=="outer" else unit["line_groups"]
    for gm in groups:
        for inds in gm.values():
            vals=[unit["F"][i] for i in inds]
            shuffle_in_place(vals,rng)
            for k,i in enumerate(inds): out[i]=vals[k]
    return out


def lag_rates(units: list[dict], family_arrays: list[list[int]] | None = None) -> list[dict]:
    eq=[0]*len(LAG_BINS); den=[0]*len(LAG_BINS)
    for ui,u in enumerate(units):
        F = family_arrays[ui] if family_arrays is not None else u["F"]
        for bi,pairs in enumerate(u["pairs"]):
            den[bi]+=len(pairs)
            eq[bi]+=sum(F[i]==F[j] for i,j in pairs)
    return [{"rate":eq[i]/den[i] if den[i] else None,"equal":eq[i],"n":den[i]} for i in range(len(LAG_BINS))]


def return_and_medium(units: list[dict], family_arrays: list[list[int]] | None = None) -> dict:
    gaps=[0]*len(RETURN_BINS)
    med={"all":0,"direct":0,"one_intervening":0,"two_plus_intervening":0,"has_short_step_le5":0,"no_short_step_le5":0,"denominator_samecue_pairs":0}
    for ui,u in enumerate(units):
        F = family_arrays[ui] if family_arrays is not None else u["F"]
        positions=defaultdict(list)
        for i,f in enumerate(F): positions[f].append(i)
        # rank maps and prefix counts make the 21-50 decomposition O(1) per
        # matching pair instead of rescanning every occurrence list.
        rank_by_family={}
        short_prefix={}
        for f,arr in positions.items():
            ranks={pos:k for k,pos in enumerate(arr)}
            pref=[0]
            for k in range(1,len(arr)):
                d=arr[k]-arr[k-1]
                gaps[_return_bin_index(d)]+=1
                pref.append(pref[-1] + (1 if d <= 5 else 0))
            rank_by_family[f]=ranks
            short_prefix[f]=pref
        for i,j in u["pairs"][4]:
            med["denominator_samecue_pairs"]+=1
            f=F[i]
            if f!=F[j]: continue
            med["all"]+=1
            ai=rank_by_family[f][i]; bj=rank_by_family[f][j]
            intervening=bj-ai-1
            if intervening==0:
                med["direct"]+=1
                continue
            if intervening==1: med["one_intervening"]+=1
            else: med["two_plus_intervening"]+=1
            # pref[k] counts <=5 gaps ending at occurrence indices 1..k.
            has_short=(short_prefix[f][bj]-short_prefix[f][ai]) > 0
            if has_short: med["has_short_step_le5"]+=1
            else: med["no_short_step_le5"]+=1
    den=med["denominator_samecue_pairs"]
    rates={k:(v/den if den else None) for k,v in med.items() if k!="denominator_samecue_pairs"}
    return {"consecutive_return_counts":gaps,"medium_counts":med,"medium_rates":rates}


def _null_stat(obs: float | int | None, values: list[float | int | None]) -> dict:
    values=[x for x in values if x is not None]
    if obs is None or not values:
        return {"obs":obs,"null_mean":None,"excess":None,"z":None,"p2":None}
    mean=sum(values)/len(values)
    if len(values)>1:
        var=sum((x-mean)**2 for x in values)/(len(values)-1)
        sd=math.sqrt(var)
    else: sd=0.0
    ge=1+sum(x>=obs for x in values)
    le=1+sum(x<=obs for x in values)
    p2=min(1.0,2*min(ge/(len(values)+1),le/(len(values)+1)))
    return {"obs":obs,"null_mean":mean,"excess":obs-mean,"z":((obs-mean)/sd if sd else None),"p2":p2}


def profile(corpus: Corpus, permutations: int = DEFAULT_PERMUTATIONS) -> dict:
    units=encode_units(corpus)
    obs_lag=lag_rates(units)
    obs_chain=return_and_medium(units)
    outer_lag=[[] for _ in LAG_BINS]
    line_lag=[[] for _ in LAG_BINS]
    gap_null=[[] for _ in RETURN_BINS]
    medium_keys=["all","direct","one_intervening","two_plus_intervening","has_short_step_le5","no_short_step_le5"]
    med_null={k:[] for k in medium_keys}

    for rep in range(permutations):
        ro=Mulberry32(0x33445566 + rep*65537)
        rl=Mulberry32(0x778899AA + rep*104729)
        outer=[permute_families(u,ro,"outer") for u in units]
        line=[permute_families(u,rl,"line") for u in units]
        lo=lag_rates(units,outer); ll=lag_rates(units,line); ch=return_and_medium(units,outer)
        for i in range(len(LAG_BINS)):
            if lo[i]["rate"] is not None: outer_lag[i].append(lo[i]["rate"])
            if ll[i]["rate"] is not None: line_lag[i].append(ll[i]["rate"])
        for i,v in enumerate(ch["consecutive_return_counts"]): gap_null[i].append(v)
        for k in medium_keys: med_null[k].append(ch["medium_rates"][k])

    return {
        "tool": {"name":"Voynich Generative Diagnostic Toolkit","version":VERSION,"protocol":PROTOCOL_ID},
        "corpus": {"name":corpus.name,"raw_tokens":corpus.raw_tokens,"valid_12slot_family_tokens":corpus.valid_tokens,"valid_fraction":(corpus.valid_tokens/corpus.raw_tokens if corpus.raw_tokens else None),**corpus.metadata},
        "frozen_definitions": {
            "cue":"first two non-empty FAMILY components including slot indices",
            "lag_bins":LAG_LABELS,
            "return_bins":RETURN_LABELS,
            "outer_null":"shuffle exact FAMILY labels within (outer unit, cue), preserving positions and cue composition",
            "line_null":"shuffle exact FAMILY labels within (line, cue), preserving positions and line-level cue/FAMILY multiset",
            "medium_21_50":"same-cue pairs at token distance 21-50; short-chain categories exclude direct pairs",
            "permutations":permutations,
        },
        "family_spectrum": family_spectrum(corpus),
        "outer_plus_cue_null": {LAG_LABELS[i]:_null_stat(obs_lag[i]["rate"],outer_lag[i]) for i in range(len(LAG_BINS)) if obs_lag[i]["rate"] is not None},
        "line_plus_cue_null": {LAG_LABELS[i]:_null_stat(obs_lag[i]["rate"],line_lag[i]) for i in range(len(LAG_BINS)) if obs_lag[i]["rate"] is not None},
        "consecutive_return": {RETURN_LABELS[i]:_null_stat(obs_chain["consecutive_return_counts"][i],gap_null[i]) for i in range(len(RETURN_BINS))},
        "medium_21_50": {
            "denominator_samecue_pairs":obs_chain["medium_counts"]["denominator_samecue_pairs"],
            "counts":{k:obs_chain["medium_counts"][k] for k in medium_keys},
            "stats":{k:_null_stat(obs_chain["medium_rates"][k],med_null[k]) for k in medium_keys},
        },
    }


def fetch_verified(source: dict, path: Path) -> None:
    data=urllib.request.urlopen(source["url"],timeout=90).read()
    got=git_blob_sha1(data)
    if got!=source["blob"]:
        raise RuntimeError(f"Git blob mismatch for {source['filename']}: {got} != {source['blob']}")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)


def read_verified(source: dict, path: Path, fetch: bool) -> str:
    if not path.exists():
        if not fetch: raise RuntimeError(f"missing {path}; use --fetch")
        fetch_verified(source,path)
    data=path.read_bytes(); got=git_blob_sha1(data)
    if got!=source["blob"]:
        raise RuntimeError(f"cached Git blob mismatch for {path}: {got} != {source['blob']}")
    return data.decode("utf-8")



def _compare_expected(actual, expected, path: str = "root", *, rel_tol: float = 1e-10, abs_tol: float = 1e-12) -> list[str]:
    """Compare an actual result against an expected *subset* recursively.

    Expected JSON deliberately need not repeat every field in the result bundle.
    This keeps the golden fixture focused on scientific/adapter checkpoints while
    allowing additive metadata in later software-only revisions.
    """
    errors=[]
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [f"{path}: expected object, got {type(actual).__name__}"]
        for key, exp in expected.items():
            if key not in actual:
                errors.append(f"{path}.{key}: missing")
            else:
                errors.extend(_compare_expected(actual[key], exp, f"{path}.{key}", rel_tol=rel_tol, abs_tol=abs_tol))
        return errors
    if isinstance(expected, list):
        if not isinstance(actual, list):
            return [f"{path}: expected list, got {type(actual).__name__}"]
        if len(actual) != len(expected):
            errors.append(f"{path}: length {len(actual)} != expected {len(expected)}")
            return errors
        for i,(a,e) in enumerate(zip(actual,expected)):
            errors.extend(_compare_expected(a,e,f"{path}[{i}]",rel_tol=rel_tol,abs_tol=abs_tol))
        return errors
    # bool is a subclass of int; compare it before numeric handling.
    if isinstance(expected, bool) or expected is None or isinstance(expected, str):
        if actual != expected:
            errors.append(f"{path}: {actual!r} != expected {expected!r}")
        return errors
    if isinstance(expected, (int,float)) and not isinstance(expected,bool):
        if not isinstance(actual,(int,float)) or isinstance(actual,bool):
            return [f"{path}: expected numeric {expected!r}, got {actual!r}"]
        if isinstance(expected,int) and isinstance(actual,int):
            if actual != expected:
                errors.append(f"{path}: {actual} != expected {expected}")
        elif not math.isclose(float(actual),float(expected),rel_tol=rel_tol,abs_tol=abs_tol):
            errors.append(f"{path}: {actual!r} != expected {expected!r} (rtol={rel_tol}, atol={abs_tol})")
        return errors
    if actual != expected:
        errors.append(f"{path}: {actual!r} != expected {expected!r}")
    return errors


def check_reference_bundle(bundle: dict, expected_path: Path) -> list[str]:
    expected=json.loads(expected_path.read_text(encoding="utf-8"))
    if expected.get("protocol") != PROTOCOL_ID:
        return [f"expected fixture protocol {expected.get('protocol')!r} != tool protocol {PROTOCOL_ID!r}"]
    return _compare_expected(bundle, expected.get("expected", {}))

def comparison_markdown(profiles: list[dict]) -> str:
    names=[p["corpus"]["name"] for p in profiles]
    lines=["# VGDT side-by-side profile", "", "No aggregate similarity score is computed.", ""]
    lines.append("| metric | " + " | ".join(names) + " |")
    lines.append("|---|" + "|".join(["---:"]*len(names)) + "|")
    for key,label in [("types","FAMILY types"),("hapax","hapax"),("mid_2_to_20","2–20"),("high_21_plus","21+"),("top10_share","Top-10 share")]:
        vals=[]
        for p in profiles:
            v=p["family_spectrum"][key]
            vals.append(f"{v:.6f}" if isinstance(v,float) else str(v))
        lines.append(f"| {label} | " + " | ".join(vals) + " |")
    lines.append("")
    lines.append("## LINE+CUE lag excess")
    lines.append("")
    lines.append("| lag | " + " | ".join(names) + " |")
    lines.append("|---|" + "|".join(["---:"]*len(names)) + "|")
    for lag in LAG_LABELS:
        vals=[]
        for p in profiles:
            x=p["line_plus_cue_null"].get(lag,{}).get("excess")
            vals.append("NA" if x is None else f"{x:+.6f}")
        lines.append(f"| {lag} | " + " | ".join(vals) + " |")
    lines.append("")
    lines.append("## 21–50 short-chain excess")
    lines.append("")
    for p in profiles:
        s=p["medium_21_50"]["stats"]["has_short_step_le5"]
        ex="NA" if s["excess"] is None else f"{s['excess']:+.6f}"
        z="NA" if s["z"] is None else f"{s['z']:.3f}"
        lines.append(f"- **{p['corpus']['name']}**: excess {ex}, z={z}")
    return "\n".join(lines)+"\n"


def load_profile(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_corpus(path: str, fmt: str, name: str | None = None, lines_per_unit: int = 29, include_single_line_units: bool = False) -> Corpus:
    text=Path(path).read_text(encoding="utf-8")
    if fmt=="zl3b": return parse_zl3b(text,name or "ZL3b clean42 P")
    if fmt=="timm": return parse_timm(text,name or "Timm fixed generator",lines_per_unit)
    if fmt=="blocks": return parse_blocks(text,name or Path(path).stem,not include_single_line_units)
    raise ValueError(fmt)


def cmd_profile(args):
    corpus=load_corpus(args.input,args.format,args.name,args.lines_per_unit,args.include_single_line_units)
    result=profile(corpus,args.permutations)
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(out)


def cmd_compare(args):
    ps=[load_profile(Path(p)) for p in args.profiles]
    md=comparison_markdown(ps)
    if args.output:
        Path(args.output).write_text(md,encoding="utf-8"); print(args.output)
    else: print(md)


def pair_markdown(a: dict, b: dict, lm: dict) -> str:
    names=[a["corpus"]["name"],b["corpus"]["name"]]
    lines=["# VGDT pair report","","No aggregate similarity score is computed.","",f"Length-matched FAMILY spectrum uses n={lm['n']} and {lm['repetitions']} deterministic subsamples.",""]
    lines.append("| FAMILY metric | "+" | ".join(names)+" |")
    lines.append("|---|---:|---:|")
    for k,label in [("types","types"),("hapax","hapax"),("mid_2_to_20","2–20"),("high_21_plus","21+"),("top10_share","Top-10 share")]:
        va=lm["a"][k]["median"]; vb=lm["b"][k]["median"]
        fa=f"{va:.6f}" if isinstance(va,float) and not float(va).is_integer() else str(int(va) if isinstance(va,float) else va)
        fb=f"{vb:.6f}" if isinstance(vb,float) and not float(vb).is_integer() else str(int(vb) if isinstance(vb,float) else vb)
        lines.append(f"| {label} | {fa} | {fb} |")
    lines += ["","## LINE+CUE residuals","","| lag | "+" | ".join(names)+" |","|---|---:|---:|"]
    for lag in LAG_LABELS:
        vals=[]
        for p in (a,b):
            x=p["line_plus_cue_null"].get(lag,{}).get("excess")
            vals.append("NA" if x is None else f"{x:+.6f}")
        lines.append(f"| {lag} | {vals[0]} | {vals[1]} |")
    lines += ["","## 21–50 non-direct chains containing a <=5 step",""]
    for p in (a,b):
        st=p["medium_21_50"]["stats"]["has_short_step_le5"]
        ex="NA" if st["excess"] is None else f"{st['excess']:+.6f}"
        z="NA" if st["z"] is None else f"{st['z']:.3f}"
        lines.append(f"- **{p['corpus']['name']}**: excess {ex}, z={z}")
    return "\n".join(lines)+"\n"


def cmd_pair(args):
    a=load_corpus(args.a_input,args.a_format,args.a_name,args.a_lines_per_unit,args.a_include_single_line_units)
    b=load_corpus(args.b_input,args.b_format,args.b_name,args.b_lines_per_unit,args.b_include_single_line_units)
    pa=profile(a,args.permutations); pb=profile(b,args.permutations); lm=length_matched_spectrum(a,b,args.spectrum_reps)
    result={"tool":{"name":"Voynich Generative Diagnostic Toolkit","version":VERSION,"protocol":PROTOCOL_ID},"a":pa,"b":pb,"length_matched_family_spectrum":lm}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    md=out.with_suffix(".md"); md.write_text(pair_markdown(pa,pb,lm),encoding="utf-8")
    print(md)


def cmd_reference(args):
    data_dir=Path(args.data_dir); out_dir=Path(args.output_dir); out_dir.mkdir(parents=True,exist_ok=True)
    texts={}
    for key,src in SOURCES.items(): texts[key]=read_verified(src,data_dir/src["filename"],args.fetch)
    corpora=[parse_zl3b(texts["zl3b"]),parse_timm(texts["timm"]),parse_blocks(texts["naibbe"],"Naibbe reference cipher",True)]
    profiles=[]
    keys=["zl3b","timm","naibbe"]
    for key,c in zip(keys,corpora):
        print(f"profiling {c.name} ...",file=sys.stderr)
        p=profile(c,args.permutations); profiles.append(p)
        (out_dir/f"{key}.json").write_text(json.dumps(p,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lm_timm=length_matched_spectrum(corpora[0],corpora[1],args.spectrum_reps)
    lm_naibbe=length_matched_spectrum(corpora[0],corpora[2],args.spectrum_reps)
    (out_dir/"zl3b_vs_timm_spectrum.json").write_text(json.dumps(lm_timm,indent=2)+"\n",encoding="utf-8")
    (out_dir/"zl3b_vs_naibbe_spectrum.json").write_text(json.dumps(lm_naibbe,indent=2)+"\n",encoding="utf-8")
    md=comparison_markdown(profiles)
    md += "\n---\n\n" + pair_markdown(profiles[0],profiles[1],lm_timm)
    md += "\n---\n\n" + pair_markdown(profiles[0],profiles[2],lm_naibbe)
    (out_dir/"comparison.md").write_text(md,encoding="utf-8")
    bundle={
        "protocol":PROTOCOL_ID,
        "settings":{"permutations":args.permutations,"spectrum_reps":args.spectrum_reps},
        "sources":{k:{"blob":v["blob"],"filename":v["filename"],"url":v["url"]} for k,v in SOURCES.items()},
        "profiles":dict(zip(keys,profiles)),
        "length_matched":{"zl3b_vs_timm":lm_timm,"zl3b_vs_naibbe":lm_naibbe},
    }
    bundle_path=out_dir/"reference_bundle.json"
    bundle_path.write_text(json.dumps(bundle,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    if args.check:
        errors=check_reference_bundle(bundle,Path(args.check))
        if errors:
            print("REFERENCE CHECK FAILED",file=sys.stderr)
            for e in errors[:100]: print(" - "+e,file=sys.stderr)
            if len(errors)>100: print(f" - ... {len(errors)-100} more",file=sys.stderr)
            raise SystemExit(1)
        print("REFERENCE CHECK OK",file=sys.stderr)
    print(out_dir/"comparison.md")

def build_parser():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest="command",required=True)
    a=sub.add_parser("profile",help="profile one corpus against its own frozen nulls")
    a.add_argument("--input",required=True); a.add_argument("--format",choices=["zl3b","timm","blocks"],required=True)
    a.add_argument("--output",required=True); a.add_argument("--name")
    a.add_argument("--permutations",type=int,default=DEFAULT_PERMUTATIONS)
    a.add_argument("--lines-per-unit",type=int,default=29,help="timm/fixed-line adapter")
    a.add_argument("--include-single-line-units",action="store_true",help="blocks adapter only; frozen Naibbe run excludes them from nulls")
    a.set_defaults(func=cmd_profile)
    b=sub.add_parser("compare",help="side-by-side profiles; deliberately no aggregate similarity score")
    b.add_argument("profiles",nargs="+"); b.add_argument("--output"); b.set_defaults(func=cmd_compare)
    q=sub.add_parser("pair",help="profile two raw corpora and add a length-matched FAMILY-spectrum comparison")
    q.add_argument("--a-input",required=True); q.add_argument("--a-format",choices=["zl3b","timm","blocks"],required=True); q.add_argument("--a-name")
    q.add_argument("--b-input",required=True); q.add_argument("--b-format",choices=["zl3b","timm","blocks"],required=True); q.add_argument("--b-name")
    q.add_argument("--a-lines-per-unit",type=int,default=29); q.add_argument("--b-lines-per-unit",type=int,default=29)
    q.add_argument("--a-include-single-line-units",action="store_true"); q.add_argument("--b-include-single-line-units",action="store_true")
    q.add_argument("--permutations",type=int,default=DEFAULT_PERMUTATIONS); q.add_argument("--spectrum-reps",type=int,default=DEFAULT_SPECTRUM_REPS)
    q.add_argument("--output",required=True); q.set_defaults(func=cmd_pair)
    c=sub.add_parser("reference-suite",help="run pinned ZL3b/Timm/Naibbe reference panel")
    c.add_argument("--data-dir",default="data"); c.add_argument("--output-dir",default="results/vgdt_v0_1")
    c.add_argument("--fetch",action="store_true"); c.add_argument("--permutations",type=int,default=DEFAULT_PERMUTATIONS)
    c.add_argument("--spectrum-reps",type=int,default=DEFAULT_SPECTRUM_REPS)
    c.add_argument("--check",help="golden reference fixture; nonzero exit on mismatch")
    c.set_defaults(func=cmd_reference)
    return p


def main():
    args=build_parser().parse_args(); args.func(args)

if __name__=="__main__": main()
