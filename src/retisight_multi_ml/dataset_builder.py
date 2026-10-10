from __future__ import annotations

from pathlib import Path

import pandas as pd

CANONICAL_COLUMNS = [
    "source_dataset",
    "research_patient_id",
    "research_eye_id",
    "source_patient_id",
    "source_eye_id",
    "patient_id_norm",
    "eye_id_norm",
    "eye_laterality",
    "baseline_visit_id",
    "baseline_date",
    "linkage_status",
    "age_years",
    "sex",
    "diabetes_type",
    "diabetes_duration_years",
    "insulin_use",
    "baseline_bcva_etdrs",
    "baseline_cst_um",
    "dr_severity",
    "irf_present",
    "srf_present",
    "dril_present",
    "hrf_present",
    "ez_disruption_present",
    "number_of_annotated_scans",
    "hba1c_percent",
    "hypertension",
    "dyslipidemia",
    "renal_disease",
    "egfr_ml_min_1_73m2",
]


def build_dataset(features_dir: Path, processed_dir: Path, report_dir: Path) -> pd.DataFrame:
    processed_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(features_dir / "baseline_features.csv")
    if "source_patient_id" not in df.columns and "study_folder" in df.columns:
        df["source_patient_id"] = df["study_folder"]
    if "source_eye_id" not in df.columns and "eye_id_norm" in df.columns:
        df["source_eye_id"] = df["eye_id_norm"]
    for column in CANONICAL_COLUMNS:
        if column not in df.columns:
            df[column] = pd.NA
    dataset = df[CANONICAL_COLUMNS].copy()
    duplicate_keys = int(dataset["research_eye_id"].duplicated().sum())
    dataset.to_csv(processed_dir / "multimodal_baseline.csv", index=False)
    lineage = []
    for col in CANONICAL_COLUMNS:
        lineage.append(
            {
                "feature": col,
                "source": "public_source_or_null_schema_placeholder",
                "temporal_role": "baseline_predictor" if col not in {"linkage_status"} else "metadata",
            }
        )
    pd.DataFrame(lineage).to_csv(processed_dir / "feature_provenance.csv", index=False)
    report = "\n".join(
        [
            "# Completeness Report",
            "",
            f"- Rows: {len(dataset)}",
            f"- Unique research eyes: {dataset['research_eye_id'].nunique(dropna=True)}",
            f"- Unique research patients: {dataset['research_patient_id'].nunique(dropna=True)}",
            f"- Duplicate research_eye_id rows: {duplicate_keys}",
            "",
            "Hospital-only variables are intentionally null unless supplied by authorized hospital data.",
        ]
    )
    (report_dir / "completeness_report.md").write_text(report, encoding="utf-8")
    return dataset
