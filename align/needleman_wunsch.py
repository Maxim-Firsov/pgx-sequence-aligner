from __future__ import annotations

from .scoring import ScoringScheme

NEG_INF = -10**9


def _build_stats(aligned_a: str, aligned_b: str) -> dict:
    matches = 0
    mismatches = 0
    gap_count = 0
    gap_opens = 0
    in_gap = False

    for base_a, base_b in zip(aligned_a, aligned_b, strict=True):
        if "-" in (base_a, base_b):
            gap_count += 1
            if not in_gap:
                gap_opens += 1
            in_gap = True
            continue

        in_gap = False
        if base_a == base_b:
            matches += 1
        else:
            mismatches += 1

    aligned_length = len(aligned_a)
    identity = (matches / aligned_length) if aligned_length else 0.0
    return {
        "aligned_length": aligned_length,
        "matches": matches,
        "mismatches": mismatches,
        "gap_characters": gap_count,
        "gap_opens": gap_opens,
        "identity": round(identity, 4),
    }


def _traceback_global(
    seq_a: str,
    seq_b: str,
    traceback: list[list[str | None]],
) -> tuple[str, str]:
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

    return "".join(reversed(aligned_a)), "".join(reversed(aligned_b))


def _traceback_affine(
    seq_a: str,
    seq_b: str,
    trace_m: list[list[tuple[str, str] | None]],
    trace_x: list[list[tuple[str, str] | None]],
    trace_y: list[list[tuple[str, str] | None]],
    start_state: str,
    start_i: int,
    start_j: int,
    local: bool,
) -> tuple[str, str]:
    aligned_a: list[str] = []
    aligned_b: list[str] = []
    state = start_state
    i = start_i
    j = start_j

    while i > 0 or j > 0:
        trace = trace_m if state == "M" else trace_x if state == "X" else trace_y
        prev = trace[i][j]
        if prev is None:
            break

        prev_state, move = prev
        if move == "diag":
            aligned_a.append(seq_a[i - 1])
            aligned_b.append(seq_b[j - 1])
            i -= 1
            j -= 1
        elif move == "up":
            aligned_a.append(seq_a[i - 1])
            aligned_b.append("-")
            i -= 1
        elif move == "left":
            aligned_a.append("-")
            aligned_b.append(seq_b[j - 1])
            j -= 1

        state = prev_state
        if local and (i == 0 or j == 0) and prev is None:
            break

    return "".join(reversed(aligned_a)), "".join(reversed(aligned_b))


def _traceback_local(
    seq_a: str,
    seq_b: str,
    traceback: list[list[str | None]],
    start_i: int,
    start_j: int,
) -> tuple[str, str]:
    aligned_a = []
    aligned_b = []
    i = start_i
    j = start_j

    while i > 0 and j > 0 and traceback[i][j] is not None:
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
        elif direction == "left":
            aligned_a.append("-")
            aligned_b.append(seq_b[j - 1])
            j -= 1
        else:
            break

    return "".join(reversed(aligned_a)), "".join(reversed(aligned_b))


def align(
    seq_a: str,
    seq_b: str,
    match: int = 1,
    mismatch: int = -1,
    gap: int = -2,
    mode: str = "global",
    gap_model: str = "linear",
    gap_open: int = -3,
    gap_extend: int = -1,
) -> dict:
    if mode not in {"global", "local"}:
        raise ValueError("mode must be 'global' or 'local'")
    if gap_model not in {"linear", "affine"}:
        raise ValueError("gap_model must be 'linear' or 'affine'")

    scoring = ScoringScheme(
        match=match,
        mismatch=mismatch,
        gap=gap,
        gap_open=gap_open,
        gap_extend=gap_extend,
    )
    rows = len(seq_a) + 1
    cols = len(seq_b) + 1

    if gap_model == "affine":
        return _align_affine(seq_a, seq_b, scoring, mode)

    scores = [[0] * cols for _ in range(rows)]
    traceback = [[None] * cols for _ in range(rows)]

    if mode == "global":
        for i in range(1, rows):
            scores[i][0] = i * gap
            traceback[i][0] = "up"

        for j in range(1, cols):
            scores[0][j] = j * gap
            traceback[0][j] = "left"

    best_local_score = 0
    best_local_position = (0, 0)

    for i in range(1, rows):
        for j in range(1, cols):
            diag_score = scores[i - 1][j - 1] + scoring.score_pair(seq_a[i - 1], seq_b[j - 1])
            up_score = scores[i - 1][j] + scoring.gap
            left_score = scores[i][j - 1] + scoring.gap

            if mode == "local":
                best_score = max(0, diag_score, up_score, left_score)
            else:
                best_score = max(diag_score, up_score, left_score)
            scores[i][j] = best_score

            if mode == "local" and best_score == 0:
                traceback[i][j] = None
            elif best_score == diag_score:
                traceback[i][j] = "diag"
            elif best_score == up_score:
                traceback[i][j] = "up"
            else:
                traceback[i][j] = "left"

            if mode == "local" and best_score > best_local_score:
                best_local_score = best_score
                best_local_position = (i, j)

    if mode == "global":
        aligned_a, aligned_b = _traceback_global(seq_a, seq_b, traceback)
        score = scores[-1][-1]
    else:
        aligned_a, aligned_b = _traceback_local(
            seq_a,
            seq_b,
            traceback,
            best_local_position[0],
            best_local_position[1],
        )
        score = best_local_score

    return {
        "aligned_seq_a": aligned_a,
        "aligned_seq_b": aligned_b,
        "score": score,
        "mode": mode,
        "gap_model": gap_model,
        "stats": _build_stats(aligned_a, aligned_b),
    }


