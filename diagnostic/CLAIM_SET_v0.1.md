# VGDT v0.1 claim set

Date: 2026-09-30

This file separates direct observations, mechanism-localisation statements, and claims that are **not** supported by the v0.1 instrument.

## A. Direct observations in the frozen reference suite

Using the same 12-slot FAMILY representation and the frozen v0.1 panel on the pinned reference outputs:

1. The FAMILY spectra differ strongly.
   - ZL3b clean42 P: 24,250 valid tokens, 745 FAMILY types, 227 hapax, Top-10 share 0.36635.
   - Timm fixed self-citation output: 7,856 valid tokens, 197 FAMILY types, 37 hapax, Top-10 share 0.59496.
   - Naibbe reference ciphertext: 30,233 valid tokens, 980 FAMILY types, 180 hapax, Top-10 share 0.34052.

2. After preserving each line's cue-conditioned FAMILY composition, the immediate lag-1 residual has three different signs/magnitudes.
   - ZL3b full clean42: excess +0.01593, z ≈ +3.56.
   - Timm: excess +0.00187, z ≈ +0.21.
   - Naibbe: excess -0.02373, z ≈ -4.40.

3. ZL3b's 21–50 same-cue all-pair excess is not a direct medium-return excess under the OUTER+CUE null.
   - all exact-FAMILY pairs: excess +0.00586, z ≈ +4.03;
   - direct consecutive medium returns: excess -0.00218, z ≈ -3.44;
   - two-or-more intervening occurrences: excess +0.01058, z ≈ +7.34;
   - non-direct chains containing a <=5-token step: excess +0.01172, z ≈ +7.05;
   - non-direct chains with no <=5-token step: excess -0.00368, z ≈ -3.05.

4. The same short-chain enrichment is not reproduced by the two reference controls.
   - Timm <=5-step chain excess: -0.00327, z ≈ -1.02.
   - Naibbe <=5-step chain excess: -0.00249, z ≈ -2.36.

5. For ZL3b, strengthening the null from OUTER+CUE to LINE+CUE removes the positive 2–50 lag residuals as a class. Lag 1 remains positively enriched; the 6–10 bin becomes negatively displaced in the full-clean42 reference run.

## B. Mechanism-localisation statements supported by those observations

These are statements about what level of structure is sufficient to account for a statistic, not claims about historical causation.

1. Much of the apparent short-to-medium exact-FAMILY clustering in ZL3b is explained by line-level FAMILY composition rather than requiring an independent exact-FAMILY memory extending tens of tokens.

2. The apparent 21–50 positive tail is largely produced by burst chains containing shorter returns, not by an excess of direct 21–50 consecutive returns.

3. Timm's fixed output contains substantial outer/page-scale FAMILY structure, but the positive 6–20 lag residual seen under OUTER+CUE is largely removed when line composition is preserved.

4. Naibbe's reference ciphertext leaves a strong *negative* immediate ordering residual after line composition is preserved. Therefore its FAMILY dynamics are not equivalent to either the ZL3b or Timm reference profile at this resolution.

5. A common diagnostic panel can distinguish different sources of apparent Voynich-like structure without converting them into a single Voynich-similarity score.

## C. Claims v0.1 does not support

VGDT v0.1 does not establish that:

- Voynichese is meaningless;
- Voynichese contains plaintext or lacks plaintext;
- the manuscript was produced by self-citation, Naibbe, a mechanical device, a natural language, or any unique historical mechanism;
- Timm's broader self-citation hypothesis is refuted because one fixed implementation misses some constraints;
- the Naibbe cipher is refuted as a demonstration that meaningful plaintext can yield Voynich-like ciphertext;
- the diagnostic panel is a general classifier for language, cipher, pseudo-text, or meaning;
- similar diagnostic profiles imply the same historical cause;
- the current framework is methodologically novel outside Voynich studies.

## D. Strongest safe headline

> In the frozen reference data, several apparent Voynichese recurrence effects can be localised to cheaper levels of structure: line-level FAMILY composition explains most positive 2–50-token clustering, while the remaining 21–50 all-pair excess is dominated by chains of shorter returns rather than direct medium-range recurrence. Applying the same panel to fixed self-citation and meaning-preserving Naibbe outputs yields different FAMILY-level residual signatures.

## E. Population note

Earlier exploratory reports quoted a historical held-out TEST split, where LINE+CUE lag 1 gave z ≈ +2.58. The v0.1 reference suite uses full clean42 and gives z ≈ +3.56. These values refer to different populations. The direction and interpretation of the immediate positive residue are consistent.
