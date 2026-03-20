from __future__ import annotations

import pytest

from src.cli import parse_args


def test_parse_args_rejects_affine_flags_in_linear_mode() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--gap-open", "-4"])


def test_parse_args_rejects_linear_gap_in_affine_mode() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--gap-model", "affine", "--gap", "-3"])


def test_parse_args_sets_linear_defaults() -> None:
    args = parse_args([])

    assert args.gap_model == "linear"
    assert args.gap == -2
    assert args.gap_open == -3
    assert args.gap_extend == -1


def test_parse_args_sets_affine_defaults() -> None:
    args = parse_args(["--gap-model", "affine"])

    assert args.gap_model == "affine"
    assert args.gap == -2
    assert args.gap_open == -3
    assert args.gap_extend == -1
