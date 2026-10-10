from __future__ import annotations

import re
from typing import Any

import pandas as pd


def clean_column_name(value: Any) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def normalize_identifier(value: Any) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip().upper()
    if text.endswith(".0") and text[:-2].isdigit():
        text = text[:-2]
    return text or None


def normalize_eye(value: Any) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip().upper()
    if text in {"OD", "RIGHT", "R"}:
        return "OD"
    if text in {"OS", "LEFT", "L"}:
        return "OS"
    return None


def parse_visit(value: Any) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip().upper()
    match = re.search(r"V\\s*(\\d+)", text)
    if match:
        return f"V{int(match.group(1))}"
    return text or None


def path_parts(path: str) -> dict[str, str | None]:
    bits = [p for p in str(path).split("/") if p]
    return {
        "trial": bits[0] if len(bits) > 0 else None,
        "arm": bits[1] if len(bits) > 1 else None,
        "study_folder": bits[2].upper() if len(bits) > 2 else None,
        "visit": parse_visit(bits[3]) if len(bits) > 3 else None,
        "eye_laterality": normalize_eye(bits[4]) if len(bits) > 4 else None,
        "image_name": bits[5] if len(bits) > 5 else None,
    }

