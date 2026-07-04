"""Preprocessing service for the HR Analytics ML pipeline.

Responsibilities
----------------
- Accept a raw IBM HR DataFrame and a user-defined PreprocessConfig
- Build a sklearn Pipeline that encodes, scales, and splits features
- Fit the pipeline on the training split ONLY (prevents data leakage)
- Return train/test splits alongside the fitted pipeline artifact

IBM HR Dataset notes
---------------------
Target: Attrition (Yes / No) — kept as-is; sklearn handles string labels.
Constant columns to drop by default: EmployeeCount (all=1), Over18 (all='Y'),
StandardHours (all=80), EmployeeNumber (ID with no predictive value).
Class imbalance: attrition datasets are typically imbalanced —
use class_weight='balanced' in models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    MinMaxScaler,
    OrdinalEncoder,
    StandardScaler,
)


ImputeStrategy = Literal["mean", "median", "most_frequent", "constant"]
ScalingStrategy = Literal["standard", "minmax", "none"]
EncodingStrategy = Literal["ordinal", "onehot"]


@dataclass(frozen=True)
class PreprocessConfig:
    target_column: str = "Attrition"
    numeric_impute_strategy: ImputeStrategy = "median"
    categorical_impute_strategy: ImputeStrategy = "most_frequent"
    scaling_strategy: ScalingStrategy = "standard"
    encoding_strategy: EncodingStrategy = "ordinal"
    drop_columns: tuple[str, ...] = field(default_factory=tuple)
    test_size: float = 0.2
    random_state: int = 42


@dataclass
class PreprocessResult:
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    pipeline: Pipeline
    feature_names: list[str]
    config: PreprocessConfig
    class_labels: tuple


def preprocess(dataframe: pd.DataFrame, config: PreprocessConfig) -> PreprocessResult:
    _validate(dataframe, config)

    df = dataframe.drop(columns=list(config.drop_columns), errors="ignore").copy()

    X = df.drop(columns=[config.target_column])
    y = df[config.target_column]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=config.test_size,
        random_state=config.random_state,
        stratify=_safe_stratify(y),
    )

    numeric_cols = [c for c in X_train.columns if pd.api.types.is_numeric_dtype(X_train[c])]
    categorical_cols = [c for c in X_train.columns if c not in numeric_cols]

    pipeline = _build_pipeline(config, numeric_cols, categorical_cols)

    X_train_transformed = pipeline.fit_transform(X_train)
    X_test_transformed = pipeline.transform(X_test)

    feature_names = _get_feature_names(pipeline, numeric_cols, categorical_cols, config.encoding_strategy)

    X_train_df = pd.DataFrame(X_train_transformed, columns=feature_names)
    X_test_df = pd.DataFrame(X_test_transformed, columns=feature_names)

    return PreprocessResult(
        X_train=X_train_df,
        X_test=X_test_df,
        y_train=y_train.reset_index(drop=True),
        y_test=y_test.reset_index(drop=True),
        pipeline=pipeline,
        feature_names=feature_names,
        config=config,
        class_labels=tuple(sorted(y.dropna().unique())),
    )


def _validate(dataframe: pd.DataFrame, config: PreprocessConfig) -> None:
    if config.target_column not in dataframe.columns:
        raise PreprocessingError(
            f"Target column '{config.target_column}' not found. "
            f"Available columns: {list(dataframe.columns)}"
        )

    feature_cols = [
        c for c in dataframe.columns
        if c != config.target_column and c not in config.drop_columns
    ]
    if not feature_cols:
        raise PreprocessingError(
            "No feature columns remain after removing the target and dropped columns."
        )

    min_rows = max(10, int(1 / config.test_size))
    if len(dataframe) < min_rows:
        raise PreprocessingError(
            f"Dataset has only {len(dataframe)} rows. "
            f"Need at least {min_rows} for a {config.test_size:.0%} test split."
        )

    target_missing_pct = dataframe[config.target_column].isna().mean()
    if target_missing_pct > 0.3:
        raise PreprocessingError(
            f"Target column '{config.target_column}' is {target_missing_pct:.0%} missing."
        )


def _safe_stratify(y: pd.Series) -> pd.Series | None:
    counts = y.dropna().value_counts()
    if counts.empty or (counts < 2).any():
        return None
    return y


def _build_pipeline(
    config: PreprocessConfig,
    numeric_cols: list[str],
    categorical_cols: list[str],
) -> Pipeline:
    transformers = []

    if numeric_cols:
        numeric_steps: list = [
            ("imputer", SimpleImputer(strategy=config.numeric_impute_strategy)),
        ]
        if config.scaling_strategy == "standard":
            numeric_steps.append(("scaler", StandardScaler()))
        elif config.scaling_strategy == "minmax":
            numeric_steps.append(("scaler", MinMaxScaler()))
        transformers.append(("numeric", Pipeline(numeric_steps), numeric_cols))

    if categorical_cols:
        categorical_steps: list = [
            ("imputer", SimpleImputer(strategy=config.categorical_impute_strategy, fill_value="Unknown")),
        ]
        if config.encoding_strategy == "ordinal":
            categorical_steps.append(
                ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1))
            )
        else:
            from sklearn.preprocessing import OneHotEncoder  # noqa: PLC0415
            categorical_steps.append(
                ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
            )
        transformers.append(("categorical", Pipeline(categorical_steps), categorical_cols))

    column_transformer = ColumnTransformer(transformers=transformers, remainder="drop")
    return Pipeline([("preprocessor", column_transformer)])


def _get_feature_names(pipeline, numeric_cols, categorical_cols, encoding_strategy) -> list[str]:
    try:
        ct = pipeline.named_steps["preprocessor"]
        return list(ct.get_feature_names_out())
    except Exception:
        names = list(numeric_cols)
        if encoding_strategy == "ordinal":
            names += list(categorical_cols)
        return names


class PreprocessingError(ValueError):
    """Raised when the dataset or config cannot produce a valid preprocessing pipeline."""
