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


app = FastAPI()


@app.post("/align")
def align_sequences(payload: AlignRequest) -> dict:
    return align(
        payload.seq_a,
        payload.seq_b,
        match=payload.match,
        mismatch=payload.mismatch,
        gap=payload.gap,
    )