def _align_affine(seq_a: str, seq_b: str, scoring: ScoringScheme, mode: str) -> dict:
    rows = len(seq_a) + 1
    cols = len(seq_b) + 1

    matrix_m = [[NEG_INF] * cols for _ in range(rows)]
    matrix_x = [[NEG_INF] * cols for _ in range(rows)]
    matrix_y = [[NEG_INF] * cols for _ in range(rows)]
    trace_m: list[list[tuple[str, str] | None]] = [[None] * cols for _ in range(rows)]
    trace_x: list[list[tuple[str, str] | None]] = [[None] * cols for _ in range(rows)]
    trace_y: list[list[tuple[str, str] | None]] = [[None] * cols for _ in range(rows)]

    matrix_m[0][0] = 0
    if mode == "global":
        for i in range(1, rows):
            matrix_x[i][0] = scoring.gap_open + (i - 1) * scoring.gap_extend
            trace_x[i][0] = ("M", "up") if i == 1 else ("X", "up")
        for j in range(1, cols):
            matrix_y[0][j] = scoring.gap_open + (j - 1) * scoring.gap_extend
            trace_y[0][j] = ("M", "left") if j == 1 else ("Y", "left")
    else:
        for i in range(rows):
            matrix_m[i][0] = 0
        for j in range(cols):
            matrix_m[0][j] = 0

    best_score = 0 if mode == "local" else NEG_INF
    best_position = ("M", len(seq_a), len(seq_b))

    for i in range(1, rows):
        for j in range(1, cols):
            candidates_m = [
                (matrix_m[i - 1][j - 1], "M"),
                (matrix_x[i - 1][j - 1], "X"),
                (matrix_y[i - 1][j - 1], "Y"),
            ]
            prev_m_score, prev_m_state = max(candidates_m, key=lambda item: item[0])
            matrix_m[i][j] = prev_m_score + scoring.score_pair(seq_a[i - 1], seq_b[j - 1])
            trace_m[i][j] = (prev_m_state, "diag")

            candidates_x = [
                (matrix_m[i - 1][j] + scoring.gap_open, "M"),
                (matrix_x[i - 1][j] + scoring.gap_extend, "X"),
            ]
            prev_x_score, prev_x_state = max(candidates_x, key=lambda item: item[0])
            matrix_x[i][j] = prev_x_score
            trace_x[i][j] = (prev_x_state, "up")

            candidates_y = [
                (matrix_m[i][j - 1] + scoring.gap_open, "M"),
                (matrix_y[i][j - 1] + scoring.gap_extend, "Y"),
            ]
            prev_y_score, prev_y_state = max(candidates_y, key=lambda item: item[0])
            matrix_y[i][j] = prev_y_score
            trace_y[i][j] = (prev_y_state, "left")

            if mode == "local":
                if matrix_m[i][j] < 0:
                    matrix_m[i][j] = 0
                    trace_m[i][j] = None
                if matrix_x[i][j] < 0:
                    matrix_x[i][j] = 0
                    trace_x[i][j] = None
                if matrix_y[i][j] < 0:
                    matrix_y[i][j] = 0
                    trace_y[i][j] = None

            current_state, current_score = max(
                (("M", matrix_m[i][j]), ("X", matrix_x[i][j]), ("Y", matrix_y[i][j])),
                key=lambda item: item[1],
            )
            if current_score > best_score:
                best_score = current_score
                best_position = (current_state, i, j)

    if mode == "global":
        end_state, score = max(
            (("M", matrix_m[-1][-1]), ("X", matrix_x[-1][-1]), ("Y", matrix_y[-1][-1])),
            key=lambda item: item[1],
        )
        aligned_a, aligned_b = _traceback_affine(
            seq_a,
            seq_b,
            trace_m,
            trace_x,
            trace_y,
            end_state,
            len(seq_a),
            len(seq_b),
            local=False,
        )
    else:
        end_state, end_i, end_j = best_position
        score = best_score
        aligned_a, aligned_b = _traceback_affine(
            seq_a,
            seq_b,
            trace_m,
            trace_x,
            trace_y,
            end_state,
            end_i,
            end_j,
            local=True,
        )

    return {
        "aligned_seq_a": aligned_a,
        "aligned_seq_b": aligned_b,
        "score": score,
        "mode": mode,
        "gap_model": "affine",
        "stats": _build_stats(aligned_a, aligned_b),
    }
