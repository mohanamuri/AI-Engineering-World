"""Evaluation metrics service for the loan eligibility ML pipeline.

Computes the full suite of classification metrics expected in production
ML systems and ML interviews: accuracy, precision, recall, F1, ROC AUC,
confusion matrix, and per-class classification report.

Interview note — Choosing the right metric
-------------------------------------------
Accuracy is misleading on imbalanced datasets. Example: if 90% of loans
are approved, a model that always predicts "approved" gets 90% accuracy
while being completely useless.

Use case                      → Preferred metric
─────────────────────────────────────────────────
Imbalanced classes            → F1, ROC AUC
Cost of false negatives high  → Recall (e.g., fraud, disease detection)
Cost of false positives high  → Precision (e.g., spam filtering)
Balanced classes              → Accuracy is fine as a headline metric

For loan eligibility: missing a creditworthy applicant (false negative)
costs the lender revenue; approving a bad applicant (false positive) risks
default. The right trade-off depends on the business — this is why we
expose the full confusion matrix and ROC curve, not just accuracy.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class EvaluationResult:
    """Complete evaluation output for one trained model.

    Attributes
    ----------
    accuracy : float
        Overall fraction of correct predictions.
    precision : float
        Weighted average precision across classes.
    recall : float
        Weighted average recall across classes.
    f1 : float
        Weighted average F1 score.
    roc_auc : float | None
        ROC AUC score. None when predict_proba is unavailable or
        multi-class with >2 classes and no probability support.
    confusion_matrix : np.ndarray, shape (n_classes, n_classes)
        Row = actual class, column = predicted class.
    class_labels : list
        Ordered class labels matching confusion matrix rows/columns.
    fpr : np.ndarray | None
        False positive rates for ROC curve (binary only).
    tpr : np.ndarray | None
        True positive rates for ROC curve (binary only).
    classification_report : dict
        Per-class precision, recall, F1, and support.
    model_name : str
        Name of the model that produced these results.
    """

    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float | None
    confusion_matrix: np.ndarray
    class_labels: list
    fpr: np.ndarray | None
    tpr: np.ndarray | None
    classification_report: dict
    model_name: str


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def evaluate(model, X_test: pd.DataFrame, y_test: pd.Series) -> EvaluationResult:
    """Compute the full evaluation suite for a fitted classifier.

    Parameters
    ----------
    model : fitted sklearn estimator
        Must implement predict(). predict_proba() is used when available.
    X_test : pd.DataFrame
        Preprocessed test features.
    y_test : pd.Series
        True labels for the test split.

    Returns
    -------
    EvaluationResult with all classification metrics.
    """
    y_pred = model.predict(X_test)
    class_labels = sorted(y_test.unique().tolist())
    is_binary = len(class_labels) == 2

    accuracy = float(accuracy_score(y_test, y_pred))
    precision = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
    recall = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
    f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

    cm = confusion_matrix(y_test, y_pred, labels=class_labels)

    roc_auc, fpr, tpr = _compute_roc(model, X_test, y_test, class_labels, is_binary)

    report = classification_report(
        y_test, y_pred,
        labels=class_labels,
        output_dict=True,
        zero_division=0,
    )

    return EvaluationResult(
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1=f1,
        roc_auc=roc_auc,
        confusion_matrix=cm,
        class_labels=class_labels,
        fpr=fpr,
        tpr=tpr,
        classification_report=report,
        model_name=getattr(model, "__class__", type(model)).__name__,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _compute_roc(
    model,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    class_labels: list,
    is_binary: bool,
) -> tuple[float | None, np.ndarray | None, np.ndarray | None]:
    """Return (roc_auc, fpr, tpr) — all None if probabilities unavailable."""
    if not hasattr(model, "predict_proba"):
        return None, None, None

    try:
        proba = model.predict_proba(X_test)
    except Exception:
        return None, None, None

    try:
        if is_binary:
            positive_proba = proba[:, 1]
            roc_auc = float(roc_auc_score(y_test, positive_proba))
            fpr, tpr, _ = roc_curve(y_test, positive_proba, pos_label=class_labels[1])
            return roc_auc, np.asarray(fpr), np.asarray(tpr)
        else:
            roc_auc = float(
                roc_auc_score(y_test, proba, multi_class="ovr", average="weighted")
            )
            return roc_auc, None, None
    except Exception:
        return None, None, None
