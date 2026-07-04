"""Model training service for the HR Analytics ML pipeline.

Same four classifiers as the loan ML tier, with class_weight='balanced'
enabled by default to handle the IBM HR class imbalance (~16 % attrition).

Interview note — Class Imbalance
----------------------------------
HR attrition datasets are typically imbalanced — often ~80/20 or more.
Without correction, classifiers optimise for the majority class and predict
"No" for everything, missing all flight risks.

Two common fixes:
  1. class_weight='balanced'  — sklearn re-weights samples inversely
     proportional to class frequency. No extra data needed.
  2. SMOTE oversampling        — synthetically creates minority-class samples.

We use class_weight='balanced' here because it adds no data leakage risk
and works seamlessly inside sklearn's Pipeline.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

try:
    from xgboost import XGBClassifier
    _XGBOOST_AVAILABLE = True
except ImportError:
    _XGBOOST_AVAILABLE = False


SUPPORTED_MODELS = [
    "Logistic Regression",
    "Decision Tree",
    "Random Forest",
    "XGBoost",
]


@dataclass
class TrainResult:
    model_name: str
    model: Any
    feature_names: list[str]
    train_accuracy: float
    test_accuracy: float
    training_time_seconds: float
    hyperparams: dict[str, Any]


def train(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    model_name: str,
    hyperparams: dict[str, Any],
) -> TrainResult:
    estimator = _build_estimator(model_name, hyperparams)

    t0 = time.perf_counter()
    estimator.fit(X_train, y_train)
    elapsed = time.perf_counter() - t0

    train_accuracy = float(accuracy_score(y_train, estimator.predict(X_train)))
    test_accuracy = float(accuracy_score(y_test, estimator.predict(X_test)))

    return TrainResult(
        model_name=model_name,
        model=estimator,
        feature_names=list(X_train.columns),
        train_accuracy=train_accuracy,
        test_accuracy=test_accuracy,
        training_time_seconds=round(elapsed, 4),
        hyperparams=hyperparams,
    )


def get_hyperparameter_defaults(model_name: str) -> dict[str, Any]:
    defaults: dict[str, dict[str, Any]] = {
        "Logistic Regression": {"C": 1.0, "max_iter": 1000, "solver": "lbfgs"},
        "Decision Tree": {"max_depth": 5, "min_samples_split": 10, "min_samples_leaf": 5},
        "Random Forest": {"n_estimators": 100, "max_depth": 10, "min_samples_split": 5},
        "XGBoost": {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 4},
    }
    if model_name not in defaults:
        raise TrainingError(f"Unknown model: '{model_name}'. Choose from: {SUPPORTED_MODELS}")
    return defaults[model_name]


def _build_estimator(model_name: str, hyperparams: dict[str, Any]) -> Any:
    if model_name == "Logistic Regression":
        return LogisticRegression(
            C=hyperparams.get("C", 1.0),
            max_iter=hyperparams.get("max_iter", 1000),
            solver=hyperparams.get("solver", "lbfgs"),
            class_weight="balanced",
            random_state=42,
        )

    if model_name == "Decision Tree":
        return DecisionTreeClassifier(
            max_depth=hyperparams.get("max_depth", 5),
            min_samples_split=hyperparams.get("min_samples_split", 10),
            min_samples_leaf=hyperparams.get("min_samples_leaf", 5),
            class_weight="balanced",
            random_state=42,
        )

    if model_name == "Random Forest":
        return RandomForestClassifier(
            n_estimators=hyperparams.get("n_estimators", 100),
            max_depth=hyperparams.get("max_depth", 10),
            min_samples_split=hyperparams.get("min_samples_split", 5),
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )

    if model_name == "XGBoost":
        if not _XGBOOST_AVAILABLE:
            raise TrainingError("XGBoost is not installed. Run: pip install xgboost>=2.0")
        # XGBoost uses scale_pos_weight instead of class_weight
        return XGBClassifier(
            n_estimators=hyperparams.get("n_estimators", 100),
            learning_rate=hyperparams.get("learning_rate", 0.1),
            max_depth=hyperparams.get("max_depth", 4),
            scale_pos_weight=hyperparams.get("scale_pos_weight", 5),
            random_state=42,
            eval_metric="logloss",
            verbosity=0,
        )

    raise TrainingError(f"Unknown model: '{model_name}'. Choose from: {SUPPORTED_MODELS}")


class TrainingError(ValueError):
    """Raised when a training run cannot proceed."""
