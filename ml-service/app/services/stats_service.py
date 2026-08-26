import numpy as np
import pandas as pd


def get_numeric_stats(df: pd.DataFrame) -> dict:
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty:
        return {}
    stats = numeric_df.describe().T
    stats["skewness"] = numeric_df.skew()
    stats["kurtosis"] = numeric_df.kurtosis()
    stats["median"] = numeric_df.median()
    stats = stats.round(2).replace({np.nan: None})
    return stats.to_dict(orient="index")


def get_categorical_stats(df: pd.DataFrame, max_categories: int = 10) -> dict:
    cat_df = df.select_dtypes(include=["object", "category", "bool"])
    if cat_df.empty:
        return {}
    summary = {}
    for col in cat_df.columns:
        counts = cat_df[col].value_counts().head(max_categories)
        percentages = (cat_df[col].value_counts(normalize=True).head(max_categories) * 100).round(2)
        summary[col] = {
            "unique_count": int(cat_df[col].nunique()),
            "top_value": cat_df[col].mode()[0] if not cat_df[col].mode().empty else "N/A",
            "distribution": {str(k): {"count": int(counts[k]), "percentage": float(percentages[k])} for k in counts.index},
        }
    return summary


def get_correlation_matrix(df: pd.DataFrame):
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        return None
    return numeric_df.corr().round(3).replace({np.nan: None}).to_dict()
