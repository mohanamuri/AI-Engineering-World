"""Data loader for hr_xai — same as hr_ml but with xai-namespaced session keys."""

from __future__ import annotations
import csv
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO, StringIO
from pathlib import Path
import pandas as pd
from pandas.errors import EmptyDataError, ParserError

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
DATAFRAME_SESSION_KEY = "hr_xai_dataframe"
DATASET_METADATA_SESSION_KEY = "hr_xai_dataset_metadata"
DATASET_FINGERPRINT_SESSION_KEY = "hr_xai_dataset_fingerprint"


class DatasetValidationError(ValueError):
    pass


@dataclass(frozen=True)
class LoadedDataset:
    dataframe: pd.DataFrame
    filename: str
    size_bytes: int
    fingerprint: str

    @property
    def metadata(self):
        return {"filename": self.filename, "size_bytes": self.size_bytes,
                "rows": len(self.dataframe), "columns": len(self.dataframe.columns)}


def load_csv(filename: str, content: bytes) -> LoadedDataset:
    if Path(filename).suffix.lower() != ".csv":
        raise DatasetValidationError("Only .csv files supported.")
    if not content or len(content) > MAX_UPLOAD_BYTES:
        raise DatasetValidationError("File is empty or too large.")
    try:
        text = content.decode("utf-8-sig")
        headers = [h.strip() for h in next(csv.reader(StringIO(text), strict=True))]
        df = pd.read_csv(BytesIO(content), encoding="utf-8-sig")
    except Exception as exc:
        raise DatasetValidationError(f"Could not read CSV: {exc}") from exc
    if df.empty:
        raise DatasetValidationError("CSV has no data rows.")
    df.columns = headers
    return LoadedDataset(df, Path(filename).name, len(content), sha256(content).hexdigest())
