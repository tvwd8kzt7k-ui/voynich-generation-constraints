# VGDT v0.1 protocol freeze — 2026-09-30

Protocol ID: `VGDT-FAMILY-NULLS-2026-09-30-v0.1`

This document freezes the first reusable diagnostic panel extracted from the Voynich generative-constraints project.

The instrument is **Voynich-derived but not Voynich-scored**. Each corpus is first evaluated against nulls built from that corpus. Cross-corpus comparison is performed only after those self-relative profiles have been computed.

## Development provenance

The component measurements were developed while analysing Voynichese and while auditing Torsten Timm's fixed self-citation output. Timm's published output is therefore a development/control corpus, not a pristine post-freeze holdout.

The v0.1 panel below was fixed before scoring Michael Greshko's Naibbe reference ciphertext with these measurements. The Naibbe file structure was inspected only to define an adapter that respects its genuine lines and blank-delimited blocks; no bins, nulls, cue definitions, or decomposition categories were changed after seeing the Naibbe results.

Any later diagnostic suggested by Voynich, Timm, Naibbe, or another corpus belongs to a later protocol version.

## Representation

Use the parent project's frozen EVA normalization, 12-slot decoder, and FAMILY map.

A FAMILY is the 12-slot tuple after concrete slot faces have been mapped to their frozen FAMILY labels.

Cue = the first two non-empty FAMILY components, including slot indices.

Invalid 12-slot tokens are excluded from FAMILY analysis. Their source lines remain part of the structural adapter so that line/page/block boundaries are not silently rewritten around parse failures.

## Core panel

### 1. FAMILY frequency spectrum

Report:

- valid FAMILY tokens;
- FAMILY types;
- hapax FAMILY types;
- FAMILY types occurring 2–20 times;
- FAMILY types occurring 21+ times;
- Top-10 FAMILY token share.

No aggregate similarity score is produced.

### 2. Cue-conditioned exact-FAMILY lag spectrum

Fixed token-distance bins:

`1 / 2–5 / 6–10 / 11–20 / 21–50 / 51–100`

Pairs are compared only when both positions have the same cue.

### 3. OUTER+CUE null

Within each genuine outer unit and cue stratum, permute exact-FAMILY labels among their observed positions.

Preserved:

- outer-unit membership;
- token positions;
- cue at every position;
- exact-FAMILY multiset within each outer-unit × cue stratum.

Destroyed:

- ordering of FAMILY labels inside those strata.

### 4. LINE+CUE null

Within each physical line and cue stratum, permute exact-FAMILY labels among their observed positions.

Preserved:

- physical lines;
- token positions;
- cue at every position;
- exact-FAMILY multiset within each line × cue stratum.

Destroyed:

- ordering of FAMILY labels inside those finer strata.

This is the stronger composition-preserving null. If an OUTER+CUE residual disappears under LINE+CUE, line composition is sufficient to account for that residual at the tested resolution.

### 5. Consecutive exact-FAMILY return gaps

Fixed bins:

`1 / 2–5 / 6–10 / 11–20 / 21–50 / 51–100 / 101+`

A consecutive return is the gap between successive occurrences of the same exact FAMILY within the same analysed outer unit.

### 6. 21–50 same-cue pair decomposition

For same-cue exact-FAMILY matches at distance 21–50, report:

- all exact-FAMILY matches;
- direct consecutive return;
- exactly one intervening same-FAMILY occurrence;
- two or more intervening same-FAMILY occurrences;
- non-direct chain containing at least one <=5-token step;
- non-direct chain containing no <=5-token step.

Direct pairs are not counted in either short-chain category.

This decomposition is intended to distinguish direct medium-range return from medium-range similarity produced by chains of shorter returns.

## Randomization

Frozen reference setting: **400 deterministic permutations** per null.

The implementation uses Mulberry32 with separate deterministic seed streams:

- OUTER+CUE: `0x33445566 + replicate_index * 65537`;
- LINE+CUE: `0x778899AA + replicate_index * 104729`.

`replicate_index` is 0-based. Group traversal follows first occurrence order in the parsed corpus.

Changing the number of permutations, RNG, seed stream, or group traversal is allowed for development or sensitivity analysis, but such a run is not the frozen v0.1 reference result.

## Length-controlled cross-corpus spectrum comparison

When two corpora have different valid FAMILY-token counts, downsample the longer corpus without replacement to the shorter count.

Frozen reference setting:

- 500 deterministic repetitions;
- A-side sampling seed: `0xA1B2C3D4 + replicate_index * 65537`;
- B-side sampling seed: `0x1A2B3C4D + replicate_index * 104729`;
- forward partial Fisher–Yates sampling without replacement;
- report medians and central 95% sampling intervals using linear quantiles at `(N-1)p`;
- do not collapse the comparison to a single score.

This control applies to the spectrum comparison only. Lag/null/return analyses use each corpus at its own full valid length.

## Adapter policy

### ZL3b

- frozen clean42 material;
- locus `P` only;
- physical manuscript page = outer unit;
- physical transcription line = line.

### Timm fixed generator

- pinned published generated body;
- 29 generated lines = one outer unit/page;
- final partial page is retained for v0.1 recurrence/null metrics;
- generated line = line;
- no bifolio, context, hand, or other manuscript metadata is invented.

### Naibbe reference ciphertext

- source-preserved non-empty ciphertext line = line;
- blank-delimited block = outer unit;
- one-line blocks remain in the FAMILY spectrum;
- one-line blocks are excluded from recurrence/null metrics because they provide no multi-line outer-unit comparison.

### New external generators

Use genuine documented units when they exist.

If no meaningful outer-unit structure exists, do not fabricate manuscript pages. Either:

1. use one explicit single outer unit and state the limitation; or
2. restrict interpretation to line-level and spectrum measurements.

Adapter decisions must be made from source/documentation structure before inspecting diagnostic results.

## Anti-tuning rule

After inspecting a new corpus, do not change the following and present the changed run as v0.1:

- FAMILY representation;
- cue definition;
- lag bins;
- return-gap bins;
- OUTER+CUE null;
- LINE+CUE null;
- 21–50 decomposition categories;
- reference permutation counts;
- length-control repetition count.

A useful new diagnostic is recorded for the next protocol version.

## Interpretation rules

VGDT v0.1 does not classify:

- meaning vs meaninglessness;
- natural language vs cipher vs pseudo-text;
- authorship;
- historical production mechanism.

A residual means only that the tested null did not remove it.

If a stronger structure-preserving null removes an effect, the newly preserved structure is sufficient to account for that effect at the tested resolution. This is a mechanism-localisation statement, not proof of a unique historical cause.

If an effect survives, the current null is insufficient. The tool does not automatically name the missing mechanism.

Similar profiles do not prove identical mechanisms. Different profiles show that the measured mechanisms are not equivalent at this resolution.

## Frozen stopping rule for the v0.1 release

The v0.1 instrument is release-ready when:

1. one implementation runs the same frozen panel on ZL3b, Timm, and Naibbe;
2. pinned public inputs are verified by commit/blob identity;
3. golden regression outputs reproduce the already-recorded reference values;
4. a one-command reference suite succeeds on a clean environment;
5. all adapter choices and non-applicable comparisons are explicit;
6. the public documentation states the interpretation ceiling above.

Voynichese itself does not need to be deciphered, semantically classified, or historically explained for this instrument release to be complete.
