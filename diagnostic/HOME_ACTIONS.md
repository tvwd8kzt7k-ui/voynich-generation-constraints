# Actions to do on the repository owner's machine

GitHub publication is deliberately deferred. None of the remaining research/analysis work depends on GitHub write access.

## 1. Put the package in the parent repository

Recommended destination:

```text
voynich-generation-constraints/
└── diagnostic/
    ├── vgdt.py
    ├── README.md
    ├── PROTOCOL_FREEZE_v0.1.md
    ├── REFERENCE_EXPECTATIONS.json
    ├── REFERENCE_VALIDATION.md
    ├── CLAIM_SET_v0.1.md
    ├── TECHNICAL_REPORT_DRAFT.md
    └── ...
```

Do not copy the release zip itself into `diagnostic/`.

## 2. Run the only remaining release gate

From `voynich-generation-constraints/diagnostic/`:

```bash
python -m unittest discover -s tests -v
python vgdt.py reference-suite --fetch --check REFERENCE_EXPECTATIONS.json
```

Required final marker:

```text
REFERENCE CHECK OK
```

The first run is expected to take materially longer than the unit tests because it performs 400 deterministic null permutations on three corpora plus 500 length-control repetitions.

If the check fails, do **not** change bins, FAMILY definitions, cue definitions, null definitions, or seeds. Treat the failure as a parity/implementation bug and compare the failed path with `REFERENCE_EXPECTATIONS.json`.

## 3. Git operations

After the reference check passes, either upload the directory through GitHub's UI or use Git locally. A conventional branch would be:

```bash
git checkout -b diagnostic/v0.1-release
git add diagnostic
git commit -m "Add frozen VGDT v0.1 diagnostic suite"
git push -u origin diagnostic/v0.1-release
```

Then open/merge the PR after checking the diff. The existing Timm external-audit PR is not a dependency of VGDT v0.1; either merge order is acceptable.

## 4. Parent README addition

Add a short section linking to `diagnostic/README.md` and state that the new layer is a mechanism diagnostic rather than a decipherment or scalar Voynich-similarity score. A ready-to-paste draft is in `PARENT_REPO_INTEGRATION.md`.

## 5. Archive

After the repository state is final:

1. create a Git tag/release for the diagnostic version or the next parent-project release;
2. archive that exact commit/release on Zenodo;
3. replace the provisional citation wording in `CITATION.cff` with the resulting DOI if appropriate;
4. freeze the DOI/commit in the technical report.

## 6. External contact

After the archive exists, send the short report/repository link to Torsten Timm. Do not send a moving branch as the sole reference; include the immutable tag/commit/DOI.
