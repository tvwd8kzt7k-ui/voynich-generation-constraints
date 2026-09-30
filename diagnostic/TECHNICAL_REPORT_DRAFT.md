# Decomposing Voynich-like recurrence with nested structure-preserving nulls

## A frozen diagnostic comparison of ZL3b, Timm self-citation, and the Naibbe cipher

**Draft — 2026-09-30**

## Abstract

Statistical properties of the Voynich Manuscript are often evaluated by asking whether a proposed generator reproduces a collection of manuscript-like measurements. This study asks a narrower question: when an apparent recurrence effect is observed, at what structural level does it disappear once progressively stronger composition-preserving nulls are applied? We use a frozen 12-slot FAMILY representation and compare the Voynich ZL3b clean42 transcription subset with two published controls: the fixed output of Timm and Schinner's self-citation generator and a meaning-preserving reference ciphertext produced by Greshko's Naibbe cipher. Each corpus is first evaluated against nulls constructed from itself; no scalar Voynich-similarity score is computed. In ZL3b, positive exact-FAMILY clustering from lag 2 through lag 50 under a page-level cue-conditioned null is largely removed when each physical line's cue-conditioned FAMILY composition is preserved. The remaining 21–50 all-pair excess is not an excess of direct medium returns: direct consecutive returns are deficient, while chains containing multiple intervening occurrences and at least one <=5-token step are strongly enriched. The two controls produce different residual signatures. Timm's fixed output is much more FAMILY-concentrated and becomes near-null at lag 1 after line composition is preserved; Naibbe is more FAMILY-diverse and retains a strong negative lag-1 residual. These results do not identify plaintext, meaning, or a unique historical production process. They show that apparently similar Voynich-like statistics can arise from distinguishable levels of generative structure, and that nested structure-preserving nulls can localise which level still requires explanation.

## 1. Scope

This is not a decipherment and does not classify the Voynich Manuscript as language, cipher, hoax, or meaningless text. The aim is to package one late-stage result of the generative-constraints project as a reproducible diagnostic instrument.

The central question is:

> When a corpus shows an exact-FAMILY recurrence signature, which progressively cheaper structural description is already sufficient to reproduce it?

The approach differs from a scalar similarity test. Each corpus is first compared with null distributions generated from that same corpus while preserving selected structure. Cross-corpus comparison is made only after these self-relative profiles have been obtained.

## 2. Relation to existing generator comparisons

Timm and Schinner proposed a self-citation mechanism in which previously written strings are copied and modified; their published generator demonstrates that a meaningless iterative process can reproduce several Voynich-like statistical properties. Timm (2026) develops the broader argument that Voynichese is a dynamic text whose vocabulary and usage change during production. The fixed public generated text is used here as one control, not as a stand-in for every possible self-citation implementation or for that broader dynamic-production hypothesis.

Greshko's Naibbe cipher is a verbose homophonic substitution cipher designed to transform Latin or Italian plaintext into decipherable Voynich-like ciphertext while reproducing multiple manuscript statistics. It is therefore especially useful as a contrasting control: its output is meaning-preserving by construction, whereas the fixed Timm output is generated without plaintext.

Rozanova and Temerev (2026) independently compare Voynichese with matched prose, cipher, and pseudo-text controls, including Naibbe and self-citation, and emphasize that several conventional unit assumptions fail. The present analysis should therefore not be described as the first neutral comparison of these generators. Its narrower contribution is the use of nested composition-preserving nulls and return-chain decomposition to ask which structural level accounts for a measured recurrence effect.

## 3. Frozen representation

The analysis uses the parent project's 12-slot decomposition. Concrete slot values are mapped to FAMILY labels, yielding a 12-component FAMILY tuple for each valid token.

For every FAMILY, a cue is defined as the first two non-empty FAMILY components, including their slot indices. The cue is intentionally coarse: the null models preserve it while randomising the remaining exact-FAMILY identity at different structural levels.

Invalid 12-slot tokens are excluded from FAMILY statistics, but their source line boundaries are not collapsed. This prevents parse failure from silently changing the document structure used by the null models.

## 4. Frozen diagnostic panel

Six token-distance bins are fixed in advance:

`1 / 2–5 / 6–10 / 11–20 / 21–50 / 51–100`.

For positions sharing the same cue, the observed statistic is the rate at which the exact FAMILY is equal.

