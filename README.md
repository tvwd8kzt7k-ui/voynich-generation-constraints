# Reproducible Generative Constraints in Voynichese

**This is not a decipherment.**  
This repository provides executable tests for statistical constraints on the generation of Voynich transcription strings. It does not identify a plaintext, language, cipher, author, or unique historical production mechanism.

The main question is narrower:

> **What measurable constraints must any proposed account of Voynichese generation be able to reproduce?**

The current release is organized so that a third party can obtain pinned public transcriptions, verify their exact source identity, rerun the analyses, and compare the outputs with frozen machine-readable checkpoints.

## Reproduce the current evidence

Requirements: Python 3.10+ and internet access.

```bash
python tools/run_all_evidence.py --fetch
```

This runs the primary ZL3b analyses and the IT2a cross-transcription robustness pass.

A successful run should end with PASS results for the frozen checkpoints. The raw transcription texts are **not redistributed** in this repository; the runners fetch byte-pinned public mirror copies and verify their Git blob SHA-1 values before analysis.

For the primary ZL3b evidence only:

```bash
python tools/run_core_evidence.py --fetch
```

For IT2a robustness only:

```bash
python tools/run_transcription_robustness.py --fetch
```

See [`THIRD_PARTY_REPRODUCTION.md`](THIRD_PARTY_REPRODUCTION.md) for the reproduction protocol and [`CORE_EVIDENCE_MANIFEST.json`](CORE_EVIDENCE_MANIFEST.json) for the claim-to-code map.

## What currently reproduces

The present core consists of five explicit measurements plus deterministic structural checkpoints.

| Measurement | ZL3b | IT2a |
| --- | ---: | ---: |
| clean42 valid 12-slot tokens | 24,250 | 24,233 |
| exact types | 2,711 | 2,842 |
| low-dimensional box-2 coverage | 90.025% | 88.577% |
| low-dimensional box-3 coverage | 97.835% | 97.416% |
| context gain over family baseline | +0.049640 nats/token | +0.049585 |
| hand gain over family baseline | +0.046673 nats/token | +0.045859 |
| uniform all-seen reuse gain | +0.014136 nats/token | +0.014255 |
| bifolio-local true gain | +0.024825 nats/event | +0.024509 |
| true bifolio source − wrong-source mean | +0.051512 nats/event | +0.051291 |
| bifolios positive vs wrong-source mean | 42/42 | 42/42 |
| line-preserving within-line excess | +0.010883 | +0.010826 |
| line-preserving cross-line excess | −0.007370 | −0.006957 |

IT2a is an alternate transcription of the **same manuscript**, not an independent corpus. Agreement therefore tests robustness to transcription choices; it is not a replication on independent material.

### 1. Low-dimensional family variation

Within high-frequency family forms, most concrete-form variation is concentrated in a small number of slots. On the primary CAL8 set, fixing every slot to its family-modal face covers 43.88% of tokens; freeing the one, two, or three most variable slots raises coverage to 71.03%, 90.02%, and 97.83%.

“Box-k” is only a mathematical description of this restricted variation. It is not evidence for a literal box, bag, table, or physical device.

### 2. Context and hand both predict concrete-form choice

Conditioned on family form, both manuscript context and scribal hand improve prediction of the exact concrete form relative to a global family-conditioned baseline. In the current canonical specification, context is slightly better in aggregate, but there is no robust bifolio-level context-over-hand dominance.

### 3. Broad exact reuse is real but insufficient

Uniformly increasing the probability of every previously seen exact form improves conditional prediction. However, even strong uniform reinforcement does not reproduce the observed concentration of exact forms and hapax counts. The evidence therefore supports a reuse component but requires additional selectivity.

### 4. Bifolio-local state survives context and hand controls

After conditioning the baseline on slot, family, context, and hand, concrete-face frequencies observed in the opposite half of the **true bifolio** improve prediction. True bifolio source halves also outperform wrong-bifolio source halves.

At the current fixed setting, the true-minus-wrong-source mean is positive for all 42 tested bifolios in both ZL3b and IT2a.

This is evidence for a bifolio-local shared state in the transcription statistics. It does not identify the historical cause of that state.

### 5. Weak ordering persistence is line-local

