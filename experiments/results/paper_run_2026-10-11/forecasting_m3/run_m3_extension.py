"""Run the fixed M3 Monthly subset using the project's forecasting service."""

from __future__ import annotations

import json
import hashlib
import platform
import sys
import time
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
import sklearn
import statsmodels


RUN_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "ml-service"))

from app.services import forecasting_service as fs


SOURCE_ZIP = RUN_DIR / "m3_monthly_dataset.zip"
SOURCE_TSF = "m3_monthly_dataset.tsf"
SOURCE_DOI = "10.5281/zenodo.4656298"
HORIZON = 18
WINDOWS = 4
MIN_TRAIN = 30
N_SERIES = 20
SEASONAL_PERIOD = 12
FIXED_METHODS = ["naive", "seasonal_naive", "holt", "arima", "sarima", "ensemble"]
AUTO_METHODS = ["auto", "auto_no_shortlist"]


def load_m3_series() -> tuple[list[dict], int]:
    with zipfile.ZipFile(SOURCE_ZIP) as archive:
        lines = archive.read(SOURCE_TSF).decode("latin-1").splitlines()
    try:
        data_start = lines.index("@data") + 1
    except ValueError as exc:
        raise ValueError("M3 TSF source has no @data section.") from exc

    eligible = []
    min_length = MIN_TRAIN + WINDOWS * HORIZON
    for line_number, line in enumerate(lines[data_start:], start=data_start + 1):
        if not line:
            continue
        try:
            series_id, start_timestamp, value_text = line.split(":", 2)
            values = np.asarray([float(value) for value in value_text.split(",")])
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Invalid M3 observation at source line {line_number}.") from exc
        if not np.isfinite(values).all():
            raise ValueError(f"Non-finite values in M3 series {series_id}.")
        if values.size >= min_length:
            eligible.append(
                {
                    "series": series_id,
                    "start": pd.Timestamp(start_timestamp[:10]),
                    "values": values,
                }
            )

    if len(eligible) < N_SERIES:
        raise ValueError(
            f"Only {len(eligible)} M3 series meet the {min_length}-point minimum."
        )
    selected_indices = np.linspace(
        0, len(eligible) - 1, num=N_SERIES, dtype=int
    )
    selected = [eligible[index] for index in selected_indices]
    if len({item["series"] for item in selected}) != N_SERIES:
        raise ValueError("Deterministic M3 selection produced duplicate series.")
    return selected, len(eligible)


def prepare_subset(selected: list[dict]) -> pd.DataFrame:
    rows = []
    for item in selected:
        dates = pd.date_range(item["start"], periods=len(item["values"]), freq="MS")
        rows.extend(
            {
                "series": item["series"],
                "ds": date,
                "y": float(value),
            }
            for date, value in zip(dates, item["values"], strict=True)
        )
    subset = pd.DataFrame(rows)
    subset.to_csv(RUN_DIR / "m3_monthly_subset.csv", index=False)
    return subset


def run_benchmark(selected: list[dict]) -> pd.DataFrame:
    rows = []
    for series_number, item in enumerate(selected, start=1):
        dates = pd.date_range(item["start"], periods=len(item["values"]), freq="MS")
        full = pd.DataFrame({"date": dates, "value": item["values"]})
        n = len(full)
        for window in range(WINDOWS):
            test_end = n - window * HORIZON
            test_start = test_end - HORIZON
            train = full.iloc[:test_start]
            test = full.iloc[test_start:test_end]
            if len(train) < MIN_TRAIN or len(test) != HORIZON:
                raise ValueError(f"Invalid evaluation split for M3 series {item['series']}.")

            train_series = fs._prep_series(train, "date", "value")
            actual = test["value"].to_numpy(dtype=float)
            base = {
                "series": item["series"],
                "series_length": n,
                "window": window,
                "horizon": HORIZON,
                "train_size": len(train),
            }

            for method in FIXED_METHODS:
                started = time.perf_counter()
                result = fs.run_forecast(
                    train,
                    "date",
                    "value",
                    HORIZON,
                    model=method,
                    seasonal_period=SEASONAL_PERIOD,
                )
                elapsed = time.perf_counter() - started
                forecast = np.asarray(
                    [point["value"] for point in result["forecast"]], dtype=float
                )
                mase = fs._mase(actual, forecast, train_series)
                if not np.isfinite(mase):
                    raise ValueError(f"Non-finite MASE for {item['series']} {method}.")
                rows.append(
                    {
                        **base,
                        "method": method,
                        "mase": mase,
                        "picked": method,
                        "seconds": elapsed,
                        "candidate_count": 1,
                    }
                )

            for method, use_shortlist in [
                ("auto", True),
                ("auto_no_shortlist", False),
            ]:
                started = time.perf_counter()
                result = fs.run_forecast(
                    train,
                    "date",
                    "value",
                    HORIZON,
                    model="auto",
                    seasonal_period=SEASONAL_PERIOD,
                    use_shortlist=use_shortlist,
                )
                elapsed = time.perf_counter() - started
                forecast = np.asarray(
                    [point["value"] for point in result["forecast"]], dtype=float
                )
                mase = fs._mase(actual, forecast, train_series)
                if not np.isfinite(mase):
                    raise ValueError(
                        f"Non-finite MASE for {item['series']} {method}."
                    )
                rows.append(
                    {
                        **base,
                        "method": method,
                        "mase": mase,
                        "picked": result["model_used"],
                        "seconds": elapsed,
                        "candidate_count": len(result["candidates_evaluated"]),
                    }
                )
        print(f"  {series_number}/{N_SERIES} series: {item['series']}", flush=True)

    raw = pd.DataFrame(rows)
    raw.to_csv(RUN_DIR / "m3_forecasting_raw.csv", index=False)
    return raw


def main() -> None:
    if not SOURCE_ZIP.is_file():
        raise FileNotFoundError(f"Required M3 archive is missing: {SOURCE_ZIP}")
    selected, eligible_count = load_m3_series()
    subset = prepare_subset(selected)
    raw = run_benchmark(selected)
    environment = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scikit-learn": sklearn.__version__,
        "scipy": scipy.__version__,
        "statsmodels": statsmodels.__version__,
    }
    evidence = {
        "environment": environment,
        "source": {
            "title": "M3 Monthly Dataset",
            "doi": SOURCE_DOI,
            "url": "https://zenodo.org/records/4656298",
            "license": "CC BY 4.0",
            "archive": SOURCE_ZIP.name,
            "archive_sha256": hashlib.sha256(SOURCE_ZIP.read_bytes()).hexdigest(),
        },
        "selection": {
            "eligible_series": eligible_count,
            "selected_series": [item["series"] for item in selected],
            "minimum_series_length": MIN_TRAIN + WINDOWS * HORIZON,
            "rule": (
                "From eligible M3 Monthly series in source order, select 20 indices "
                "equally spaced from first to last using numpy.linspace with integer "
                "indices. Eligibility is series length >= 30 + 4*18 = 102."
            ),
        },
        "evaluation": {
            "horizon": HORIZON,
            "windows_per_series": WINDOWS,
            "minimum_training_points": MIN_TRAIN,
            "seasonal_period": SEASONAL_PERIOD,
            "series_count": len(selected),
            "raw_rows": len(raw),
        },
    }
    (RUN_DIR / "m3_environment.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Raw rows: {len(raw)}; selected series: {len(selected)}")


if __name__ == "__main__":
    main()
