from __future__ import annotations


def align(
    seq_a: str,
    seq_b: str,
    match: int = 1,
    mismatch: int = -1,
    gap: int = -2,
) -> dict:
    rows = len(seq_a) + 1
    cols = len(seq_b) + 1

    scores = [[0] * cols for _ in range(rows)]
    traceback = [[None] * cols for _ in range(rows)]

    for i in range(1, rows):
        scores[i][0] = i * gap
        traceback[i][0] = "up"

    for j in range(1, cols):
        scores[0][j] = j * gap
        traceback[0][j] = "left"

    for i in range(1, rows):
        for j in range(1, cols):
            diag_score = scores[i - 1][j - 1] + (
                match if seq_a[i - 1] == seq_b[j - 1] else mismatch
            )
            up_score = scores[i - 1][j] + gap
            left_score = scores[i][j - 1] + gap

            best_score = max(diag_score, up_score, left_score)
            scores[i][j] = best_score

            if best_score == diag_score:
                traceback[i][j] = "diag"
            elif best_score == up_score:
                traceback[i][j] = "up"
            else:
                traceback[i][j] = "left"

    aligned_a = []
    aligned_b = []
    i = len(seq_a)
    j = len(seq_b)

    while i > 0 or j > 0:
        direction = traceback[i][j]

        if direction == "diag":
            aligned_a.append(seq_a[i - 1])
            aligned_b.append(seq_b[j - 1])
            i -= 1
            j -= 1
        elif direction == "up":
            aligned_a.append(seq_a[i - 1])
            aligned_b.append("-")
            i -= 1
        else:
            aligned_a.append("-")
            aligned_b.append(seq_b[j - 1])
            j -= 1

    return {
        "aligned_seq_a": "".join(reversed(aligned_a)),
        "aligned_seq_b": "".join(reversed(aligned_b)),
        "score": scores[-1][-1],
    }
