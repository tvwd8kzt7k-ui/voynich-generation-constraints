# Release gate

Current status: **v0.1 protocol frozen; expert-facing implementation assembled; 9 local unit tests pass; CLI smoke tests pass; authoritative golden fixture independently recomputed from all three pinned public blobs.**

The only remaining software-release gate is one direct end-to-end execution of the packaged Python CLI on a normal connected machine. GitHub write/merge/tag operations are not required for the analysis work and can be done later by the repository owner.

Run:

```bash
python -m unittest discover -s tests -v
python vgdt.py reference-suite --fetch --check REFERENCE_EXPECTATIONS.json
```

Expected terminal marker: `REFERENCE CHECK OK`.

This is a software parity check, not a new scientific tuning round. If it fails, fix implementation or adapter discrepancies without changing the frozen definitions in `PROTOCOL_FREEZE_v0.1.md`.

After that succeeds, the remaining publication operations are administrative:

1. copy/merge the `diagnostic` package into the public repository;
2. rerun the checked reference suite from the repository root;
3. tag the release;
4. archive the release on Zenodo;
5. send the release/report to Timm and other external reviewers.

No new Voynich result is required for v0.1 completion.
