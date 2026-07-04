"""Neural-network training service for the HR Analytics DL pipeline.

Uses sklearn's MLPClassifier with class_weight simulation via sample_weight
to handle attrition class imbalance. MLPClassifier doesn't natively support
class_weight, so we compute sample weights manually from class frequencies.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.neural_network import MLPClassifier
from sklearn.utils.class_weight import compute_sample_weight


ARCHITECTURES = {
    "Shallow (128)": (128,),
    "Medium (128 → 64)": (128, 64),
    "Deep (256 → 128 → 64)": (256, 128, 64),
    "Wide (512 → 256)": (512, 256),
}


@dataclass
class DLTrainResult:
    model_name: str
    model: Any
    feature_names: list[str]
    train_accuracy: float
    test_accuracy: float
    training_time_seconds: float
    hyperparams: dict[str, Any]
    loss_curve: list[float] = field(default_factory=list)
    n_iter: int = 0


def train(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    architecture_name: str,
    activation: str,
    solver: str,
    learning_rate_init: float,
    max_iter: int,
    alpha: float,
) -> DLTrainResult:
    if architecture_name not in ARCHITECTURES:
        raise DLTrainingError(f"Unknown architecture: '{architecture_name}'.")

    hidden_layer_sizes = ARCHITECTURES[architecture_name]
    hyperparams = {
        "architecture": architecture_name,
        "hidden_layer_sizes": hidden_layer_sizes,
        "activation": activation,
        "solver": solver,
        "learning_rate_init": learning_rate_init,
        "max_iter": max_iter,
        "alpha": alpha,
    }

    estimator = MLPClassifier(
        hidden_layer_sizes=hidden_layer_sizes,
        activation=activation,
        solver=solver,
        learning_rate_init=learning_rate_init,
        max_iter=max_iter,
        alpha=alpha,
        random_state=42,
        early_stopping=False,
    )

    # MLPClassifier doesn't support class_weight — use sample_weight instead
    sample_weights = compute_sample_weight("balanced", y_train)

    t0 = time.perf_counter()
    try:
        estimator.fit(X_train, y_train, sample_weight=sample_weights)
    except Exception as exc:
        raise DLTrainingError(f"MLPClassifier.fit() failed: {exc}") from exc
    elapsed = time.perf_counter() - t0

    train_accuracy = float(accuracy_score(y_train, estimator.predict(X_train)))
    test_accuracy = float(accuracy_score(y_test, estimator.predict(X_test)))

    loss_curve = (
        [float(v) for v in estimator.loss_curve_]
        if hasattr(estimator, "loss_curve_") and estimator.loss_curve_ else []
    )
    n_iter = int(estimator.n_iter_) if hasattr(estimator, "n_iter_") else max_iter

    return DLTrainResult(
        model_name=f"MLP · {architecture_name}",
        model=estimator,
        feature_names=list(X_train.columns),
        train_accuracy=train_accuracy,
        test_accuracy=test_accuracy,
        training_time_seconds=round(elapsed, 4),
        hyperparams=hyperparams,
        loss_curve=loss_curve,
        n_iter=n_iter,
    )


class DLTrainingError(ValueError):
    pass
