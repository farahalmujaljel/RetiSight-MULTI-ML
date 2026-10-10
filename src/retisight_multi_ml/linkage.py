from __future__ import annotations

from pathlib import Path

import pandas as pd

OCT_SHEETS_TO_ARM = {
    "Monthly": "GILA",
    "GILA": "GILA",
    "Year 3 GILA": "GILA",
    "GILA Vision": "GILA",
    "TREX": "TREX",
    "Year 3 TREX": "TREX",
    "TREX Vision": "TREX",
}


def build_linkage(interim_dir: Path, report_dir: Path) -> pd.DataFrame:
    report_dir.mkdir(parents=True, exist_ok=True)
    biomarker = pd.read_pickle(interim_dir / "olives_biomarkers_clean.pkl")
    oct_base = pd.read_pickle(interim_dir / "oct_dme_baseline.pkl")
    eyes = (
        biomarker.groupby(["study_folder", "patient_id_norm", "eye_id_norm", "eye_laterality", "arm"], dropna=False)
        .agg(
            annotated_images=("path_trial_arm_folder_visit_eye_image_name", "count"),
            visits=("visit", lambda s: ",".join(sorted({str(v) for v in s.dropna()}))),
        )
        .reset_index()
    )
    oct_ids = oct_base[["study_id", "source_sheet"]].drop_duplicates()
    candidates = eyes.merge(oct_ids, left_on="study_folder", right_on="study_id", how="left")
    candidates["expected_arm"] = candidates["source_sheet"].map(OCT_SHEETS_TO_ARM)
    candidates["arm_consistent"] = candidates["expected_arm"].isna() | (
        candidates["arm"].str.upper() == candidates["expected_arm"].str.upper()
    )
    candidates["linkage_status"] = "UNMATCHED"
    matched = candidates["study_id"].notna()
    candidates.loc[matched & candidates["arm_consistent"], "linkage_status"] = "CANDIDATE_EXACT_MATCH"
    candidates.loc[matched & ~candidates["arm_consistent"], "linkage_status"] = "AMBIGUOUS"
    candidates["matching_rule"] = candidates["linkage_status"].map(
        {
            "CANDIDATE_EXACT_MATCH": "OLIVES path study_folder exactly equals OCT-DME StudyID; arm is consistent where inferable.",
            "AMBIGUOUS": "Study folder equals StudyID but arm/sheet relationship conflicts.",
            "UNMATCHED": "No OCT-DME StudyID exactly matches OLIVES path study_folder.",
        }
    )
    candidates["identity_verification_status"] = candidates["linkage_status"].map(
        {
            "CANDIDATE_EXACT_MATCH": "REQUIRES_SOURCE_CROSSWALK_CONFIRMATION",
            "AMBIGUOUS": "NOT_VERIFIED",
            "UNMATCHED": "NOT_VERIFIED",
        }
    )
    candidates["research_patient_id"] = candidates["patient_id_norm"].map(lambda x: f"RP-{x}" if pd.notna(x) else None)
    candidates["research_eye_id"] = candidates.apply(
        lambda r: f"RE-{r.patient_id_norm}-{r.eye_id_norm}" if pd.notna(r.patient_id_norm) and pd.notna(r.eye_id_norm) else None,
        axis=1,
    )
    adjudicated_rows = []
    group_cols = ["study_folder", "patient_id_norm", "eye_id_norm", "eye_laterality", "arm"]
    for _keys, group in candidates.groupby(group_cols, dropna=False):
        verified_rows = group[group["linkage_status"].eq("CANDIDATE_EXACT_MATCH")]
        ambiguous_rows = group[group["linkage_status"].eq("AMBIGUOUS")]
        if not verified_rows.empty:
            chosen = verified_rows.iloc[0].copy()
            chosen["linkage_status"] = "CANDIDATE_EXACT_MATCH"
        elif not ambiguous_rows.empty:
            chosen = ambiguous_rows.iloc[0].copy()
            chosen["linkage_status"] = "AMBIGUOUS"
        else:
            chosen = group.iloc[0].copy()
            chosen["linkage_status"] = "UNMATCHED"
        chosen["candidate_source_sheets"] = ",".join(sorted(group["source_sheet"].dropna().astype(str).unique()))
        chosen["candidate_match_count"] = int(len(group))
        adjudicated_rows.append(chosen)
    matches = pd.DataFrame(adjudicated_rows)
    matches.to_csv(report_dir / "matching_report.csv", index=False)
    matches[matches["linkage_status"] == "AMBIGUOUS"].to_csv(
        report_dir / "ambiguous_matches.csv", index=False
    )
    stats = matches["linkage_status"].value_counts(dropna=False).to_dict()
    candidates_exact = matches[matches["linkage_status"] == "CANDIDATE_EXACT_MATCH"]
    text = "\n".join(
        [
            "# Linkage Validation",
            "",
            "Exact-match candidates require equality between the OLIVES image-path study folder and OCT-DME `StudyID`.",
            "This is reproducible matching evidence, not independently verified identity. No source crosswalk was found in the available documentation.",
            "",
            f"- Candidate eyes: {matches[['patient_id_norm', 'eye_id_norm']].drop_duplicates().shape[0]}",
            f"- Exact-match candidate eyes: {candidates_exact[['patient_id_norm', 'eye_id_norm']].drop_duplicates().shape[0]}",
            f"- Exact-match candidate patients: {candidates_exact['patient_id_norm'].nunique()}",
            "- Independently verified eyes: 0",
            "- DoD implication: MULTI-03 remains BLOCKED until the data owner or source documentation confirms the crosswalk.",
            *[f"- {k}: {v}" for k, v in stats.items()],
        ]
    )
    (report_dir / "linkage_validation.md").write_text(text, encoding="utf-8")
    return matches
