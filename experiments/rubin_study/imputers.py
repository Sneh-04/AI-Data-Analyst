"""Imputation and scalar-analysis helpers for the Rubin coverage study."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
import sys
from typing import Literal, TypeAlias

import numpy as np
import pandas as pd
from scipy.stats import t
from sklearn.experimental import enable_iterative_imputer as _enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer, KNNImputer, SimpleImputer
from sklearn.linear_model import BayesianRidge
import statsmodels.api as sm


_ML_SERVICE_DIR = Path(__file__).resolve().parents[2] / "ml-service"
if str(_ML_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(_ML_SERVICE_DIR))

from app.services.imputation_uncertainty import (  # noqa: E402  # type: ignore[reportMissingImports]
    RubinPooledEstimate,
    pool_rubins_rules,
)

ImputationMethod: TypeAlias = Literal[
    "median", "knn", "mice_improper", "mice_proper"
]
ScalarAnalysis: TypeAlias = Callable[[pd.DataFrame], tuple[float, float, float]]


def _validated_numeric_frame(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if df.empty:
        raise ValueError("df must contain at least one row and one column")
    if df.shape[1] == 0:
        raise ValueError("df must contain at least one row and one column")
    if not all(pd.api.types.is_numeric_dtype(dtype) for dtype in df.dtypes):
        raise ValueError("all columns must be numeric")
    numeric = df.astype(float)
    if np.isinf(numeric.to_numpy()).any():
        raise ValueError("df must not contain infinite values")
    all_missing = numeric.columns[numeric.isna().all()].tolist()
    if all_missing:
        raise ValueError(f"columns cannot be entirely missing: {all_missing}")
    return numeric


def _restore_observed_values(completed: np.ndarray, original: pd.DataFrame) -> pd.DataFrame:
    values = np.array(completed, dtype=float, copy=True)
    observed = original.notna().to_numpy()
    original_values = original.to_numpy(dtype=float)
    values[observed] = original_values[observed]
    if not np.isfinite(values).all():
        raise ValueError("imputer produced non-finite completed values")
    return pd.DataFrame(values, index=original.index.copy(), columns=original.columns.copy())


def _iterative_imputer(seed: int) -> IterativeImputer:
    return IterativeImputer(
        estimator=BayesianRidge(),
        sample_posterior=True,
        max_iter=10,
        random_state=seed,
        skip_complete=True,
        keep_empty_features=True,
    )


def impute_m_datasets(
    df: pd.DataFrame,
    m: int,
    seed: int,
    method: ImputationMethod,
) -> list[pd.DataFrame]:
    """Return ``m`` completed numeric frames for a pre-specified study method.

    The MICE methods return stochastic completed datasets. ``mice_proper``
    bootstraps rows with replacement separately for every draw, fits the
    chained imputer on that bootstrap sample, then transforms the original
    incomplete frame. Median and KNN are single-imputation baselines; to keep
    the requested list shape, their one deterministic completion is copied
    ``m`` times. Analyze only the first copy for those methods and use a naive
    single-imputation interval, not Rubin pooling.
    """
    if isinstance(m, bool) or not isinstance(m, (int, np.integer)) or m < 1:
        raise ValueError("m must be a positive integer")
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)):
        raise ValueError("seed must be an integer")
    methods = {"median", "knn", "mice_improper", "mice_proper"}
    if method not in methods:
        raise ValueError(f"method must be one of {sorted(methods)}")

    numeric = _validated_numeric_frame(df)
    if method in {"median", "knn"}:
        if method == "median":
            imputer = SimpleImputer(strategy="median", keep_empty_features=True)
        else:
            imputer = KNNImputer(n_neighbors=5, keep_empty_features=True)
        completed = _restore_observed_values(
            imputer.fit_transform(numeric.to_numpy(copy=True)), numeric
        )
        return [completed.copy(deep=True) for _ in range(m)]

    completed_datasets: list[pd.DataFrame] = []
    for draw in range(m):
        imputer_seed = int(seed) + 100 + draw
        if method == "mice_improper":
            imputer = _iterative_imputer(imputer_seed)
            completed = imputer.fit_transform(numeric.to_numpy(copy=True))
        else:
            bootstrap_seed = int(seed) + 100 + draw
            bootstrap_rng = np.random.RandomState(bootstrap_seed)
            bootstrap_indices = bootstrap_rng.choice(
                len(numeric), size=len(numeric), replace=True
            )
            bootstrap = numeric.iloc[bootstrap_indices]
            imputer = _iterative_imputer(int(seed) + 200 + draw)
            imputer.fit(bootstrap.to_numpy(copy=True))
            completed = imputer.transform(numeric.to_numpy(copy=True))
        completed_datasets.append(_restore_observed_values(completed, numeric))
    return completed_datasets


def analyze_column_mean(
    completed: pd.DataFrame, column: str
) -> tuple[float, float, float]:
    """Return ``(Q, U, complete_data_df)`` for a completed-column mean."""
    data = _analysis_series(completed, column)
    n = len(data)
    if n < 2:
        raise ValueError("column mean analysis requires at least two rows")
    estimate = float(data.mean())
    within_variance = float(data.var(ddof=1) / n)
    return estimate, within_variance, float(n - 1)


def analyze_ols_coefficient(
    completed: pd.DataFrame, outcome: str, predictor: str
) -> tuple[float, float, float]:
    """Return ``(Q, U, complete_data_df)`` for an intercept OLS slope.

    ``U`` is the HC3 heteroskedasticity-robust covariance estimate for the
    requested predictor. The returned degrees of freedom are the fitted model's
    residual degrees of freedom.
    """
    y = _analysis_series(completed, outcome)
    x = _analysis_series(completed, predictor)
    if outcome == predictor:
        raise ValueError("outcome and predictor must be different columns")
    if len(y) <= 2:
        raise ValueError("OLS analysis requires at least three rows")
    if x.nunique(dropna=False) < 2:
        raise ValueError("OLS predictor must have nonzero variance")
    intercept_name = "__rubin_intercept__"
    predictor_name = "__rubin_predictor__"
    design = pd.DataFrame(
        {intercept_name: np.ones(len(x)), predictor_name: x.to_numpy()},
        index=x.index,
    )
    fit = sm.OLS(y, design, missing="raise").fit(cov_type="HC3")
    estimate = float(fit.params[predictor_name])
    within_variance = float(fit.cov_params().loc[predictor_name, predictor_name])
    complete_data_df = float(fit.df_resid)
    if not np.isfinite([estimate, within_variance, complete_data_df]).all():
        raise ValueError("OLS analysis produced non-finite estimate or variance")
    if within_variance < 0 or complete_data_df <= 0:
        raise ValueError("OLS analysis produced invalid variance or degrees of freedom")
    return estimate, within_variance, complete_data_df


def _analysis_series(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        raise ValueError(f"unknown analysis column: {column}")
    values = frame[column]
    if not pd.api.types.is_numeric_dtype(values.dtype):
        raise ValueError(f"analysis column must be numeric: {column}")
    if values.isna().any() or not np.isfinite(values.to_numpy(dtype=float)).all():
        raise ValueError(f"analysis column must be complete and finite: {column}")
    return values.astype(float)


def pool_scalar_analysis(
    completed_datasets: Sequence[pd.DataFrame],
    analysis: ScalarAnalysis,
    confidence_level: float = 0.95,
) -> RubinPooledEstimate:
    """Analyze each completed frame and pool its estimates with Rubin's Rules."""
    if len(completed_datasets) < 2:
        raise ValueError("Rubin pooling requires at least two completed datasets")
    results = [analysis(frame) for frame in completed_datasets]
    degrees_of_freedom = [result[2] for result in results]
    if not np.allclose(degrees_of_freedom, degrees_of_freedom[0]):
        raise ValueError("complete-data degrees of freedom must match across imputations")
    return pool_rubins_rules(
        [result[0] for result in results],
        [result[1] for result in results],
        complete_data_df=degrees_of_freedom[0],
        confidence_level=confidence_level,
    )


