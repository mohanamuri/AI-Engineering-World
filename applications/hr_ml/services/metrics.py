"""Evaluation metrics service for the HR Analytics ML pipeline.

Computes accuracy, precision, recall, F1, ROC AUC, confusion matrix,
and per-class classification report.

Interview note — Why F1 matters more than accuracy for attrition
-----------------------------------------------------------------
HR attrition datasets are typically imbalanced. A naive model that
always predicts No gets high accuracy but catches zero flight risks.
F1 score for the minority class (Yes) is the right headline metric here.
ROC AUC captures model discrimination across all thresholds.
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


@dataclass
class EvaluationResult:
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


def evaluate(model, X_test: pd.DataFrame, y_test: pd.Series) -> EvaluationResult:
    y_pred = model.predict(X_test)
    class_labels = sorted(y_test.unique().tolist())
    is_binary = len(class_labels) == 2

    accuracy = float(accuracy_score(y_test, y_pred))
    precision = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
    recall = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
    f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

    cm = confusion_matrix(y_test, y_pred, labels=class_labels)
    roc_auc, fpr, tpr = _compute_roc(model, X_test, y_test, class_labels, is_binary)
    report = classification_report(y_test, y_pred, labels=class_labels, output_dict=True, zero_division=0)

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


def _compute_roc(model, X_test, y_test, class_labels, is_binary):
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
            roc_auc = float(roc_auc_score(y_test, proba, multi_class="ovr", average="weighted"))
            return roc_auc, None, None
    except Exception:
        return None, None, None
