"""Neural-network training service for the loan eligibility DL pipeline.

Uses sklearn's MLPClassifier (Multi-Layer Perceptron) — a fully-connected
feed-forward neural network — to demonstrate the deep learning tier.

Interview notes
---------------
Why MLPClassifier for the DL tier?
  • It is pure sklearn — no extra dependency, identical interface to other
    classifiers in this project (fit / predict / predict_proba).
  • It exposes `loss_curve_` after fitting, letting us plot training loss
    per epoch — the signature DL artifact absent from all classical models.
  • For production DL you would use PyTorch or TensorFlow; MLPClassifier
    is the right pedagogical step between "classical ML" and "deep learning".

Architecture design
  hidden_layer_sizes=(128, 64) means:
    Input → Dense(128, ReLU) → Dense(64, ReLU) → Softmax(n_classes)

  Batch norm and dropout are not supported by MLPClassifier; those require
  a framework like PyTorch.

Solver choice
  adam  — adaptive learning rate, good default for most datasets
  sgd   — stochastic gradient descent; requires careful lr tuning
  lbfgs — L-BFGS quasi-Newton; efficient for small datasets (< 10k rows)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.neural_network import MLPClassifier


# ---------------------------------------------------------------------------
# Architecture catalogue
# ---------------------------------------------------------------------------

ARCHITECTURES = {
    "Shallow (128)": (128,),
    "Medium (128 → 64)": (128, 64),
    "Deep (256 → 128 → 64)": (256, 128, 64),
    "Wide (512 → 256)": (512, 256),
}


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class DLTrainResult:
    """Everything the evaluate and download pages need from a DL training run.

    Attributes
    ----------
    model_name : str
        Human-readable label (e.g. "MLP · Medium (128 → 64)").
    model : MLPClassifier (fitted)
        Serialisable with joblib.
    feature_names : list[str]
        Column names of X_train — for feature importance / download.
    train_accuracy : float
        Accuracy on the training set.
    test_accuracy : float
        Accuracy on the held-out test set.
    training_time_seconds : float
        Wall-clock time for the fit() call.
    hyperparams : dict
        Hyperparameters used — stored for the metrics JSON export.
    loss_curve : list[float]
        Training loss per epoch (from MLPClassifier.loss_curve_).
        Empty list if the solver did not record a loss curve (e.g. lbfgs).
    n_iter : int
        Number of epochs actually run.
    """

    model_name: str
    model: Any
    feature_names: list[str]
    train_accuracy: float
    test_accuracy: float
    training_time_seconds: float
    hyperparams: dict[str, Any]
    loss_curve: list[float] = field(default_factory=list)
    n_iter: int = 0


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

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
    """Fit an MLPClassifier and return a DLTrainResult.

    Parameters
    ----------
    X_train, y_train : training split from PreprocessResult
    X_test, y_test   : test split from PreprocessResult
    architecture_name : key from ARCHITECTURES
    activation        : 'relu', 'tanh', or 'logistic'
    solver            : 'adam', 'sgd', or 'lbfgs'
    learning_rate_init: initial step size
    max_iter          : maximum number of epochs
    alpha             : L2 regularisation coefficient

    Returns
    -------
    DLTrainResult with fitted model, loss curve, and metrics.

    Raises
    ------
    DLTrainingError
        If architecture_name is unrecognised or training fails.
    """
    if architecture_name not in ARCHITECTURES:
        raise DLTrainingError(
            f"Unknown architecture: '{architecture_name}'. "
            f"Choose from: {list(ARCHITECTURES)}"
        )

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

    t0 = time.perf_counter()
    try:
        estimator.fit(X_train, y_train)
    except Exception as exc:
        raise DLTrainingError(f"MLPClassifier.fit() failed: {exc}") from exc
    elapsed = time.perf_counter() - t0

    train_accuracy = float(accuracy_score(y_train, estimator.predict(X_train)))
    test_accuracy = float(accuracy_score(y_test, estimator.predict(X_test)))

    loss_curve: list[float] = (
        [float(v) for v in estimator.loss_curve_]
        if hasattr(estimator, "loss_curve_") and estimator.loss_curve_
        else []
    )
    n_iter: int = int(estimator.n_iter_) if hasattr(estimator, "n_iter_") else max_iter

    model_label = f"MLP · {architecture_name}"

    return DLTrainResult(
        model_name=model_label,
        model=estimator,
        feature_names=list(X_train.columns),
        train_accuracy=train_accuracy,
        test_accuracy=test_accuracy,
        training_time_seconds=round(elapsed, 4),
        hyperparams=hyperparams,
        loss_curve=loss_curve,
        n_iter=n_iter,
    )


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class DLTrainingError(ValueError):
    """Raised when a deep-learning training run cannot proceed."""
