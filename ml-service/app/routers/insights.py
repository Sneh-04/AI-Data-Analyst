import pandas as pd
from fastapi import APIRouter

from app.models.schemas import InsightsRequest
from app.services import insights_service as svc

router = APIRouter()


@router.post("/generate")
def generate_insights(req: InsightsRequest):
    df = pd.DataFrame(req.records)
    if req.focus_columns:
        df = df[[c for c in req.focus_columns if c in df.columns]]

    computed = svc.generate_offline_insights(df)
    summary = svc.generate_llm_summary(computed, req.llm_provider) if req.use_llm else None
    return {"insights": computed, "executive_summary": summary}
