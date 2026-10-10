from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .cleaning import clean_olives_biomarkers, clean_olives_clinical_images
from .feature_metadata import feature_metadata_frame, validate_baseline_predictor_allowlist
from .oct_aggregation import aggregate_baseline_oct

BIOMARKER_FEATURES = [
    "irf_present",
    "srf_present",
    "dril_present",
    "hrf_present",
    "ez_disruption_present",
]


def build_olives_native_baseline(raw_dir: Path, processed_dir: Path, report_dir: Path) -> pd.DataFrame:
    processed_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    clinical = clean_olives_clinical_images(raw_dir / "Clinical_Data_Images.xlsx")
    biomarkers = clean_olives_biomarkers(raw_dir / "Biomarker_Clinical_Data_Images.csv")

    baseline_clinical = _baseline_clinical(clinical)
    baseline_biomarkers = aggregate_baseline_oct(biomarkers)
    dataset = baseline_clinical.merge(
        baseline_biomarkers,
        on=["study_folder", "patient_id_norm", "eye_id_norm", "eye_laterality"],
        how="left",
        validate="one_to_one",
    )
    dataset["cohort_state"] = "INTERNALLY_VERIFIED_OLIVES_PATIENT_EYE"
    dataset["cross_dataset_linkage_status"] = "NOT_REQUIRED_FOR_OLIVES_NATIVE_EXPORT"
    dataset["baseline_visit_id"] = "V1"
    dataset["baseline_timing_status"] = "OLIVES_VISIT_LABEL_ONLY"
    dataset["source_dataset"] = "OLIVES"
    dataset["research_patient_id"] = "OLIVES-P-" + dataset["patient_id_norm"].astype(str)
    dataset["research_eye_id"] = "OLIVES-E-" + dataset["patient_id_norm"].astype(str) + "-" + dataset[
        "eye_id_norm"
    ].astype(str)
    dataset = _ordered_columns(dataset)
    dataset.to_csv(processed_dir / "olives_native_baseline.csv", index=False)

    validation = validate_olives_native_baseline(dataset, clinical, biomarkers)
    leakage_errors = validate_baseline_predictor_allowlist(
        [
            "baseline_bcva_etdrs",
            "baseline_cst_um",
            "irf_present",
            "srf_present",
            "dril_present",
            "hrf_present",
            "ez_disruption_present",
            "number_of_annotated_scans",
        ]
    )
    if leakage_errors:
        raise ValueError(f"Baseline predictor metadata validation failed: {leakage_errors}")
    _write_reports(dataset, validation, report_dir)
    return dataset


def validate_olives_native_baseline(
    dataset: pd.DataFrame, clinical: pd.DataFrame, biomarkers: pd.DataFrame
) -> dict[str, Any]:
    baseline_clinical = clinical[clinical["visit"].eq("V1") & clinical["trial"].eq("TREX DME")]
    duplicate_scan_paths = int(clinical["file_path"].duplicated().sum())
    visit_conflicts = (
        clinical[clinical["trial"].eq("TREX DME")]
        .groupby(["patient_id_norm", "eye_id_norm", "visit"], dropna=False)
        .agg(bcva_values=("bcva", "nunique"), cst_values=("cst", "nunique"))
    )
    biomarker_baseline = biomarkers[biomarkers["visit"].eq("V1") & biomarkers["trial"].eq("TREX DME")]
    biomarker_conflicts = _annotation_conflicts(biomarker_baseline)
    return {
        "rows": int(len(dataset)),
        "unique_patients": int(dataset["research_patient_id"].nunique()),
        "unique_eyes": int(dataset["research_eye_id"].nunique()),
        "duplicate_research_eye_ids": int(dataset["research_eye_id"].duplicated().sum()),
        "baseline_v1_clinical_eye_count": int(
            baseline_clinical[["patient_id_norm", "eye_id_norm"]].drop_duplicates().shape[0]
        ),
        "duplicate_clinical_scan_paths": duplicate_scan_paths,
        "clinical_visit_measurement_conflicts": int(
            ((visit_conflicts["bcva_values"] > 1) | (visit_conflicts["cst_values"] > 1)).sum()
        ),
        "baseline_biomarker_eye_count": int(
            biomarker_baseline[["patient_id_norm", "eye_id_norm"]].drop_duplicates().shape[0]
        ),
        "biomarker_duplicate_scan_records": int(
            biomarker_baseline[
                ["patient_id_norm", "eye_id_norm", "visit", "eye_laterality", "scan_number"]
            ].duplicated().sum()
        ),
        "biomarker_conflicting_duplicate_annotations": int(biomarker_conflicts),
        "post_baseline_biomarker_columns": int(
            dataset.filter(regex=r"post|follow|change|response", axis=1).shape[1]
        ),
        "missing_baseline_bcva": int(dataset["baseline_bcva_etdrs"].isna().sum()),
        "missing_baseline_cst": int(dataset["baseline_cst_um"].isna().sum()),
    }


