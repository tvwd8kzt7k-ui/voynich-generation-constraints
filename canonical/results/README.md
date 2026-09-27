# Canonical result checkpoints

The `*_expected.json` files are compact machine-readable checkpoints for current explicitly specified analyses. They are intentionally smaller than the full rerun output.

Correspondence:

- `low_dimensional_family.py` -> `low_dimensional_family_expected.json`
- `context_hand.py` -> `context_hand_expected.json`
- `uniform_reuse.py` -> `uniform_reuse_expected.json`
- `bifolio_local_face_bias.py` -> `bifolio_local_face_bias_expected.json`

Full reruns include per-family, per-bifolio, per-direction, or simulation detail where applicable.

The transcription input is external and must match the pinned Git blob SHA-1. Use `python tools/run_core_evidence.py --fetch` for the complete current core path.
