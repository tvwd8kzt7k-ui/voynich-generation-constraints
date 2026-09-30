# Voynich Generative Diagnostic Toolkit (VGDT) v0.1

VGDT is a **mechanism diagnostic**, not a decipherment and not a Voynich-similarity scorer.

It was extracted from the 2026 Voynich generative-constraints work after the same frozen measurements gave different signatures for the Voynich Manuscript, Torsten Timm's fixed self-citation generator, and Michael Greshko's Naibbe cipher output.

The design rule is simple:

> Profile each corpus against nulls built from that corpus first. Compare profiles only afterwards.

That prevents the tool from silently treating Voynich as a target score.

## What v0.1 measures

The frozen panel contains:

- the same 12-slot FAMILY normalization used in the parent project;
- FAMILY frequency spectrum: types, hapax, 2–20, 21+, Top-10 share;
- exact-FAMILY recurrence at lags `1 / 2–5 / 6–10 / 11–20 / 21–50 / 51–100`, conditioned on a cue made from the first two non-empty FAMILY components;
- an **OUTER+CUE null** that preserves outer-unit membership and cue composition;
- a stronger **LINE+CUE null** that also preserves each line's FAMILY/cue multiset;
- consecutive-return gaps;
- decomposition of 21–50 same-cue returns into direct versus chained returns, including whether a chain contains a short (<=5-token) step.

The output is a diagnostic profile. There is intentionally **no aggregate similarity score, ranking, or winner**.

## Why this can be a finished tool while Voynich is still unsolved

The stopping criterion is operational, not historical. v0.1 is complete when:

1. the representation is fixed;
2. each null states exactly what it preserves and destroys;
3. seeds, bins and statistics are frozen;
4. the same code accepts Voynich and candidate generators;
5. results are machine-readable and reproducible;
6. the tool does not invent missing manuscript metadata.

None of those require knowing what the manuscript means or how it was historically produced.

## Quick use

Python 3.10+, standard library only.

Profile a normal EVA-like candidate whose blank lines delimit outer units:

```bash
python vgdt.py profile \
  --format blocks \
  --input candidate.txt \
  --output candidate_profile.json
```

Profile the pinned Timm-style fixed-line output:

```bash
python vgdt.py profile \
  --format timm \
  --input generated_text.txt \
  --output timm_profile.json
```

Profile ZL3b clean42 P loci:

```bash
python vgdt.py profile \
  --format zl3b \
  --input ZL3b-n.txt \
  --output zl3b_profile.json
```

Compare already-generated profiles:

```bash
python vgdt.py compare zl3b_profile.json timm_profile.json candidate_profile.json \
  --output comparison.md
```

For a fair two-corpus FAMILY-spectrum comparison, use `pair`. It profiles both corpora independently and additionally downsamples the longer FAMILY stream to the shorter length 500 times. It still does not collapse the result to one score.

```bash
python vgdt.py pair \
  --a-input ZL3b-n.txt --a-format zl3b --a-name Voynich \
  --b-input candidate.txt --b-format blocks --b-name Candidate \
  --output voynich_vs_candidate.json
```

Run the three pinned reference corpora from scratch:

```bash
python vgdt.py reference-suite --fetch --check REFERENCE_EXPECTATIONS.json
```

The reference suite fetches byte-pinned public files, verifies Git blob SHA-1, profiles them independently, writes machine-readable profiles plus a side-by-side Markdown report, and checks the frozen v0.1 golden fixture. A successful checked run prints `REFERENCE CHECK OK`. The third-party texts are not redistributed in this package.

## Input semantics

### `blocks`

Non-empty source lines are lines. Blank lines delimit outer units. One-line outer units are included in the FAMILY spectrum but excluded from recurrence/null tests by default. This is the frozen adapter used for the Naibbe reference output.

### `timm`

Initial `#` header lines are ignored. The body is chunked into 29-line outer units. The final partial chunk is retained for the v0.1 recurrence/null profile. This does not invent bifolio, hand or context metadata.

### `zl3b`

Only locus `P` lines from the frozen clean42 bifolio set are retained. Physical manuscript pages are the outer units.

## Interpretation discipline

A residual means only that it was **not removed by the current null**. It is not automatically evidence for language, meaning, memory, cognition, copying, or a historical device.

If a stronger null removes an effect, the cheaper preserved structure is sufficient to explain that effect at the resolution tested. If the effect survives, the current null is insufficient; the tool does not name the missing cause for you.

This is the point of the instrument: it localizes what still needs explanation.

## Relationship to the parent repository

This is a self-contained candidate for a new diagnostic layer of `voynich-generation-constraints`. It does not replace the existing canonical evidence package, the Timm audit, or historical exploratory records. It packages the later FAMILY/null decomposition as a reusable expert-facing instrument.

## Reference-population note

The v0.1 reference suite profiles the full frozen clean42 ZL3b population. Some earlier exploratory reports quoted a historical TRAIN/TEST split; those z-scores are not expected to be numerically identical to the full-clean42 reference run. The qualitative immediate LINE+CUE residue is preserved. See `REFERENCE_VALIDATION.md`.
