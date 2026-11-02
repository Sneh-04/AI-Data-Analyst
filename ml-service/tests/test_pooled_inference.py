import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.imputation_uncertainty import pool_rubins_rules
from app.services.multiple_imputation import (
    apply_mnar_delta,
    impute_m_datasets,
)

test_internal_api_key = "test-shared-key-0123456789abcdef"
client = TestClient(app, headers={"X-Internal-Key": test_internal_api_key})


@pytest.fixture(autouse=True)
def configure_internal_api_key(monkeypatch):
    monkeypatch.setenv("INTERNAL_API_KEY", test_internal_api_key)


def _incomplete_frame():
    rng = np.random.RandomState(12)
    predictor = rng.normal(size=120)
    target = 1.5 + 2.25 * predictor + rng.normal(scale=0.8, size=120)
    frame = pd.DataFrame({"target": target, "predictor": predictor, "constant": 4.0})
    frame.loc[[1, 8, 15, 22, 39, 51, 74, 91, 108], "target"] = np.nan
    frame.loc[[4, 17, 33, 60, 83], "predictor"] = np.nan
    return frame


def test_rubin_pooling_matches_hard_coded_reference_values():
    pooled = pool_rubins_rules(
        estimates=[2.0, 4.0, 6.0],
        within_variances=[1.0, 1.0, 1.0],
        complete_data_df=20,
    )
    assert pooled.estimate == pytest.approx(4.0)
    assert pooled.within_imputation_variance == pytest.approx(1.0)
    assert pooled.between_imputation_variance == pytest.approx(4.0)
    assert pooled.total_variance == pytest.approx(19 / 3)
    assert pooled.degrees_of_freedom == pytest.approx(1.425728050351527)
    assert pooled.confidence_interval == pytest.approx(
        (-12.297192921016105, 20.297192921016105)
    )


def test_same_seed_produces_identical_imputations():
    frame = _incomplete_frame()
    first = impute_m_datasets(frame, "target", 4, 21, "proper")
    second = impute_m_datasets(frame, "target", 4, 21, "proper")
    for left, right in zip(first, second):
        pd.testing.assert_frame_equal(left, right)


@pytest.mark.parametrize("method", ["proper", "improper"])
def test_observed_cells_are_never_changed(method):
    frame = _incomplete_frame()
    completed = impute_m_datasets(frame, "target", 3, 5, method)
    observed = frame.select_dtypes(include=[np.number]).drop(columns="constant")
    for dataset in completed:
        for column in observed:
            mask = observed[column].notna()
            np.testing.assert_array_equal(
                dataset.loc[mask, column].to_numpy(),
                observed.loc[mask, column].to_numpy(),
            )
        assert "constant" not in dataset.columns


def test_delta_shifts_only_imputed_target_cells():
    frame = _incomplete_frame()
    completed = impute_m_datasets(frame, "target", 2, 7, "proper")[0]
    observed_sd = frame["target"].std(ddof=1)
    shifted = apply_mnar_delta(completed, frame, "target", 0.75, observed_sd)
    missing = frame["target"].isna()
    np.testing.assert_allclose(
        shifted.loc[missing, "target"] - completed.loc[missing, "target"],
        0.75 * observed_sd,
    )
    np.testing.assert_array_equal(
        shifted.loc[~missing, "target"], frame.loc[~missing, "target"]
    )
    pd.testing.assert_frame_equal(
        shifted.loc[:, ["predictor"]], completed.loc[:, ["predictor"]]
    )


def test_proper_and_improper_imputations_differ():
    frame = _incomplete_frame()
    proper = impute_m_datasets(frame, "target", 4, 15, "proper")
    improper = impute_m_datasets(frame, "target", 4, 15, "improper")
    assert any(
        not np.allclose(left["target"], right["target"])
        for left, right in zip(proper, improper)
    )


def test_proper_imputation_fills_sparse_missing_values_in_original_rows():
    frame = pd.DataFrame(
        {
            "target": np.arange(30, dtype=float),
            "predictor": np.arange(30, dtype=float) ** 2,
        }
    )
    frame.loc[0, "target"] = np.nan
    frame.loc[1, "predictor"] = np.nan
    completed = impute_m_datasets(frame, "target", 5, 2, "proper")
    assert all(not dataset.isna().any().any() for dataset in completed)
    for dataset in completed:
        assert dataset.loc[2, "target"] == frame.loc[2, "target"]
        assert dataset.loc[2, "predictor"] == frame.loc[2, "predictor"]