def _baseline_clinical(clinical: pd.DataFrame) -> pd.DataFrame:
    baseline = clinical[clinical["trial"].eq("TREX DME") & clinical["visit"].eq("V1")].copy()
    group_cols = ["trial", "arm", "study_folder", "patient_id_norm", "eye_id_norm", "eye_laterality"]
    conflicts = _clinical_measurement_conflicts(baseline, group_cols)
    if conflicts:
        raise ValueError(f"Conflicting baseline clinical measurements found: {conflicts[:5]}")
    grouped = (
        baseline.groupby(group_cols, dropna=False)
        .agg(
            baseline_bcva_etdrs=("bcva", "first"),
            baseline_cst_um=("cst", "first"),
            baseline_scan_rows=("file_path", "count"),
            baseline_unique_scan_paths=("file_path", "nunique"),
            baseline_bcva_unique_values=("bcva", "nunique"),
            baseline_cst_unique_values=("cst", "nunique"),
        )
        .reset_index()
    )
    return grouped


def _clinical_measurement_conflicts(clinical: pd.DataFrame, group_cols: list[str]) -> list[dict[str, Any]]:
    grouped = (
        clinical.groupby(group_cols, dropna=False)
        .agg(bcva_values=("bcva", "nunique"), cst_values=("cst", "nunique"))
        .reset_index()
    )
    conflicts = grouped[(grouped["bcva_values"] > 1) | (grouped["cst_values"] > 1)]
    return conflicts.to_dict("records")


def _annotation_conflicts(biomarkers: pd.DataFrame) -> int:
    biomarker_cols = [
        "fluid_irf",
        "fluid_srf",
        "dril",
        "ir_hrf",
        "disruption_of_ez",
    ]
    duplicates = biomarkers[
        biomarkers[["patient_id_norm", "eye_id_norm", "visit", "eye_laterality", "scan_number"]].duplicated(
            keep=False
        )
    ]
    if duplicates.empty:
        return 0
    conflict_groups = duplicates.groupby(
        ["patient_id_norm", "eye_id_norm", "visit", "eye_laterality", "scan_number"], dropna=False
    )[biomarker_cols].nunique()
    return int((conflict_groups > 1).any(axis=1).sum())


def _ordered_columns(dataset: pd.DataFrame) -> pd.DataFrame:
    preferred = [
        "source_dataset",
        "cohort_state",
        "cross_dataset_linkage_status",
        "research_patient_id",
        "research_eye_id",
        "patient_id_norm",
        "eye_id_norm",
        "eye_laterality",
        "trial",
        "arm",
        "study_folder",
        "baseline_visit_id",
        "baseline_timing_status",
        "baseline_bcva_etdrs",
        "baseline_cst_um",
        "baseline_scan_rows",
        "baseline_unique_scan_paths",
        "number_of_annotated_scans",
        *BIOMARKER_FEATURES,
    ]
    rest = [c for c in dataset.columns if c not in preferred]
    return dataset[[c for c in preferred if c in dataset.columns] + rest]


def _write_reports(dataset: pd.DataFrame, validation: dict[str, Any], report_dir: Path) -> None:
    biomarker_lines = ["# Aggregate Biomarker Statistics", ""]
    for feature in BIOMARKER_FEATURES:
        if feature in dataset:
            values = pd.to_numeric(dataset[feature], errors="coerce")
            biomarker_lines.append(
                f"- {feature}: observed={int(values.notna().sum())}, positive={int(values.fillna(0).sum())}, missing={int(values.isna().sum())}"
            )
    (report_dir / "olives_native_biomarker_statistics.md").write_text(
        "\n".join(biomarker_lines), encoding="utf-8"
    )

    validation_lines = [
        "# OLIVES-Native Dataset Validation",
        "",
        "This report summarizes aggregate validation only; row-level OLIVES exports remain ignored by Git.",
        "",
        *[f"- {key}: {value}" for key, value in validation.items()],
        "",
        "Scientific status: complete for internally consistent OLIVES-native baseline features; not a substitute for cross-dataset verification or six-month response labels.",
    ]
    (report_dir / "olives_native_dataset_validation.md").write_text(
        "\n".join(validation_lines), encoding="utf-8"
    )
    feature_metadata_frame().to_csv(report_dir / "olives_native_feature_manifest.csv", index=False)
    manifest_lines = [
        "# OLIVES-Native Feature Manifest",
        "",
        "This manifest lists supported features and temporal predictor eligibility.",
        "",
    ]
    for row in feature_metadata_frame().itertuples(index=False):
        manifest_lines.append(
            "- "
            f"{row.feature_name}: source={row.source_dataset}; "
            f"time={row.observation_time}; role={row.temporal_role}; "
            f"eligible={row.allowed_as_baseline_predictor}; "
            "missingness_recorded_in=row-level ignored export"
        )
    (report_dir / "olives_native_feature_manifest.md").write_text(
        "\n".join(manifest_lines), encoding="utf-8"
    )
