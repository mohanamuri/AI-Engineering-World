"""Exploration service for the HR Analytics ML pipeline.

Produces summary statistics and chart data for the Explore page.
Designed for the IBM HR Attrition dataset but works with any binary
classification dataset whose target column is a string (e.g. Yes/No).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class ExplorationResult:
    """Pre-computed exploration data passed to the UI."""
    shape: tuple[int, int]
    dtypes: pd.Series
    missing: pd.Series           # count of nulls per column
    describe: pd.DataFrame       # numeric summary statistics
    target_distribution: pd.Series  # value_counts for target column
    attrition_by_dept: pd.DataFrame | None
    attrition_by_role: pd.DataFrame | None
    attrition_by_age: pd.DataFrame | None
    attrition_by_overtime: pd.DataFrame | None


def explore(dataframe: pd.DataFrame, target_col: str = "Attrition") -> ExplorationResult:
    missing = dataframe.isnull().sum()
    target_dist = (
        dataframe[target_col].value_counts()
        if target_col in dataframe.columns
        else pd.Series(dtype=int)
    )

    dept_col = _find_col(dataframe, "Department")
    role_col = _find_col(dataframe, "JobRole")
    overtime_col = _find_col(dataframe, "OverTime")
    age_col = _find_col(dataframe, "Age")

    attrition_by_dept = _crosstab(dataframe, target_col, dept_col)
    attrition_by_role = _crosstab(dataframe, target_col, role_col)
    attrition_by_overtime = _crosstab(dataframe, target_col, overtime_col)

    attrition_by_age = None
    if age_col and target_col in dataframe.columns:
        bins = [18, 25, 35, 45, 55, 70]
        labels = ["18-24", "25-34", "35-44", "45-54", "55+"]
        tmp = dataframe[[age_col, target_col]].copy()
        tmp["AgeGroup"] = pd.cut(tmp[age_col], bins=bins, labels=labels, right=False)
        attrition_by_age = _crosstab(tmp, target_col, "AgeGroup")

    return ExplorationResult(
        shape=dataframe.shape,
        dtypes=dataframe.dtypes,
        missing=missing,
        describe=dataframe.describe(include="all"),
        target_distribution=target_dist,
        attrition_by_dept=attrition_by_dept,
        attrition_by_role=attrition_by_role,
        attrition_by_age=attrition_by_age,
        attrition_by_overtime=attrition_by_overtime,
    )


def _find_col(df: pd.DataFrame, name: str) -> str | None:
    return name if name in df.columns else None


def _crosstab(df: pd.DataFrame, target_col: str, group_col: str | None) -> pd.DataFrame | None:
    if group_col is None or target_col not in df.columns:
        return None
    ct = pd.crosstab(df[group_col], df[target_col], normalize="index") * 100
    ct.columns = [f"{c} (%)" for c in ct.columns]
    ct["Total"] = df.groupby(group_col)[target_col].count()
    return ct.reset_index()
