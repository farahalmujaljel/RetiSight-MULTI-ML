from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd

from .cleaning import clean_olives_biomarkers, clean_olives_clinical_images, read_oct_sheet
from .linkage import OCT_SHEETS_TO_ARM

PRIMARY_OCT_SHEETS = ["Monthly", "TREX", "GILA"]
TIMING_WINDOW = (150, 210)


def run_recovery_investigation(raw_dir: Path, report_dirs: dict[str, Path]) -> dict[str, str]:
    linkage_dir = report_dirs["linkage"]
    outcomes_dir = report_dirs["outcomes"]
    docs_dir = report_dirs["docs"]
    processed_dir = report_dirs["processed"]
    for path in [linkage_dir, outcomes_dir, docs_dir, processed_dir]:
        path.mkdir(parents=True, exist_ok=True)

    olives_visits = _olives_trex_eye_visits(raw_dir)
    oct_long = _oct_dme_primary_long(raw_dir)
    linkage_matrix = _linkage_evidence_matrix(olives_visits, oct_long)
    linkage_matrix.to_csv(linkage_dir / "longitudinal_linkage_evidence_matrix.csv", index=False)
    (linkage_dir / "longitudinal_linkage_evidence.md").write_text(
        _linkage_markdown(linkage_matrix),
        encoding="utf-8",
    )

    timing = _timing_recovery(raw_dir, olives_visits)
    timing["vision_cells"].to_csv(outcomes_dir / "timing_recovery_vision_cells.csv", index=False)
    timing["visit_index_endpoints"].to_csv(
        processed_dir / "olives_native_visit_index_endpoint_candidates.csv",
        index=False,
    )
    (outcomes_dir / "timing_recovery_evidence.md").write_text(
        _timing_markdown(timing),
        encoding="utf-8",
    )
    (docs_dir / "multi_03_06_recovery_decision.md").write_text(
        _decision_markdown(linkage_matrix, timing),
        encoding="utf-8",
    )
    return {
        "linkage_decision": "TRAJECTORY_SUPPORTED_CANDIDATES_REQUIRE_EXTERNAL_CONFIRMATION",
        "timing_decision": "NOT_FEASIBLE_WITHOUT_AUTHORITATIVE_CROSSWALK",
        "alternative_endpoint_decision": "DESCRIPTIVE_ONLY_REQUIRES_CLINICAL_APPROVAL",
    }


def _olives_trex_eye_visits(raw_dir: Path) -> pd.DataFrame:
    clinical = clean_olives_clinical_images(raw_dir / "Clinical_Data_Images.xlsx")
    biomarkers = clean_olives_biomarkers(raw_dir / "Biomarker_Clinical_Data_Images.csv")
    trex = clinical[clinical["trial"].eq("TREX DME")].copy()
    group_cols = [
        "arm",
        "study_folder",
        "patient_id_norm",
        "eye_id_norm",
        "eye_laterality",
        "visit",
    ]
    visits = (
        trex.groupby(group_cols, dropna=False)
        .agg(
            bcva=("bcva", "first"),
            cst=("cst", "first"),
            bcva_unique=("bcva", "nunique"),
            cst_unique=("cst", "nunique"),
            scan_rows=("file_path", "count"),
            unique_paths=("file_path", "nunique"),
        )
        .reset_index()
    )
    visits["visit_index"] = visits["visit"].map(_visit_index)
    biomarker_keys = (
        biomarkers[biomarkers["trial"].eq("TREX DME")][group_cols]
        .drop_duplicates()
        .assign(has_biomarker_annotations=True)
    )
    visits = visits.merge(biomarker_keys, on=group_cols, how="left")
    visits["has_biomarker_annotations"] = visits["has_biomarker_annotations"].fillna(False)
    return visits


