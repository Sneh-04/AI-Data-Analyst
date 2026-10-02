import numpy as np
import pandas as pd


# Sentinel values that encode missing data in real-world datasets (Mohammed et al. 2024)
SENTINEL_MISSING_VALUES = {"-99", "-999", "n/a", "na", "none", "unknown", "null", "?", "missing", ""}


def detect_mnar_signals(df: pd.DataFrame) -> list[str]:
    if df.shape[1] > 50 or len(df) > 100_000:
        return []

    signals = []
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in df.columns:
        missing = df[col].isnull()
        if not missing.any():
            continue

        for other_col in numeric_cols:
            if other_col == col:
                continue
            paired = pd.DataFrame({"missing": missing.astype(int), "value": df[other_col]}).dropna()
            correlation = paired["missing"].corr(paired["value"])
            if pd.notna(correlation) and abs(correlation) > 0.3:
                signals.append(
                    f"Missingness in '{col}' is correlated with '{other_col}' (r={correlation:.2f}) -- may not be random (MNAR)."
                )

        midpoint = len(df) // 2
        if midpoint > 0 and midpoint < len(df):
            first_rate = missing.iloc[:midpoint].mean()
            second_rate = missing.iloc[midpoint:].mean()
            if abs(first_rate - second_rate) > 0.15:
                signals.append(
                    f"Missingness in '{col}' differs between the first and second half of rows "
                    f"({first_rate:.1%} vs {second_rate:.1%}) -- may not be random (MNAR)."
                )
    return signals


def calculate_health_score(df: pd.DataFrame, weights: dict | None = None, previous_score: int | None = None) -> dict:
    """Calculate data quality score with optional custom weights (enables version tracking/trending).

    Args:
        df: Input DataFrame
        weights: Optional dict with keys 'completeness', 'uniqueness', 'consistency', 'outliers'
                 must sum to 1.0. Defaults to equal-weighted hardcoded baseline.
        previous_score: Optional score (0-100) from an earlier dataset_version. A static,
                 one-shot score can't show whether quality is improving or degrading across
                 cleaning iterations (Adaptive DQ Scoring, 2024). Pass the prior version's
                 score (e.g. from DatasetVersion history) to get a drift signal. NOTE: this
                 only tracks score drift, not the full facet-aware (data/source/system/task/
                 human) framework Mohammed et al. (2024) call for -- those facets need
                 metadata this platform doesn't currently collect from a CSV upload alone.
    """
    if df is None or df.empty:
        return {"score": 0, "grade": "N/A", "completeness": 0, "uniqueness": 0,
                "consistency": 0, "outliers_score": 0, "issues": ["No dataset loaded."],
                "sentinel_missing_count": 0, "weights_used": None, "mnar_signals": [],
                "score_trend": None, "previous_score": previous_score}

    # Surface informative missingness because its pattern can bias downstream analysis.
    mnar_signals = detect_mnar_signals(df)

    # Validate and set weights
    default_weights = {"completeness": 0.35, "uniqueness": 0.25, "consistency": 0.20, "outliers": 0.20}
    if weights is not None:
        weight_sum = sum(weights.values())
        if not (0.99 <= weight_sum <= 1.01):  # Allow small floating point error
            raise ValueError(f"Weights must sum to 1.0, got {weight_sum}")
        weights_to_use = weights
    else:
        weights_to_use = default_weights

    total_cells = df.shape[0] * df.shape[1]
    total_nulls = int(df.isnull().sum().sum())

    # Count sentinel missing values in object/string columns (fixes completeness overestimation)
    sentinel_missing_count = 0
    for col in df.select_dtypes(include=["object"]).columns:
        for val in df[col].dropna():
            if isinstance(val, str) and val.strip().lower() in SENTINEL_MISSING_VALUES:
                sentinel_missing_count += 1
    total_nulls += sentinel_missing_count

    completeness = max(0, (1 - (total_nulls / total_cells if total_cells > 0 else 0)) * 100)

    dup_rows = int(df.duplicated().sum())
    uniqueness = max(0, (1 - (dup_rows / len(df) if len(df) > 0 else 0)) * 100)

    consistency_penalties = 0
    for col in df.select_dtypes(include=["object"]).columns:
        numeric_convertible = pd.to_numeric(df[col], errors="coerce").notnull().sum()
        if 0 < numeric_convertible < len(df) * 0.8:
            consistency_penalties += 10
    consistency = max(0, 100 - consistency_penalties)

    outlier_count = 0
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        if iqr > 0:
            outlier_count += int(((df[col] < (q1 - 1.5 * iqr)) | (df[col] > (q3 + 1.5 * iqr))).sum())

    total_numeric_cells = len(df) * max(1, len(numeric_cols))
    outlier_ratio = outlier_count / total_numeric_cells if total_numeric_cells > 0 else 0
    outliers_score = max(0, (1 - outlier_ratio) * 100)

    final_score = int(round(
        completeness * weights_to_use["completeness"] + 
        uniqueness * weights_to_use["uniqueness"] + 
        consistency * weights_to_use["consistency"] + 
        outliers_score * weights_to_use["outliers"]
    ))

    if final_score >= 90:
        grade = "A (Excellent)"
    elif final_score >= 75:
        grade = "B (Good)"
    elif final_score >= 60:
        grade = "C (Fair)"
    elif final_score >= 45:
        grade = "D (Poor)"
    else:
        grade = "F (Critical)"

    issues = []
    if total_nulls > 0:
        issues.append(f"Found {total_nulls} missing values across columns.")
    if sentinel_missing_count > 0:
        issues.append(f"Found {sentinel_missing_count} placeholder values (e.g. '-99', 'N/A') that may represent hidden missing data.")
    if dup_rows > 0:
        issues.append(f"Found {dup_rows} duplicate rows in the dataset.")
    if outlier_count > 0:
        issues.append(f"Detected {outlier_count} statistical outlier values in numeric fields.")
    if consistency_penalties > 0:
        issues.append("Detected potential mixed data types in categorical text columns.")
    if mnar_signals:
        issues.append("Potential non-random missingness detected -- see mnar_signals for details.")
    if not issues:
        issues.append("No critical data quality issues detected. Dataset is clean!")

    score_trend = None
    if previous_score is not None:
        delta = final_score - previous_score
        if delta > 3:
            score_trend = "improving"
        elif delta < -3:
            score_trend = "declining"
        else:
            score_trend = "stable"
        issues.append(f"Score {score_trend} vs. previous version ({previous_score} -> {final_score}).")

    return {
        "score": final_score, "grade": grade,
        "completeness": round(completeness, 1), "uniqueness": round(uniqueness, 1),
        "consistency": round(consistency, 1), "outliers_score": round(outliers_score, 1),
        "issues": issues,
        "sentinel_missing_count": sentinel_missing_count,
        "weights_used": weights_to_use,
        "mnar_signals": mnar_signals,
        "score_trend": score_trend,
        "previous_score": previous_score,
    }
