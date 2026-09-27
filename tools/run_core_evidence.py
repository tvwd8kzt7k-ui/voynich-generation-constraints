#!/usr/bin/env python3
"""One-command third-party reproduction of the current core evidence.

The transcription is not redistributed. Supply --input, or use --fetch to
retrieve the byte-pinned public mirror snapshot. All scientific commands are
then run against their machine-readable expected checkpoints.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINNED_URL = (
    "https://raw.githubusercontent.com/matthewdgreen/cipher_benchmark/"
    "729aad62d12483c549e64a2541d4f9255538c8cf/"
    "benchmark/unsolved/sources/voynich/transcriptions/ZL3b-n.txt"
)

# Import only for source identity verification.
sys.path.insert(0, str(ROOT))
from canonical.core import ho  # noqa: E402


def run(cmd):
    print("\n$", " ".join(map(str, cmd)), flush=True)
    subprocess.run([str(x) for x in cmd], cwd=ROOT, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path)
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--output-dir", type=Path, default=ROOT / "replay_outputs" / "core")
    a = ap.parse_args()

    if a.input and a.fetch:
        raise SystemExit("choose either --input or --fetch")
    if not a.input and not a.fetch:
        raise SystemExit("supply --input /path/to/ZL3b-n.txt or use --fetch")

    if a.fetch:
        inp = ROOT / "data" / "ZL3b-n.txt"
        inp.parent.mkdir(parents=True, exist_ok=True)
        if not inp.exists():
            print("fetching pinned ZL3b mirror snapshot...", flush=True)
            with urllib.request.urlopen(PINNED_URL) as r:
                inp.write_bytes(r.read())
    else:
        inp = a.input.resolve()

    data = inp.read_bytes()
    got = ho.git_blob_sha1(data)
    if got != ho.EXPECTED_GIT_BLOB_SHA1:
        raise SystemExit(f"input Git blob SHA-1 mismatch: {got} != {ho.EXPECTED_GIT_BLOB_SHA1}")
    print(f"input verified: {got}")

    out = a.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    py = sys.executable

    jobs = [
        ("canonical/tests/low_dimensional_family.py", "canonical/results/low_dimensional_family_expected.json", "low_dimensional_family.json"),
        ("canonical/tests/context_hand.py", "canonical/results/context_hand_expected.json", "context_hand.json"),
        ("canonical/tests/uniform_reuse.py", "canonical/results/uniform_reuse_expected.json", "uniform_reuse.json"),
        ("canonical/tests/bifolio_local_face_bias.py", "canonical/results/bifolio_local_face_bias_expected.json", "bifolio_local_face_bias.json"),
        ("frozen/human_operation/run_freeze.py", "frozen/human_operation/expected_results.json", "human_operation_freeze.json"),
    ]
    for script, expected, outfile in jobs:
        run([py, ROOT / script, "--input", inp, "--output", out / outfile, "--check", ROOT / expected])

    # Deterministic descriptive reconstruction retained because it directly
    # verifies logged CAL8/clean42 structural checkpoints.
    run([
        py, ROOT / "exploratory/log_reconstruction/cal8_exact_structure_reconstructed.py",
        "--input", inp,
        "--output", out / "cal8_exact_structure.json",
        "--check", ROOT / "results/cal8_exact_structure_reference.json",
    ])

    print("\nCORE REPRODUCTION: PASS")
    print(f"outputs: {out}")


if __name__ == "__main__":
    main()
