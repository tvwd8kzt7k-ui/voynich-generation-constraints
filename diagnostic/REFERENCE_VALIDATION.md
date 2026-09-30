# VGDT v0.1 reference validation notes

Date: 2026-09-30

## What has been independently checked

The three public reference files were read at their pinned Git commits and their blob identities were independently confirmed:

- ZL3b: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Timm fixed output: `31b5f847097d6c31e210d1ebc23ea9878f456607`
- Naibbe reference ciphertext: `c95b95507e603ca9a7b0dadba2d13eb314e9b7ea`

An independent implementation of the frozen v0.1 representation, adapters, deterministic Mulberry32 streams, 400 permutations, and 500 length-control samples was run against those exact blobs. `REFERENCE_EXPECTATIONS.json` records the resulting golden subset.

Headline adapter/spectrum checkpoints:

| corpus | valid FAMILY tokens | FAMILY types | hapax | 2–20 | 21+ | Top-10 share |
|---|---:|---:|---:|---:|---:|---:|
| ZL3b clean42 P | 24,250 | 745 | 227 | 383 | 135 | 0.366351 |
| Timm fixed output | 7,856 | 197 | 37 | 109 | 51 | 0.594959 |
| Naibbe reference | 30,233 | 980 | 180 | 579 | 221 | 0.340522 |

The full-clean42 LINE+CUE lag-1 residual is positive for ZL3b (`excess ≈ +0.01593`, `z ≈ +3.56`), near null for the Timm fixed output (`excess ≈ +0.00187`, `z ≈ +0.21`), and strongly negative for Naibbe (`excess ≈ -0.02373`, `z ≈ -4.40`).

The packaged CLI was also smoke-tested locally for `profile` and `pair`; both produced non-empty JSON/Markdown outputs, and all 9 unit tests passed.

For ZL3b, the 21–50 all-pair excess is not a direct medium-return effect: direct returns are deficient while chains with two or more intervening occurrences and chains containing a <=5-token step are strongly enriched. The Timm and Naibbe controls do not reproduce that same burst-chain signature.

## Why some numbers differ slightly from exploratory notes

Earlier exploratory runs used the same scientific null definitions but did not yet have the final v0.1 RNG/seed contract. Monte Carlo null means therefore differ slightly. Observed corpus counts/rates are unchanged, and the qualitative conclusions are unchanged. The v0.1 golden fixture is now the authoritative **software-reproduction target**.

A second difference is population scope. The earlier line-composition report quoted the historical held-out TEST split (`LINE+CUE lag1 z ≈ +2.58`). The v0.1 reference suite deliberately profiles the full clean42 corpus, where the corresponding frozen run gives `z ≈ +3.56`. These are different populations, not conflicting estimates.

## Remaining release check

The current execution environment cannot make outbound network requests from the local Python process, so the packaged Python CLI has not yet performed its own direct `--fetch` replay against the three public files here. This is an environment limitation, not a missing analysis definition.

Before public release, run on a normal connected machine:

```bash
python -m unittest discover -s tests -v
python vgdt.py reference-suite --fetch --check REFERENCE_EXPECTATIONS.json
```

The second command must end with `REFERENCE CHECK OK`. No scientific definition is to be changed to make the check pass; any mismatch is an implementation/parity bug to diagnose.