def naive_single_imputation_interval(
    estimate: float,
    within_variance: float,
    complete_data_df: float,
    confidence_level: float = 0.95,
) -> dict[str, object]:
    """Calculate a labeled naive interval for a single-imputation baseline."""
    if not np.isfinite([estimate, within_variance, complete_data_df]).all():
        raise ValueError("estimate, variance, and degrees of freedom must be finite")
    if within_variance < 0 or complete_data_df <= 0:
        raise ValueError("variance must be non-negative and degrees of freedom positive")
    if not 0 < confidence_level < 1:
        raise ValueError("confidence_level must be strictly between zero and one")
    standard_error = float(np.sqrt(within_variance))
    critical_value = float(t.ppf((1 + confidence_level) / 2, complete_data_df))
    return {
        "interval_type": "naive single imputation",
        "confidence_level": confidence_level,
        "estimate": float(estimate),
        "standard_error": standard_error,
        "degrees_of_freedom": float(complete_data_df),
        "confidence_interval": (
            float(estimate - critical_value * standard_error),
            float(estimate + critical_value * standard_error),
        ),
    }


__all__ = [
    "ImputationMethod",
    "ScalarAnalysis",
    "analyze_column_mean",
    "analyze_ols_coefficient",
    "impute_m_datasets",
    "naive_single_imputation_interval",
    "pool_scalar_analysis",
]
