"""Loan DL — FastAPI router.

Neural network (MLP) pipeline: upload→explore→preprocess→train→evaluate→predict→download
Reuses loan_ml services for everything except training.

Prefix: /api/loan-dl
"""

import io
from typing import Any, Optional

import joblib
import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from api.session_store import Session, SessionNotFound, create_session, require_session
from applications.loan_ml.services import data_loader, exploration, metrics, preprocessor
from applications.loan_ml.services.data_loader import DatasetValidationError
from applications.loan_ml.services.preprocessor import PreprocessConfig, PreprocessingError
from applications.loan_dl.services.trainer import (
    ARCHITECTURES, DLTrainResult, DLTrainingError, train,
)

router = APIRouter(prefix="/api/loan-dl", tags=["Loan DL"])


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
    architecture_name: str = "Medium (128 → 64)"
    activation: str = "relu"
    solver: str = "adam"
    learning_rate_init: float = 0.001
    max_iter: int = 200
    alpha: float = 0.0001

class TrainResponse(BaseModel):
    model_name: str
    train_accuracy: float
    test_accuracy: float
    training_time_seconds: float
    n_iter: int
    loss_curve: list[float]
    hyperparams: dict[str, Any]

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

class ArchitecturesResponse(BaseModel):
    architectures: list[str]


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/architectures", response_model=ArchitecturesResponse)
def list_architectures():
    """List available MLP architectures."""
    return {"architectures": list(ARCHITECTURES.keys())}


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
    try:
        result = train(
            pr.X_train, pr.y_train, pr.X_test, pr.y_test,
            req.architecture_name, req.activation, req.solver,
            req.learning_rate_init, req.max_iter, req.alpha,
        )
    except (DLTrainingError, ValueError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    session.train_result = result
    session.eval_result = metrics.evaluate(result.model, pr.X_test, pr.y_test)
    return {
        "model_name": result.model_name, "train_accuracy": result.train_accuracy,
        "test_accuracy": result.test_accuracy, "training_time_seconds": result.training_time_seconds,
        "n_iter": result.n_iter, "loss_curve": result.loss_curve,
        "hyperparams": result.hyperparams,
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


@router.get("/{session_id}/download/model")
def download_model(session_id: str):
    session = _get_session(session_id)
    if session.train_result is None:
        raise HTTPException(status_code=400, detail="Run /train first.")
    buf = io.BytesIO()
    joblib.dump(session.train_result.model, buf)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/octet-stream",
                             headers={"Content-Disposition": "attachment; filename=loan_dl_model.pkl"})


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
                             headers={"Content-Disposition": "attachment; filename=loan_dl_bundle.pkl"})


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_session(session_id: str) -> Session:
    try:
        return require_session(session_id)
    except SessionNotFound:
        raise HTTPException(status_code=404,
                            detail=f"Session '{session_id}' not found. Call POST /api/loan-dl/upload first.")

def _require_dataframe(session: Session) -> pd.DataFrame:
    if session.dataframe is None:
        raise HTTPException(status_code=400, detail="No dataset loaded. Call /upload first.")
    return session.dataframe
