import pandas as pd
from fastapi import APIRouter

from app.models.schemas import CleaningRequest, TypeConversionRequest, DatasetPayload
from app.services import cleaning_service as svc

router = APIRouter()


@router.post("/clean")
def clean_dataset(req: CleaningRequest):
    df = pd.DataFrame(req.records)
    original_df = df.copy()
    repair_log = []

    df, missing_repairs = svc.fill_missing_values(
        df, strategy=req.strategy, custom_strategies=req.custom_strategies
    )
    repair_log.extend(missing_repairs)

    if req.remove_duplicates:
        df = svc.remove_duplicate_rows(df)

    if req.outlier_method == "iqr":
        cols = req.outlier_columns or df.select_dtypes(include="number").columns.tolist()
        for col in cols:
            df, outlier_repairs = svc.handle_outliers_iqr(df, col)
            repair_log.extend(outlier_repairs)
    elif req.outlier_method == "isolation_forest":
        cols = req.outlier_columns or df.select_dtypes(include="number").columns.tolist()
        df, outlier_repairs = svc.handle_outliers_isolation_forest(df, cols)
        repair_log.extend(outlier_repairs)

    summary = svc.get_cleaning_summary(original_df, df)
    # Keep a bounded audit trail so explainability cannot create an oversized response.
    response = {
        "cleaned_records": df.to_dict(orient="records"),
        "summary": summary,
        "repair_log": repair_log[:500],
    }
    if len(repair_log) > 500:
        response["repair_log_truncated"] = True
    return response


@router.post("/suggest-types")
def suggest_types(payload: DatasetPayload):
    df = pd.DataFrame(payload.records)
    return {"suggestions": svc.suggest_type_conversions(df)}


@router.post("/convert-types")
def convert_types(req: TypeConversionRequest):
    df = pd.DataFrame(req.records)
    df = svc.convert_column_types(df, req.conversions)
    return {"records": df.to_dict(orient="records")}
