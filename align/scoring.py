from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoringScheme:
    """Simple affine-free scoring controls for pairwise alignment."""

    match: int = 1
    mismatch: int = -1
    gap: int = -2
    gap_open: int = -3
    gap_extend: int = -1
    wildcard: str = "N"
    wildcard_score: int = 0

    def score_pair(self, base_a: str, base_b: str) -> int:
        if base_a == self.wildcard or base_b == self.wildcard:
            return self.wildcard_score
        return self.match if base_a == base_b else self.mismatch
