# Parent README integration draft

Suggested section for the top-level `README.md`:

## FAMILY-level mechanism diagnostic

The repository now includes a frozen expert-facing diagnostic layer in [`diagnostic/`](diagnostic/README.md). It applies the same 12-slot FAMILY representation and nested structure-preserving nulls to Voynichese and external candidate generators.

The diagnostic is **not** a decipherment and does not compute a scalar "Voynich-likeness" score. Each corpus is first compared with nulls constructed from itself. The main use is to determine which apparent recurrence effects disappear when outer-unit or line-level FAMILY composition is preserved.

The v0.1 reference suite includes byte-pinned ZL3b, Torsten Timm's fixed self-citation output, and Michael Greshko's Naibbe reference ciphertext:

```bash
cd diagnostic
python -m unittest discover -s tests -v
python vgdt.py reference-suite --fetch --check REFERENCE_EXPECTATIONS.json
```

See [`diagnostic/PROTOCOL_FREEZE_v0.1.md`](diagnostic/PROTOCOL_FREEZE_v0.1.md) for the frozen definitions and [`diagnostic/TECHNICAL_REPORT_DRAFT.md`](diagnostic/TECHNICAL_REPORT_DRAFT.md) for the current scientific write-up.
