from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from align.needleman_wunsch import align


def read_fasta_sequences(path: Path) -> list[str]:
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


def main() -> None:
    fasta_path = PROJECT_ROOT / "data" / "sample.fasta"
    sequences = read_fasta_sequences(fasta_path)

    if len(sequences) < 2:
        raise ValueError("sample.fasta must contain at least two sequences")

    result = align(sequences[0], sequences[1])

    print(f"Score: {result['score']}")
    print(result["aligned_seq_a"])
    print(result["aligned_seq_b"])


if __name__ == "__main__":
    main()
