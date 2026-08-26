import pandas as pd
from fastapi import APIRouter

from app.models.schemas import CleaningRequest, TypeConversionRequest, DatasetPayload
from app.services import cleaning_service as svc

router = APIRouter()


@router.post("/clean")
def clean_dataset(req: CleaningRequest):
    df = pd.DataFrame(req.records)
    original_df = df.copy()

    df = svc.fill_missing_values(df, strategy=req.strategy, custom_strategies=req.custom_strategies)

    if req.remove_duplicates:
        df = svc.remove_duplicate_rows(df)

    if req.outlier_method == "iqr":
        cols = req.outlier_columns or df.select_dtypes(include="number").columns.tolist()
        for col in cols:
            df = svc.handle_outliers_iqr(df, col)
    elif req.outlier_method == "isolation_forest":
        cols = req.outlier_columns or df.select_dtypes(include="number").columns.tolist()
        df = svc.handle_outliers_isolation_forest(df, cols)

    summary = svc.get_cleaning_summary(original_df, df)
    return {"cleaned_records": df.to_dict(orient="records"), "summary": summary}


@router.post("/suggest-types")
def suggest_types(payload: DatasetPayload):
    df = pd.DataFrame(payload.records)
    return {"suggestions": svc.suggest_type_conversions(df)}


@router.post("/convert-types")
def convert_types(req: TypeConversionRequest):
    df = pd.DataFrame(req.records)
    df = svc.convert_column_types(df, req.conversions)
    return {"records": df.to_dict(orient="records")}
