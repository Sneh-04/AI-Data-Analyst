"""Multiple imputation and complete-data analyses for pooled inference."""

from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.linear_model import BayesianRidge

ImputationMethod = Literal["proper", "improper"]
Estimand = Literal["mean", "ols_slope"]


def impute_m_datasets(
    df: pd.DataFrame,
    target: str,
    m: int,
    seed: int,
    method: ImputationMethod,
) -> list[pd.DataFrame]:
    """Create ``m`` numeric imputations while retaining every observed cell."""
    if method not in ("proper", "improper"):
        raise ValueError("method must be 'proper' or 'improper'")
    if m < 2:
        raise ValueError("m must be at least 2")
    if target not in df.columns:
        raise ValueError(f"target column {target!r} is missing")

    numeric = df.select_dtypes(include=[np.number]).copy()
    if target not in numeric.columns:
        raise ValueError("target must be numeric")
    if np.isinf(numeric.to_numpy(dtype=float)).any():
        raise ValueError("numeric columns must not contain infinite values")

    retained = [
        column
        for column in numeric.columns
        if numeric[column].nunique(dropna=True) > 1 or column == target
    ]
    numeric = numeric.loc[:, retained]
    if numeric[target].notna().sum() == 0:
        raise ValueError("target must have at least one observed value")

    values = numeric.to_numpy(dtype=float)
    observed = ~np.isnan(values)
    incomplete_columns = np.isnan(values).any(axis=0)
    rng = np.random.RandomState(seed % (2**32))
    completed_datasets: list[pd.DataFrame] = []

    for _ in range(m):
        draw_seed = int(rng.randint(0, np.iinfo(np.int32).max))
        imputer = IterativeImputer(
            estimator=BayesianRidge(),
            sample_posterior=True,
            max_iter=10,
            skip_complete=True,
            random_state=draw_seed,
        )
        if method == "proper":
            bootstrap = None
            for _ in range(100):
                candidate = rng.randint(0, len(numeric), size=len(numeric))
                bootstrap_values = values[candidate]
                has_observed = ~np.isnan(bootstrap_values).all(axis=0)
                has_missing = np.isnan(bootstrap_values).any(axis=0)
                if has_observed.all() and has_missing[incomplete_columns].all():
                    bootstrap = candidate
                    break
            if bootstrap is None:
                raise ValueError("could not draw a bootstrap sample with observed values")
            imputer.fit(values[bootstrap])
            completed = imputer.transform(values)
        else:
            completed = imputer.fit_transform(values)

        # Transforming observed entries should be an identity; restore them explicitly.
        completed[observed] = values[observed]
        completed_datasets.append(
            pd.DataFrame(completed, columns=numeric.columns, index=numeric.index)
        )
    return completed_datasets


def analyze_completed_data(
    complete_data: pd.DataFrame,
    target: str,
    estimand: Estimand,
    predictor: str | None = None,
) -> tuple[float, float, float]:
    """Return estimate, its sampling variance, and complete-data degrees of freedom."""
    values = complete_data[target].to_numpy(dtype=float)
    n = len(values)
    if estimand == "mean":
        if n < 2:
            raise ValueError("at least two complete rows are required")
        return float(np.mean(values)), float(np.var(values, ddof=1) / n), float(n - 1)

    if estimand != "ols_slope":
        raise ValueError("estimand must be 'mean' or 'ols_slope'")
    if predictor is None or predictor not in complete_data.columns:
        raise ValueError("predictor is required for an OLS slope")
    if n < 3:
        raise ValueError("at least three complete rows are required")

    model = sm.OLS(
        values,
        sm.add_constant(complete_data[predictor].to_numpy(dtype=float), has_constant="add"),
    ).fit(cov_type="HC3")
    return (
        float(model.params[1]),
        float(model.cov_params()[1, 1]),
        float(n - 2),
    )


def apply_mnar_delta(
    complete_data: pd.DataFrame,
    original_data: pd.DataFrame,
    target: str,
    delta: float,
    observed_sd: float,
) -> pd.DataFrame:
    """Shift only imputed target cells by ``delta`` observed standard deviations."""
    adjusted = complete_data.copy()
    missing = original_data[target].isna()
    adjusted.loc[missing, target] += delta * observed_sd
    adjusted.loc[~missing, target] = original_data.loc[~missing, target]
    return adjusted


def median_fill_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Median-fill selected numeric columns for the explicitly naive comparator."""
    result = df.loc[:, columns].copy()
    for column in columns:
        if result[column].isna().any():
            median = result[column].median()
            if pd.isna(median):
                raise ValueError(f"column {column!r} has no observed values")
            result[column] = result[column].fillna(median)
    return result
