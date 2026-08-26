import pandas as pd
from fastapi import APIRouter, HTTPException

from app.models.schemas import ForecastRequest
from app.services import forecasting_service as svc

router = APIRouter()


@router.post("/run")
def run_forecast(req: ForecastRequest):
    df = pd.DataFrame(req.records)
    if req.date_column not in df.columns or req.value_column not in df.columns:
        raise HTTPException(400, "date_column or value_column not found in dataset")
    result = svc.run_forecast(df, req.date_column, req.value_column, req.periods, req.model)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result
