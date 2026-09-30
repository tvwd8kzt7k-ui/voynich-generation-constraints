# Localizing Voynichese recurrence with nested structure-preserving nulls

## A frozen comparison of ZL3b, Timm self-citation, and the Naibbe cipher

**Daiki Matsuda — technical report v0.1 — 2026-09-30**

**DOI:** `10.5281/zenodo.23065615`

## Abstract

Statistical studies of the Voynich Manuscript often ask whether a proposed generator reproduces a set of manuscript-like measurements. This report asks a different question: **when an apparent recurrence effect is observed, at what structural level does it disappear once progressively more local composition is preserved?**

A frozen 12-slot FAMILY representation is applied to three pinned public corpora: the ZL3b clean42 Voynich transcription population, the fixed public output of Timm and Schinner's self-citation generator, and a meaning-preserving reference ciphertext produced by Greshko's Naibbe cipher. Each corpus is first evaluated against null distributions generated from that corpus itself. No scalar "Voynich similarity" score is computed.

In ZL3b, exact-FAMILY matching is positively enriched from lag 1 through lag 50 under a page-level cue-conditioned null. When each physical line's cue-conditioned FAMILY composition is also preserved, the positive 2–50 residuals disappear as a class; the remaining clear positive ordering residue is immediate lag 1. The apparent 21–50 all-pair excess is not an excess of direct medium-range returns: direct consecutive returns are deficient, whereas chains containing multiple intervening occurrences and at least one short (<=5-token) step are strongly enriched.

The two reference controls leave different residual signatures under the same panel. Timm's fixed output is substantially more FAMILY-concentrated than ZL3b and has a near-null lag-1 residual after line composition is preserved. Naibbe is more FAMILY-diverse than ZL3b at matched length and retains a strong negative lag-1 residual. These results do not identify plaintext, meaning, authorship, or a unique historical production mechanism. They show that several superficially similar Voynich-like statistics can be localized to different levels of generative structure, and that nested structure-preserving nulls can identify which level still requires explanation.

## 1. Research question and scope

This report is not a decipherment and does not classify the Voynich Manuscript as natural language, cipher, pseudo-text, hoax, or meaningless text.

The narrow question is:

> **Given an observed exact-FAMILY recurrence signature, what structural description is already sufficient to reproduce it, and what residual remains after that structure is held fixed?**

The resulting instrument is **Voynich-derived but not Voynich-scored**. A corpus is not assigned a single distance from the manuscript. Instead, each corpus is compared with null distributions constructed from its own observed structure. Cross-corpus comparison is made only after these self-relative residual profiles have been computed.

This distinction is central. A generator may reproduce a headline statistic for reasons different from those operating in the manuscript. Conversely, a mismatch in one fixed implementation does not by itself reject the broader class of mechanisms to which that implementation belongs.

## 2. Relation to prior work

Timm and Schinner (2020) presented a self-citation process in which previously written forms are copied and modified, showing that an iterative process without encoded plaintext can reproduce several statistical properties associated with Voynichese. Timm (2026) further argues that the manuscript should be treated as a dynamically evolving text rather than as the output of a static system. The fixed public generated text used here is therefore a concrete control implementation, not a substitute for the broader self-citation or dynamic-production hypotheses.

Greshko's Naibbe cipher (2025) is a verbose homophonic substitution cipher designed to transform Latin or Italian plaintext into decipherable Voynich-like ciphertext while reproducing multiple manuscript statistics. It provides a useful contrasting control because semantic plaintext is preserved by construction while the surface text is deliberately made Voynich-like.

Rozanova and Temerev (2026) independently compare Voynichese with matched prose, cipher, and pseudo-text controls, including Naibbe and self-citation, while challenging standard assumptions about glyph, token, and space units. The present report therefore does **not** claim novelty for neutral multi-control comparison itself. Its narrower contribution is to use **nested composition-preserving nulls plus return-chain decomposition** to localize an observed recurrence effect to the level of structure that is sufficient to account for it.

