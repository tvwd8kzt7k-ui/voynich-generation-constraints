# Release gate

Current status: **v0.1 scientific protocol frozen; implementation integrated into the public parent repository; current GitHub `main` snapshot has passed the full connected-machine release gate.**

On 2026-10-01, the repository was downloaded from GitHub as a fresh ZIP and tested on a normal networked Windows environment from `diagnostic/`.

The unit-test suite completed successfully:

```text
Ran 9 tests in 0.029s

OK
```

The complete pinned three-corpus reference suite was then executed with network fetching enabled:

```bash
python vgdt.py reference-suite --fetch --check REFERENCE_EXPECTATIONS.json
```

It completed with:

```text
REFERENCE CHECK OK
```

The run fetched and verified the pinned ZL3b, Timm, and Naibbe reference inputs and reproduced the frozen v0.1 expectations.

The software parity gate is therefore **passed**.

This result freezes the implementation against the definitions in `PROTOCOL_FREEZE_v0.1.md`. A future failure is to be treated as an implementation, environment, source-availability, or provenance problem—not as a reason to retune FAMILY definitions, cue definitions, lag bins, null definitions, seeds, or return-chain categories within v0.1.

## Remaining release work

No further Voynich analysis is required for v0.1.

The remaining work is publication and archival administration:

1. update release-state documentation to reflect the successful connected-machine replay;
2. reserve the VGDT v0.1 archive DOI;
3. add the final citation/archive metadata;
4. regenerate `MANIFEST.sha256` from the final release tree;
5. create the immutable VGDT v0.1 tag and GitHub release;
6. archive that exact release on Zenodo;
7. send the immutable release/report reference to external reviewers.

Any change to the frozen scientific definitions after this point requires a new protocol version rather than silent modification of v0.1.
