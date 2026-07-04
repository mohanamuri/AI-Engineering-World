"""CSV loading for HR Deep Learning — same logic as hr_ml, different session keys."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO, StringIO
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError


MAX_UPLOAD_BYTES = 10 * 1024 * 1024
DATAFRAME_SESSION_KEY = "hr_dl_dataframe"
DATASET_METADATA_SESSION_KEY = "hr_dl_dataset_metadata"
DATASET_FINGERPRINT_SESSION_KEY = "hr_dl_dataset_fingerprint"


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
    _validate_file(filename, content)
    headers = _read_headers(content)
    try:
        df = pd.read_csv(BytesIO(content), encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DatasetValidationError("File must use UTF-8 encoding.") from exc
    except EmptyDataError as exc:
        raise DatasetValidationError("CSV file is empty.") from exc
    except ParserError as exc:
        raise DatasetValidationError("Invalid CSV structure.") from exc
    except (OSError, ValueError) as exc:
        raise DatasetValidationError("Could not read CSV.") from exc
    _validate_dataframe(df, headers)
    return LoadedDataset(df, Path(filename).name, len(content), sha256(content).hexdigest())


def _validate_file(filename, content):
    if Path(filename).suffix.lower() != ".csv":
        raise DatasetValidationError("Only .csv files are supported.")
    if not content:
        raise DatasetValidationError("File is empty.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise DatasetValidationError(f"File exceeds {MAX_UPLOAD_BYTES // (1024*1024)} MB limit.")


def _read_headers(content):
    try:
        text = content.decode("utf-8-sig")
        return [h.strip() for h in next(csv.reader(StringIO(text), strict=True))]
    except (StopIteration, csv.Error, UnicodeDecodeError) as exc:
        raise DatasetValidationError("Could not read CSV headers.") from exc


def _validate_dataframe(df, headers):
    if df.empty or len(headers) < 2:
        raise DatasetValidationError("CSV must have headers and at least one data row.")
    if df.dropna(how="all").empty:
        raise DatasetValidationError("CSV has no populated rows.")
    df.columns = headers
