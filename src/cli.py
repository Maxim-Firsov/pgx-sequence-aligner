from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from align.needleman_wunsch import align


def read_fasta_sequences(path: Path) -> list[str]:
    """Read plain FASTA records into a sequence list."""
    sequences: list[str] = []
    current: list[str] = []

    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            # FASTA headers delimit records; sequence lines are concatenated so
            # wrapped inputs behave like contiguous biological sequences.
            if current:
                sequences.append("".join(current))
                current = []
            continue
        current.append(line)

    if current:
        sequences.append("".join(current))

    return sequences


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pairwise sequence alignment demo CLI.")
    parser.add_argument(
        "--input",
        default=str(PROJECT_ROOT / "data" / "sample.fasta"),
        help="FASTA file containing at least two sequences.",
    )
    parser.add_argument("--match", type=int, default=1, help="Match reward.")
    parser.add_argument("--mismatch", type=int, default=-1, help="Mismatch penalty.")
    parser.add_argument("--gap", type=int, default=-2, help="Gap penalty.")
    parser.add_argument(
        "--gap-model",
        choices=["linear", "affine"],
        default="linear",
        help="Gap penalty model.",
    )
    parser.add_argument("--gap-open", type=int, default=-3, help="Affine gap-open penalty.")
    parser.add_argument("--gap-extend", type=int, default=-1, help="Affine gap-extension penalty.")
    parser.add_argument(
        "--mode",
        choices=["global", "local"],
        default="global",
        help="Alignment mode.",
    )
    return parser


def main() -> None:
    """Run the aligner against the first two FASTA records and print a compact report."""
    args = build_parser().parse_args()
    fasta_path = Path(args.input).expanduser().resolve()
    sequences = read_fasta_sequences(fasta_path)

    if len(sequences) < 2:
        raise ValueError("input FASTA must contain at least two sequences")

    result = align(
        sequences[0],
        sequences[1],
        match=args.match,
        mismatch=args.mismatch,
        gap=args.gap,
        mode=args.mode,
        gap_model=args.gap_model,
        gap_open=args.gap_open,
        gap_extend=args.gap_extend,
    )

    print(f"Mode: {result['mode']}")
    print(f"Gap model: {result['gap_model']}")
    print(f"Score: {result['score']}")
    print(result["aligned_seq_a"])
    print(result["aligned_seq_b"])
    print("Stats:")
    for key, value in result["stats"].items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
