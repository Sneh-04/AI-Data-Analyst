"""Verified OpenML dataset registry and reproducible cache manifest helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import errno
import hashlib
import json
from pathlib import Path
import platform
import socket
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import numpy as np
import pandas as pd
import sklearn
from sklearn.datasets import fetch_openml


EXPERIMENTS_DIR = Path(__file__).resolve().parents[1]
DATASET_DIR = Path(__file__).resolve().parent
CACHE_DIR = DATASET_DIR / "cache"
METADATA_DIR = DATASET_DIR / "metadata"
MANIFEST_PATH = DATASET_DIR / "manifest.json"
NETWORK_ATTEMPTS = 3


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    source: str
    data_id: int
    version: int
    target_column: str
    task_type: str
    n_rows: int
    n_numeric: int
    n_categorical: int
    natural_missing_fraction: float
    license_citation_note: str
    sentinel_missing_columns: tuple[str, ...] = ()


DATASETS: dict[str, DatasetSpec] = {
    spec.name: spec
    for spec in (
        DatasetSpec("adult", "OpenML:adult", 1590, 2, "class", "classification", 48842, 6, 8, 0.0095,
                    "UCI Adult/Census Income (Kohavi, 1996); OpenML copy; license not stated in OpenML metadata."),
        DatasetSpec("heart-statlog", "OpenML:heart-statlog", 53, 1, "class", "classification", 270, 13, 0, 0.0,
                    "Statlog Heart; UCI/OpenML attribution; license not stated in OpenML metadata."),
        DatasetSpec("breast-w", "OpenML:breast-w", 15, 1, "Class", "classification", 699, 9, 0, 0.0025,
                    "Wisconsin Breast Cancer Original (Wolberg); UCI/OpenML attribution; license not stated in OpenML metadata."),
        DatasetSpec("hepatitis", "OpenML:hepatitis", 55, 1, "Class", "classification", 155, 6, 13, 0.0567,
                    "UCI Hepatitis; OpenML attribution; license not stated in OpenML metadata."),
        DatasetSpec("cylinder-bands", "OpenML:cylinder-bands", 6332, 2, "band_type", "classification", 540, 18, 19, 0.05,
                    "UCI Cylinder Bands; OpenML attribution; license not stated in OpenML metadata."),
        DatasetSpec("soybean", "OpenML:soybean", 42, 1, "class", "classification", 683, 0, 35, 0.0978,
                    "UCI Soybean (Large); OpenML attribution; license not stated in OpenML metadata."),
        DatasetSpec("credit-approval", "OpenML:credit-approval", 29, 1, "class", "classification", 690, 6, 9, 0.0065,
                    "UCI Credit Approval; OpenML attribution; license not stated in OpenML metadata."),
        DatasetSpec("dermatology", "OpenML:dermatology", 35, 1, "class", "classification", 366, 1, 33, 0.0006,
                    "UCI Dermatology; OpenML attribution; license not stated in OpenML metadata."),
        DatasetSpec("mushroom", "OpenML:mushroom", 24, 1, "class", "classification", 8124, 0, 22, 0.0139,
                    "UCI Mushroom; OpenML attribution; license not stated in OpenML metadata."),
        DatasetSpec("credit-g", "OpenML:credit-g", 31, 1, "class", "classification", 1000, 7, 13, 0.0,
                    "Statlog German Credit / UCI; OpenML attribution; license not stated in OpenML metadata."),
        DatasetSpec("bank-marketing", "OpenML:bank-marketing", 1461, 1, "Class", "classification", 45211, 7, 9, 0.0,
                    "UCI Bank Marketing (Moro et al., 2014); OpenML attribution; verify source license before redistribution."),
        DatasetSpec("wine-quality-red", "OpenML:wine-quality-red", 40691, 1, "class", "classification", 1599, 11, 0, 0.0,
                    "Wine Quality (Cortez et al., 2009); UCI/OpenML attribution; verify source license before redistribution."),
        DatasetSpec("diabetes", "OpenML:diabetes", 37, 1, "class", "classification", 768, 8, 0, 0.1061,
                    "Pima Indians Diabetes; zero values in plas/pres/skin/insu/mass are treated as sentinel missing, not observed measurements.",
                    ("plas", "pres", "skin", "insu", "mass")),
        DatasetSpec("telco-customer-churn", "OpenML:telco-customer-churn", 42178, 1, "Churn", "classification", 7043, 4, 15, 0.0008,
                    "IBM Telco Customer Churn; OpenML copy; license not stated in OpenML metadata."),
        DatasetSpec("pc1", "OpenML:pc1", 1068, 1, "defects", "classification", 1109, 21, 0, 0.0,
                    "NASA Metrics Data Program PC1; OpenML attribution; license not stated in OpenML metadata."),
    )
}


class DatasetLoadError(ValueError):
    """Raised when OpenML data does not match the verified registry entry."""


NUMERIC_STRING_COLUMNS = {
    "telco-customer-churn": ("TotalCharges",),
}


def classify_openml_features(
    frame: pd.DataFrame,
    feature_types: dict[str, str],
    numeric_string_columns: tuple[str, ...] = (),
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Apply OpenML numeric/nominal metadata, with explicit string-numeric overrides."""
    missing_metadata = [column for column in frame.columns if column not in feature_types]
    if missing_metadata:
        raise DatasetLoadError(f"OpenML feature metadata missing columns: {missing_metadata}.")
    classified = frame.copy()
    coercion_counts: dict[str, int] = {}
    overrides = set(numeric_string_columns)
    for column in classified.columns:
        metadata_type = feature_types[column].lower()
        if metadata_type == "numeric" or column in overrides:
            source = classified[column]
            converted = pd.to_numeric(source, errors="coerce")
            coercion_counts[column] = int((source.notna() & converted.isna()).sum())
            classified[column] = converted
        elif metadata_type in {"nominal", "string", "ordinal"}:
            classified[column] = classified[column].astype("category")
        elif metadata_type != "date":
            raise DatasetLoadError(
                f"Unsupported OpenML feature type {feature_types[column]!r} for {column!r}."
            )
    unknown_overrides = overrides.difference(classified.columns)
    if unknown_overrides:
        raise DatasetLoadError(f"Numeric-string override columns are absent: {sorted(unknown_overrides)}.")
    return classified, coercion_counts


