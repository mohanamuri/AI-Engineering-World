"""Framework-independent dataset exploration services."""

from __future__ import annotations

from dataclasses import dataclass
import re

import pandas as pd
from pandas.api.types import is_numeric_dtype


TARGET_COLUMN_CANDIDATES = (
    "LoanApproved",
    "Loan_Status",
    "LoanStatus",
    "Approved",
    "Target",
)


@dataclass(frozen=True)
class DatasetProfile:
    """High-level characteristics of a dataframe."""

    rows: int
    columns: int
    missing_values: int
    duplicate_rows: int
    memory_bytes: int
    numeric_columns: tuple[str, ...]
    categorical_columns: tuple[str, ...]


def profile_dataset(dataframe: pd.DataFrame) -> DatasetProfile:
    """Calculate dataset KPIs and semantic column groups."""
    numeric_columns = tuple(
        str(column)
        for column in dataframe.select_dtypes(include="number").columns
    )
    categorical_columns = tuple(
        str(column)
        for column in dataframe.columns
        if str(column) not in numeric_columns
    )

    return DatasetProfile(
        rows=len(dataframe),
        columns=len(dataframe.columns),
        missing_values=int(dataframe.isna().sum().sum()),
        duplicate_rows=int(dataframe.duplicated().sum()),
        memory_bytes=int(dataframe.memory_usage(index=True, deep=True).sum()),
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
    )


def statistical_summary(
    dataframe: pd.DataFrame,
    *,
    include_categorical: bool = False,
) -> pd.DataFrame:
    """Return descriptive statistics for the requested column types."""
    if include_categorical:
        return dataframe.describe(include="all").transpose()

    numeric_data = dataframe.select_dtypes(include="number")
    if numeric_data.empty:
        return pd.DataFrame()
    return numeric_data.describe().transpose()


def missing_value_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Return per-column missing counts and percentages."""
    missing_counts = dataframe.isna().sum()
    denominator = len(dataframe)
    percentages = (
        missing_counts.div(denominator).mul(100)
        if denominator
        else missing_counts.astype(float)
    )

    return (
        pd.DataFrame(
            {
                "Column": missing_counts.index.astype(str),
                "Missing Values": missing_counts.astype(int).values,
                "Missing (%)": percentages.round(2).values,
            }
        )
        .sort_values(
            by=["Missing Values", "Column"],
            ascending=[False, True],
            ignore_index=True,
        )
    )


def detect_target_column(dataframe: pd.DataFrame) -> str | None:
    """Detect a conventional loan target column without guessing from values."""
    canonical_columns = {
        _canonicalize_column_name(str(column)): str(column)
        for column in dataframe.columns
    }

    for candidate in TARGET_COLUMN_CANDIDATES:
        match = canonical_columns.get(_canonicalize_column_name(candidate))
        if match is not None:
            return match

    target_tokens = ("approved", "approval", "eligibility", "status", "target")
    semantic_matches = [
        str(column)
        for column in dataframe.columns
        if any(
            token in _canonicalize_column_name(str(column))
            for token in target_tokens
        )
    ]
    return semantic_matches[0] if len(semantic_matches) == 1 else None


def target_distribution(
    dataframe: pd.DataFrame,
    target_column: str,
) -> pd.DataFrame:
    """Return target value counts, retaining missing target values."""
    if target_column not in dataframe.columns:
        raise KeyError(f"Unknown target column: {target_column}")

    counts = (
        dataframe[target_column]
        .astype("string")
        .fillna("Missing")
        .value_counts(dropna=False)
    )
    return counts.rename_axis("Value").reset_index(name="Count")


def numeric_feature(dataframe: pd.DataFrame, column: str) -> pd.Series:
    """Return a validated numeric feature for visualization."""
    if column not in dataframe.columns:
        raise KeyError(f"Unknown feature column: {column}")
    if not is_numeric_dtype(dataframe[column]):
        raise TypeError(f"Feature is not numeric: {column}")
    return dataframe[column].dropna()


def correlation_matrix(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Calculate Pearson correlations for numeric features."""
    numeric_data = dataframe.select_dtypes(include="number")
    if numeric_data.empty:
        return pd.DataFrame()
    return numeric_data.corr()


def dataframe_to_csv(dataframe: pd.DataFrame) -> bytes:
    """Serialize the current dataframe as UTF-8 CSV bytes."""
    return dataframe.to_csv(index=False).encode("utf-8")


def _canonicalize_column_name(column: str) -> str:
    return re.sub(r"[^a-z0-9]", "", column.casefold())

