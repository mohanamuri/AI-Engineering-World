"""Model training service for the loan eligibility ML pipeline.

Supports four classifiers that cover the full spectrum taught in ML interviews:
  - Logistic Regression  : linear baseline, interpretable coefficients
  - Decision Tree        : non-linear, fully interpretable tree structure
  - Random Forest        : bagging ensemble, robust, feature importances
  - XGBoost              : boosting ensemble, state-of-the-art on tabular data

Interview note — Bias-Variance Tradeoff
-----------------------------------------
Each model sits at a different point on the bias-variance spectrum:

  High bias  ◄────────────────────────────► High variance
  Logistic       Decision Tree      Random Forest / XGBoost
  Regression     (deep, unpruned)   (with tuned depth)

A single Decision Tree overfits easily (high variance).
Random Forest corrects this by averaging many trees trained on bootstrap
samples (bagging), reducing variance without increasing bias much.
XGBoost instead builds trees sequentially, each correcting the residual
errors of the previous one (boosting), which reduces bias.

Interview note — Why wrap sklearn estimators?
----------------------------------------------
We wrap them in a dataclass so:
  1. The page layer never imports sklearn directly (separation of concerns)
  2. Training metadata (time, scores) travels with the model object
  3. The result is a single serialisable unit (model + metadata together)
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


# ---------------------------------------------------------------------------
# Supported model catalogue
# ---------------------------------------------------------------------------

SUPPORTED_MODELS = [
    "Logistic Regression",
    "Decision Tree",
    "Random Forest",
    "XGBoost",
]


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class TrainResult:
    """Everything the evaluate and download pages need from a training run.

    Attributes
    ----------
    model_name : str
        Human-readable name from SUPPORTED_MODELS.
    model : sklearn estimator (fitted)
        The trained classifier. Serialisable with joblib.
    feature_names : list[str]
        Column names of X_train — needed for feature importance charts.
    train_accuracy : float
        Accuracy on the training set (check for overfitting).
    test_accuracy : float
        Accuracy on the held-out test set (generalisation estimate).
    training_time_seconds : float
        Wall-clock time for the fit() call.
    hyperparams : dict
        The hyperparameters used — stored for the metrics JSON export.
    """

    model_name: str
    model: Any
    feature_names: list[str]
    train_accuracy: float
    test_accuracy: float
    training_time_seconds: float
    hyperparams: dict[str, Any]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def train(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    model_name: str,
    hyperparams: dict[str, Any],
) -> TrainResult:
    """Fit a classifier and return a TrainResult.

    Parameters
    ----------
    X_train, y_train : training split from PreprocessResult
    X_test, y_test   : test split from PreprocessResult
    model_name       : one of SUPPORTED_MODELS
    hyperparams      : dict of hyperparameter name → value

    Returns
    -------
    TrainResult with fitted model, scores, and metadata.

    Raises
    ------
    TrainingError
        If model_name is unrecognised or XGBoost is requested but not installed.
    """
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
    """Return sensible default hyperparameters for a given model.

    Used by the train page to pre-populate UI controls.
    """
    defaults: dict[str, dict[str, Any]] = {
        "Logistic Regression": {
            "C": 1.0,
            "max_iter": 1000,
            "solver": "lbfgs",
        },
        "Decision Tree": {
            "max_depth": 5,
            "min_samples_split": 10,
            "min_samples_leaf": 5,
        },
        "Random Forest": {
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 5,
        },
        "XGBoost": {
            "n_estimators": 100,
            "learning_rate": 0.1,
            "max_depth": 4,
        },
    }
    if model_name not in defaults:
        raise TrainingError(f"Unknown model: '{model_name}'. Choose from: {SUPPORTED_MODELS}")
    return defaults[model_name]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_estimator(model_name: str, hyperparams: dict[str, Any]) -> Any:
    if model_name == "Logistic Regression":
        return LogisticRegression(
            C=hyperparams.get("C", 1.0),
            max_iter=hyperparams.get("max_iter", 1000),
            solver=hyperparams.get("solver", "lbfgs"),
            random_state=42,
        )

    if model_name == "Decision Tree":
        return DecisionTreeClassifier(
            max_depth=hyperparams.get("max_depth", 5),
            min_samples_split=hyperparams.get("min_samples_split", 10),
            min_samples_leaf=hyperparams.get("min_samples_leaf", 5),
            random_state=42,
        )

    if model_name == "Random Forest":
        return RandomForestClassifier(
            n_estimators=hyperparams.get("n_estimators", 100),
            max_depth=hyperparams.get("max_depth", 10),
            min_samples_split=hyperparams.get("min_samples_split", 5),
            random_state=42,
            n_jobs=-1,
        )

    if model_name == "XGBoost":
        if not _XGBOOST_AVAILABLE:
            raise TrainingError(
                "XGBoost is not installed. Run: pip install xgboost>=2.0"
            )
        return XGBClassifier(
            n_estimators=hyperparams.get("n_estimators", 100),
            learning_rate=hyperparams.get("learning_rate", 0.1),
            max_depth=hyperparams.get("max_depth", 4),
            random_state=42,
            eval_metric="logloss",
            verbosity=0,
        )

    raise TrainingError(
        f"Unknown model: '{model_name}'. Choose from: {SUPPORTED_MODELS}"
    )


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class TrainingError(ValueError):
    """Raised when a training run cannot proceed."""
