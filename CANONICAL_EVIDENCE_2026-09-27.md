# Canonical evidence state — 2026-09-27

This note separates the **current evidence** from the historical path by which hypotheses were invented.

The physical/cognitive reconstruction ideas (rule table, booklet, front/back, finger position, bags/stones, shortcuts, favorites as conscious choices, etc.) are not treated as evidence. They remain optional thinking aids. The evidentiary layer is limited to pinned data, explicit transformations, explicit models/nulls, and machine-readable outputs.

## Canonical input

- transcription mirror: `matthewdgreen/cipher_benchmark`
- commit: `729aad62d12483c549e64a2541d4f9255538c8cf`
- path: `benchmark/unsolved/sources/voynich/transcriptions/ZL3b-n.txt`
- Git blob SHA-1: `2a4533ab9bdfa85db9bad602d590978953055df1`
- analysis set: frozen clean42 list
- canonical valid-token count on clean42: **24,250**

The older exploratory checkpoint of 23,615 tokens is not used as a target. Its missing exclusion rule is not reconstructed by numerical fitting.

## Direct / deterministic structure checkpoints

The reconstructed CAL8 descriptive analysis reproduces the logged observations exactly:

- 4,963 valid tokens;
- 1,181 exact types;
- exact-count bins: 687 / 169 / 70 / 86 / 75 / 47 / 47 for counts 1 / 2 / 3 / 4–5 / 6–10 / 11–20 / 21+;
- 47 count>=21 exact forms, belonging to 24 family forms;
- within those high-frequency families, 33 exact-form pairs: 23 at face-Hamming distance 1, 10 at distance 2, 0 at distance >=3;
- using all 2,817 tokens in those 24 families, weighted top-1/top-2/top-3 variable-slot coverage is approximately 71.03% / 90.02% / 97.83%;
- 16/24 families have at most two effectively variable slots under the explicit `<95% modal share and >=5 alternative occurrences` rule.

The clean42 observed exact spectrum is:

- 24,250 tokens;
- 2,711 exact types;
- 1,343 hapax types;
- 1,160 types with counts 2–20;
- 208 types with count >=21.

The raw strict-line-interior cross-half exact recurrence is 10,454 / 17,326 = **0.6033706568**.

## Context versus hand — new canonical comparison

`canonical/tests/context_hand.py` is a new explicit analysis, not an attempt to recreate an undocumented historical driver.

The model conditions exact choice on the family form. Its theoretical concrete support is generated from the family map. Global exact probabilities use Jeffreys alpha=0.5; context (`I|L`) and hand (`H`) are each shrunk to the global distribution with tau=100. Evaluation is leave-one-bifolio-out across clean42.

Current aggregate results:

- global: -1.86841925 nats/token;
- context: -1.81877885, gain +0.04964040;
- hand: -1.82174611, gain +0.04667314;
- context+hand interaction model: -1.81261017;
- hand-after-context increment: +0.00616868.

Both context and hand beat the global model on 38/42 bifolios. Context beats hand on only **18/42** bifolios, and the median bifolio context-minus-hand difference is slightly negative (-0.00080583 nats/token).

Therefore the old exploratory wording **"context is more robust than hand" is not retained as a canonical conclusion**. The supported statement is:

> Both manuscript context and hand contain predictive information about exact concrete-form choice beyond a global family-conditioned distribution. In this canonical specification the aggregate context score is slightly better, but there is no robust bifolio-level dominance of context over hand.

## Uniform all-seen reuse — new canonical comparison

`canonical/tests/uniform_reuse.py` tests an explicit broad-reuse mechanism: inside each bifolio and family, every exact form already seen receives the same multiplicative accessibility weight. The base distribution is the canonical context model above.

Nested LOBO selection chooses weight 2.0 for all 42 targets on the fixed grid. Conditional predictive likelihood improves:

- baseline: -1.81877885 nats/token;
- all-seen reuse: -1.80464293;
- gain: +0.01413591;
- positive target bifolios: 29/42.

So the broad statement **"uniform reuse simply fails" is too strong**.

However, fixed-seed free exact-choice simulation on the observed family/context scaffold still fails to recover the observed concentration. Observed is 2,711 types / 1,343 hapax. Median simulations remain:

| uniform seen weight | exact types | hapax |
| ---: | ---: | ---: |
| 1 | 4000.5 | 2739.0 |
| 2 | 3813.0 | 2630.0 |
| 4 | 3619.5 | 2484.5 |
| 8 | 3456.0 | 2351.0 |
| 16 | 3295.0 | 2192.5 |
| 32 | 3149.5 | 2046.5 |

Even very strong uniform reinforcement leaves substantially too many distinct types and hapax. Under this canonical implementation it also does **not** reproduce the old claimed signature of "too many medium-frequency forms"; that historical wording is therefore not carried forward.

The current supported statement is:

