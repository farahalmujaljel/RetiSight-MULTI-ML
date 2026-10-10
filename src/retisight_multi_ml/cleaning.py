from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .normalization import clean_column_name, normalize_identifier, path_parts


def clean_olives_biomarkers(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.rename(columns={c: clean_column_name(c) for c in df.columns})
    path_col = "path_trial_arm_folder_visit_eye_image_name"
    parts = pd.DataFrame([path_parts(p) for p in df[path_col]])
    df = pd.concat([df, parts], axis=1)
    df["source_dataset"] = "olives_biomarkers"
    df["source_row"] = range(len(df))
    df["patient_id_norm"] = df["patient_id"].map(normalize_identifier)
    df["eye_id_norm"] = df["eye_id"].map(normalize_identifier)
    df["scan_number"] = pd.to_numeric(df["scan_n_49"], errors="coerce")
    return df


def clean_olives_clinical_images(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path)
    df = df.rename(columns={c: clean_column_name(c) for c in df.columns})
    parts = pd.DataFrame([path_parts(p) for p in df["file_path"]])
    df = pd.concat([df, parts], axis=1)
    df["source_dataset"] = "olives_clinical_images"
    df["source_row"] = range(len(df))
    df["patient_id_norm"] = df["patient_id"].map(normalize_identifier)
    df["eye_id_norm"] = df["eye_id"].map(normalize_identifier)
    return df


def read_oct_sheet(path: Path, sheet: str) -> pd.DataFrame:
    raw = pd.read_excel(path, sheet_name=sheet, header=None)
    header_idx = None
    for idx in range(min(6, len(raw))):
        values = {str(v).strip().lower() for v in raw.iloc[idx].dropna().tolist()}
        if "studyid" in values:
            header_idx = idx
            break
    if header_idx is None:
        header_idx = 0
    header = raw.iloc[header_idx].ffill()
    df = raw.iloc[header_idx + 1 :].copy()
    names = []
    seen: dict[str, int] = {}
    for i, value in enumerate(header):
        base = clean_column_name(value if pd.notna(value) else f"col_{i}")
        seen[base] = seen.get(base, 0) + 1
        names.append(base if seen[base] == 1 else f"{base}_{seen[base]}")
    df.columns = names
    df = df.dropna(how="all").reset_index(drop=True)
    df["source_sheet"] = sheet
    df["source_row"] = df.index + header_idx + 2
    return df


def clean_oct_dme(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    sheets = pd.ExcelFile(path).sheet_names
    rows = []
    baselines = []
    for sheet in sheets:
        df = read_oct_sheet(path, sheet)
        if "studyid" not in df.columns:
            continue
        df["study_id"] = df["studyid"].map(normalize_identifier)
        df = df[df["study_id"].notna()].copy()
        rows.append(df)
        base_cols = [c for c in df.columns if c in {"study_id", "source_sheet", "source_row"}]
        for c in [
            "etdrs",
            "oct",
            "age_at_enrollment",
            "gender",
            "dia_type",
            "dia_duration",
            "insulinuser",
            "dr_level",
        ]:
            if c in df.columns:
                base_cols.append(c)
        baselines.append(df.loc[:, list(dict.fromkeys(base_cols))])
    all_rows = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    baseline = pd.concat(baselines, ignore_index=True) if baselines else pd.DataFrame()
    if not baseline.empty:
        baseline = baseline.drop_duplicates(subset=["study_id", "source_sheet"], keep="first")
    return all_rows, baseline


def write_clean_outputs(raw_dir: Path, interim_dir: Path, report_dir: Path) -> dict[str, int]:
    interim_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    biomarker = clean_olives_biomarkers(raw_dir / "Biomarker_Clinical_Data_Images.csv")
    clinical = clean_olives_clinical_images(raw_dir / "Clinical_Data_Images.xlsx")
    oct_rows, oct_baseline = clean_oct_dme(raw_dir / "OCT-DME.xlsx")
    biomarker.to_pickle(interim_dir / "olives_biomarkers_clean.pkl")
    clinical.to_pickle(interim_dir / "olives_clinical_images_clean.pkl")
    oct_rows.to_pickle(interim_dir / "oct_dme_clean.pkl")
    oct_baseline.to_pickle(interim_dir / "oct_dme_baseline.pkl")
    summary = {
        "olives_biomarker_rows": int(len(biomarker)),
        "olives_clinical_image_rows": int(len(clinical)),
        "oct_dme_clean_rows": int(len(oct_rows)),
        "oct_dme_baseline_rows": int(len(oct_baseline)),
        "biomarker_duplicate_paths": int(biomarker["path_trial_arm_folder_visit_eye_image_name"].duplicated().sum()),
        "clinical_duplicate_paths": int(clinical["file_path"].duplicated().sum()),
    }
    (report_dir / "cleaning_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (report_dir / "cleaning_report.md").write_text(_cleaning_md(summary), encoding="utf-8")
    return summary


def _cleaning_md(summary: dict[str, int]) -> str:
    return "\n".join(["# Cleaning Report", "", *[f"- {k}: {v}" for k, v in summary.items()]])
