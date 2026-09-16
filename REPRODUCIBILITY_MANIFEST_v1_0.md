# Voynich generation-constraints study — reproducibility manifest v1.0

Date fixed: 2026-09-14

## 1. Scope

This manifest identifies the source transcriptions, fixed analysis snapshots, data splits, principal seeds, recovered source files, reference software environment, and release policy used for the public report `voynich_generation_constraints_report_v1_0`.

The project does **not** claim byte-for-byte recovery of every historical stochastic run. Reproduction is divided into:

- exact historical source recovered;
- behaviorally exact reconstruction;
- fixed-output / aggregate-statistic reproduction;
- unrecovered or rejected reconstruction.

## 2. Upstream transcription provenance

### ZL3b

- Source family: Zandbergen-Landini (ZL) transcription.
- Maintainers/authors: René Zandbergen and Gabriel Landini.
- Upstream file: `ZL3b-n.txt`.
- IVTFF header: `#=IVTFF Eva- 2.0 M 5`.
- Upstream version line: `Version 3b of 13/05/2025`.
- Distribution page: https://www.voynich.nu/transcr.html
- Direct file: https://www.voynich.nu/data/ZL3b-n.txt

### IT2a

- Source family: `IT`, the converted Takeshi Takahashi transcription included in the Landini-Stolfi Interlinear (LSI) file.
- Historical transcription represented: Takeshi Takahashi, 1999 state as incorporated into LSI.
- Upstream file: `IT2a-n.txt`.
- IVTFF header: `#=IVTFF EvaT 2.0 M 3`.
- File provenance header: `Extracted from LSI_ivtff_0d.txt`.
- Upstream version line: `Version 2a of 02/02/2023 modified 25/06/2025`.
- Distribution page: https://www.voynich.nu/transcr.html
- Direct file: https://www.voynich.nu/data/IT2a-n.txt

Important: the source/version identification above is reconstructed from the public IVTFF files and transliteration documentation. The original browser/download event used during the research was not independently logged. Therefore the analysis-snapshot hashes below, not a claim of byte identity with today's upstream raw file, are authoritative for exact analysis input identity.

## 3. Fixed analysis-input identifiers

These hashes identify the analysis snapshots used by the historical scripts after acquisition/preparation. They should not be interpreted as hashes of the current upstream raw transcription files.

- ZL3b analysis snapshot SHA-256: `a9e3c187fbb18f9a8944faa017c4376fb122d19034ab2066dfc14333208c87ab`
- IT2a analysis snapshot SHA-256: `837226f9730da3ab0e98d09603a5054cd285ffbcc847c7ddbe0178b660ffbab2`
- External-evaluation mapping SHA-256: `7c312708be1656c4e425362cca8adb5318a43b7349299ecfd587d5b6ddad1655`

Historical parser code refers locally to `/mnt/data/zl3b_from_pdf.txt` and `/mnt/data/it2a_pdf.txt`. These are local working-artifact names, not upstream filenames.

## 4. Fixed data splits

### Calibration set (8 bifolios)

Scientific set:

`T3, F4, C3, A4, B3, C2, M3, M1`

Historical code iteration order:

`C3, F4, M1, A4, M3, B3, T3, C2`

### Primary external evaluation set

- 24 bifolios fixed in `voy_packet_external_cv.csv`.
- These 24 were not used for principal model fitting/tuning in the main grammar result.

### HOLD7

`D2, E1, E2, F1, F3, Q1, S2`

HOLD7 is not globally pristine across the entire research program. It is only valid as a holdout for branches that did not inspect it before the corresponding preregistration.

## 5. Principal randomization state

- Main historical seed family: `20260906` with branch-specific fixed offsets.
- New deterministic reruns: set `PYTHONHASHSEED=0`.
- Historical `PYTHONHASHSEED` was not recovered.
- Therefore NumPy seed equality alone does not license a byte-identical claim for old stochastic outputs when candidate ordering depended on Python hash/set/dict order.

## 6. Recovered source identifiers

- `voy_gamma_fullnull.py` SHA-256: `33617f5a489c41cb84257fab183f95b692119547fef7f66e5b10881462829454`
- recovered historical START source SHA-256: `0ade93372647577bc27058c8766d591c33a0b5f4642b8b082b1cfdb49220f11a`

The line-last closure has a behaviorally exact reconstruction for the stored fold outputs, but the original historical source is not fully recovered. A free-running bridge that converted the recovered predictive gamma term directly into sequential sampling was tested and rejected; it is not part of the accepted historical reconstruction.

## 7. Reference reproduction environment

This is the environment fixed on 2026-09-14 for future reruns. It is **not** claimed to be the exact historical environment of every experiment.

- Python: 3.13.5
- platform: Linux 6.18.44 x86_64, glibc 2.41
- NumPy: 2.3.5
- pandas: 2.2.3
- SciPy: 1.17.0
- scikit-learn: 1.8.0
- Matplotlib: 3.10.8
- python-docx: 1.2.0
- required deterministic environment variable for new reruns: `PYTHONHASHSEED=0`

See `requirements-reference.txt` for the package-version subset relevant to this report.

## 8. Release / redistribution policy for transcription data

The manuscript itself is public-domain historical material, but the modern scholarly transcriptions are separately authored research works. The public source files are distributed via voynich.nu for research, but no explicit open-content license was identified for the transcription text.

For that reason, the public reproducibility package should use the conservative policy below:

1. Do not bundle the raw `ZL3b-n.txt` or `IT2a-n.txt` transcription files.
2. Provide upstream URLs, version/header information, analysis-snapshot hashes, and preprocessing/parser code.
3. Redistribute code, aggregate statistics, figures, model outputs, and documentation separately from the raw transcription text.
4. Cite the original transcribers/maintainers.
5. Anyone planning commercial redistribution of the transcription text should verify rights independently with the relevant rights holders/maintainers.

This is a publication-policy choice, not a legal determination of copyright status.

## 9. Core result checkpoints

A reproduction of the main line should recover, within the stated historical/reconstruction limits:

- observed same-type share: approximately `0.44399`;
- fifth-order slot-model simulated share: approximately `0.41815`;
- recovery ratio: approximately `94.18%`;
- true sheet beats same-quire wrong sheet in `23/24` external bifolios;
- exact-word-memory comparison overproduces same-type sharing to approximately `139.5%` of observed;
- strict-interior occupied-length lag-1 correlation: approximately `r = 0.2128`;
- lag 5–6 correlations compatible with zero;
- simple finite-component/card families fail to jointly reproduce lexical reuse, positive local length dependence, local form structure, and line-boundary geometry.

## 10. Public source references

- René Zandbergen, “Transliteration of the Text,” Voynich MS: https://www.voynich.nu/transcr.html
- ZL3b source file: https://www.voynich.nu/data/ZL3b-n.txt
- IT2a source file: https://www.voynich.nu/data/IT2a-n.txt
- VCAT source provenance documentation: https://github.com/noah-chelednik/voynich-data/blob/main/docs/sources.md
- VCAT transcription licensing/provenance note: https://github.com/noah-chelednik/voynich-data/blob/main/docs/SOURCES_LICENSE.md
