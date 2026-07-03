"""Explainability service for the loan eligibility XAI pipeline.

Wraps SHAP and LIME to produce model-agnostic explanations for any
sklearn classifier trained in this platform.

Interview notes
---------------
SHAP (SHapley Additive exPlanations)
  Based on cooperative game theory. Each feature's SHAP value measures
  its marginal contribution to the prediction across all possible feature
  coalitions. Guarantees consistency and local accuracy.

  Explainer selection strategy:
    TreeExplainer  — exact, fast for tree-based models (RF, XGBoost, DT)
    LinearExplainer — exact, fast for linear models (Logistic Regression)
    KernelExplainer — model-agnostic via perturbation; slow, use small sample

LIME (Local Interpretable Model-agnostic Explanations)
  Fits a simple linear model in the neighbourhood of a single prediction
  (perturbed samples weighted by proximity). Fast, intuitive, but
  explanation can vary between runs and is not globally consistent.

SHAP vs LIME
  SHAP: globally consistent, theoretically grounded, can be slow for
        non-tree models. Best for: understanding the model overall.
  LIME: fast, locally faithful, easy to explain to stakeholders.
        Best for: explaining one specific decision to an end user.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ExplainResult:
    """Precomputed explanation artifacts passed to the explain page.

    Attributes
    ----------
    shap_values : np.ndarray, shape (n_samples, n_features)
        SHAP values for the positive class (or class 1 in binary).
    shap_base_value : float
        The expected model output (baseline).
    feature_names : list[str]
        Feature names matching columns of X_test.
    X_test_sample : pd.DataFrame
        The sample of X_test used to compute SHAP values.
    class_names : list[str]
        Human-readable class labels.
    model_name : str
        Name of the explained model.
    explainer_type : str
        'tree', 'linear', or 'kernel' — for display purposes.
    """

    shap_values: np.ndarray
    shap_base_value: float
    feature_names: list[str]
    X_test_sample: pd.DataFrame
    class_names: list[str]
    model_name: str
    explainer_type: str
    lime_explainer: Any = field(default=None, repr=False)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_explanation(
    model: Any,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    class_names: list[str],
    model_name: str,
    max_shap_samples: int = 200,
) -> ExplainResult:
    """Compute SHAP values and build a LIME explainer for the test set.

    Parameters
    ----------
    model            : fitted sklearn estimator
    X_train          : training features (used to background SHAP / LIME)
    X_test           : test features to explain
    class_names      : list of string class labels
    model_name       : human-readable model name for display
    max_shap_samples : cap test rows for global SHAP (speed vs coverage)

    Returns
    -------
    ExplainResult with SHAP values, base value, and LIME explainer.
    """
    import shap
    from lime import lime_tabular

    # Sample X_test if large (KernelExplainer is slow)
    X_sample = X_test.iloc[:max_shap_samples] if len(X_test) > max_shap_samples else X_test

    explainer, explainer_type = _build_shap_explainer(model, X_train, X_sample)
    shap_values, base_value = _extract_shap_values(explainer, X_sample, explainer_type)

    lime_exp = lime_tabular.LimeTabularExplainer(
        training_data=X_train.values,
        feature_names=list(X_train.columns),
        class_names=[str(c) for c in class_names],
        mode="classification",
        random_state=42,
    )

    return ExplainResult(
        shap_values=shap_values,
        shap_base_value=float(base_value),
        feature_names=list(X_sample.columns),
        X_test_sample=X_sample.reset_index(drop=True),
        class_names=[str(c) for c in class_names],
        model_name=model_name,
        explainer_type=explainer_type,
        lime_explainer=lime_exp,
    )


def explain_instance_lime(
    result: ExplainResult,
    model: Any,
    row_index: int,
    num_features: int = 10,
) -> list[tuple[str, float]]:
    """Return LIME feature contributions for a single test instance.

    Returns
    -------
    List of (feature_label, weight) tuples, sorted by |weight| descending.
    """
    instance = result.X_test_sample.iloc[row_index].values
    explanation = result.lime_explainer.explain_instance(
        instance,
        model.predict_proba,
        num_features=num_features,
        top_labels=1,
    )
    label = explanation.available_labels()[0]
    return sorted(explanation.as_list(label=label), key=lambda x: abs(x[1]), reverse=True)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_shap_explainer(model: Any, X_train: pd.DataFrame, X_sample: pd.DataFrame):
    """Select and build the most efficient SHAP explainer for the model."""
    import shap

    # Tree-based models: exact, fast
    if hasattr(model, "feature_importances_") and not _is_logistic(model):
        try:
            explainer = shap.TreeExplainer(model)
            return explainer, "tree"
        except Exception:
            pass

    # Linear models: exact, fast
    if _is_logistic(model):
        try:
            explainer = shap.LinearExplainer(model, X_train)
            return explainer, "linear"
        except Exception:
            pass

    # Fallback: KernelExplainer (slow — sample background)
    background = shap.sample(X_train, min(50, len(X_train)))
    explainer = shap.KernelExplainer(model.predict_proba, background)
    return explainer, "kernel"


def _is_logistic(model: Any) -> bool:
    return type(model).__name__ == "LogisticRegression"


def _extract_shap_values(
    explainer: Any,
    X_sample: pd.DataFrame,
    explainer_type: str,
) -> tuple[np.ndarray, float]:
    """Return (shap_values for positive class, base_value) as numpy arrays."""
    import shap

    raw = explainer(X_sample) if explainer_type in ("tree", "linear") else explainer.shap_values(X_sample)

    # shap.Explanation object (new API)
    if hasattr(raw, "values"):
        values = raw.values
        base = raw.base_values
        # Binary classification: values shape may be (n, f) or (n, f, 2)
        if values.ndim == 3:
            values = values[:, :, 1]
            base = base[:, 1] if base.ndim > 1 else base
        base_value = float(np.mean(base))
        return values, base_value

    # Old API: list of arrays per class
    if isinstance(raw, list):
        values = np.array(raw[1]) if len(raw) > 1 else np.array(raw[0])
        base_value = float(np.mean(explainer.expected_value[1])) if isinstance(explainer.expected_value, (list, np.ndarray)) else float(explainer.expected_value)
        return values, base_value

    # Single array (binary)
    base_value = float(np.mean(explainer.expected_value)) if hasattr(explainer, "expected_value") else 0.0
    return np.array(raw), base_value


class ExplainerError(ValueError):
    """Raised when explanation computation fails."""
