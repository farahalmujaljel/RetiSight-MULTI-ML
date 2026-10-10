from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_table(path: Path, sheet_name: str | None = None, header: int | None = 0) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path, sheet_name=sheet_name, header=header)
    raise ValueError(f"Unsupported table format: {path}")


def excel_sheets(path: Path) -> list[str]:
    if path.suffix.lower() not in {".xlsx", ".xls"}:
        return []
    return pd.ExcelFile(path).sheet_names

