#!/usr/bin/env python3
"""One-command reproduction of the pinned IT2a robustness pass."""
from __future__ import annotations

import argparse
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IT2A_URL = (
    "https://raw.githubusercontent.com/oklo/voynich_gpt/"
    "2d7c61c387ad6962de730caf73c48612bc8f6957/IT2a-n.txt"
)

sys.path.insert(0, str(ROOT))
from canonical.core import ho  # noqa: E402
from canonical.tests.it2a_robustness import IT2A_GIT_BLOB_SHA1  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path)
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--output", type=Path, default=ROOT / "replay_outputs" / "it2a_robustness.json")
    a = ap.parse_args()
    if a.input and a.fetch:
        raise SystemExit("choose either --input or --fetch")
    if not a.input and not a.fetch:
        raise SystemExit("supply --input /path/to/IT2a-n.txt or use --fetch")

    if a.fetch:
        inp = ROOT / "data" / "IT2a-n.txt"
        inp.parent.mkdir(parents=True, exist_ok=True)
        if not inp.exists():
            print("fetching pinned IT2a mirror snapshot...", flush=True)
            with urllib.request.urlopen(IT2A_URL) as r:
                inp.write_bytes(r.read())
    else:
        inp = a.input.resolve()

    got = ho.git_blob_sha1(inp.read_bytes())
    if got != IT2A_GIT_BLOB_SHA1:
        raise SystemExit(f"IT2a input Git blob SHA-1 mismatch: {got} != {IT2A_GIT_BLOB_SHA1}")
    print(f"IT2a input verified: {got}")

    a.output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        ROOT / "canonical/tests/it2a_robustness.py",
        "--input", inp,
        "--output", a.output,
        "--check", ROOT / "canonical/results/it2a_robustness_expected.json",
    ]
    print("$", " ".join(map(str, cmd)), flush=True)
    subprocess.run([str(x) for x in cmd], cwd=ROOT, check=True)
    print("\nIT2A ROBUSTNESS: PASS")
    print(f"output: {a.output}")


if __name__ == "__main__":
    main()
