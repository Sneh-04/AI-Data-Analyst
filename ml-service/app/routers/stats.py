import pandas as pd
from fastapi import APIRouter

from app.models.schemas import DatasetPayload
from app.services import stats_service as svc

router = APIRouter()


@router.post("/numeric")
def numeric_stats(payload: DatasetPayload):
    df = pd.DataFrame(payload.records)
    return svc.get_numeric_stats(df)


@router.post("/categorical")
def categorical_stats(payload: DatasetPayload):
    df = pd.DataFrame(payload.records)
    return svc.get_categorical_stats(df)


@router.post("/correlation")
def correlation(payload: DatasetPayload):
    df = pd.DataFrame(payload.records)
    result = svc.get_correlation_matrix(df)
    return {"correlation": result}
