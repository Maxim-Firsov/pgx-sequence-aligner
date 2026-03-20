from __future__ import annotations

import argparse
from pathlib import Path

from align.needleman_wunsch import align


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_fasta_sequences(path: Path) -> list[str]:
    """Read plain FASTA records into a sequence list."""
    sequences: list[str] = []
    current: list[str] = []

    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
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
    parser.add_argument("--gap", type=int, default=None, help="Linear gap penalty.")
    parser.add_argument(
        "--gap-model",
        choices=["linear", "affine"],
        default="linear",
        help="Gap penalty model.",
    )
    parser.add_argument("--gap-open", type=int, default=None, help="Affine gap-open penalty.")
    parser.add_argument("--gap-extend", type=int, default=None, help="Affine gap-extension penalty.")
    parser.add_argument(
        "--mode",
        choices=["global", "local"],
        default="global",
        help="Alignment mode.",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse and validate CLI arguments."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.gap_model == "linear":
        if args.gap_open is not None or args.gap_extend is not None:
            parser.error("--gap-open and --gap-extend require --gap-model affine")
        args.gap = -2 if args.gap is None else args.gap
        args.gap_open = -3
        args.gap_extend = -1
        return args

    if args.gap is not None:
        parser.error("--gap is only valid with --gap-model linear")
    args.gap = -2
    args.gap_open = -3 if args.gap_open is None else args.gap_open
    args.gap_extend = -1 if args.gap_extend is None else args.gap_extend
    return args


def main(argv: list[str] | None = None) -> None:
    """Run the aligner against the first two FASTA records and print a compact report."""
    args = parse_args(argv)
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
