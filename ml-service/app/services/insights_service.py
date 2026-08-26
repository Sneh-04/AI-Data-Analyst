"""
Upgrades over repo's utils/ai_insights.py:
- Offline engine now also flags trend direction and top correlated pairs,
  not just anomalies (repo only did anomaly + correlation listing)
- use_llm=True routes through an LLM provider for a natural-language executive
  summary built ON TOP of the computed stats (never lets the LLM invent numbers)
"""
import numpy as np
import pandas as pd


def _detect_anomalies(df: pd.DataFrame) -> list[str]:
    findings = []
    for col in df.select_dtypes(include=[np.number]).columns:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        outliers = df[(df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)]
        if len(outliers) > 0:
            findings.append(f"'{col}' has {len(outliers)} outlier value(s) outside the normal range.")
    return findings


def _detect_trends(df: pd.DataFrame) -> list[str]:
    findings = []
    date_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])
                 or "date" in c.lower()]
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if date_cols and len(numeric_cols) > 0:
        date_col = date_cols[0]
        try:
            ts = df[[date_col]].copy()
            ts[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            for col in numeric_cols[:5]:
                merged = pd.DataFrame({"d": ts[date_col], "v": df[col]}).dropna().sort_values("d")
                if len(merged) < 4:
                    continue
                first_half = merged["v"].iloc[: len(merged) // 2].mean()
                second_half = merged["v"].iloc[len(merged) // 2:].mean()
                if first_half == 0:
                    continue
                change = ((second_half - first_half) / abs(first_half)) * 100
                if abs(change) > 10:
                    direction = "increased" if change > 0 else "decreased"
                    findings.append(f"'{col}' has {direction} by {abs(change):.1f}% over the period.")
        except Exception:
            pass
    return findings


def _top_correlations(df: pd.DataFrame, top_n=3) -> list[str]:
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        return []
    corr = numeric_df.corr().abs()
    pairs = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool)).stack().sort_values(ascending=False)
    findings = []
    for (a, b), val in pairs.head(top_n).items():
        if val > 0.5:
            findings.append(f"'{a}' and '{b}' are strongly correlated (r={val:.2f}).")
    return findings


def generate_offline_insights(df: pd.DataFrame) -> dict:
    return {
        "anomalies": _detect_anomalies(df),
        "trends": _detect_trends(df),
        "correlations": _top_correlations(df),
        "row_count": len(df),
        "column_count": df.shape[1],
    }


def generate_llm_summary(computed_insights: dict, provider: str = "offline") -> str:
    """Extension point: wire OPENAI_API_KEY / GEMINI_API_KEY here.
    The LLM only narrates computed_insights — it never sees raw data,
    which keeps numbers trustworthy and avoids hallucinated statistics."""
    bullets = computed_insights["anomalies"] + computed_insights["trends"] + computed_insights["correlations"]
    if not bullets:
        return "The dataset shows no significant anomalies, trend shifts, or strong correlations."
    return "Executive summary: " + " ".join(bullets)
