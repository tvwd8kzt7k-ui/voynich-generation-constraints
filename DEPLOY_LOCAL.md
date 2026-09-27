# Deploy executable v0.8 to the repository

Prepared for repository:

`tvwd8kzt7k-ui/voynich-generation-constraints`

The repository was read at main commit:

`4b393c68ebbd6ee1072e88bec2dee49cf630c7cb`

The connected GitHub integration could read the repository, but GitHub rejected write operations with HTTP 403. This directory is therefore a commit-ready overlay.

## Recommended path

Clone or update the repository, then create a branch:

```bash
git clone https://github.com/tvwd8kzt7k-ui/voynich-generation-constraints.git
cd voynich-generation-constraints
git checkout main
git pull --ff-only
git checkout -b repro-v0.8-executable
```

Copy every file from this bundle into the repository root, preserving directories. Then run:

```bash
python tools/run_all_evidence.py --fetch
git status --short
git add -A
git commit -m "Publish executable v0.8 reproducibility core"
git push -u origin repro-v0.8-executable
```

Open a pull request from `repro-v0.8-executable` to `main`. The included GitHub Actions workflow will rerun the ZL3b and IT2a evidence on the PR.

Fetched transcription files go under `data/`; generated outputs go under `replay_outputs/`. Both are ignored by `.gitignore`.
