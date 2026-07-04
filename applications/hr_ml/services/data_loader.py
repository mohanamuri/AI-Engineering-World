"""CSV loading and validation for the HR Analytics ML workflow."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO, StringIO
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError


MAX_UPLOAD_BYTES = 10 * 1024 * 1024
DATAFRAME_SESSION_KEY = "hr_ml_dataframe"
DATASET_METADATA_SESSION_KEY = "hr_ml_dataset_metadata"
DATASET_FINGERPRINT_SESSION_KEY = "hr_ml_dataset_fingerprint"


class DatasetValidationError(ValueError):
    """Raised when an uploaded file is not a usable CSV dataset."""


@dataclass(frozen=True)
class LoadedDataset:
    """Validated dataset and the metadata needed by the UI."""

    dataframe: pd.DataFrame
    filename: str
    size_bytes: int
    fingerprint: str

    @property
    def metadata(self) -> dict[str, object]:
        return {
            "filename": self.filename,
            "size_bytes": self.size_bytes,
            "rows": len(self.dataframe),
            "columns": len(self.dataframe.columns),
        }


def load_csv(filename: str, content: bytes) -> LoadedDataset:
    """Parse and validate CSV bytes without depending on Streamlit."""
    _validate_file(filename, content)
    headers = _read_headers(content)

    try:
        dataframe = pd.read_csv(BytesIO(content), encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DatasetValidationError(
            "The file must use UTF-8 text encoding."
        ) from exc
    except EmptyDataError as exc:
        raise DatasetValidationError("The CSV file is empty.") from exc
    except ParserError as exc:
        raise DatasetValidationError(
            "The CSV structure is invalid. Check delimiters and quoted values."
        ) from exc
    except (OSError, ValueError) as exc:
        raise DatasetValidationError("The CSV file could not be read.") from exc

    _validate_dataframe(dataframe, headers)

    return LoadedDataset(
        dataframe=dataframe,
        filename=Path(filename).name,
        size_bytes=len(content),
        fingerprint=sha256(content).hexdigest(),
    )


def _validate_file(filename: str, content: bytes) -> None:
    if Path(filename).suffix.lower() != ".csv":
        raise DatasetValidationError("Only files with a .csv extension are supported.")

    if not content:
        raise DatasetValidationError("The uploaded file is empty.")

    if len(content) > MAX_UPLOAD_BYTES:
        limit_mb = MAX_UPLOAD_BYTES // (1024 * 1024)
        raise DatasetValidationError(
            f"The CSV exceeds the {limit_mb} MB upload limit."
        )


def _read_headers(content: bytes) -> list[str]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DatasetValidationError(
            "The file must use UTF-8 text encoding."
        ) from exc

    try:
        headers = next(csv.reader(StringIO(text), strict=True))
    except StopIteration as exc:
        raise DatasetValidationError("The CSV file is empty.") from exc
    except csv.Error as exc:
        raise DatasetValidationError(
            "The CSV structure is invalid. Check delimiters and quoted values."
        ) from exc

    return [header.strip() for header in headers]


def _validate_dataframe(dataframe: pd.DataFrame, headers: list[str]) -> None:
    if dataframe.empty:
        raise DatasetValidationError(
            "The CSV must contain a header row and at least one data row."
        )

    if len(headers) < 2:
        raise DatasetValidationError(
            "The CSV must contain at least two columns."
        )

    if any(not header for header in headers):
        raise DatasetValidationError(
            "Every column must have a descriptive header."
        )

    normalized_headers = [header.casefold() for header in headers]
    if len(normalized_headers) != len(set(normalized_headers)):
        raise DatasetValidationError(
            "Column headers must be unique (ignoring capitalization)."
        )

    if dataframe.dropna(how="all").empty:
        raise DatasetValidationError(
            "The CSV does not contain any populated data rows."
        )

    dataframe.columns = headers
