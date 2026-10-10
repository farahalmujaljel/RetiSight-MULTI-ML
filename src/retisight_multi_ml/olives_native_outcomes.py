from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from .cleaning import clean_olives_biomarkers, clean_olives_clinical_images


def visit_elapsed_days(visit_label: Any) -> int | None:
    """Return elapsed days only for documented week-style labels such as W24."""
    if pd.isna(visit_label):
        return None
    text = str(visit_label).strip().upper()
    match = re.fullmatch(r"W(\d+)", text)
    if not match:
        return None
    return int(match.group(1)) * 7


def reconstruct_olives_eye_visits(raw_dir: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    clinical = clean_olives_clinical_images(raw_dir / "Clinical_Data_Images.xlsx")
    biomarkers = clean_olives_biomarkers(raw_dir / "Biomarker_Clinical_Data_Images.csv")

    group_cols = [
        "trial",
        "arm",
        "study_folder",
        "patient_id_norm",
        "eye_id_norm",
        "eye_laterality",
        "visit",
    ]
    eye_visits = (
        clinical.groupby(group_cols, dropna=False)
        .agg(
            source_image_rows=("file_path", "count"),
            unique_paths=("file_path", "nunique"),
            bcva_unique_values=("bcva", "nunique"),
            cst_unique_values=("cst", "nunique"),
            bcva_etdrs=("bcva", "first"),
            cst_um=("cst", "first"),
        )
        .reset_index()
    )
    eye_visits["elapsed_days"] = eye_visits["visit"].map(visit_elapsed_days)
    eye_visits["cohort_state"] = "INTERNALLY_VERIFIED_OLIVES_PATIENT_EYE_VISIT"
    eye_visits["visit_timing_status"] = eye_visits["elapsed_days"].map(
        lambda value: "DOCUMENTED_WEEK_LABEL" if pd.notna(value) else "VISIT_SEQUENCE_ONLY"
    )

    biomarker_keys = biomarkers[group_cols].drop_duplicates()
    biomarker_keys["has_expert_biomarkers_for_visit"] = True
    eye_visits = eye_visits.merge(biomarker_keys, on=group_cols, how="left")
    eye_visits["has_expert_biomarkers_for_visit"] = eye_visits[
        "has_expert_biomarkers_for_visit"
    ].fillna(False)

    trex = eye_visits[eye_visits["trial"].eq("TREX DME")]
    consistency = {
        "clinical_image_rows": int(len(clinical)),
        "clinical_eye_visit_records": int(len(eye_visits)),
        "trex_eye_visit_records": int(len(trex)),
        "trex_patients": int(trex["patient_id_norm"].nunique()),
        "trex_eyes": int(trex[["patient_id_norm", "eye_id_norm"]].drop_duplicates().shape[0]),
        "bcva_conflicting_eye_visits": int((eye_visits["bcva_unique_values"] > 1).sum()),
        "cst_conflicting_eye_visits": int((eye_visits["cst_unique_values"] > 1).sum()),
        "non_49_scan_eye_visits": int((eye_visits["source_image_rows"] != 49).sum()),
        "trex_elapsed_day_records": int(trex["elapsed_days"].notna().sum()),
        "trex_visit_labels": sorted(trex["visit"].dropna().astype(str).unique().tolist()),
    }
    return eye_visits, consistency


def audit_olives_native_outcomes(
    raw_dir: Path,
    processed_dir: Path,
    output_dir: Path,
    lower_day: int = 150,
    upper_day: int = 210,
) -> str:
    output_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    eye_visits, consistency = reconstruct_olives_eye_visits(raw_dir)
    eye_visits.to_csv(processed_dir / "olives_native_eye_visits.csv", index=False)
    trex = eye_visits[eye_visits["trial"].eq("TREX DME")].copy()

    baseline = trex[trex["visit"].eq("V1")].copy()
    timed_followup = trex[
        trex["elapsed_days"].between(lower_day, upper_day, inclusive="both")
        & trex["bcva_etdrs"].notna()
    ].copy()

    feasibility_decision = "NOT_FEASIBLE"
    reasons = [
        "TREX-DME OLIVES-native visit labels are sequence labels (V1-V27), not elapsed weeks or dates.",
        "No TREX-DME OLIVES-native records have documented elapsed days in the 150-210 day window.",
        "Study arm is available from the OLIVES path, but eye-level injection dates/counts before six months are not available in the ML-centric clinical table.",
        "The official documentation supports TREX-DME treatment cohorts and visits every 4-16 weeks, but does not map each V-label to an elapsed day.",
    ]

    if not timed_followup.empty:
        feasibility_decision = "REQUIRES_CLINICAL_REVIEW"
        reasons.insert(
            0,
            "Some timed follow-up records were found, but treatment exposure/time-zero assumptions still require review.",
        )

    status = {
        **consistency,
        "baseline_v1_trex_records": int(len(baseline)),
        "timed_150_210_day_trex_records": int(len(timed_followup)),
        "feasibility_decision": feasibility_decision,
        "candidate_cross_dataset_state": "CANDIDATE_EXACT_MATCH_ONLY",
        "externally_verified_cross_dataset_links": 0,
    }
    (output_dir / "olives_native_outcome_recovery_summary.json").write_text(
        json.dumps(status, indent=2),
        encoding="utf-8",
    )
    (output_dir / "olives_native_outcome_recovery.md").write_text(
        _decision_markdown(status, reasons),
        encoding="utf-8",
    )
    return feasibility_decision


def _decision_markdown(status: dict[str, Any], reasons: list[str]) -> str:
    lines = [
        "# MULTI-06A OLIVES-Native Longitudinal Outcome Recovery",
        "",
        f"- Decision: {status['feasibility_decision']}",
        f"- Internally verified OLIVES TREX-DME patients: {status['trex_patients']}",
        f"- Internally verified OLIVES TREX-DME eyes: {status['trex_eyes']}",
        f"- TREX-DME eye-visit records: {status['trex_eye_visit_records']}",
        f"- Baseline V1 TREX-DME records: {status['baseline_v1_trex_records']}",
        f"- TREX-DME records with documented 150-210 day timing: {status['timed_150_210_day_trex_records']}",
        f"- BCVA conflicts within patient-eye-visit: {status['bcva_conflicting_eye_visits']}",
        f"- CST conflicts within patient-eye-visit: {status['cst_conflicting_eye_visits']}",
        f"- Non-49-scan patient-eye-visits: {status['non_49_scan_eye_visits']}",
        "",
        "## Cohort States",
        "",
        "- Internally verified OLIVES patient-eye records: reconstructed from OLIVES-native `Patient_ID`, `Eye_ID`, path visit, BCVA, and CST.",
        "- Candidate cross-dataset matches with OCT-DME.xlsx: exact path-folder/StudyID matches only.",
        "- Externally verified cross-dataset links: 0.",
        "",
        "## Scientific Decision",
        "",
        "The OLIVES-native longitudinal table is suitable for descriptive patient-eye-visit "
        "reconstruction, but it does not support a scientifically defensible six-month anti-VEGF "
        "response label without additional timing and treatment documentation.",
        "",
        "Reasons:",
        "",
    ]
    lines.extend(f"- {reason}" for reason in reasons)
    lines.extend(
        [
            "",
            "Modeling remains disabled. Do not assume that `V22` or any other TREX-DME `V` label equals six months.",
        ]
    )
    return "\n".join(lines)
