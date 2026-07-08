"""Loan XAI — FastAPI router.

ML pipeline + explainability: upload→explore→preprocess→train→explain→download
Exposes SHAP global importance and LIME local explanations via REST.

Prefix: /api/loan-xai
"""

import io
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from api.session_store import Session, SessionNotFound, create_session, require_session
from applications.loan_ml.services import data_loader, exploration, metrics, preprocessor
from applications.loan_ml.services.data_loader import DatasetValidationError
from applications.loan_ml.services.preprocessor import PreprocessConfig, PreprocessingError
from applications.loan_ml.services.trainer import SUPPORTED_MODELS, TrainingError, train, get_hyperparameter_defaults
from applications.loan_xai.services.explainer import (
    ExplainerError, build_explanation, explain_instance_lime,
)

router = APIRouter(prefix="/api/loan-xai", tags=["Loan XAI"])


# ─── Schemas ──────────────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    session_id: str
    rows: int
    columns: int
    filename: str

class ExploreResponse(BaseModel):
    rows: int
    columns: int
    missing_values: int
    duplicate_rows: int
    numeric_columns: list[str]
    categorical_columns: list[str]
    detected_target: Optional[str]
    missing_summary: list[dict]

class PreprocessRequest(BaseModel):
    target_column: str
    numeric_impute_strategy: str = "median"
    categorical_impute_strategy: str = "most_frequent"
    scaling_strategy: str = "standard"
    encoding_strategy: str = "ordinal"
    test_size: float = 0.2
    random_state: int = 42
    drop_columns: list[str] = []

class PreprocessResponse(BaseModel):
    train_rows: int
    test_rows: int
    feature_count: int
    feature_names: list[str]
    class_labels: list[str]

class TrainRequest(BaseModel):
    model_name: str
    hyperparams: dict[str, Any] = {}

class TrainResponse(BaseModel):
    model_name: str
    train_accuracy: float
    test_accuracy: float
    training_time_seconds: float
    hyperparams: dict[str, Any]

class ExplainRequest(BaseModel):
    instance_index: int = 0
    num_features: int = 10

class SHAPFeature(BaseModel):
    feature: str
    mean_abs_shap: float

class LIMEFeature(BaseModel):
    feature: str
    weight: float

class ExplainResponse(BaseModel):
    explainer_type: str
    model_name: str
    shap_base_value: float
    shap_feature_importance: list[SHAPFeature]
    lime_explanation: list[LIMEFeature]
    predicted_class: str

