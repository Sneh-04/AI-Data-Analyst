import pandas as pd

from typing import Optional, Dict

from fastapi import APIRouter, HTTPException

from app.models.schemas import DatasetPayload

from app.services import health_service as svc

router = APIRouter()


class HealthScoreRequest(DatasetPayload):
    """Extend DatasetPayload to optionally accept custom health score weights
    and the previous version's score (for drift-aware trending)."""

    weights: Optional[Dict[str, float]] = None
    previous_score: Optional[int] = None


@router.post("/score")
def health_score(payload: HealthScoreRequest):
    df = pd.DataFrame(payload.records)

    try:
        return svc.calculate_health_score(df, weights=payload.weights, previous_score=payload.previous_score)
    except ValueError as exception:
        raise HTTPException(status_code=400, detail=str(exception))