After fixing each line's concrete-face composition, a small same-face ordering excess remains within lines. The corresponding cross-line excess is absent and slightly negative.

The same sign pattern and nearly the same magnitude appear in ZL3b and IT2a.

## What this release supports

The current results support a **constrained generative account** of Voynichese: family structure, low-dimensional concrete variation, contextual and hand-conditioned preferences, bifolio-local state, selective exact-form concentration, and weak line-local ordering all contribute measurable structure.

A proposed language, cipher, copying, pseudo-language, stochastic, or mechanical account can be evaluated against the same constraints.

The strongest claim of this release is therefore:

> **Any adequate account of Voynichese generation should explain this reproducible constraint set.**

## What this release does not establish

These analyses do **not** by themselves establish that:

- the manuscript is meaningless;
- the text was generated by a literal machine;
- there was no plaintext or semantic process;
- a unique historical mechanism has been identified;
- a literal bag, table, booklet, card system, front/back rule, or cognitive routine was used.

Those are separate historical or semantic hypotheses.

The clean42 material was repeatedly inspected while the models and nulls were being developed. The current analyses are therefore **reproducible exploratory/frozen evidence**, not a pristine preregistered confirmation.

## Why two transcriptions are included

ZL3b is the primary transcription. IT2a is used as a robustness check against ZL3b-specific reading or tokenization choices.

The primary and alternate inputs are pinned by repository, commit, path, and Git blob SHA-1. Their texts are not bundled.

See [`TRANSCRIPTION_ROBUSTNESS_2026-09-27.md`](TRANSCRIPTION_ROBUSTNESS_2026-09-27.md) for the full side-by-side comparison.

## Evidence map

The current public-facing evidence is separated from the historical path by which the hypotheses were developed.

- [`CANONICAL_EVIDENCE_2026-09-27.md`](CANONICAL_EVIDENCE_2026-09-27.md): current evidentiary statements and interpretation limits
- [`CLAIM_EVIDENCE_MAP.md`](CLAIM_EVIDENCE_MAP.md): claims → scripts → expected outputs
- [`CORE_EVIDENCE_MANIFEST.json`](CORE_EVIDENCE_MANIFEST.json): machine-readable core manifest
- [`THIRD_PARTY_REPRODUCTION.md`](THIRD_PARTY_REPRODUCTION.md): external reproduction protocol
- [`TRANSCRIPTION_ROBUSTNESS_2026-09-27.md`](TRANSCRIPTION_ROBUSTNESS_2026-09-27.md): ZL3b / IT2a comparison
- [`FREEZE_2026-09-26.md`](FREEZE_2026-09-26.md): historical freeze record, retained as research history rather than the current evidentiary authority

Earlier Q-series and Minimal Scribe material belongs to the archived research record and is not required for the one-command current reproduction in this repository.

## Falsification is welcome

Useful external checks include:

1. run the package unchanged on a clean machine and report the environment and result;
2. independently reimplement the parser or one of the core tests;
3. apply equivalent measurements to additional transcription systems;
4. propose stronger null models for the bifolio-local or line-local effects;
5. test alternative generative accounts against the same constraint set.

External reproductions—successful or failed—should report the package version, Git commit, Python version, operating system, input blob identities, command used, and resulting output.

## Earlier publication

An earlier documentation-focused report was archived as:

Daiki Matsuda (2026), *Generative Constraints in the Voynich Manuscript: From Known Structure to Reproducible Tests*. Zenodo.  
DOI: 10.5281/zenodo.22754587

The present executable assembly supersedes the earlier repository statement that end-to-end reproduction code was unavailable.

## Research process and attribution

The project used extensive AI assistance for code generation, statistical work, literature search, research-log organization, reconstruction, testing, and drafting. Human decisions determined the research objective, hypothesis selection, interpretation limits, and stopping decisions.

AI assistance is part of the provenance record; it is not evidence for the validity of the results.

## License and transcription provenance

Code/documentation reuse terms are separated from third-party transcription provenance. See [`CODE_LICENSE_NOTICE.md`](CODE_LICENSE_NOTICE.md) and [`PROVENANCE.md`](PROVENANCE.md).

The modern transcription texts are not redistributed in this repository.
