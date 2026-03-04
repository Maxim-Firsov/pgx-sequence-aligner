from __future__ import annotations

import unittest

from align.needleman_wunsch import align


class AlignmentTests(unittest.TestCase):
    def test_global_alignment_returns_expected_score(self) -> None:
        result = align("ACCGTATGCA", "ACGTTTGCA", mode="global")
        self.assertEqual(result["score"], 5)
        self.assertEqual(result["aligned_seq_a"], "ACCGTATGCA")
        self.assertEqual(result["aligned_seq_b"], "A-CGTTTGCA")
        self.assertEqual(result["stats"]["matches"], 8)
        self.assertEqual(result["stats"]["gap_opens"], 1)

    def test_local_alignment_finds_best_matching_window(self) -> None:
        result = align("ACCGTATGCA", "ACGTTTGCA", mode="local")
        self.assertEqual(result["score"], 6)
        self.assertEqual(result["aligned_seq_a"], "CGTATGCA")
        self.assertEqual(result["aligned_seq_b"], "CGTTTGCA")

    def test_affine_alignment_prefers_single_gap_run(self) -> None:
        result = align(
            "ACTGGT",
            "ACTTTGGT",
            mode="global",
            gap_model="affine",
            gap_open=-4,
            gap_extend=-1,
        )
        self.assertEqual(result["gap_model"], "affine")
        self.assertEqual(result["aligned_seq_a"], "AC--TGGT")
        self.assertEqual(result["aligned_seq_b"], "ACTTTGGT")
        self.assertEqual(result["stats"]["gap_opens"], 1)

    def test_wildcard_base_scores_neutrally(self) -> None:
        result = align("ACNG", "ACTG", mode="global")
        self.assertEqual(result["score"], 3)


if __name__ == "__main__":
    unittest.main()