def _openml_feature_types(data_id: int) -> dict[str, str]:
    url = f"https://www.openml.org/api/v1/json/data/features/{data_id}"
    with urlopen(url, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    features = payload["data_features"]["feature"]
    return {
        feature["name"]: feature["data_type"]
        for feature in features
        if feature.get("is_target") != "true"
        and feature.get("is_ignore") != "true"
        and feature.get("is_row_identifier") != "true"
    }


def _is_retryable_network_error(error: BaseException) -> bool:
    if isinstance(error, HTTPError):
        return error.code in {408, 429} or 500 <= error.code < 600
    if isinstance(error, (URLError, TimeoutError, ConnectionError, socket.gaierror)):
        return True
    if isinstance(error, OSError):
        return error.errno in {
            errno.ECONNABORTED,
            errno.ECONNREFUSED,
            errno.ECONNRESET,
            errno.EHOSTUNREACH,
            errno.ENETUNREACH,
            errno.EPIPE,
            errno.ETIMEDOUT,
        }
    reason = getattr(error, "reason", None)
    if isinstance(reason, BaseException) and reason is not error:
        return _is_retryable_network_error(reason)
    cause = error.__cause__ or error.__context__
    if isinstance(cause, BaseException) and cause is not error:
        return _is_retryable_network_error(cause)
    return False


def _retry_network_fetch(fetch, label: str):
    last_error: Exception | None = None
    for attempt in range(NETWORK_ATTEMPTS):
        try:
            return fetch()
        except Exception as error:
            if not _is_retryable_network_error(error):
                raise
            last_error = error
            if attempt + 1 < NETWORK_ATTEMPTS:
                time.sleep(2**attempt)
    assert last_error is not None
    raise last_error


def _feature_metadata_cache_path(spec: DatasetSpec, cache_dir: Path) -> Path:
    metadata_dir = (
        METADATA_DIR
        if cache_dir.resolve() == CACHE_DIR.resolve()
        else cache_dir / "feature_metadata"
    )
    return metadata_dir / f"{spec.name}-{spec.data_id}.json"


def _metadata_manifest_reference(path: Path, cache_dir: Path) -> str:
    try:
        return path.relative_to(DATASET_DIR).as_posix()
    except ValueError:
        return path.relative_to(cache_dir).as_posix()


def _record_feature_types_in_manifest(
    spec: DatasetSpec,
    feature_types: dict[str, str],
    sidecar_path: Path,
    cache_dir: Path,
    manifest_path: Path,
) -> None:
    if not manifest_path.is_file():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    record = manifest.get(spec.name)
    if not isinstance(record, dict):
        return
    record["openml_feature_type_by_column"] = feature_types
    record["feature_metadata_cache_file"] = _metadata_manifest_reference(
        sidecar_path, cache_dir
    )
    record["feature_metadata_cache_sha256"] = hashlib.sha256(
        sidecar_path.read_bytes()
    ).hexdigest()
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _write_feature_metadata_cache(
    spec: DatasetSpec, feature_types: dict[str, str], cache_dir: Path
) -> Path:
    path = _feature_metadata_cache_path(spec, cache_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "data_id": spec.data_id,
                "version": spec.version,
                "feature_types": feature_types,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def _load_feature_types(
    spec: DatasetSpec,
    cache_dir: Path,
    manifest_record: dict[str, Any] | None = None,
    manifest_path: Path | None = None,
) -> dict[str, str]:
    path = _feature_metadata_cache_path(spec, cache_dir)
    if path.is_file():
        raw = path.read_bytes()
        expected_digest = (
            manifest_record.get("feature_metadata_cache_sha256")
            if manifest_record
            else None
        )
        if expected_digest and hashlib.sha256(raw).hexdigest() != expected_digest:
            raise DatasetLoadError(f"Cached feature metadata SHA-256 mismatch: {path}")
        cached = json.loads(raw.decode("utf-8"))
        feature_types = cached.get("feature_types")
        manifest_types = (
            manifest_record.get("openml_feature_type_by_column")
            if manifest_record
            else None
        )
        if (
            cached.get("data_id") == spec.data_id
            and cached.get("version") == spec.version
            and isinstance(feature_types, dict)
            and feature_types
            and (not manifest_types or manifest_types == feature_types)
        ):
            return {str(name): str(kind) for name, kind in feature_types.items()}
        raise DatasetLoadError(f"Invalid cached OpenML feature metadata: {path}")

    manifest_types = (
        manifest_record.get("openml_feature_type_by_column")
        if manifest_record
        else None
    )
    if isinstance(manifest_types, dict) and manifest_types:
        feature_types = {str(name): str(kind) for name, kind in manifest_types.items()}
    else:
        feature_types = _retry_network_fetch(
            lambda: _openml_feature_types(spec.data_id),
            f"OpenML feature metadata for {spec.name}",
        )
    path = _write_feature_metadata_cache(spec, feature_types, cache_dir)
    if manifest_path is not None:
        _record_feature_types_in_manifest(
            spec, feature_types, path, cache_dir, manifest_path
        )
    return feature_types


def dataset_frame_sha256(features: pd.DataFrame, target: pd.Series) -> str:
    """Hash a canonical CSV serialization of the resulting feature/target frame."""
    table = features.copy()
    table[target.name] = target.to_numpy()
    return hashlib.sha256(table.to_csv(index=False).encode("utf-8")).hexdigest()


def sync_feature_metadata_manifest(
    manifest_path: Path = MANIFEST_PATH,
    cache_dir: Path = CACHE_DIR,
    registry: dict[str, DatasetSpec] = DATASETS,
) -> None:
    """Record verified metadata sidecar paths and hashes without changing data records."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for name, spec in registry.items():
        record = manifest.get(name)
        if not isinstance(record, dict):
            raise DatasetLoadError(f"Manifest has no record for {name!r}.")
        path = _feature_metadata_cache_path(spec, cache_dir)
        if not path.is_file():
            raise FileNotFoundError(f"Feature metadata cache is missing: {path}")
        cached = json.loads(path.read_text(encoding="utf-8"))
        feature_types = cached.get("feature_types")
        if (
            cached.get("data_id") != spec.data_id
            or cached.get("version") != spec.version
            or not isinstance(feature_types, dict)
        ):
            raise DatasetLoadError(f"Invalid cached OpenML feature metadata: {path}")
        manifest_types = record.get("openml_feature_type_by_column")
        if manifest_types and manifest_types != feature_types:
            raise DatasetLoadError(
                f"Cached feature metadata disagrees with manifest for {name!r}."
            )
        record["openml_feature_type_by_column"] = feature_types
        record["feature_metadata_cache_file"] = _metadata_manifest_reference(
            path, cache_dir
        )
        record["feature_metadata_cache_sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _read_verified_dataset_cache(
    spec: DatasetSpec, cache_dir: Path, record: dict[str, Any]
) -> tuple[pd.DataFrame, pd.Series] | None:
    filename = record.get("cached_file")
    expected_digest = record.get("sha256")
    if not filename or not expected_digest:
        return None
    path = cache_dir / filename
    if not path.is_file():
        return None
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected_digest:
        raise DatasetLoadError(f"Cached dataset SHA-256 mismatch: {path}")
    table = pd.read_csv(path)
    if list(table.columns).count(spec.target_column) != 1:
        raise DatasetLoadError(f"Cached dataset has no unique target column: {path}")
    if len(table) != spec.n_rows:
        raise DatasetLoadError(
            f"{spec.name}: cached row count is {len(table)}, expected {spec.n_rows}."
        )
    target = table.pop(spec.target_column).rename(spec.target_column)
    return table, target


def validate_registry(registry: dict[str, DatasetSpec] = DATASETS) -> None:
    """Fail loudly for incomplete or inconsistent dataset metadata."""
    if not registry:
        raise ValueError("Dataset registry must not be empty.")
    for key, spec in registry.items():
        if key != spec.name:
            raise ValueError(f"Registry key {key!r} does not match dataset name {spec.name!r}.")
        if not all((spec.name, spec.source, spec.target_column, spec.license_citation_note)):
            raise ValueError(f"Dataset {spec.name!r} is missing required descriptive metadata.")
        if spec.task_type not in {"classification", "regression"}:
            raise ValueError(f"Dataset {spec.name!r} has unsupported task type {spec.task_type!r}.")
        if spec.data_id <= 0 or spec.version <= 0 or spec.n_rows <= 0:
            raise ValueError(f"Dataset {spec.name!r} has invalid OpenML identifiers or row count.")
        if spec.n_numeric < 0 or spec.n_categorical < 0 or spec.n_numeric + spec.n_categorical < 5:
            raise ValueError(f"Dataset {spec.name!r} must declare at least five features.")
        if not 0.0 <= spec.natural_missing_fraction < 1.0:
            raise ValueError(f"Dataset {spec.name!r} has an invalid missing fraction.")


def fetch_dataset(spec: DatasetSpec, cache_dir: Path = CACHE_DIR) -> tuple[pd.DataFrame, pd.Series, dict[str, Any]]:
    """Fetch by the verified OpenML name/version, then check its stable data ID."""
    manifest_path = (
        MANIFEST_PATH
        if cache_dir.resolve() == CACHE_DIR.resolve()
        else cache_dir.parent / "manifest.json"
    )
    manifest: dict[str, Any] = {}
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_record = manifest.get(spec.name)
    cached = (
        _read_verified_dataset_cache(spec, cache_dir, manifest_record)
        if isinstance(manifest_record, dict)
        else None
    )
    if cached is not None:
        features, target = cached
        feature_types = _load_feature_types(
            spec, cache_dir, manifest_record, manifest_path
        )
        features, _ = classify_openml_features(
            features, feature_types, NUMERIC_STRING_COLUMNS.get(spec.name, ())
        )
        raw_dtypes = manifest_record.get("raw_dtype_by_column", {})
        raw_nunique = manifest_record.get("raw_nunique_by_column", {})
        coercion_counts = manifest_record.get(
            "numeric_coercion_new_missing_count", {}
        )
        return features, target, {
            "data_id": spec.data_id,
            "version": spec.version,
            "feature_types": feature_types,
            "raw_dtypes": raw_dtypes,
            "raw_nunique": raw_nunique,
            "numeric_coercion_counts": coercion_counts,
            "source": "verified_local_cache",
        }

    # A cache miss here may still be served by sklearn's own data_home cache;
    # otherwise fetch_openml contacts OpenML for dataset metadata and data files.
    bunch = _retry_network_fetch(
        lambda: fetch_openml(
            name=spec.name,
            version=spec.version,
            as_frame=True,
            data_home=cache_dir,
            parser="auto",
        ),
        f"OpenML dataset {spec.name}",
    )
    data_id = int(bunch.details.get("id", -1))
    version = int(bunch.details.get("version", -1))
    if data_id != spec.data_id or version != spec.version:
        raise DatasetLoadError(
            f"{spec.name}: expected OpenML id/version {spec.data_id}/{spec.version}, "
            f"received {data_id}/{version}."
        )
    if bunch.target is None:
        raise DatasetLoadError(f"{spec.name}: OpenML returned no target column.")
    if isinstance(bunch.target, pd.DataFrame):
        if bunch.target.shape[1] != 1:
            raise DatasetLoadError(f"{spec.name}: expected one target, got {bunch.target.shape[1]}.")
        target = bunch.target.iloc[:, 0]
    else:
        target = bunch.target
    if target.name != spec.target_column:
        raise DatasetLoadError(
            f"{spec.name}: expected target {spec.target_column!r}, received {target.name!r}."
        )

    features = bunch.data.copy()
    if len(features) != spec.n_rows or len(target) != spec.n_rows:
        raise DatasetLoadError(
            f"{spec.name}: expected {spec.n_rows} rows, received {len(features)}."
        )
    feature_types = _load_feature_types(
        spec, cache_dir, manifest_record, manifest_path
    )
    raw_dtypes = {column: str(dtype) for column, dtype in features.dtypes.items()}
    raw_nunique = {
        column: int(features[column].nunique(dropna=True)) for column in features.columns
    }
    missing_metadata = [column for column in features.columns if column not in feature_types]
    if missing_metadata:
        raise DatasetLoadError(
            f"{spec.name}: OpenML metadata omitted feature columns: {missing_metadata}."
        )
    features, coercion_counts = classify_openml_features(
        features,
        feature_types,
        NUMERIC_STRING_COLUMNS.get(spec.name, ()),
    )
    missing_sentinels = [col for col in spec.sentinel_missing_columns if col not in features.columns]
    if missing_sentinels:
        raise DatasetLoadError(f"{spec.name}: sentinel columns missing from fetched data: {missing_sentinels}.")
    for column in spec.sentinel_missing_columns:
        features[column] = features[column].mask(features[column].eq(0))
    return features, target.rename(spec.target_column), {
        "data_id": data_id,
        "version": version,
        "feature_types": feature_types,
        "raw_dtypes": raw_dtypes,
        "raw_nunique": raw_nunique,
        "numeric_coercion_counts": coercion_counts,
        "source": "openml",
    }


def write_manifest_record(
    spec: DatasetSpec,
    table: pd.DataFrame,
    cache_file: Path,
    manifest_path: Path = MANIFEST_PATH,
    fetch_date: str | None = None,
    feature_types: dict[str, str] | None = None,
    numeric_coercion_counts: dict[str, int] | None = None,
    raw_dtypes: dict[str, str] | None = None,
    raw_nunique: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Record metadata and a content digest for the local, ignored CSV cache."""
    if not cache_file.is_file():
        raise FileNotFoundError(f"Dataset cache is missing: {cache_file}")
    digest = hashlib.sha256(cache_file.read_bytes()).hexdigest()
    feature_columns = [
        column for column in table.columns if column != spec.target_column
    ]
    numeric_columns = (
        [
            column
            for column in feature_columns
            if feature_types.get(column, "").lower() == "numeric"
            or column in NUMERIC_STRING_COLUMNS.get(spec.name, ())
        ]
        if feature_types is not None
        else [
            column
            for column in feature_columns
            if pd.api.types.is_numeric_dtype(table[column].dtype)
        ]
    )
    record = {
        "data_id": spec.data_id,
        "version": spec.version,
        "shape": [int(table.shape[0]), int(table.shape[1])],
        "dtype_counts": {
            str(dtype): int(count)
            for dtype, count in table.dtypes.astype(str).value_counts().sort_index().items()
        },
        "n_numeric": len(numeric_columns),
        "n_categorical": len(feature_columns) - len(numeric_columns),
        "raw_dtype_by_column": dict(raw_dtypes or {}),
        "final_dtype_by_column": {
            str(column): str(table[column].dtype) for column in feature_columns
        },
        "raw_nunique_by_column": dict(raw_nunique or {}),
        "openml_feature_type_by_column": dict(feature_types or {}),
        "feature_metadata_cache_file": (
            _metadata_manifest_reference(
                _feature_metadata_cache_path(spec, cache_file.parent),
                cache_file.parent,
            )
            if feature_types
            else None
        ),
        "feature_metadata_cache_sha256": (
            hashlib.sha256(
                _write_feature_metadata_cache(
                    spec, feature_types, cache_file.parent
                ).read_bytes()
            ).hexdigest()
            if feature_types
            else None
        ),
        "feature_type_counts": (
            {
                kind: int(sum(
                    feature_types.get(column, "").lower() == kind
                    for column in table.columns
                    if column != spec.target_column
                ))
                for kind in ("numeric", "nominal", "string", "date", "ordinal")
                if any(
                    feature_types.get(column, "").lower() == kind
                    for column in table.columns
                    if column != spec.target_column
                )
            }
            if feature_types is not None
            else {}
        ),
        "numeric_coercion_new_missing_count": dict(numeric_coercion_counts or {}),
        "per_column_missing_rate": {
            str(column): float(rate)
            for column, rate in table.isna().mean().items()
        },
        "sha256": digest,
        "cached_file": cache_file.name,
        "fetch_date": fetch_date or datetime.now(timezone.utc).date().isoformat(),
        "library_versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
        },
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {}
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest[spec.name] = record
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


validate_registry()
