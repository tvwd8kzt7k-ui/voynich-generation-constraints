# Third-party reproduction — executable core v0.8

The shortest external check is:

```bash
python tools/run_all_evidence.py --fetch
```

Requirements: Python 3.10+ and internet access. No third-party Python package is required for the current core command.

The command runs the primary ZL3b core and the pinned IT2a robustness pass. The runners verify Git blob SHA-1 identities before analysis and compare each output against machine-readable frozen checkpoints. A successful run ends with:

```text
ALL EVIDENCE REPRODUCTION: PASS
```

## Primary ZL3b only

```bash
python tools/run_core_evidence.py --fetch
```

Pinned input:

- repository: `matthewdgreen/cipher_benchmark`
- commit: `729aad62d12483c549e64a2541d4f9255538c8cf`
- path: `benchmark/unsolved/sources/voynich/transcriptions/ZL3b-n.txt`
- Git blob SHA-1: `2a4533ab9bdfa85db9bad602d590978953055df1`

## IT2a robustness only

```bash
python tools/run_transcription_robustness.py --fetch
```

Pinned input:

- repository: `oklo/voynich_gpt`
- commit: `2d7c61c387ad6962de730caf73c48612bc8f6957`
- path: `IT2a-n.txt`
- Git blob SHA-1: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

IT2a is an alternate transcription of the same physical manuscript. Agreement is therefore a transcription-robustness check, not independent-corpus replication.

## What is tested

1. Low-dimensional concrete variation within high-frequency families.
2. Context and scribal-hand predictive effects on exact choice.
3. Broad all-seen exact reuse: predictive contribution and insufficiency for the observed spectrum.
4. Bifolio-local concrete-face state against wrong-bifolio controls.
5. Line-composition-preserving within-line versus cross-line ordering.
6. Deterministic CAL8/clean42 descriptive structural checkpoints.

## What reproduction would establish

A successful run establishes that the released transformations and tests yield the frozen numerical results on the byte-pinned public transcription copies. It does not establish a unique historical production mechanism, prove semantic absence, identify an author, or prove a literal mechanical device.

The stronger next checks are independent reimplementation, stronger nulls, and additional transcription systems.

## Reporting an external reproduction

Please record:

- repository commit tested;
- Python version;
- operating system;
- command used;
- verified input blob identities;
- PASS/FAIL status and any differing values.