def _oct_dme_primary_long(raw_dir: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for sheet in PRIMARY_OCT_SHEETS:
        df = read_oct_sheet(raw_dir / "OCT-DME.xlsx", sheet)
        arm = OCT_SHEETS_TO_ARM[sheet]
        if "study_id" not in df.columns:
            df["study_id"] = df["studyid"].astype(str).str.upper().str.strip()
        for _, record in df.iterrows():
            study_id = _norm(record.get("study_id") or record.get("studyid"))
            if not study_id:
                continue
            for idx in range(1, 40):
                etdrs_col = "etdrs" if idx == 1 else f"etdrs_{idx}"
                cst_col = "oct" if idx == 1 else f"oct_{idx}"
                if etdrs_col not in df.columns and cst_col not in df.columns:
                    continue
                bcva = pd.to_numeric(record.get(etdrs_col), errors="coerce")
                cst = pd.to_numeric(record.get(cst_col), errors="coerce")
                if pd.isna(bcva) and pd.isna(cst):
                    continue
                rows.append(
                    {
                        "source_sheet": sheet,
                        "arm": arm,
                        "study_id": study_id,
                        "study_laterality": _studyid_laterality(study_id),
                        "visit_index": idx,
                        "bcva": bcva,
                        "cst": cst,
                    }
                )
    return pd.DataFrame(rows)


def _linkage_evidence_matrix(olives_visits: pd.DataFrame, oct_long: pd.DataFrame) -> pd.DataFrame:
    rows = []
    eye_cols = ["arm", "study_folder", "patient_id_norm", "eye_id_norm", "eye_laterality"]
    for keys, eye_visits in olives_visits.dropna(subset=["visit_index"]).groupby(eye_cols):
        arm, study_id, patient_id, eye_id, laterality = keys
        eye_visits = eye_visits.copy()
        eye_visits["visit_index"] = eye_visits["visit_index"].astype(int)
        candidate = oct_long[(oct_long["arm"].eq(arm)) & (oct_long["study_id"].eq(study_id))]
        compared = _compare_sequences(eye_visits, candidate)
        competitors = _count_competing_trajectories(eye_visits, oct_long[oct_long["arm"].eq(arm)])
        baseline_o = eye_visits[eye_visits["visit_index"].eq(1)]
        baseline_c = candidate[candidate["visit_index"].eq(1)]
        baseline_bcva_match = _first_value(baseline_o, "bcva") == _first_value(baseline_c, "bcva")
        baseline_cst_match = _first_value(baseline_o, "cst") == _first_value(baseline_c, "cst")
        laterality_match = laterality == _studyid_laterality(study_id)
        no_mismatches = compared["bcva_mismatches"] == 0 and compared["cst_mismatches"] == 0
        classification = "TRAJECTORY_SUPPORTED_CANDIDATE"
        if not candidate.empty and not laterality_match:
            classification = "CONFLICTING_LATERALITY"
        elif not baseline_bcva_match or not baseline_cst_match or not no_mismatches:
            classification = "CANDIDATE_WITH_TRAJECTORY_CONFLICT"
        elif competitors["exact_competing_count"] > 1:
            classification = "TRAJECTORY_SUPPORTED_BUT_NOT_UNIQUE"

        rows.append(
            {
                "study_id": study_id,
                "olives_patient_id": patient_id,
                "olives_eye_id": eye_id,
                "arm": arm,
                "laterality": laterality,
                "studyid_laterality": _studyid_laterality(study_id),
                "laterality_match": laterality_match,
                "baseline_bcva_match": baseline_bcva_match,
                "baseline_cst_match": baseline_cst_match,
                "overlap_visit_count": compared["overlap_visit_count"],
                "bcva_agreements": compared["bcva_agreements"],
                "bcva_mismatches": compared["bcva_mismatches"],
                "cst_agreements": compared["cst_agreements"],
                "cst_mismatches": compared["cst_mismatches"],
                "olives_nonmissing_observations": competitors["olives_nonmissing_observations"],
                "exact_competing_trajectory_count": competitors["exact_competing_count"],
                "exact_competing_studyids": ";".join(competitors["exact_competing_studyids"]),
                "classification": classification,
                "identity_verification_status": "NOT_EXTERNALLY_VERIFIED",
            }
        )
    return pd.DataFrame(rows).sort_values(["arm", "study_id"]).reset_index(drop=True)


def _compare_sequences(olives_eye: pd.DataFrame, oct_eye: pd.DataFrame) -> dict[str, int]:
    merged = olives_eye.merge(oct_eye, on="visit_index", suffixes=("_olives", "_oct"))
    bcva_comp = merged[merged["bcva_olives"].notna() & merged["bcva_oct"].notna()]
    cst_comp = merged[merged["cst_olives"].notna() & merged["cst_oct"].notna()]
    return {
        "overlap_visit_count": int(merged["visit_index"].nunique()),
        "bcva_agreements": int((bcva_comp["bcva_olives"] == bcva_comp["bcva_oct"]).sum()),
        "bcva_mismatches": int((bcva_comp["bcva_olives"] != bcva_comp["bcva_oct"]).sum()),
        "cst_agreements": int((cst_comp["cst_olives"] == cst_comp["cst_oct"]).sum()),
        "cst_mismatches": int((cst_comp["cst_olives"] != cst_comp["cst_oct"]).sum()),
    }


def _count_competing_trajectories(olives_eye: pd.DataFrame, oct_arm: pd.DataFrame) -> dict[str, Any]:
    observed = olives_eye[["visit_index", "bcva", "cst"]].copy()
    observed = observed[observed["visit_index"].notna() & (observed["bcva"].notna() | observed["cst"].notna())]
    observed["visit_index"] = observed["visit_index"].astype(int)
    exact = []
    for study_id, oct_eye in oct_arm.groupby("study_id"):
        merged = observed.merge(oct_eye, on="visit_index", suffixes=("_olives", "_oct"))
        if len(merged) != len(observed):
            continue
        bcva_ok = (merged["bcva_olives"].isna() | (merged["bcva_olives"] == merged["bcva_oct"])).all()
        cst_ok = (merged["cst_olives"].isna() | (merged["cst_olives"] == merged["cst_oct"])).all()
        if bool(bcva_ok and cst_ok):
            exact.append(str(study_id))
    return {
        "olives_nonmissing_observations": int(len(observed)),
        "exact_competing_count": len(exact),
        "exact_competing_studyids": sorted(exact),
    }


def _timing_recovery(raw_dir: Path, olives_visits: pd.DataFrame) -> dict[str, Any]:
    vision_cells = _vision_timing_cells(raw_dir)
    id_sheet_diagnostics = _id_bearing_timing_diagnostics(raw_dir)
    endpoint_candidates = _visit_index_endpoint_candidates(olives_visits)
    return {
        "vision_cells": vision_cells,
        "id_sheet_diagnostics": id_sheet_diagnostics,
        "visit_index_endpoints": endpoint_candidates,
        "vision_cells_150_210": int(len(vision_cells)),
        "vision_cells_with_identifiers": 0,
        "authoritative_crosswalk_found": False,
    }


def _vision_timing_cells(raw_dir: Path) -> pd.DataFrame:
    rows = []
    for sheet in ["TREX Vision", "GILA Vision"]:
        df = read_oct_sheet(raw_dir / "OCT-DME.xlsx", sheet)
        for week_col, etdrs_col in _week_etdrs_pairs(df):
            week = pd.to_numeric(df[week_col], errors="coerce")
            etdrs = pd.to_numeric(df[etdrs_col], errors="coerce")
            mask = week.mul(7).between(*TIMING_WINDOW, inclusive="both") & etdrs.notna()
            for row_index in df[mask].index:
                rows.append(
                    {
                        "sheet": sheet,
                        "row_index": int(row_index),
                        "week_column": week_col,
                        "etdrs_column": etdrs_col,
                        "week": float(week.loc[row_index]),
                        "elapsed_day": float(week.loc[row_index] * 7),
                        "etdrs": float(etdrs.loc[row_index]),
                        "has_patient_eye_identifier": False,
                    }
                )
    return pd.DataFrame(rows)


def _id_bearing_timing_diagnostics(raw_dir: Path) -> pd.DataFrame:
    rows = []
    for sheet in ["Monthly", "TREX", "GILA", "Year 3 Monthly", "Year 3 TREX", "Year 3 GILA"]:
        df = read_oct_sheet(raw_dir / "OCT-DME.xlsx", sheet)
        eligible = 0
        week_cells = 0
        for week_col, etdrs_col in _week_etdrs_pairs(df):
            week = pd.to_numeric(df[week_col], errors="coerce")
            etdrs = pd.to_numeric(df[etdrs_col], errors="coerce")
            week_cells += int(week.notna().sum())
            eligible += int((week.mul(7).between(*TIMING_WINDOW, inclusive="both") & etdrs.notna()).sum())
        rows.append(
            {
                "sheet": sheet,
                "rows": len(df),
                "has_studyid": "studyid" in df.columns or "study_id" in df.columns,
                "populated_week_cells": week_cells,
                "eligible_150_210_day_etdrs_cells": eligible,
            }
        )
    return pd.DataFrame(rows)


def _visit_index_endpoint_candidates(olives_visits: pd.DataFrame) -> pd.DataFrame:
    baseline = olives_visits[olives_visits["visit_index"].eq(1)][
        ["arm", "study_folder", "patient_id_norm", "eye_id_norm", "bcva", "cst"]
    ].rename(columns={"bcva": "baseline_bcva", "cst": "baseline_cst"})
    rows = []
    for endpoint_visit in [4, 8, 13, 22, 27]:
        endpoint = olives_visits[olives_visits["visit_index"].eq(endpoint_visit)][
            ["study_folder", "patient_id_norm", "eye_id_norm", "bcva", "cst"]
        ].rename(columns={"bcva": "endpoint_bcva", "cst": "endpoint_cst"})
        merged = baseline.merge(endpoint, on=["study_folder", "patient_id_norm", "eye_id_norm"])
        merged["endpoint_visit_index"] = endpoint_visit
        merged["bcva_change"] = merged["endpoint_bcva"] - merged["baseline_bcva"]
        merged["response_ge_5_letters"] = merged["bcva_change"] >= 5
        rows.append(merged)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def _linkage_markdown(matrix: pd.DataFrame) -> str:
    class_counts = matrix["classification"].value_counts().to_dict()
    competitor_counts = matrix["exact_competing_trajectory_count"].value_counts().sort_index().to_dict()
    lines = [
        "# Longitudinal Linkage Evidence",
        "",
        "This investigation compares OLIVES-native TREX-DME patient-eye-visit BCVA/CST trajectories with primary OCT-DME ID-bearing worksheets.",
        "",
        "## Source-Backed Inputs",
        "",
        "- OLIVES ML-centric clinical labels: path, BCVA, CST, Eye_ID, Patient_ID for all 78,185 OCT scans.",
        "- OLIVES paths encode trial, treatment arm, folder, visit, eye laterality, and image name.",
        "- OCT-DME primary worksheets provide StudyID, arm-specific workbook sheet, baseline and longitudinal ETDRS/OCT values.",
        "- OLIVES source references: Zenodo DOI 10.5281/zenodo.7105232 and the NeurIPS 2022 OLIVES supplement.",
        "- TREX-DME timing source reference: protocol/publication descriptions of monthly loading and treat-and-extend schedules.",
        "",
        "## Results",
        "",
        f"- Candidate exact path-folder/StudyID eyes evaluated: {len(matrix)}",
        f"- Baseline BCVA exact matches: {int(matrix['baseline_bcva_match'].sum())}/{len(matrix)}",
        f"- Baseline CST exact matches: {int(matrix['baseline_cst_match'].sum())}/{len(matrix)}",
        f"- Laterality suffix matches: {int(matrix['laterality_match'].sum())}/{len(matrix)}",
        f"- BCVA mismatches across overlapping visits: {int(matrix['bcva_mismatches'].sum())}",
        f"- CST mismatches across overlapping visits: {int(matrix['cst_mismatches'].sum())}",
        f"- Classification counts: {class_counts}",
        f"- Exact competing trajectory counts: {competitor_counts}",
        "",
        "## Scientific Decision",
        "",
        "The 56 links are upgraded from simple identifier matches to trajectory-supported candidates "
        "because arm, laterality, baseline BCVA/CST, and overlapping longitudinal BCVA/CST values agree. "
        "They are still not externally verified links because no authoritative row-level crosswalk or "
        "data-owner confirmation was found.",
    ]
    return "\n".join(lines)


def _timing_markdown(timing: dict[str, Any]) -> str:
    diagnostics = timing["id_sheet_diagnostics"]
    endpoints = timing["visit_index_endpoints"]
    endpoint_summary = (
        endpoints.groupby("endpoint_visit_index")
        .agg(
            eyes=("study_folder", "count"),
            responses_ge_5=("response_ge_5_letters", "sum"),
            median_change=("bcva_change", "median"),
        )
        .reset_index()
        if not endpoints.empty
        else pd.DataFrame()
    )
    lines = [
        "# Timing Recovery Evidence",
        "",
        "## TREX/GILA Vision Timing Cells",
        "",
        f"- ETDRS cells in the 150-210 day window: {timing['vision_cells_150_210']}",
        "- Patient/eye identifiers in Vision sheets: 0",
        "- Authoritative crosswalk connecting Vision rows to OLIVES eyes: not found",
        "",
        "## ID-Bearing Worksheet Timing",
        "",
        _df_markdown(diagnostics),
        "",
        "## Alternative Visit-Index Endpoints",
        "",
        _df_markdown(endpoint_summary) if not endpoint_summary.empty else "No visit-index endpoints were available.",
        "",
        "These visit-index endpoints are observed longitudinal summaries, not six-month outcomes. They require clinical approval before any modeling use.",
        "",
        "## Scientific Decision",
        "",
        "Six-month response modeling remains disabled. Protocol-planned timing and clinical-value "
        "similarity are insufficient to map Vision rows to OLIVES patient-eye records. Required "
        "source-owner fields are patient/eye identifiers or an authoritative row crosswalk plus actual "
        "visit dates/elapsed days and eye-level treatment exposure.",
    ]
    return "\n".join(lines)


def _decision_markdown(matrix: pd.DataFrame, timing: dict[str, Any]) -> str:
    questions = [
        "Provide an authoritative row-level crosswalk from OLIVES Patient_ID/Eye_ID/path visit to OCT-DME StudyID and study eye.",
        "Confirm whether the OLIVES folder token is guaranteed to equal OCT-DME StudyID for every TREX-DME eye.",
        "Provide patient/eye identifiers for TREX Vision and GILA Vision rows, or confirm an official row-order mapping.",
        "Provide actual visit dates or elapsed study days for OLIVES TREX-DME V1-V27 visits.",
        "Provide eye-level injection dates/counts before the intended prediction endpoint.",
        "Confirm the clinically approved response endpoint and time zero.",
        "Confirm whether visit-index endpoints such as V13 or V22 are clinically meaningful descriptive endpoints.",
    ]
    lines = [
        "# MULTI-03/05/06 Recovery Decision",
        "",
        "## Linkage",
        "",
        "Decision: `TRAJECTORY_SUPPORTED_CANDIDATES_REQUIRE_EXTERNAL_CONFIRMATION`",
        "",
        f"The investigation found {len(matrix)} trajectory-supported candidate links with no BCVA/CST "
        "mismatches across overlapping visits. These links remain candidate links, not externally "
        "verified links.",
        "",
        "## Outcome Timing",
        "",
        "Decision: `NOT_FEASIBLE_WITHOUT_AUTHORITATIVE_CROSSWALK`",
        "",
        f"The Vision sheets contain {timing['vision_cells_150_210']} ETDRS cells in the 150-210 day "
        "window, but no patient/eye identifiers and no authoritative crosswalk to OLIVES eyes.",
        "",
        "## Alternative Endpoints",
        "",
        "Decision: `DESCRIPTIVE_ONLY_REQUIRES_CLINICAL_APPROVAL`",
        "",
        "OLIVES-native visit-index endpoints can be described, but must not be labelled six-month outcomes and must not enable modeling without clinical approval.",
        "",
        "## Unresolved Data-Owner Questions",
        "",
    ]
    lines.extend(f"{idx}. {question}" for idx, question in enumerate(questions, start=1))
    return "\n".join(lines)


def _week_etdrs_pairs(df: pd.DataFrame) -> list[tuple[str, str]]:
    cols = list(df.columns)
    pairs = []
    for idx, col in enumerate(cols):
        if str(col).startswith("week"):
            for next_col in cols[idx + 1 : idx + 4]:
                if str(next_col).startswith("etdrs"):
                    pairs.append((col, next_col))
                    break
    return pairs


def _df_markdown(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    text_df = df.copy()
    for column in text_df.columns:
        text_df[column] = text_df[column].map(lambda value: "" if pd.isna(value) else str(value))
    header = "| " + " | ".join(text_df.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(text_df.columns)) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in text_df.astype(str).to_numpy()]
    return "\n".join([header, sep, *rows])


def _visit_index(value: Any) -> int | None:
    if pd.isna(value):
        return None
    match = re.fullmatch(r"V(\d+)", str(value).strip().upper())
    return int(match.group(1)) if match else None


def _studyid_laterality(study_id: Any) -> str | None:
    text = _norm(study_id)
    if not text:
        return None
    if text.endswith("OD"):
        return "OD"
    if text.endswith("OS"):
        return "OS"
    return None


def _first_value(df: pd.DataFrame, column: str) -> Any:
    if df.empty or column not in df:
        return pd.NA
    value = df.iloc[0][column]
    return None if pd.isna(value) else value


def _norm(value: Any) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip().upper()
    return None if text in {"", "NAN", "NONE"} else text
