# PGx Sequence Aligner

Pairwise sequence alignment repository built around pharmacogenomics-flavored DNA examples. It implements dynamic programming, configurable scoring schemes, affine versus linear gaps, and exposes the aligner through both a CLI and a small FastAPI service.

## Problem Statement

Pharmacogenomics workflows often begin with comparing short reference and sample sequences to identify substitutions, insertions, or deletions worth investigating further. This repository implements deterministic pairwise alignment primitives that can sit upstream of later annotation or curation steps.

## Technical Approach

- `global` mode performs end-to-end alignment.
- `local` mode recovers the highest-scoring matching subsequence.
- `linear` and `affine` gap models are both supported.
- Wildcard nucleotide `N` is treated neutrally rather than as a hard mismatch.
- Alignment statistics are returned with the score so downstream tools can inspect identity and gap behavior.

## Architecture

```text
FASTA / JSON input
        |
        v
ScoringScheme(match, mismatch, gap model)
        |
        v
Dynamic programming matrices
        |
        +--> traceback reconstruction
        |
        v
Aligned sequences + score + alignment stats
        |
        +--> CLI output
        |
        +--> FastAPI /align response
```

## Repository Layout

- `align/scoring.py`: scoring controls for matches, mismatches, wildcards, and gap penalties
- `align/needleman_wunsch.py`: global/local alignment with linear and affine gap support
- `src/cli.py`: FASTA-driven command-line entry point
- `api/main.py`: FastAPI service wrapper
- `data/sample.fasta`: demo input with PGx-flavored sequence windows
- `tests/test_alignment.py`: regression tests for global, local, wildcard, and affine behavior
- `.github/workflows/ci.yml`: automated test workflow

## Example Usage

```powershell
python src\cli.py --mode global --gap-model affine
python src\cli.py --mode local
uvicorn api.main:app --reload
```

Observed affine-gap CLI output with `data/sample.fasta`:

```text
Mode: global
Gap model: affine
Score: 22
ATGACCAGTTCANCGTATGCATGGACT
ATGACCAATTCAGCGTTTGCATGGACT
Stats:
  aligned_length: 27
  matches: 24
  mismatches: 3
  gap_characters: 0
  gap_opens: 0
  identity: 0.8889
```

## API Example

```http
POST /align
Content-Type: application/json

{
  "seq_a": "ACTGGT",
  "seq_b": "ACTTTGGT",
  "mode": "global",
  "gap_model": "affine",
  "match": 1,
  "mismatch": -1,
  "gap_open": -4,
  "gap_extend": -1
}
```

## Design Decisions

- Affine gaps were added because bioinformatics workflows distinguish between opening a gap and extending one.
- Local alignment remains useful for short shared windows where full-length alignment would dilute the signal.
- The implementation stays dependency-light so the scoring logic is readable enough to discuss line-by-line.

## Limitations

- This is pairwise alignment only; it is not a full read mapper or multiple-alignment engine.
- The scoring system is intentionally simple and does not yet use substitution matrices.
- Input handling is designed for short educational/demo FASTA files rather than large batch workflows.

## Running The Project

```powershell
python -m pip install -e .
python src\cli.py --input data\sample.fasta --mode global --gap-model affine
python -m unittest discover -s tests
```
