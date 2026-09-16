# Generative Constraints in the Voynich Manuscript

**This is not a decipherment.** This repository documents the public v1.0 study of constraints on the generation of Voynich transcription strings. It does not identify a language, plaintext, cipher, or historical writing mechanism.

**Current status: documentation and reference metadata only.** Neither this repository nor the archived release ZIP contains the analysis programs, prepared input snapshots, EXT24 mapping CSV, or machine-readable reference outputs needed for end-to-end reproduction. The results below are reported in the publication; they have not been independently recomputed for this repository.

## Read the report

Daiki Matsuda (2026), *Generative Constraints in the Voynich Manuscript: From Known Structure to Reproducible Tests*. Zenodo, published 2026-09-14. Version-specific DOI: [10.5281/zenodo.22754587](https://doi.org/10.5281/zenodo.22754587).

- [English report (PDF)](https://zenodo.org/records/22754587/files/voynich_generation_constraints_report_v1_0_EN.pdf?download=1)
- [Japanese report (PDF)](https://zenodo.org/records/22754587/files/voynich_generation_constraints_report_v1_0_JP.pdf?download=1)
- [Public release ZIP](https://zenodo.org/records/22754587/files/voynich_report_v1_0_release.zip?download=1)

The PDFs label the report **v1.0**; Zenodo labels the record **v1**. The English PDF cover uses *Exploring Generative Constraints in the Voynich Manuscript: From Known Structure to Reproducible Generative Constraints*. The citation above follows the Zenodo record title.

日本語：本研究は解読ではなく、転写文字列に見られる生成制約を検証した報告です。このリポジトリは公開版の文書・参照情報を整理したもので、解析コードや評価用CSVはまだ含みません。完全な再実行環境の公開とは区別してください。

## What was tested

The report uses Zattera's existing 12-slot representation as an analytical coordinate system, with 8 calibration bifolios (CAL8) and 24 external-evaluation bifolios (EXT24). Comparisons include wrong sheets from the same quire, complete-form memorization, and finite-component/card/depletion models.

ZL3b is the principal transcription; IT2a checks robustness to transcription differences. They represent the **same physical manuscript**, so agreement is not independent replication on another manuscript. A transcribed token is an operational unit, not an assumed natural-language word.

## Reported checkpoints and limits

| Checkpoint | Reported result |
| --- | --- |
| Observed identical-form sharing | 0.44399 |
| Fifth-order slot model with sheet-specific preferences | 0.41815 sharing; approximately 94.18% of observed |
| True sheet versus same-quire wrong sheet | True sheet wins in 23/24 external bifolios |
| Complete-form-memory control | Approximately 139.5% of observed sharing |
| Strict line-interior occupied-slot count, lag 1 | r = 0.2128 |
| Lags 5-6 | Bootstrap intervals include zero |

Sources: English report sections 5-6 and Appendix A; Japanese report sections 5-6 and Appendix A; [manifest section 9](REPRODUCIBILITY_MANIFEST_v1_0.md#9-core-result-checkpoints).

The report's interpretation combines within-token constraints, sheet/bifolio preferences, page history, short-range local state, and line boundaries. Tested simple generator families fail to reproduce the main statistics jointly. This does not exclude every possible simple generator or establish a unique historical cause. The 12-slot representation is prior work, and individual structural phenomena are not all claimed as new discoveries.

A complete historical free-running generator has not been recovered. A reconstruction that fed the predictive length term directly into sequential sampling was tested and rejected. HOLD7 is not globally pristine: its holdout status depends on the particular research branch.

## What is actually available

| File in this repository | Purpose |
| --- | --- |
| `README.md` | Publication guide and current availability limits |
| `REPRODUCIBILITY_MANIFEST_v1_0.md` | Unmodified manifest extracted from the public release ZIP |
| `requirements-reference.txt` | Unmodified six-package reference list extracted from that ZIP |
| `CITATION.cff` | Citation metadata pointing to the published report |
| `LICENSE.md` | Documentation license and third-party provenance exclusions |

The archived ZIP contains exactly four files:

1. `voynich_generation_constraints_report_v1_0.pdf` (Japanese; identical bytes to the separately published `_JP.pdf`)
2. `voynich_generation_constraints_report_v1_0.docx` (Japanese)
3. `REPRODUCIBILITY_MANIFEST_v1_0.md`
4. `requirements-reference.txt`

The English PDF is distributed separately. References in the report or manifest to recovered source files, preprocessing code, saved fold outputs, or evidence files describe the research record and intended reproduction workflow; they do **not** mean those artifacts are included in this release. In particular, `voy_gamma_fullnull.py`, the historical START source, `voy_packet_external_cv.csv`, and the Appendix B evidence files are not included here or in that ZIP. Hashes alone do not supply the missing files.

## Reproduction status

The manifest distinguishes recovered historical source, behaviorally exact reconstruction, aggregate-output reproduction, and unrecovered/rejected reconstruction. This repository preserves those distinctions; it does not supply an executable reproduction pipeline.

The reference environment was fixed on 2026-09-14: Python 3.13.5, Linux 6.18.44 x86_64 / glibc 2.41, and the packages listed in `requirements-reference.txt`. This is a reference package subset, not a complete lockfile or the recovered environment of every historical run. It has not been installation-tested as part of this documentation publication. Installing it alone cannot reproduce the research.

Future deterministic reruns should set `PYTHONHASHSEED=0` before starting Python. Historical hash ordering was not recovered, and matching NumPy seeds alone does not establish byte-identical stochastic results.

Before an end-to-end rerun can be offered, the following artifacts need to be recovered, reviewed, and published where permitted:

- Exact preprocessing/parser and 12-slot canonicalization code, with lawful instructions for obtaining the required inputs.
- The fixed EXT24 mapping CSV and branch-specific configurations, seeds, and offsets.
- Analysis implementations, clearly marked as historical source or later reconstruction.
- Machine-readable reference outputs, comparison tolerances, and tested execution commands.

The report's section 10 gives the intended sequence: verify input identities and splits, fit/select on CAL8, evaluate on EXT24, then compare component results with reference outputs. This is a roadmap, not a runnable command sequence for the current release.

## Transcription provenance

The [manifest](REPRODUCIBILITY_MANIFEST_v1_0.md) records ZL3b (René Zandbergen and Gabriel Landini) and IT2a (Takeshi Takahashi's transcription as incorporated into the Landini-Stolfi Interlinear and converted to IVTFF). See the [upstream distribution page](https://www.voynich.nu/transcr.html).

The manifest's SHA-256 values identify **prepared analysis snapshots**, not today's upstream raw files. The original acquisition event was not independently logged. Downloading an upstream file does not by itself reconstruct the historical analysis input.

No raw upstream transcriptions or prepared transcription snapshots are redistributed here. The release records that no explicit open-content license for those transcription texts was identified; this is a conservative distribution policy, not a legal finding. The documentation license does not grant rights to third-party transcription text. See [LICENSE.md](LICENSE.md).

## Citation and research process

Please cite the version-specific Zenodo report above; [CITATION.cff](CITATION.cff) provides the metadata. For changes to repository documentation, also identify the relevant Git commit. The report DOI identifies the archived publication, not every subsequent repository revision.

The report discloses extensive AI assistance in code generation, statistical work, literature search, research-log organization, reconstruction, and drafting. Human decisions set the research objective, hypothesis selection, interpretation limits, and stopping criteria. AI assistance is not evidence that the results are valid.

## Source verification

On 2026-09-16, the three inspected release files matched the MD5 checksums displayed on the Zenodo record:

| Archived file | Zenodo MD5 |
| --- | --- |
| `voynich_generation_constraints_report_v1_0_EN.pdf` | `749bb699750303c4f6c1950b180374e3` |
| `voynich_generation_constraints_report_v1_0_JP.pdf` | `1ab294513c871fa7d13bb62a67750a74` |
| `voynich_report_v1_0_release.zip` | `d1574a9cc06e743caf2b082473195bc2` |

These checks establish file correspondence with the record, not independent validation of the research results.
