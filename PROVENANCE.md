# Provenance

This repository separates current executable evidence from the historical path by which the hypotheses were developed.

## Current canonical analyses

Files under `canonical/` are current explicit analyses specified after the exploratory phase. They are not claimed to be recovered historical source. Their purpose is to make current scientific claims executable and auditable.

`frozen/human_operation/run_freeze.py` is a post-v1 reproduction implementation of the 2026-09-26 line-ordering diagnostics.

`exploratory/log_reconstruction/cal8_exact_structure_reconstructed.py` is retained because it deterministically reproduces descriptive checkpoints whose definitions are recoverable. It is labeled reconstructed-from-log and is not treated as historical source code.

## Primary transcription pin

- repository: `matthewdgreen/cipher_benchmark`
- commit: `729aad62d12483c549e64a2541d4f9255538c8cf`
- path: `benchmark/unsolved/sources/voynich/transcriptions/ZL3b-n.txt`
- Git blob SHA-1: `2a4533ab9bdfa85db9bad602d590978953055df1`

## Alternate transcription pin

- transcription: IT2a
- repository: `oklo/voynich_gpt`
- commit: `2d7c61c387ad6962de730caf73c48612bc8f6957`
- path: `IT2a-n.txt`
- Git blob SHA-1: `7f491b574b65e5fba6b553e57372c3fa50e10fec`
- IVTFF header: `#=IVTFF EvaT 2.0 M 3`

The modern transcription texts are not redistributed by this repository.

## Research process

The project used extensive AI assistance for code generation, statistical work, literature search, research-log organization, reconstruction, testing, and drafting. Human decisions set the research objective, hypothesis selection, interpretation limits, and stopping decisions. AI assistance is part of the provenance record; it is not evidence for the validity of the results.
