"""Pooling utilities for inferential estimates from multiple imputed datasets."""

from dataclasses import dataclass
import math
from numbers import Real

import numpy as np
from scipy.stats import t


@dataclass(frozen=True)
class RubinPooledEstimate:
    """Rubin-pooled scalar estimate and Barnard-Rubin inferential uncertainty."""

    estimate: float
    within_imputation_variance: float
    between_imputation_variance: float
    total_variance: float
    standard_error: float
    degrees_of_freedom: float
    confidence_interval: tuple[float, float] | None
    relative_increase_in_variance: float | None
    missing_information_fraction: float | None
    lambda_fraction: float | None
    finite_df_adjusted_fmi: float | None
    relative_efficiency: float | None
    imputations: int


def pool_rubins_rules(
    estimates: list[float] | tuple[float, ...] | np.ndarray,
    within_variances: list[float] | tuple[float, ...] | np.ndarray,
    complete_data_df: float,
    confidence_level: float = 0.95,
) -> RubinPooledEstimate:
    """Pool scalar analysis estimates and their valid within-imputation variances.

    ``within_variances`` must contain the variance of the same inferential
    estimand in each completed-data analysis (for example, the model-based
    variance of a regression coefficient). Predictive spread of imputed cells
    is not a substitute. The imputation service does not know the downstream
    estimand, so callers must fit their analysis to every completed dataset and
    provide these variances along with the complete-data degrees of freedom.

    Returns ``confidence_interval=None`` when Barnard-Rubin degrees of freedom
    are zero, as can occur when between-imputation variance is positive but
    within-imputation variance is zero; a finite t interval is not supported
    in that case.
    """
    q_values = np.asarray(estimates, dtype=float)
    u_values = np.asarray(within_variances, dtype=float)
    if q_values.ndim != 1 or u_values.ndim != 1 or q_values.size != u_values.size:
        raise ValueError("estimates and within_variances must be equal-length 1D sequences")
    if q_values.size < 2:
        raise ValueError("at least two imputations are required")
    if not np.isfinite(q_values).all():
        raise ValueError("estimates must all be finite")
    if not np.isfinite(u_values).all() or np.any(u_values < 0):
        raise ValueError("within_variances must all be finite and non-negative")
    if (
        isinstance(complete_data_df, (bool, np.bool_))
        or not isinstance(complete_data_df, (Real, np.integer, np.floating))
    ):
        raise ValueError("complete_data_df must be finite and greater than zero")
    complete_data_df = float(complete_data_df)
    if not math.isfinite(complete_data_df) or complete_data_df <= 0:
        raise ValueError("complete_data_df must be finite and greater than zero")
    if (
        isinstance(confidence_level, (bool, np.bool_))
        or not isinstance(confidence_level, (Real, np.integer, np.floating))
    ):
        raise ValueError("confidence_level must be strictly between zero and one")
    confidence_level = float(confidence_level)
    if not math.isfinite(confidence_level) or not 0 < confidence_level < 1:
        raise ValueError("confidence_level must be strictly between zero and one")

    m = int(q_values.size)
    scale = float(np.max(np.abs(q_values)))
    if scale == 0:
        estimate = 0.0
        between_variance = 0.0
    else:
        scaled_values = q_values / scale
        scaled_mean = math.fsum(float(value) for value in scaled_values) / m
        estimate = scale * scaled_mean
        scaled_variance = math.fsum(
            (float(value) - scaled_mean) ** 2 for value in scaled_values
        ) / (m - 1)
        scaled_sd = math.sqrt(scaled_variance)
        if scaled_sd and scale > math.sqrt(float(np.finfo(float).max)) / scaled_sd:
            raise ValueError("between-imputation variance exceeds floating-point range")
        between_variance = (scale * scaled_sd) ** 2

    within_scale = float(np.max(u_values))
    within_variance = (
        0.0
        if within_scale == 0
        else within_scale * math.fsum(float(value / within_scale) for value in u_values) / m
    )
    between_multiplier = 1.0 + 1.0 / m
    max_float = float(np.finfo(float).max)
    if between_variance > (max_float - within_variance) / between_multiplier:
        raise ValueError("total variance exceeds floating-point range")
    total_variance = within_variance + between_multiplier * between_variance
    standard_error = math.sqrt(total_variance)

    if within_variance == 0:
        relative_increase = None
    else:
        ratio = between_variance / within_variance
        if ratio > max_float / between_multiplier:
            relative_increase = None
        else:
            relative_increase = between_multiplier * ratio

    if total_variance == 0:
        lambda_fraction = None
        relative_efficiency = None
        finite_df_adjusted_fmi = None
        missing_information_fraction = None
    else:
        lambda_fraction = between_multiplier * between_variance / total_variance
        relative_efficiency = 1.0 / (1.0 + lambda_fraction / m)
        missing_information_fraction = lambda_fraction

        if within_variance == 0 and between_variance > 0:
            finite_df_adjusted_fmi = None
        else:
            if within_variance > 0:
                r_value = relative_increase if relative_increase is not None else 0.0
            else:
                r_value = 0.0
            old_degrees_of_freedom = (
                (m - 1) / lambda_fraction**2 if lambda_fraction > 0 else math.inf
            )
            observed_degrees_of_freedom = (
                (complete_data_df + 1.0)
                / (complete_data_df + 3.0)
                * complete_data_df
                * (1.0 - lambda_fraction)
            )
            if old_degrees_of_freedom == math.inf and observed_degrees_of_freedom <= 0:
                finite_df_adjusted_fmi = None
            elif observed_degrees_of_freedom <= 0:
                finite_df_adjusted_fmi = None
            else:
                barnard_degrees_of_freedom = 1.0 / (
                    1.0 / old_degrees_of_freedom + 1.0 / observed_degrees_of_freedom
                )
                finite_df_adjusted_fmi = (
                    r_value + 2.0 / (barnard_degrees_of_freedom + 3.0)
                ) / (1.0 + r_value)

    if total_variance == 0:
        degrees_of_freedom = 0.0
        confidence_interval = None
    else:
        if lambda_fraction is None or lambda_fraction == 0:
            old_degrees_of_freedom = math.inf
        else:
            old_degrees_of_freedom = (m - 1) / lambda_fraction**2
        observed_degrees_of_freedom = (
            (complete_data_df + 1.0)
            / (complete_data_df + 3.0)
            * complete_data_df
            * (1.0 - lambda_fraction)
            if lambda_fraction is not None
            else 0.0
        )
        if observed_degrees_of_freedom <= 0:
            degrees_of_freedom = 0.0
            confidence_interval = None
        else:
            degrees_of_freedom = 1.0 / (
                1.0 / old_degrees_of_freedom + 1.0 / observed_degrees_of_freedom
            )
            if degrees_of_freedom <= 0:
                confidence_interval = None
            else:
                critical_value = float(t.ppf((1.0 + confidence_level) / 2.0, degrees_of_freedom))
                margin = critical_value * standard_error
                lower, upper = estimate - margin, estimate + margin
                if not math.isfinite(lower) or not math.isfinite(upper):
                    raise ValueError("confidence interval exceeds floating-point range")
                confidence_interval = (lower, upper)

    return RubinPooledEstimate(
        estimate=estimate,
        within_imputation_variance=within_variance,
        between_imputation_variance=between_variance,
        total_variance=total_variance,
        standard_error=standard_error,
        degrees_of_freedom=degrees_of_freedom,
        confidence_interval=confidence_interval,
        relative_increase_in_variance=relative_increase,
        missing_information_fraction=missing_information_fraction,
        lambda_fraction=lambda_fraction,
        finite_df_adjusted_fmi=finite_df_adjusted_fmi,
        relative_efficiency=relative_efficiency,
        imputations=m,
    )
