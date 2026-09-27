#!/usr/bin/env python3
"""Shared canonical record layer for post-freeze data checks.

This layer deliberately ignores historical reconstruction questions.  It uses
one pinned transcription, one pinned parser, and the frozen clean42 list.
"""
from __future__ import annotations

import importlib.util
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FROZEN = ROOT / "frozen" / "human_operation" / "run_freeze.py"

spec = importlib.util.spec_from_file_location("human_operation_freeze", FROZEN)
if spec is None or spec.loader is None:
    raise RuntimeError(f"could not import frozen parser: {FROZEN}")
ho = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ho)


def iter_clean42_records(text: str):
    """Yield canonical exact/family records in physical page/line/token order."""
    headers, lines = ho.parse_zl3b(text)
    pages_by_bif = defaultdict(list)
    for page, h in headers.items():
        if not ho.PAGE_RE.match(page) or not all(k in h for k in ("Q", "B", "P")):
            continue
        bif = h["Q"] + h["B"]
        if bif in ho.CLEAN42_SET:
            pages_by_bif[bif].append(page)
    for bif in pages_by_bif:
        pages_by_bif[bif].sort(key=lambda p: ho.POS_ORDER.get(headers[p].get("P", "Z"), 99))

    for bif in ho.CLEAN42:
        for page in pages_by_bif.get(bif, []):
            h = headers[page]
            ctx = f"{h.get('I','?')}|{h.get('L','?')}"
            hand = h.get("H", "?")
            line_idx = 0
            for code, body in lines.get(page, []):
                if not (len(code) >= 2 and code[1] == "P"):
                    continue
                tok_idx = 0
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
                        "page": page,
                        "line": line_idx,
                        "token_in_line": tok_idx,
                        "context": ctx,
                        "hand": hand,
                        "exact": tuple(slots),
                        "family": family,
                    }
                    tok_idx += 1
                line_idx += 1


def support_for_family(family: tuple[str, ...]):
    """Enumerate every concrete 12-slot form licensed by a family tuple."""
    forms = [tuple("" for _ in range(12))]
    for j, fam in enumerate(family):
        if not fam:
            continue
        members = ho.FAMILY_MEMBERS[j][fam]
        nxt = []
        for form in forms:
            for face in members:
                z = list(form)
                z[j] = face
                nxt.append(tuple(z))
        forms = nxt
    return forms
