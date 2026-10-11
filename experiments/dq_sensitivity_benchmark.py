"""
Is the data-health score a *valid* measure? Controlled corruption study.

Take real, essentially clean tables, inject a KNOWN amount of one kind of corruption, and check whether
the score (health_service.calculate_health_score) responds. A useful quality score should (1) decrease
monotonically as corruption increases and (2) respond to each kind of corruption it claims to cover.
Where it does not respond, that is a blind spot, reported rather than hidden.

Corruptions (each applied to a fraction `level` of cells/rows):
  missing_nan         set cells to NaN
  placeholder_str     replace cells with the string "N/A" (the "hidden missing value" case the sentinel check targets)
  placeholder_num     replace cells with the number -99 (a numeric placeholder; NOT detectable as a string sentinel)
  duplicate_rows      append copies of existing rows
  outliers            set cells to mean +/- 10 sd
  type_mixing         put non-numeric junk strings ("abc") into numeric columns

Datasets: diabetes, wine, breast_cancer (first 10 feats), iris (raw, un-standardised).
Run: python3 dq_sensitivity_benchmark.py
"""
import itertools
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.datasets import load_breast_cancer, load_diabetes, load_iris, load_wine

from common import RESULTS_DIR
from app.services.health_service import calculate_health_score

warnings.filterwarnings("ignore")
LEVELS = [0.0, 0.02, 0.05, 0.10, 0.20, 0.40]
N_TRIALS = 5
SEED = 42


def load():
    return {
        "diabetes": load_diabetes(as_frame=True).frame.drop(columns="target"),
        "wine": load_wine(as_frame=True).frame.drop(columns="target"),
        "breast_cancer": load_breast_cancer(as_frame=True).frame.drop(columns="target").iloc[:, :10],
        "iris": load_iris(as_frame=True).frame.drop(columns="target"),
    }


def corrupt(df: pd.DataFrame, kind: str, level: float, rng: np.random.RandomState) -> pd.DataFrame:
    out = df.copy()
    if level == 0:
        return out
    if kind == "duplicate_rows":
        extra = out.sample(frac=level, random_state=rng.randint(1_000_000))
        return pd.concat([out, extra], ignore_index=True)
    cells = rng.rand(*out.shape) < level
    out = out.astype(object) if kind in ("placeholder_str", "type_mixing") else out.astype(float)
    sd, mean = df.std().values, df.mean().values
    for j, col in enumerate(out.columns):
        idx = np.where(cells[:, j])[0]
        if kind == "missing_nan":
            out.iloc[idx, j] = np.nan
        elif kind == "placeholder_str":
            out.iloc[idx, j] = "N/A"
        elif kind == "placeholder_num":
            out.iloc[idx, j] = -99.0
        elif kind == "outliers":
            out.iloc[idx, j] = mean[j] + rng.choice([-10, 10], size=len(idx)) * sd[j]
        elif kind == "type_mixing":
            out.iloc[idx, j] = "abc"
    return out


def main():
    rows = []
    kinds = ["missing_nan", "placeholder_str", "placeholder_num", "duplicate_rows", "outliers", "type_mixing"]
    for (name, df), kind, level, trial in itertools.product(load().items(), kinds, LEVELS, range(N_TRIALS)):
        rng = np.random.RandomState(SEED + trial)
        result = calculate_health_score(corrupt(df, kind, level, rng))
        rows.append({"dataset": name, "corruption": kind, "level": level, "trial": trial,
                     "score": result["score"], "completeness": result["completeness"],
                     "uniqueness": result["uniqueness"], "consistency": result["consistency"],
                     "outliers_score": result["outliers_score"],
                     "sentinel_missing_count": result.get("sentinel_missing_count", 0)})
    raw = pd.DataFrame(rows)
    raw.to_csv(f"{RESULTS_DIR}/dq_sensitivity_raw.csv", index=False)

    curve = raw.groupby(["corruption", "level"]).score.mean().unstack("level").round(1)
    curve.to_csv(f"{RESULTS_DIR}/dq_sensitivity_curves.csv")
    verdict = []
    for kind, block in raw.groupby("corruption"):
        rho = stats.spearmanr(block["level"], block["score"]).correlation
        drop = block[block.level == 0].score.mean() - block[block.level == 0.20].score.mean()
        verdict.append({"corruption": kind, "spearman(level,score)": round(rho, 3),
                        "score_drop_at_20pct": round(drop, 1),
                        "responds": bool(rho < -0.5 and drop >= 5)})
    verdict = pd.DataFrame(verdict)
    verdict.to_csv(f"{RESULTS_DIR}/dq_sensitivity_verdict.csv", index=False)
    print("Mean health score by corruption type and level (0-100):")
    print(curve.to_markdown())
    print("\nDoes the score respond?")
    print(verdict.to_markdown(index=False))


if __name__ == "__main__":
    main()
