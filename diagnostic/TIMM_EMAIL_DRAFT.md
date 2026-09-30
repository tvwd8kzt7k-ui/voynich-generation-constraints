# Draft follow-up email to Torsten Timm

**Do not send until the frozen release has passed the reference-suite check and an immutable release/tag is available.**

Subject: Follow-up: decomposing the remaining generator/manuscript differences

Dear Torsten,

Thank you again for your explanation of the remaining gap as a possible “human element.” I took that suggestion as a reason to ask a narrower question: how much of that residual can be decomposed into smaller, testable structural effects before assigning it to a general human-versus-algorithm difference?

I have now frozen a FAMILY-level diagnostic and applied the same definitions to three public reference texts: the ZL3b Voynich population, the fixed output of your SelfCitationTextgenerator, and Greshko’s Naibbe reference ciphertext. Naibbe is useful here because it is a meaning-preserving Voynich-like cipher, so it provides a very different production mechanism from fixed self-citation.

The main result is that the three outputs leave different residual signatures under the same nested null models. In the manuscript, much of the apparent 2–50-token exact-FAMILY clustering disappears once each line’s cue-conditioned FAMILY composition is preserved, but an immediate lag-1 ordering excess remains. In the fixed self-citation output, the corresponding lag-1 residual is near the line-conditioned null. In Naibbe it is strongly negative.

A second result concerns the manuscript’s apparent 21–50-token recurrence tail. When I separate all matching pairs from consecutive returns, the positive medium-range signal is not produced by direct returns after 21–50 tokens. Direct medium returns are actually deficient. The excess is concentrated in chains with multiple intervening occurrences, especially chains containing at least one short (<=5-token) return. The same short-chain excess is not present in either fixed reference control.

I therefore do not think the remaining fixed-generator mismatch needs to be treated as one undifferentiated “human element.” At least some differences can be localized more narrowly: FAMILY frequency concentration, line composition, immediate ordering, and short-burst recurrence can be measured separately. This does not identify creativity, fatigue, visual judgment, or intuition, and it does not reject the broader self-citation/dynamic-production hypothesis. It only makes the residual category smaller and more testable.

I packaged the measurements as a frozen diagnostic rather than a Voynich-similarity score. Each corpus is tested first against nulls built from its own line/page structure, so the output is intended to show which structural level still requires explanation rather than to rank generators by similarity.

Frozen release: [IMMUTABLE RELEASE / DOI]
Repository: [REPOSITORY / TAG OR COMMIT]

If there is another production variable that you think should be conditioned on or preserved, I would be very interested to test it with the same frozen framework. In particular, your four suggestions — visual pattern recognition, creativity, fatigue, and intuition — now seem to me like candidates for decomposition into smaller observable consequences rather than a single residual class.

Best regards,
Daiki Matsuda
