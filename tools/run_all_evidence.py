#!/usr/bin/env python3
"""Run primary ZL3b core reproduction plus pinned IT2a robustness."""
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def run(args):
    print("\n$", " ".join(map(str,args)), flush=True)
    subprocess.run([str(x) for x in args], cwd=ROOT, check=True)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--fetch",action="store_true"); a=ap.parse_args()
    if not a.fetch:
        raise SystemExit("current one-command all-evidence path requires --fetch; use the two component runners for local inputs")
    run([sys.executable, ROOT/"tools/run_core_evidence.py", "--fetch"])
    run([sys.executable, ROOT/"tools/run_transcription_robustness.py", "--fetch"])
    print("\nALL EVIDENCE REPRODUCTION: PASS")
if __name__=="__main__": main()