def _request(records, **overrides):
    payload = {
        "records": records,
        "target_column": "target",
        "estimand": "mean",
        "m": 3,
        "seed": 42,
    }
    payload.update(overrides)
    return payload


def _json_records(frame):
    return frame.astype(object).where(pd.notna(frame), None).to_dict(orient="records")


def test_endpoint_returns_pooled_inference_and_required_fields():
    frame = _incomplete_frame()
    response = client.post(
        "/api/ml/inference/pooled",
        json=_request(_json_records(frame)),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["n_rows_used"] == len(frame)
    assert body["subsampled"] is False
    assert body["results"][0]["delta"] == 0.0
    assert {
        "estimate",
        "ci_lower",
        "ci_upper",
        "standard_error",
        "degrees_of_freedom",
        "within_variance",
        "between_variance",
        "total_variance",
        "lambda",
    } <= body["results"][0].keys()
    assert "Missingness mechanism (MCAR/MAR/MNAR) cannot be determined from the data alone" in body[
        "warnings"
    ]


def test_endpoint_treats_blank_csv_cells_as_missing_values():
    records = [
        {"target": "" if index % 4 == 0 else float(index)}
        for index in range(40)
    ]
    response = client.post(
        "/api/ml/inference/pooled",
        json=_request(records, m=2),
    )
    assert response.status_code == 200
    assert response.json()["missing_fraction"] == pytest.approx(0.25)


def test_endpoint_rejects_non_numeric_target():
    records = [{"target": "bad"} for _ in range(25)]
    response = client.post("/api/ml/inference/pooled", json=_request(records))
    assert response.status_code == 422


def test_endpoint_rejects_fewer_than_twenty_observed_targets():
    records = [{"target": float(index) if index < 19 else None} for index in range(25)]
    response = client.post("/api/ml/inference/pooled", json=_request(records))
    assert response.status_code == 422


def test_endpoint_rejects_bad_m():
    response = client.post(
        "/api/ml/inference/pooled",
        json=_request([{"target": index} for index in range(25)], m=1),
    )
    assert response.status_code == 422


def test_endpoint_rejects_more_than_eleven_deltas():
    response = client.post(
        "/api/ml/inference/pooled",
        json=_request(
            [{"target": index} for index in range(25)],
            deltas=[0.0] * 12,
        ),
    )
    assert response.status_code == 422


def test_endpoint_rejects_missing_slope_predictor():
    response = client.post(
        "/api/ml/inference/pooled",
        json=_request(
            [{"target": index} for index in range(25)],
            estimand="ols_slope",
        ),
    )
    assert response.status_code == 422


def test_endpoint_returns_complete_data_interval_when_target_has_no_missing_values():
    records = [{"target": float(index)} for index in range(25)]
    response = client.post("/api/ml/inference/pooled", json=_request(records))
    assert response.status_code == 200
    body = response.json()
    assert "no missing values" in body["method_note"]
    assert body["results"][0]["between_variance"] == 0.0
    assert body["results"][0]["lambda"] == 0.0
    assert body["results"][0]["ci_lower"] < body["results"][0]["estimate"]
    assert body["results"][0]["estimate"] < body["results"][0]["ci_upper"]


def test_endpoint_adds_high_missingness_and_improper_warnings():
    records = [
        {"target": float(index) if index < 30 else None}
        for index in range(50)
    ]
    response = client.post(
        "/api/ml/inference/pooled",
        json=_request(records, method="improper", m=2),
    )
    assert response.status_code == 200
    warnings = response.json()["warnings"]
    assert any("coverage may be degraded" in warning for warning in warnings)
    assert any("underestimates between-imputation variance" in warning for warning in warnings)


def test_endpoint_seeded_subsample_limits_rows_to_twenty_thousand():
    records = [{"target": index % 17} for index in range(20_001)]
    response = client.post(
        "/api/ml/inference/pooled",
        json=_request(records, seed=3),
    )
    assert response.status_code == 200
    assert response.json()["n_rows_used"] == 20_000
    assert response.json()["subsampled"] is True


def test_slope_endpoint_works_with_proper_imputation():
    frame = _incomplete_frame()
    response = client.post(
        "/api/ml/inference/pooled",
        json=_request(
            _json_records(frame),
            estimand="ols_slope",
            predictor_column="predictor",
            method="proper",
        ),
    )
    assert response.status_code == 200
    assert response.json()["results"][0]["estimate"] == pytest.approx(2.25, abs=0.3)
