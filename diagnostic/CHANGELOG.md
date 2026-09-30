# Changelog

## v0.1.0 — 2026-09-30

First extracted expert-facing diagnostic instrument.

- freezes the FAMILY/cue representation used in the late-stage Voynich decomposition work;
- separates per-corpus profiling from cross-corpus comparison;
- adds OUTER+CUE and LINE+CUE nested nulls;
- adds consecutive-return and 21–50 burst-chain decomposition;
- includes ZL3b, fixed-line/Timm, and blank-block/Naibbe adapters;
- deliberately omits any scalar Voynich-likeness score;
- pins the three reference public inputs for a reproducible reference suite.
- adds an authoritative golden reference fixture for ZL3b, Timm, and Naibbe;
- adds `reference-suite --check` for deterministic end-to-end parity verification;
- freezes RNG and sampling seed streams explicitly.

## 2026-09-30 release-candidate completion

- Added the frozen three-corpus golden reference bundle and deterministic self-check.
- Added the technical-report draft and a follow-up email draft for Torsten Timm.
- Verified the parent executable release citation against the repository `CITATION.cff`: DOI `10.5281/zenodo.23000054`. The older documentation report DOI remains a separate earlier record.
- GitHub publication remains deferred until the repository owner can run the connected-machine reference gate and publish manually.