class EvaluateResponse(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: Optional[float]
    confusion_matrix: list[list[int]]
    class_labels: list[str]
    classification_report: dict

class PredictRequest(BaseModel):
    features: dict[str, Any]

class PredictResponse(BaseModel):
    prediction: str
    probabilities: Optional[dict[str, float]]


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/models")
def list_models():
    return {
        "supported_models": SUPPORTED_MODELS,
        "hyperparameter_defaults": {m: get_hyperparameter_defaults(m) for m in SUPPORTED_MODELS},
    }


@router.post("/upload", response_model=UploadResponse)
async def upload_dataset(file: UploadFile = File(...)):
    content = await file.read()
    try:
        dataset = data_loader.load_csv(file.filename or "upload.csv", content)
    except DatasetValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    sid = create_session()
    session = require_session(sid)
    session.dataframe = dataset.dataframe
    return {"session_id": sid, "rows": dataset.dataframe.shape[0],
            "columns": dataset.dataframe.shape[1], "filename": dataset.filename}


@router.get("/{session_id}/explore", response_model=ExploreResponse)
def explore_dataset(session_id: str):
    session = _get_session(session_id)
    df = _require_dataframe(session)
    profile = exploration.profile_dataset(df)
    missing_df = exploration.missing_value_summary(df)
    return {
        "rows": profile.rows, "columns": profile.columns,
        "missing_values": profile.missing_values, "duplicate_rows": profile.duplicate_rows,
        "numeric_columns": list(profile.numeric_columns),
        "categorical_columns": list(profile.categorical_columns),
        "detected_target": exploration.detect_target_column(df),
        "missing_summary": missing_df.to_dict(orient="records"),
    }


@router.post("/{session_id}/preprocess", response_model=PreprocessResponse)
def preprocess_dataset(session_id: str, req: PreprocessRequest):
    session = _get_session(session_id)
    df = _require_dataframe(session)
    config = PreprocessConfig(
        target_column=req.target_column,
        numeric_impute_strategy=req.numeric_impute_strategy,
        categorical_impute_strategy=req.categorical_impute_strategy,
        scaling_strategy=req.scaling_strategy,
        encoding_strategy=req.encoding_strategy,
        test_size=req.test_size, random_state=req.random_state,
        drop_columns=tuple(req.drop_columns),
    )
    try:
        result = preprocessor.preprocess(df, config)
    except PreprocessingError as e:
        raise HTTPException(status_code=422, detail=str(e))
    drop_set = set(req.drop_columns) | {req.target_column}
    session.original_features = [c for c in df.columns if c not in drop_set]
    session.preprocess_result = result
    return {
        "train_rows": result.X_train.shape[0], "test_rows": result.X_test.shape[0],
        "feature_count": len(result.feature_names), "feature_names": result.feature_names,
        "class_labels": [str(c) for c in result.class_labels],
    }


@router.post("/{session_id}/train", response_model=TrainResponse)
def train_model(session_id: str, req: TrainRequest):
    session = _get_session(session_id)
    if session.preprocess_result is None:
        raise HTTPException(status_code=400, detail="Run /preprocess first.")
    pr = session.preprocess_result
    hyperparams = req.hyperparams or get_hyperparameter_defaults(req.model_name)
    try:
        result = train(pr.X_train, pr.y_train, pr.X_test, pr.y_test, req.model_name, hyperparams)
    except (TrainingError, ValueError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    session.train_result = result
    session.eval_result = metrics.evaluate(result.model, pr.X_test, pr.y_test)
    return {"model_name": result.model_name, "train_accuracy": result.train_accuracy,
            "test_accuracy": result.test_accuracy, "training_time_seconds": result.training_time_seconds,
            "hyperparams": result.hyperparams}


@router.post("/{session_id}/explain", response_model=ExplainResponse)
def explain(session_id: str, req: ExplainRequest):
    """
    Build SHAP global importance and LIME local explanation for a test instance.
    Tree-based models (Random Forest, XGBoost) are fastest — use TreeExplainer.
    """
    session = _get_session(session_id)
    if session.train_result is None or session.preprocess_result is None:
        raise HTTPException(status_code=400, detail="Run /preprocess and /train first.")
    pr = session.preprocess_result
    tr = session.train_result
    class_names = [str(c) for c in pr.class_labels]
    try:
        explain_result = build_explanation(
            tr.model, pr.X_train, pr.X_test, class_names, tr.model_name,
        )
        session.explain_result = explain_result
        lime_pairs = explain_instance_lime(explain_result, tr.model, req.instance_index, req.num_features)
    except ExplainerError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation failed: {e}")

    mean_abs_shap = np.abs(explain_result.shap_values).mean(axis=0)
    shap_importance = sorted(
        [{"feature": n, "mean_abs_shap": round(float(v), 6)}
         for n, v in zip(explain_result.feature_names, mean_abs_shap)],
        key=lambda x: x["mean_abs_shap"], reverse=True,
    )
    lime_exp = [{"feature": feat, "weight": round(float(w), 6)} for feat, w in lime_pairs]
    instance_row = pr.X_test.iloc[[req.instance_index]]
    predicted_class = str(tr.model.predict(instance_row)[0])

    return {
        "explainer_type": explain_result.explainer_type,
        "model_name": explain_result.model_name,
        "shap_base_value": round(explain_result.shap_base_value, 6),
        "shap_feature_importance": shap_importance,
        "lime_explanation": lime_exp,
        "predicted_class": predicted_class,
    }


@router.get("/{session_id}/evaluate", response_model=EvaluateResponse)
def evaluate_model(session_id: str):
    session = _get_session(session_id)
    if session.eval_result is None:
        raise HTTPException(status_code=400, detail="Run /train first.")
    er = session.eval_result
    return {
        "accuracy": er.accuracy, "precision": er.precision,
        "recall": er.recall, "f1": er.f1,
        "roc_auc": float(er.roc_auc) if er.roc_auc is not None else None,
        "confusion_matrix": er.confusion_matrix.tolist(),
        "class_labels": [str(c) for c in er.class_labels],
        "classification_report": er.classification_report,
    }


@router.post("/{session_id}/predict", response_model=PredictResponse)
def predict(session_id: str, req: PredictRequest):
    session = _get_session(session_id)
    if session.train_result is None or session.preprocess_result is None:
        raise HTTPException(status_code=400, detail="Run /preprocess and /train first.")
    original_features = session.original_features or []
    missing = [f for f in original_features if f not in req.features]
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing features: {missing}")
    input_df = pd.DataFrame({f: [req.features[f]] for f in original_features})
    pipeline = session.preprocess_result.pipeline
    model = session.train_result.model
    feature_names = session.preprocess_result.feature_names
    try:
        transformed = pipeline.transform(input_df)
        transformed_df = pd.DataFrame(transformed, columns=feature_names)
        prediction = model.predict(transformed_df)[0]
        proba = None
        if hasattr(model, "predict_proba"):
            proba_arr = model.predict_proba(transformed_df)[0]
            class_labels = [str(c) for c in session.preprocess_result.class_labels]
            proba = {cls: round(float(p), 4) for cls, p in zip(class_labels, proba_arr)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
    return {"prediction": str(prediction), "probabilities": proba}


@router.get("/{session_id}/download/bundle")
def download_bundle(session_id: str):
    session = _get_session(session_id)
    if session.train_result is None or session.preprocess_result is None:
        raise HTTPException(status_code=400, detail="Run /preprocess and /train first.")
    bundle = {
        "model": session.train_result.model,
        "pipeline": session.preprocess_result.pipeline,
        "feature_names": session.preprocess_result.feature_names,
        "original_features": session.original_features,
        "class_labels": session.preprocess_result.class_labels,
        "model_name": session.train_result.model_name,
    }
    buf = io.BytesIO()
    joblib.dump(bundle, buf)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/octet-stream",
                             headers={"Content-Disposition": "attachment; filename=loan_xai_bundle.pkl"})


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_session(session_id: str) -> Session:
    try:
        return require_session(session_id)
    except SessionNotFound:
        raise HTTPException(status_code=404,
                            detail=f"Session '{session_id}' not found. Call POST /api/loan-xai/upload first.")

def _require_dataframe(session: Session) -> pd.DataFrame:
    if session.dataframe is None:
        raise HTTPException(status_code=400, detail="No dataset loaded. Call /upload first.")
    return session.dataframe