The statistical ingredients—permutation tests, conditional nulls, stratification, and decomposition—are established methods. The contribution claimed here is their frozen organization around this specific Voynich generative question and the resulting decomposition of the recurrence signature.

## 3. Development status and anti-tuning rule

The clean42 Voynich material was repeatedly inspected during model development. The results are therefore **reproducible frozen exploratory evidence**, not a pristine preregistered confirmation.

The Timm output was also examined during development and is not a post-freeze holdout. By contrast, the v0.1 measurement panel—representation, cue definition, lag bins, null definitions, return bins, and 21–50 chain categories—was fixed before the Naibbe reference ciphertext was scored with that panel. The Naibbe file structure was inspected only to define an adapter that preserves its genuine lines and blank-delimited blocks.

The v0.1 anti-tuning rule is simple: after inspecting a new corpus, changing the FAMILY representation, cue definition, bins, nulls, or chain categories produces a **new protocol version**, not a revised v0.1 result.

## 4. Frozen representation

The analysis uses the parent project's frozen EVA normalization and 12-slot decomposition. Each valid token is represented as a 12-component tuple of concrete slot values. Concrete alternatives occupying the same structural role are then mapped to frozen FAMILY labels, producing an exact FAMILY tuple.

For every FAMILY token, the **cue** is defined as the first two non-empty FAMILY components, including their slot indices. The cue is intentionally coarse. The null models preserve it while randomizing the remaining exact-FAMILY identity at different structural levels.

Tokens that do not parse under the frozen 12-slot representation are excluded from FAMILY statistics. Their source line boundaries are not collapsed, preventing parse failures from silently rewriting document structure.

The representation is a model choice. All conclusions in this report are conditional on it.

## 5. Frozen diagnostic panel

Six token-distance bins are fixed:

`1 / 2–5 / 6–10 / 11–20 / 21–50 / 51–100`.

For positions sharing the same cue, the observed lag statistic is the proportion whose exact FAMILY is identical.

Two nested nulls are used.

**OUTER+CUE null.** Exact-FAMILY labels are permuted within each outer-unit × cue stratum. This preserves token positions, cue identity, and the exact-FAMILY multiset of each outer unit while destroying ordering inside that stratum.

**LINE+CUE null.** Exact-FAMILY labels are permuted within each physical-line × cue stratum. This preserves all of the above at a finer level: the exact FAMILY composition of every line is fixed while only within-line ordering is randomized.

The logical interpretation is deliberately limited:

> If a positive residual present under OUTER+CUE disappears under LINE+CUE, then line-level FAMILY composition is sufficient to account for that positive residual at the tested resolution.

That is a statement of statistical sufficiency, not a claim that "line composition" is the historical cause.

The panel additionally measures consecutive exact-FAMILY return gaps in bins

`1 / 2–5 / 6–10 / 11–20 / 21–50 / 51–100 / 101+`

and decomposes 21–50 same-cue matching pairs into:

- direct consecutive return;
- exactly one intervening same-FAMILY occurrence;
- two or more intervening same-FAMILY occurrences;
- non-direct chains containing at least one <=5-token return step;
- non-direct chains containing no <=5-token return step.

The reference run uses 400 deterministic permutations. With 400 permutations, the smallest attainable two-sided Monte Carlo p-value in this implementation is approximately 0.00499; z-scores and effect sizes therefore carry more resolution than the most extreme p-values.

For cross-corpus FAMILY-spectrum comparison, the longer corpus is sampled without replacement to the shorter corpus length for 500 deterministic repetitions. This length control is not used to create a combined similarity score.

## 6. Reference corpora and adapters

The reference suite uses three byte-pinned public files.