Two nested nulls are used.

**OUTER+CUE null.** Exact FAMILY labels are permuted within each outer-unit × cue stratum. For ZL3b the outer unit is a physical page; for Timm it is a 29-line generated page; for Naibbe it is a blank-delimited source block. This preserves the cue composition and exact-FAMILY multiset of each outer unit while destroying order inside it.

**LINE+CUE null.** Exact FAMILY labels are permuted within each physical line × cue stratum. This additionally preserves the exact FAMILY composition of every line. If an effect present under OUTER+CUE disappears under LINE+CUE, line composition is sufficient to account for that effect at the tested resolution.

The panel also measures consecutive exact-FAMILY return gaps in fixed bins and decomposes 21–50 same-cue matching pairs into direct returns, one intervening occurrence, two or more intervening occurrences, and non-direct chains with or without a <=5-token step.

The reference run uses 400 deterministic permutations. All RNG and sampling seed streams are part of the protocol freeze.

## 5. Reference corpora and provenance

The three reference inputs are byte-pinned public files.

| corpus | source | pinned blob | valid FAMILY tokens |
|---|---|---|---:|
| ZL3b clean42 P | `matthewdgreen/cipher_benchmark`, commit `729aad62...` | `2a4533ab...` | 24,250 |
| Timm fixed output | `TorstenTimm/SelfCitationTextgenerator`, commit `a6ede220...` | `31b5f847...` | 7,856 |
| Naibbe reference ciphertext | `greshko/naibbe-cipher`, commit `f2675ec5...` | `c95b9550...` | 30,233 |

The full hashes and paths are included in the executable release manifest. The third-party texts are not redistributed.

## 6. FAMILY spectrum

The three corpora occupy clearly different FAMILY-frequency regimes.

| metric | ZL3b | Timm | Naibbe |
|---|---:|---:|---:|
| valid FAMILY tokens | 24,250 | 7,856 | 30,233 |
| FAMILY types | 745 | 197 | 980 |
| hapax types | 227 | 37 | 180 |
| types occurring 2–20 times | 383 | 109 | 579 |
| types occurring 21+ times | 135 | 51 | 221 |
| Top-10 token share | 0.36635 | 0.59496 | 0.34052 |

Length matching does not remove the main contrast. At 7,856 tokens, ZL3b has a median 513 FAMILY types across 500 frozen subsamples, versus 197 in the complete Timm output. At 24,250 tokens, Naibbe has a median 940 FAMILY types, versus 745 in complete ZL3b.

This is not a ranking of which text is "more Voynich-like". It establishes that the controls reach superficially Voynich-like outputs using substantially different FAMILY-frequency regimes.

## 7. Nested null result

### 7.1 ZL3b

Under OUTER+CUE, ZL3b shows positive exact-FAMILY residuals from lag 1 through lag 50. The 21–50 bin, for example, has excess +0.00586 (z ≈ +4.03).

After LINE+CUE composition is preserved, the positive residuals beyond the immediate scale largely disappear:

| lag | LINE+CUE excess | z |
|---|---:|---:|
| 1 | +0.01593 | +3.56 |
| 2–5 | +0.00162 | +0.79 |
| 6–10 | -0.00474 | -2.52 |
| 11–20 | -0.00077 | -0.72 |
| 21–50 | +0.00064 | +1.53 |
| 51–100 | -0.00008 | -0.28 |

Thus line composition accounts for the positive 2–50 clustering as a class. The remaining positive ordering residue is immediate lag 1. The full-clean42 reference also has a negative deviation at 6–10, which should not be re-described as "no residual of any kind."

### 7.2 Timm fixed self-citation output

Timm's fixed output has positive OUTER+CUE residuals at 6–10 and 11–20, but these are strongly attenuated by LINE+CUE conditioning. The lag-1 LINE+CUE residual is +0.00187 (z ≈ +0.21), effectively near the null at this resolution.

This result is compatible with a generator that creates strong local/page structure while not reproducing the specific immediate FAMILY ordering residue measured in ZL3b.

### 7.3 Naibbe reference ciphertext

Naibbe shows the opposite immediate signature. Lag 1 is below both OUTER+CUE and LINE+CUE expectations. Under LINE+CUE, the lag-1 excess is -0.02373 (z ≈ -4.40).

