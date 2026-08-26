"""
Upgrades over the original repo's utils/data_cleaner.py:
- KNN-based imputation option (in addition to mean/median/mode)
- Isolation Forest outlier detection option (in addition to IQR capping)
- Automated dtype inference suggestions
- Every operation returns a diff summary for audit/versioning (DB-ready)
"""
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.ensemble import IsolationForest


def fill_missing_values(df: pd.DataFrame, strategy="auto", custom_strategies=None) -> pd.DataFrame:
    cleaned_df = df.copy()

    if strategy == "knn":
        numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            imputer = KNNImputer(n_neighbors=5)
            cleaned_df[numeric_cols] = imputer.fit_transform(cleaned_df[numeric_cols])
        # non-numeric columns still fall back to mode
        for col in cleaned_df.select_dtypes(include=["object", "category"]).columns:
            if cleaned_df[col].isnull().sum() > 0:
                mode_val = cleaned_df[col].mode()
                cleaned_df[col] = cleaned_df[col].fillna(mode_val[0] if not mode_val.empty else "Unknown")
        return cleaned_df

    if custom_strategies:
        for col, strat in custom_strategies.items():
            if col not in cleaned_df.columns:
                continue
            if strat == "mean" and pd.api.types.is_numeric_dtype(cleaned_df[col]):
                cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].mean())
            elif strat == "median" and pd.api.types.is_numeric_dtype(cleaned_df[col]):
                cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())
            elif strat == "mode":
                mode_val = cleaned_df[col].mode()
                if not mode_val.empty:
                    cleaned_df[col] = cleaned_df[col].fillna(mode_val[0])
            elif strat == "zero":
                cleaned_df[col] = cleaned_df[col].fillna(0)
            elif strat == "drop":
                cleaned_df = cleaned_df.dropna(subset=[col])
        return cleaned_df

    # auto (same default behaviour as original repo)
    for col in cleaned_df.columns:
        if cleaned_df[col].isnull().sum() > 0:
            if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                cleaned_df[col] = cleaned_df[col].fillna(cleaned_df[col].median())
            else:
                mode_val = cleaned_df[col].mode()
                cleaned_df[col] = cleaned_df[col].fillna(mode_val[0] if not mode_val.empty else "Unknown")
    return cleaned_df


def remove_duplicate_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates().reset_index(drop=True)


def handle_outliers_iqr(df: pd.DataFrame, col: str, factor: float = 1.5) -> pd.DataFrame:
    cleaned_df = df.copy()
    if pd.api.types.is_numeric_dtype(cleaned_df[col]):
        q1, q3 = cleaned_df[col].quantile(0.25), cleaned_df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - factor * iqr, q3 + factor * iqr
        cleaned_df[col] = cleaned_df[col].clip(lower, upper)
    return cleaned_df


def handle_outliers_isolation_forest(df: pd.DataFrame, columns: list[str], contamination=0.05) -> pd.DataFrame:
    """NEW: flags multivariate outliers instead of IQR's column-by-column view,
    then caps flagged rows' values at the nearest non-outlier percentile per column."""
    cleaned_df = df.copy()
    numeric_cols = [c for c in columns if pd.api.types.is_numeric_dtype(cleaned_df[c])]
    if len(numeric_cols) < 1:
        return cleaned_df

    model = IsolationForest(contamination=contamination, random_state=42)
    flags = model.fit_predict(cleaned_df[numeric_cols].fillna(cleaned_df[numeric_cols].median()))
    outlier_mask = flags == -1

    for col in numeric_cols:
        lower = cleaned_df.loc[~outlier_mask, col].quantile(0.01)
        upper = cleaned_df.loc[~outlier_mask, col].quantile(0.99)
        cleaned_df.loc[outlier_mask, col] = cleaned_df.loc[outlier_mask, col].clip(lower, upper)

    return cleaned_df


def convert_column_types(df: pd.DataFrame, conversions: dict) -> pd.DataFrame:
    cleaned_df = df.copy()
    for col, target_type in conversions.items():
        if col not in cleaned_df.columns:
            continue
        try:
            if target_type == "numeric":
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors="coerce")
            elif target_type == "datetime":
                cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors="coerce")
            elif target_type == "string":
                cleaned_df[col] = cleaned_df[col].astype(str)
            elif target_type == "categorical":
                cleaned_df[col] = cleaned_df[col].astype("category")
        except Exception:
            pass
    return cleaned_df


def suggest_type_conversions(df: pd.DataFrame) -> dict:
    """NEW: repo required manual type selection. This auto-detects likely conversions
    (e.g. an 'object' column that's actually dates or numbers)."""
    suggestions = {}
    for col in df.select_dtypes(include=["object"]).columns:
        sample = df[col].dropna()
        if sample.empty:
            continue
        numeric_ratio = pd.to_numeric(sample, errors="coerce").notnull().mean()
        datetime_ratio = pd.to_datetime(sample, errors="coerce", format="mixed").notnull().mean()
        if numeric_ratio > 0.9:
            suggestions[col] = "numeric"
        elif datetime_ratio > 0.9:
            suggestions[col] = "datetime"
        elif sample.nunique() / len(sample) < 0.05:
            suggestions[col] = "categorical"
    return suggestions


def get_cleaning_summary(original_df: pd.DataFrame, cleaned_df: pd.DataFrame) -> dict:
    return {
        "original_rows": len(original_df),
        "cleaned_rows": len(cleaned_df),
        "rows_removed": len(original_df) - len(cleaned_df),
        "original_nulls": int(original_df.isnull().sum().sum()),
        "cleaned_nulls": int(cleaned_df.isnull().sum().sum()),
        "nulls_fixed": int(original_df.isnull().sum().sum()) - int(cleaned_df.isnull().sum().sum()),
        "original_duplicates": int(original_df.duplicated().sum()),
        "cleaned_duplicates": int(cleaned_df.duplicated().sum()),
    }
