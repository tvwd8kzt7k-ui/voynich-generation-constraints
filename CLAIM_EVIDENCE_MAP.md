# Claim-to-evidence map — executable public core v0.8

This map points each current public claim to the executable artifact used to test it. Historical exploratory branches are intentionally not required for the public core.

| Current claim | Executable evidence | Frozen checkpoint |
| --- | --- | --- |
| High-frequency families occupy a low-dimensional concrete-face subset | `canonical/tests/low_dimensional_family.py` | `canonical/results/low_dimensional_family_expected.json` |
| Context and hand both predict exact choice beyond a family baseline, without robust context-over-hand dominance | `canonical/tests/context_hand.py` | `canonical/results/context_hand_expected.json` |
| Uniform all-seen exact reuse is predictive but insufficient to reproduce the observed exact-form concentration | `canonical/tests/uniform_reuse.py` | `canonical/results/uniform_reuse_expected.json` |
| The opposite half of the true bifolio predicts concrete face choice beyond context+hand and better than wrong-bifolio halves | `canonical/tests/bifolio_local_face_bias.py` | `canonical/results/bifolio_local_face_bias_expected.json` |
| A line-composition-preserving ordering excess remains within lines but not across line boundaries | `frozen/human_operation/run_freeze.py` | `frozen/human_operation/expected_results.json` |
| CAL8 exact-spectrum, high-frequency-neighborhood, variable-slot and clean42 cross-half descriptive checkpoints | `exploratory/log_reconstruction/cal8_exact_structure_reconstructed.py` | `results/cal8_exact_structure_reference.json` |
| The principal directions above survive one alternate transcription (IT2a) | `canonical/tests/it2a_robustness.py` | `canonical/results/it2a_robustness_expected.json` |

## Reproduce

```bash
python tools/run_all_evidence.py --fetch
```

The runners fetch byte-pinned public mirror copies of ZL3b and IT2a, verify Git blob SHA-1 identities, execute the analyses, and compare outputs with the frozen checkpoints above. The transcription texts are not redistributed.

## Interpretation boundary

These tests constrain the form of an adequate account of Voynichese generation. They do not uniquely establish a historical mechanical generator, semantic absence, authorial intent, or any literal bag/table/booklet implementation.