The same FAMILY diagnostic therefore distinguishes the fixed self-citation output, the meaning-preserving cipher output, and the manuscript reference population without using semantic labels as inputs.

## 8. Why the ZL3b 21–50 tail is not direct medium memory

The 21–50 all-pair statistic can look like a medium-distance recurrence process if every matching pair is counted equally. Consecutive-return analysis shows otherwise.

For ZL3b under the OUTER+CUE null:

| 21–50 component | excess | z |
|---|---:|---:|
| all matching pairs | +0.00586 | +4.03 |
| direct consecutive return | -0.00218 | -3.44 |
| exactly one intervening same FAMILY | -0.00255 | -3.69 |
| two or more intervening occurrences | +0.01058 | +7.34 |
| non-direct chain containing <=5 step | +0.01172 | +7.05 |
| non-direct chain with no <=5 step | -0.00368 | -3.05 |

The positive medium-distance tail is therefore dominated by already-bursty FAMILY sequences. A separate mechanism that remembers an exact FAMILY for 21–50 tokens and then directly recalls it is not required by this statistic.

The same <=5-step chain excess is not present in the two reference controls: Timm gives -0.00327 (z ≈ -1.02), while Naibbe gives -0.00249 (z ≈ -2.36).

## 9. Interpretation

The result supports a simpler descriptive architecture for the FAMILY side of Voynichese:

1. structural/productive FAMILY grammar;
2. coarse work-unit or register-dependent FAMILY preference;
3. line-level FAMILY composition state;
4. an immediate within-line ordering residue.

This is a model of what statistical layers are needed to reproduce the measured effects. It is not a reconstruction of the historical writing procedure.

More generally, the exercise shows why matching a collection of headline statistics is insufficient to identify a generator. A fixed self-citation process and a meaning-preserving cipher can both reproduce multiple Voynich-like properties while leaving distinguishable residual dynamics when the same nested nulls are applied.

## 10. Limitations

The analysis has several important limits.

First, the clean42 material was repeatedly inspected during model development. The result is reproducible frozen exploratory evidence, not a pristine preregistered confirmation.

Second, the 12-slot FAMILY representation is itself a modelling choice. The diagnostic is conditional on that representation and its parser.

Third, the three corpora do not possess identical native metadata. The adapters preserve genuine page/line/block structure where available and refuse to invent manuscript-specific metadata, but the outer unit is not historically equivalent across all controls.

Fourth, one fixed output from Timm and one Naibbe reference ciphertext cannot characterize every implementation or parameterization of either broader mechanism.

Fifth, the panel does not detect or exclude semantic content. It only asks what structural assumptions are needed to reproduce selected statistics.

## 11. Reproducibility

The release candidate contains:

- `PROTOCOL_FREEZE_v0.1.md` — scientific definitions and anti-tuning rule;
- `vgdt.py` — standard-library-only implementation;
- `REFERENCE_EXPECTATIONS.json` — deterministic golden subset;
- `REFERENCE_VALIDATION.md` — independent recomputation notes;
- `CLAIM_SET_v0.1.md` — claim/interpretation boundaries;
- tests and a one-command reference suite.

Reference reproduction:

```bash
python -m unittest discover -s tests -v
python vgdt.py reference-suite --fetch --check REFERENCE_EXPECTATIONS.json
```

The second command verifies input blobs and fails non-zero if the frozen checkpoints do not reproduce.

## References

- Greshko, M. A. (2025). *The Naibbe cipher: a substitution cipher that encrypts Latin and Italian as Voynich Manuscript-like ciphertext*. Cryptologia. DOI: 10.1080/01611194.2025.2566408.
- Rozanova, L., & Temerev, A. (2026). *A Glyph Is Not a Letter, a Token Is Not a Word, a Space Is Not a Space: What the Units of Voynichese Are Not*. arXiv:2608.17096.
- Timm, T., & Schinner, A. (2020). *A possible generating algorithm of the Voynich manuscript*. Cryptologia 44(1), 1–19. DOI: 10.1080/01611194.2019.1596999.
- Timm, T. (2026). *The challenge of analyzing a dynamic text: why the Voynich manuscript resists conventional interpretation*. Cryptologia. DOI: 10.1080/01611194.2026.2693462.
- Matsuda, D. (2026). *Generative Constraints in the Voynich Manuscript: From Known Structure to Reproducible Tests*. Zenodo. DOI: 10.5281/zenodo.22754587.