| corpus | source | pinned blob | valid FAMILY tokens |
|---|---|---|---:|
| ZL3b clean42 P | `matthewdgreen/cipher_benchmark`, commit `729aad62…` | `2a4533ab…` | 24,250 |
| Timm fixed output | `TorstenTimm/SelfCitationTextgenerator`, commit `a6ede220…` | `31b5f847…` | 7,856 |
| Naibbe reference ciphertext | `greshko/naibbe-cipher`, commit `f2675ec5…` | `c95b9550…` | 30,233 |

The native structural metadata are not equivalent, so the adapters preserve genuine units rather than inventing manuscript metadata.

For ZL3b, the outer unit is a physical manuscript page and the line is the physical transcription line. For Timm, 29 generated lines form the documented page-sized outer unit; no bifolio, hand, or manuscript context is invented. For Naibbe, a blank-delimited source block is the outer unit and the source-preserved non-empty ciphertext line is the line. One-line Naibbe blocks contribute to the FAMILY spectrum but are excluded from multi-line recurrence/null analyses.

The complete source paths, commits, and blob identities are recorded in the executable release.

## 7. FAMILY-frequency regimes

The three corpora occupy visibly different FAMILY-frequency regimes.

| metric | ZL3b | Timm | Naibbe |
|---|---:|---:|---:|
| valid FAMILY tokens | 24,250 | 7,856 | 30,233 |
| FAMILY types | 745 | 197 | 980 |
| hapax types | 227 | 37 | 180 |
| types occurring 2–20 times | 383 | 109 | 579 |
| types occurring 21+ times | 135 | 51 | 221 |
| Top-10 token share | 0.36635 | 0.59496 | 0.34052 |

Length control does not remove the main contrast. At 7,856 tokens, frozen ZL3b subsamples have a median of 513 FAMILY types (central 95% interval 493–532), whereas the complete Timm output has 197. At 24,250 tokens, frozen Naibbe subsamples have a median of 940 FAMILY types (928–951.525), whereas complete ZL3b has 745.

These values are not a ranking of "Voynich-likeness." They show that different generators can reach broadly Voynich-like surface statistics while occupying substantially different FAMILY-frequency regimes.

## 8. Nested-null results

### 8.1 ZL3b

Under OUTER+CUE, ZL3b has positive exact-FAMILY residuals through lag 50:

| lag | excess | z |
|---|---:|---:|
| 1 | +0.04977 | +6.42 |
| 2–5 | +0.02809 | +7.60 |
| 6–10 | +0.01208 | +3.72 |
| 11–20 | +0.00976 | +4.23 |
| 21–50 | +0.00586 | +4.03 |
| 51–100 | +0.00178 | +1.27 |

After LINE+CUE composition is preserved, the positive 2–50 residuals disappear as a class:

| lag | excess | z |
|---|---:|---:|
| 1 | +0.01593 | +3.56 |
| 2–5 | +0.00162 | +0.79 |
| 6–10 | -0.00474 | -2.52 |
| 11–20 | -0.00077 | -0.72 |
| 21–50 | +0.00064 | +1.53 |
| 51–100 | -0.00008 | -0.28 |

The main positive ordering residue left after line composition is fixed is therefore immediate lag 1. The negative 6–10 residual in the full-clean42 reference should not be paraphrased as "nothing remains beyond lag 1"; the narrower conclusion is that the **positive** 2–50 clustering does not require an independent positive medium-range exact-FAMILY memory term.

### 8.2 Timm fixed self-citation output

Timm's fixed output shows positive OUTER+CUE residuals at 6–10 (+0.01840, z=+3.44) and 11–20 (+0.00928, z=+2.23). Under LINE+CUE these are attenuated to +0.00478 (z=+1.53) and +0.00072 (z=+0.41), respectively.

Its LINE+CUE lag-1 residual is +0.00187 (z=+0.21), near the null at this resolution. Thus the fixed implementation contains strong local/page structure without reproducing the specific positive immediate FAMILY-ordering residue measured in ZL3b.

This does not reject self-citation as a broader mechanism class. It characterizes one pinned public output under one frozen representation.

