# Cross-transcription robustness — ZL3b vs IT2a

Date: 2026-09-27

## Purpose

The primary canonical analyses were developed and frozen on ZL3b. This pass applies the same current definitions to IT2a, an alternate EVA transcription of the same manuscript. The purpose is narrow: test whether the principal measurements are artifacts of ZL3b-specific transcription choices.

This is **not** independent-corpus validation and is **not** evidence that every transcription will give the same result. Both sources represent the same physical manuscript, and the clean42/CAL8 selections were already known from the ZL3b work.

## Pinned alternate input

- transcription: IT2a
- mirror repository: `oklo/voynich_gpt`
- commit: `2d7c61c387ad6962de730caf73c48612bc8f6957`
- path: `IT2a-n.txt`
- Git blob SHA-1: `7f491b574b65e5fba6b553e57372c3fa50e10fec`
- IVTFF header: `#=IVTFF EvaT 2.0 M 3`
- file provenance header: `Extracted from LSI_ivtff_0d.txt`
- version header: `Version 2a of 02/02/2023`

The transcription text is not bundled.

## Side-by-side checkpoints

| Measurement | ZL3b primary | IT2a alternate |
|---|---:|---:|
| clean42 valid 12-slot tokens | 24,250 | 24,233 |
| clean42 exact types | 2,711 | 2,842 |
| CAL8 valid tokens | 4,963 | 4,946 |
| low-dimensional box0 coverage | 43.876% | 42.434% |
| box1 coverage | 71.033% | 69.026% |
| box2 coverage | 90.025% | 88.577% |
| box3 coverage | 97.835% | 97.416% |
| context gain over family baseline, nats/token | +0.049640 | +0.049585 |
| hand gain over family baseline, nats/token | +0.046673 | +0.045859 |
| aggregate context minus hand, nats/token | +0.002967 | +0.003726 |
| uniform all-seen reuse gain, nats/token | +0.014136 | +0.014255 |
| bifolio-local true gain, nats/event | +0.024825 | +0.024509 |
| true bifolio source minus wrong-source mean, nats/event | +0.051512 | +0.051291 |
| bifolios positive vs wrong-source mean | 42/42 | 42/42 |
| line-null within-line excess | +0.010883 | +0.010826 |
| line-null cross-line excess | -0.007370 | -0.006957 |
| within-line positive bifolios | 31/42 | 34/42 |
| cross-line positive bifolios | 15/42 | 15/42 |

The exact-form spectrum changes modestly, as expected for a different transcription, but the main structural and predictive effects retain the same direction and very similar magnitude.

## Uniform-reuse diagnostic

The same qualitative failure survives. IT2a has 2,842 observed exact types and 1,418 hapax. With uniform all-seen reinforcement at weight 32, the fixed-seed simulation still has a median 3,317.5 types and 2,162 hapax. Broad reuse helps prediction, but remains insufficient to create the observed exact-form concentration.

## Line-local ordering

The line-composition-preserving null is particularly close across transcriptions:

- ZL3b within excess: `+0.0108825`; IT2a: `+0.0108260`.
- ZL3b cross-line excess: `-0.0073700`; IT2a: `-0.0069567`.

This reduces the plausibility that the sign pattern is created by ZL3b-specific face readings or tokenization decisions. It still does not identify a historical mechanism.

## Reproduce

```bash
python tools/run_transcription_robustness.py --fetch
```

To run both the ZL3b primary core and this IT2a pass:

```bash
python tools/run_all_evidence.py --fetch
```

## Interpretation ceiling

This comparison supports transcription robustness for the tested measurements. It does not establish mechanical production, semantic absence, a unique generator, or generalization to all transcription systems. The next stronger test is an independently implemented parser/analysis, ideally by a third party, and additional transcription systems where the representation can be mapped without changing the scientific question.
