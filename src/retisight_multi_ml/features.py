from __future__ import annotations

from pathlib import Path

import pandas as pd

from .oct_aggregation import aggregate_baseline_oct


def build_baseline_features(interim_dir: Path, linkage_dir: Path, output_dir: Path) -> pd.DataFrame:
    output_dir.mkdir(parents=True, exist_ok=True)
    biomarker = pd.read_pickle(interim_dir / "olives_biomarkers_clean.pkl")
    linkage = pd.read_csv(linkage_dir / "matching_report.csv", dtype=str)
    oct_base = pd.read_pickle(interim_dir / "oct_dme_baseline.pkl")
    oct_features = aggregate_baseline_oct(biomarker)
    verified = linkage[linkage["linkage_status"].eq("CANDIDATE_EXACT_MATCH")].copy()
    features = verified.merge(
        oct_features,
        on=["study_folder", "patient_id_norm", "eye_id_norm", "eye_laterality"],
        how="left",
    )
    features = features.merge(
        oct_base,
        left_on=["study_id", "source_sheet"],
        right_on=["study_id", "source_sheet"],
        how="left",
        suffixes=("", "_octdme"),
    )
    rename = {
        "etdrs": "baseline_bcva_etdrs",
        "oct": "baseline_cst_um",
        "age_at_enrollment": "age_years",
        "gender": "sex",
        "dia_type": "diabetes_type",
        "dia_duration": "diabetes_duration_years",
        "insulinuser": "insulin_use",
        "dr_level": "dr_severity",
    }
    features = features.rename(columns={k: v for k, v in rename.items() if k in features.columns})
    features["baseline_visit_id"] = "V1"
    features["baseline_date"] = pd.NA
    features["source_dataset"] = "OCT-DME + OLIVES"
    features.to_csv(output_dir / "baseline_features.csv", index=False)
    _write_biomarker_validation(features, output_dir)
    return features


def _write_biomarker_validation(features: pd.DataFrame, output_dir: Path) -> None:
    lines = [
        "# Biomarker Validation",
        "",
        "Baseline OCT biomarkers are aggregated from OLIVES `V1` B-scans only.",
        "No post-baseline biomarker annotations are included in the baseline feature table.",
        "",
        "## Linked Candidate Baseline Counts",
        "",
    ]
    for column in ["irf_present", "srf_present", "dril_present", "hrf_present", "ez_disruption_present"]:
        if column in features:
            counts = features[column].value_counts(dropna=False).to_dict()
            positives = int(pd.to_numeric(features[column], errors="coerce").fillna(0).sum())
            lines.append(f"- {column}: positives={positives}/{len(features)}; distribution={counts}")
    lines.extend(
        [
            "",
            "## Predictor Suitability",
            "",
            "- `irf_present` and `hrf_present` are constant positive in the linked candidate baseline "
            "cohort and should be excluded from comparative predictive models unless a later cohort introduces variation.",
            "- `dril_present` is extremely rare in this cohort (1 positive eye) and is unstable as an individual predictive input in small-sample modeling.",
            "- These warnings describe annotation distributions only; they are not clinical findings.",
        ]
    )
    (output_dir / "biomarker_validation.md").write_text("\n".join(lines), encoding="utf-8")