### 8.3 Naibbe reference ciphertext

Naibbe shows the opposite immediate signature. Under OUTER+CUE, lag 1 is below expectation by -0.03341 (z=-5.58). Even after line composition is preserved, lag 1 remains below expectation by -0.02373 (z=-4.40).

The three reference profiles therefore differ after the same hierarchy of preserved structure is imposed:

| corpus | LINE+CUE lag-1 excess | z |
|---|---:|---:|
| ZL3b | +0.01593 | +3.56 |
| Timm | +0.00187 | +0.21 |
| Naibbe | -0.02373 | -4.40 |

The panel does not use semantic labels as inputs. The fact that a plaintext-preserving cipher and a no-plaintext fixed generator leave different residuals is useful precisely because it demonstrates that the panel is not merely a meaning/no-meaning classifier.

## 9. Why the ZL3b 21–50 tail is not direct medium-range recurrence

The 21–50 all-pair statistic can look like medium-range memory because every matching pair is counted, whether or not the pair consists of consecutive occurrences of that FAMILY.

The return-chain decomposition gives a different picture. Under the ZL3b OUTER+CUE null:

| 21–50 component | excess | z |
|---|---:|---:|
| all matching pairs | +0.00586 | +4.03 |
| direct consecutive return | -0.00218 | -3.44 |
| exactly one intervening occurrence | -0.00255 | -3.69 |
| two or more intervening occurrences | +0.01058 | +7.34 |
| non-direct chain containing <=5 step | +0.01172 | +7.05 |
| non-direct chain with no <=5 step | -0.00368 | -3.05 |

Direct 21–50 returns are therefore deficient, not enriched. The positive all-pair tail is concentrated in FAMILY sequences that have already recurred multiple times and contain short return steps.

A separate mechanism that holds an exact FAMILY in memory for 21–50 tokens and then directly recalls it is therefore **not required by this statistic**.

The same short-chain enrichment is not reproduced by the two controls in the frozen suite. The <=5-step chain residual is -0.00327 (z=-1.02) for Timm and -0.00249 (z=-2.36) for Naibbe.

This result is the main mechanism-localisation result of v0.1: an apparent medium-distance effect is substantially reducible to a combination of local composition and short recurrence chains.

## 10. Descriptive architecture implied by the measurements

At the FAMILY level, the current measurements support a relatively compact descriptive architecture:

1. a structural/productive FAMILY grammar;
2. coarse work-unit or register-dependent FAMILY preference;
3. line-level FAMILY composition state;
4. an immediate within-line ordering residue.

This list is not a physical reconstruction. It does not imply bags, tables, cards, copying gestures, or any other historical device. It is a statement about the levels of statistical structure that remain necessary after cheaper descriptions have been conditioned on.

Several effects that initially looked like separate mechanisms become unnecessary as independent terms under this decomposition. In particular, the measured positive 21–50 tail does not require a standalone direct medium-range exact-FAMILY memory process.

## 11. What the control comparison establishes—and what it does not

The Timm and Naibbe controls serve two purposes.

First, they show that matching broad Voynich-like statistics does not force the same FAMILY dynamics. The controls occupy different frequency regimes and leave different residuals after identical conditioning steps.

Second, they provide a guard against reading every Voynich residual as evidence of semantics. Naibbe is meaning-preserving by construction, yet its v0.1 FAMILY residual pattern is not the manuscript pattern. Timm's fixed output is generated without plaintext, yet it also differs from the manuscript pattern. The panel therefore measures a level of organization that cuts across the semantic status of the control.

The comparison does **not** establish that one of these mechanisms is historically correct, that either broader hypothesis is refuted, or that the manuscript lacks or contains plaintext.

## 12. Limitations

Several limitations are material.

First, clean42 was repeatedly inspected during development. The frozen suite makes the result reproducible but does not retroactively make it confirmatory.

Second, the 12-slot FAMILY representation is a substantive modeling choice. A different representation can expose different structure.

