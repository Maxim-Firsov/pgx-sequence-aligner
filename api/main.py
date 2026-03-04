from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from align.needleman_wunsch import align


class AlignRequest(BaseModel):
    seq_a: str
    seq_b: str
    match: int = 1
    mismatch: int = -1
    gap: int = -2
    mode: str = "global"
    gap_model: str = "linear"
    gap_open: int = -3
    gap_extend: int = -1


app = FastAPI()


@app.get("/health")
def healthcheck() -> dict:
    """Minimal liveness endpoint for service checks and smoke tests."""
    return {"status": "ok"}


@app.post("/align")
def align_sequences(payload: AlignRequest) -> dict:
    """Expose the alignment routine behind a small JSON API surface."""
    return align(
        payload.seq_a,
        payload.seq_b,
        match=payload.match,
        mismatch=payload.mismatch,
        gap=payload.gap,
        mode=payload.mode,
        gap_model=payload.gap_model,
        gap_open=payload.gap_open,
        gap_extend=payload.gap_extend,
    )
