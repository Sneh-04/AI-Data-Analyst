"""Rubin-pooled inferential endpoints."""

from __future__ import annotations

import math
from typing import Any, Literal

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from scipy.stats import t

from app.services.imputation_uncertainty import pool_rubins_rules
from app.services.multiple_imputation import (
    ImputationMethod,
    analyze_completed_data,
    apply_mnar_delta,
    impute_m_datasets,
    median_fill_numeric,
)

router = APIRouter()
MAX_ROWS = 20_000


class PooledInferenceRequest(BaseModel):
    records: list[dict[str, Any]]
    target_column: str
    estimand: Literal["mean", "ols_slope"]
    predictor_column: str | None = None
    method: ImputationMethod = "proper"
    m: int = Field(default=20, ge=2, le=50, strict=True)
    seed: int = 42
    deltas: list[float] = Field(
        default_factory=lambda: [0.0], min_length=1, max_length=11
    )

    @field_validator("deltas")
    @classmethod
    def deltas_must_be_finite(cls, values: list[float]) -> list[float]:
        if not all(math.isfinite(value) for value in values):
            raise ValueError("deltas must contain only finite numbers")
        return values


def _number_column(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        raise HTTPException(status_code=422, detail=f"Column {column!r} is missing")
    values = frame[column].replace(r"^\s*$", np.nan, regex=True)
    converted = pd.to_numeric(values, errors="coerce")
    invalid = values.notna() & converted.isna()
    if invalid.any() or np.isinf(converted.dropna().to_numpy(dtype=float)).any():
        raise HTTPException(status_code=422, detail=f"Column {column!r} must be numeric")
    return converted.astype(float)


def _complete_interval(
    data: pd.DataFrame,
    target: str,
    estimand: Literal["mean", "ols_slope"],
    predictor: str | None,
) -> dict[str, float]:
    estimate, variance, degrees_of_freedom = analyze_completed_data(
        data, target, estimand, predictor
    )
    standard_error = math.sqrt(variance)
    critical_value = float(t.ppf(0.975, degrees_of_freedom))
    margin = critical_value * standard_error
    return {
        "estimate": estimate,
        "ci_lower": estimate - margin,
        "ci_upper": estimate + margin,
        "standard_error": standard_error,
        "degrees_of_freedom": degrees_of_freedom,
        "within_variance": variance,
        "between_variance": 0.0,
        "total_variance": variance,
        "lambda": 0.0,
    }


@router.post("/pooled")
def pooled_inference(payload: PooledInferenceRequest):
    if payload.estimand == "ols_slope" and not payload.predictor_column:
        raise HTTPException(
            status_code=422,
            detail="predictor_column is required for the ols_slope estimand",
        )
    if not payload.records:
        raise HTTPException(status_code=422, detail="records must not be empty")

    frame = pd.DataFrame(payload.records)
    if payload.target_column not in frame.columns:
        raise HTTPException(
            status_code=422, detail=f"Column {payload.target_column!r} is missing"
        )
    frame[payload.target_column] = _number_column(frame, payload.target_column)
    if payload.estimand == "ols_slope":
        assert payload.predictor_column is not None
        frame[payload.predictor_column] = _number_column(frame, payload.predictor_column)

    subsampled = len(frame) > MAX_ROWS
    if subsampled:
        frame = frame.sample(
            n=MAX_ROWS, random_state=payload.seed % (2**32)
        ).reset_index(drop=True)
    else:
        frame = frame.reset_index(drop=True)

    target = payload.target_column
    observed = frame[target].dropna()
    if len(observed) < 20:
        raise HTTPException(
            status_code=422, detail="At least 20 observed target values are required"
        )
    if payload.estimand == "ols_slope":
        predictor = payload.predictor_column
        assert predictor is not None
        if frame[predictor].nunique(dropna=True) < 2:
            raise HTTPException(
                status_code=422,
                detail="predictor_column must have at least two distinct observed values",
            )
    else:
        predictor = None

    missing_fraction = float(frame[target].isna().mean())
    target_missing = frame[target].isna().any()
    analysis_columns = list(dict.fromkeys([target] + ([predictor] if predictor else [])))
    complete_data: list[pd.DataFrame] = []
    method_note: str
    if target_missing:
        try:
            complete_data = impute_m_datasets(
                frame,
                target=target,
                m=payload.m,
                seed=payload.seed,
                method=payload.method,
            )
            if predictor and any(predictor not in item.columns for item in complete_data):
                raise ValueError("predictor was removed as a constant column")
        except ValueError as exception:
            raise HTTPException(status_code=422, detail=str(exception)) from exception
        method_note = (
            "Proper imputation bootstrap-resamples rows for each draw, fits the "
            "posterior-sampling iterative imputer, and imputes the original rows."
            if payload.method == "proper"
            else "Improper imputation repeats posterior-sampling iterative imputation "
            "without bootstrap-resampling rows."
        )
    else:
        try:
            complete_data = [median_fill_numeric(frame, analysis_columns)]
        except ValueError as exception:
            raise HTTPException(status_code=422, detail=str(exception)) from exception
        method_note = (
            "The target has no missing values; returned complete-data intervals "
            "without multiple-imputation pooling."
        )
    method_note += " Delta values are in observed target standard-deviation units."

    naive_data = median_fill_numeric(frame, analysis_columns)
    naive_interval = {
        **_complete_interval(naive_data, target, payload.estimand, predictor),
        "label": (
            "Naive single-imputation interval (median fill; does not account for "
            "imputation uncertainty)"
        ),
    }

    warnings = ["Missingness mechanism (MCAR/MAR/MNAR) cannot be determined from the data alone"]
    if missing_fraction >= 0.30:
        warnings.append(
            "Interval coverage may be degraded at high missing rates in our simulations"
        )
    if payload.method == "improper":
        warnings.append(
            "Improper imputation underestimates between-imputation variance in our simulations"
        )

    observed_sd = float(observed.std(ddof=1))
    results = []
    for delta in payload.deltas:
        adjusted_datasets = [
            apply_mnar_delta(item, frame, target, delta, observed_sd)
            for item in complete_data
        ]
        if not target_missing:
            result = _complete_interval(
                adjusted_datasets[0], target, payload.estimand, predictor
            )
        else:
            analyses = [
                analyze_completed_data(item, target, payload.estimand, predictor)
                for item in adjusted_datasets
            ]
            pooled = pool_rubins_rules(
                [analysis[0] for analysis in analyses],
                [analysis[1] for analysis in analyses],
                complete_data_df=analyses[0][2],
            )
            interval = pooled.confidence_interval
            result = {
                "estimate": pooled.estimate,
                "ci_lower": interval[0] if interval else None,
                "ci_upper": interval[1] if interval else None,
                "standard_error": pooled.standard_error,
                "degrees_of_freedom": pooled.degrees_of_freedom,
                "within_variance": pooled.within_imputation_variance,
                "between_variance": pooled.between_imputation_variance,
                "total_variance": pooled.total_variance,
                "lambda": pooled.missing_information_fraction,
            }
        results.append({"delta": delta, **result})

    return {
        "results": results,
        "naive_single_imputation": naive_interval,
        "missing_fraction": missing_fraction,
        "n_rows_used": len(frame),
        "subsampled": subsampled,
        "warnings": warnings,
        "method_note": method_note,
    }
