import pandas as pd
from fastapi import APIRouter

from app.models.schemas import DatasetPayload
from app.services import health_service as svc

router = APIRouter()


@router.post("/score")
def health_score(payload: DatasetPayload):
    df = pd.DataFrame(payload.records)
    return svc.calculate_health_score(df)
