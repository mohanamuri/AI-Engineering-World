"""Preprocessing service for the loan eligibility ML pipeline.

Responsibilities
----------------
- Accept a raw DataFrame and a user-defined PreprocessConfig
- Build a sklearn Pipeline that imputes, scales, and encodes features
- Fit the pipeline on the training split ONLY (prevents data leakage)
- Return train/test splits alongside the fitted pipeline artifact

Interview note — Training-serving skew
---------------------------------------
The most common cause of silent model degradation in production is fitting
preprocessors (scalers, encoders) on the full dataset, then deploying them
on new data whose distribution wasn't seen during fitting.

The correct pattern (implemented here):
  1. Split first → fit only on train → transform both train and test
  2. Package the fitted pipeline with the model → ship them together
  3. At inference time, apply the *same fitted* pipeline to new data

This is why sklearn Pipelines exist: they enforce the fit-on-train-only
contract and make the artifact a single serialisable object.
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


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ImputeStrategy = Literal["mean", "median", "most_frequent", "constant"]
ScalingStrategy = Literal["standard", "minmax", "none"]
EncodingStrategy = Literal["ordinal", "onehot"]


@dataclass(frozen=True)
class PreprocessConfig:
    """User-defined choices for the preprocessing pipeline.

    All fields have sensible defaults so the page can render immediately
    without requiring the user to configure everything explicitly.
    """

    target_column: str
    numeric_impute_strategy: ImputeStrategy = "median"
    categorical_impute_strategy: ImputeStrategy = "most_frequent"
    scaling_strategy: ScalingStrategy = "standard"
    encoding_strategy: EncodingStrategy = "ordinal"
    drop_columns: tuple[str, ...] = field(default_factory=tuple)
    test_size: float = 0.2
    random_state: int = 42


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class PreprocessResult:
    """Everything downstream stages need from the preprocessor.

    Attributes
    ----------
    X_train, X_test : pd.DataFrame
        Feature matrices — already imputed, scaled, and encoded.
    y_train, y_test : pd.Series
        Target vectors with original values preserved.
    pipeline : sklearn.pipeline.Pipeline
        Fitted ColumnTransformer pipeline. Pass this to joblib.dump()
        alongside the trained model so inference uses identical transforms.
    feature_names : list[str]
        Column names *after* encoding (used for feature importance charts).
    config : PreprocessConfig
        The config that produced this result — stored for reproducibility.
    class_labels : tuple
        Unique classes in the target column (used by evaluate page).
    """

    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    pipeline: Pipeline
    feature_names: list[str]
    config: PreprocessConfig
    class_labels: tuple


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def preprocess(
    dataframe: pd.DataFrame,
    config: PreprocessConfig,
) -> PreprocessResult:
    """Build, fit, and apply a preprocessing pipeline.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Raw uploaded dataset. Not modified in place.
    config : PreprocessConfig
        User choices from the preprocess page.

    Returns
    -------
    PreprocessResult
        Train/test splits, fitted pipeline, feature names, class labels.

    Raises
    ------
    PreprocessingError
        If the config is invalid (e.g., target column missing, too few rows).
    """
    _validate(dataframe, config)

    df = dataframe.drop(columns=list(config.drop_columns), errors="ignore").copy()

    X = df.drop(columns=[config.target_column])
    y = df[config.target_column]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=config.test_size,
        random_state=config.random_state,
        stratify=_safe_stratify(y),
    )

    numeric_cols = [
        c for c in X_train.columns
        if pd.api.types.is_numeric_dtype(X_train[c])
    ]
    categorical_cols = [
        c for c in X_train.columns
        if c not in numeric_cols
    ]

    pipeline = _build_pipeline(config, numeric_cols, categorical_cols)

    # Fit on train only — the cardinal rule
    X_train_transformed = pipeline.fit_transform(X_train)
    X_test_transformed = pipeline.transform(X_test)

    feature_names = _get_feature_names(
        pipeline, numeric_cols, categorical_cols, config.encoding_strategy
    )

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


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _validate(dataframe: pd.DataFrame, config: PreprocessConfig) -> None:
    if config.target_column not in dataframe.columns:
        raise PreprocessingError(
            f"Target column '{config.target_column}' not found in dataset. "
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
            f"Need at least {min_rows} rows for a {config.test_size:.0%} test split."
        )

    target_missing_pct = dataframe[config.target_column].isna().mean()
    if target_missing_pct > 0.3:
        raise PreprocessingError(
            f"Target column '{config.target_column}' is {target_missing_pct:.0%} missing. "
            "A target with >30% missing values cannot produce a reliable model."
        )


def _safe_stratify(y: pd.Series) -> pd.Series | None:
    """Return y for stratification only if each class has ≥2 samples."""
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
            (
                "imputer",
                SimpleImputer(
                    strategy=config.categorical_impute_strategy,
                    fill_value="Unknown",
                ),
            ),
        ]
        if config.encoding_strategy == "ordinal":
            categorical_steps.append(
                ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1))
            )
        else:
            # onehot — import here to keep top-level imports minimal
            from sklearn.preprocessing import OneHotEncoder  # noqa: PLC0415
            categorical_steps.append(
                ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
            )
        transformers.append(("categorical", Pipeline(categorical_steps), categorical_cols))

    column_transformer = ColumnTransformer(transformers=transformers, remainder="drop")
    return Pipeline([("preprocessor", column_transformer)])


def _get_feature_names(
    pipeline: Pipeline,
    numeric_cols: list[str],
    categorical_cols: list[str],
    encoding_strategy: str,
) -> list[str]:
    """Extract output column names from the fitted ColumnTransformer."""
    try:
        ct = pipeline.named_steps["preprocessor"]
        return list(ct.get_feature_names_out())
    except Exception:
        # Fallback: construct names manually
        names = list(numeric_cols)
        if encoding_strategy == "ordinal":
            names += list(categorical_cols)
        return names


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class PreprocessingError(ValueError):
    """Raised when the dataset or config cannot produce a valid preprocessing pipeline."""