> Broad all-seen reuse is a real predictive component, but it is insufficient by itself to account for the observed exact-form concentration. Additional selective structure is required.

## Human-operation line-ordering result

The 2026-09-26 line-preserving null remains the strongest narrow result in that branch:

- within line: observed same-face 0.48767719, line-preserving expectation 0.47679467, excess +0.01088252;
- crossing a line boundary: observed 0.48795537, expectation 0.49532534, excess -0.00736997;
- within-line excess positive in 31/42 bifolios; cross-line excess positive in 15/42;
- family effects are heterogeneous.

This is an ordering statement. No unique physical or cognitive implementation is inferred.

## Evidence policy from this point

1. Current claims are tied to canonical code and outputs, not to remembered exploratory numbers.
2. If an old log result cannot be regenerated from an explicit current definition, it remains historical only.
3. Historical reconstruction is not needed unless it materially changes a current scientific claim.
4. New canonical analyses may revise old freeze prose; revisions are recorded explicitly rather than forcing new analyses to match old numbers.
5. The physical production story remains outside the evidentiary core unless it yields a new separately testable prediction.

## Low-dimensional family boxes — canonical deterministic audit

`canonical/tests/low_dimensional_family.py` now states the low-dimensional claim directly, without requiring the historical box simulation driver.

In CAL8, select every family containing at least one exact form with count >=21, then include **all 2,817 tokens** from those 24 selected families. Within each family, rank slots by `1 - modal face share` (ties by alternative count and slot position). Define box-k as leaving the k highest-variability slots free while fixing all other slots to the family modal face.

Weighted token coverage is:

- box0: **0.43876464**;
- box1: **0.71033014**;
- box2: **0.90024849**;
- box3: **0.97834576**.

Under the explicit `<95% modal share and >=5 alternative occurrences` audit, 16/24 families have at most two effectively variable slots. Box2 covers at least 90% of tokens in 16/24 families and at least 95% in 15/24.

This is evidence that these high-frequency families occupy a low-dimensional subset of their theoretical concrete-face space. “Box” is mathematical shorthand only.

## Bifolio-local concrete-face state — canonical comparison

`canonical/tests/bifolio_local_face_bias.py` tests the local-state claim directly on 76,120 multi-face slot-family choice events.

For each held-out bifolio, the baseline is `P(face | slot, family, I|L, H)` fit outside that bifolio with Jeffreys smoothing. The four pages are split as the existing cross-half analyses do: sorted page positions `[0,3]` versus `[1,2]`. Counts from one half are then used to adapt the baseline when predicting the opposite half.

At the focal exploratory shrinkage setting tau=20:

- baseline: **-0.76414299 nats/event**;
- true opposite-half local model: **-0.73931800**;
- gain: **+0.02482499 nats/event**;
- true source minus the mean of 41 wrong-bifolio sources: **+0.05151177 nats/event**;
- true source beats the wrong-source mean in **83/84 directions**;
- true source ranks first among 42 sources in **27/84** directions and in the top five in **58/84**;
- same-bifolio adaptation improves over the context+hand baseline in **28/42** bifolios;
- true source beats the wrong-source mean in **42/42** bifolios.

The true-vs-wrong-source contrast is not dependent on one narrow tau value: for tau 5, 10 and 20 all 42 bifolios are positive against the wrong-source mean; the aggregate contrast remains positive through the reported tau grid up to 200.

This supports a **bifolio-local shared statistical state** after conditioning the baseline on the named context and hand fields. It does not identify a physical inventory, depletion rule, bag, or other historical implementation. The tau grid was explored on the same repeatedly inspected data, so the result remains exploratory rather than pristine confirmation.

## Relation to a mechanistic-generation interpretation

Taken together, the structural, local-state, recurrence and ordering results provide a stronger target for a mechanistic generator: substantial observed structure can be captured by explicit nonsemantic constraints and local stochastic state. That reduces the amount of structure that *requires* a semantic explanation in these measured statistics.

It is still a separate historical claim to say that the manuscript was in fact produced by a mechanical, pseudo-mechanical, or nonsemantic process. Reproduction of this package would validate the reported statistical constraints and model comparisons, not uniquely identify the manuscript's historical production method.
## Cross-transcription check added in v0.8

The current canonical definitions were applied unchanged to pinned IT2a. The principal directions survive: low-dimensional family occupancy remains high (box2 0.8858, box3 0.9742); context and hand gains are almost unchanged; uniform all-seen reuse remains predictive but insufficient for the exact spectrum; the true bifolio opposite half remains better than wrong-bifolio sources in all 42 bifolios; and the line-preserving null remains positive within lines (+0.010826) but negative across lines (-0.006957).

This is transcription robustness for one alternate EVA transcription of the same manuscript. It is not independent-corpus confirmation and does not justify a claim of universality across transcription systems. See `TRANSCRIPTION_ROBUSTNESS_2026-09-27.md`.

