import pandas as pd
from fastapi import APIRouter

from app.models.schemas import ChatRequest
from app.services import chat_service as svc

router = APIRouter()


@router.post("/ask")
def ask(req: ChatRequest):
    df = pd.DataFrame(req.records)
    return svc.answer_question(df, req.question, req.dataset_id)