Third, the outer unit is not historically equivalent across the three corpora. The adapters deliberately preserve genuine available units rather than fabricating common manuscript metadata. OUTER+CUE comparisons should therefore be read as structurally analogous, not as identical historical controls.

Fourth, one Timm output and one Naibbe reference ciphertext cannot characterize the full parameter space of either mechanism family.

Fifth, permutation significance only measures deviation from the specified null. A surviving residual does not name its cause; a disappearing residual shows sufficiency of the newly preserved structure, not unique causation.

Sixth, the panel does not test semantic content, translation, decipherability, authorship, chronology, or physical writing procedure.

## 13. Reproducibility and release status

The frozen v0.1 implementation contains:

- `PROTOCOL_FREEZE_v0.1.md` — scientific definitions and anti-tuning rule;
- `vgdt.py` — standard-library-only implementation;
- `REFERENCE_EXPECTATIONS.json` — deterministic golden subset;
- `REFERENCE_VALIDATION.md` — independent recomputation and connected-machine validation notes;
- `CLAIM_SET_v0.1.md` — claim and interpretation boundaries;
- unit tests and a one-command reference suite.

Reference reproduction is:

```bash
python -m unittest discover -s tests -v
python vgdt.py reference-suite --fetch --check REFERENCE_EXPECTATIONS.json
```

On 2026-10-01, the current GitHub `main` snapshot was downloaded as a fresh ZIP and tested from `diagnostic/` on a normally networked Windows environment.

The unit-test suite completed successfully with all 9 tests passing. The complete three-corpus reference suite then fetched and verified the pinned ZL3b, Timm, and Naibbe inputs and completed with:

```text
REFERENCE CHECK OK
```

The connected-machine software parity gate for v0.1 is therefore passed.

The scientific definitions were not changed to obtain this result. FAMILY definitions, cue definitions, lag bins, null definitions, deterministic seeds, and return-chain categories remain those frozen in `PROTOCOL_FREEZE_v0.1.md`.

The remaining work for v0.1 is archival rather than analytical: final citation metadata, an immutable release tag, and the corresponding Zenodo archive. No additional Voynich result is required for release.

## 14. Strongest supported conclusion

> **In the frozen ZL3b reference population, much of the apparent positive 2–50-token exact-FAMILY clustering is accounted for once line-level cue-conditioned FAMILY composition is preserved. The remaining 21–50 all-pair excess is dominated by chains of shorter returns rather than by an excess of direct medium-range recurrence. The same frozen panel applied to fixed self-citation and meaning-preserving Naibbe outputs yields different FAMILY-level residual signatures.**

That conclusion is narrower than a theory of the manuscript, but it is directly testable, executable, and falsifiable on additional generators and transcriptions.

## References

- Greshko, M. A. (2025). *The Naibbe cipher: a substitution cipher that encrypts Latin and Italian as Voynich Manuscript-like ciphertext*. **Cryptologia**. Published online 26 Nov 2025. DOI: `10.1080/01611194.2025.2566408`.
- Matsuda, D. (2026). *Generative Constraints in the Voynich Manuscript: From Known Structure to Reproducible Tests*. Zenodo. DOI: `10.5281/zenodo.22754587`.
- Rozanova, L., & Temerev, A. (2026). *A Glyph Is Not a Letter, a Token Is Not a Word, a Space Is Not a Space: What the Units of Voynichese Are Not*. arXiv:`2608.17096`, submitted 17 Aug 2026.
- Timm, T., & Schinner, A. (2020). *A possible generating algorithm of the Voynich manuscript*. **Cryptologia**, 44(1), 1–19. DOI: `10.1080/01611194.2019.1596999`.
- Timm, T. (2026). *The challenge of analyzing a dynamic text: why the Voynich manuscript resists conventional interpretation*. **Cryptologia**, published online 7 Sep 2026. DOI: `10.1080/01611194.2026.2693462`.
