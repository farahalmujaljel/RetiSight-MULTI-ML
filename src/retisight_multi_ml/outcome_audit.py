from __future__ import annotations

from pathlib import Path

import pandas as pd

from .cleaning import read_oct_sheet


def _visit_pairs(df: pd.DataFrame) -> list[tuple[str, str]]:
    cols = list(df.columns)
    pairs = []
    for idx, col in enumerate(cols):
        if col.startswith("week"):
            for next_col in cols[idx + 1 : idx + 4]:
                if next_col.startswith("etdrs"):
                    pairs.append((col, next_col))
                    break
    return pairs


def audit_outcomes(raw_dir: Path, processed_dir: Path, output_dir: Path, lower_day: int = 150, upper_day: int = 210) -> str:
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset = pd.read_csv(processed_dir / "multimodal_baseline.csv", dtype=str)
    rows = []
    for sheet in pd.ExcelFile(raw_dir / "OCT-DME.xlsx").sheet_names:
        df = read_oct_sheet(raw_dir / "OCT-DME.xlsx", sheet)
        if "studyid" not in df.columns:
            continue
        df["study_id"] = df["studyid"].astype(str).str.upper().str.strip()
        for _, record in df.iterrows():
            baseline = pd.to_numeric(record.get("etdrs"), errors="coerce")
            eligible = []
            for week_col, etdrs_col in _visit_pairs(df):
                week = pd.to_numeric(record.get(week_col), errors="coerce")
                etdrs = pd.to_numeric(record.get(etdrs_col), errors="coerce")
                if pd.notna(week) and pd.notna(etdrs):
                    day = float(week) * 7.0
                    if lower_day <= day <= upper_day:
                        eligible.append((abs(day - 180), day, etdrs, week_col, etdrs_col))
            chosen = sorted(eligible, key=lambda x: x[0])[0] if eligible else None
            rows.append(
                {
                    "study_id": record["study_id"],
                    "source_sheet": sheet,
                    "baseline_etdrs": baseline,
                    "eligible_followup_found": chosen is not None,
                    "followup_day": chosen[1] if chosen else pd.NA,
                    "followup_etdrs": chosen[2] if chosen else pd.NA,
                    "change_etdrs": (chosen[2] - baseline) if chosen and pd.notna(baseline) else pd.NA,
                    "candidate_response_5_letters": int((chosen[2] - baseline) >= 5)
                    if chosen and pd.notna(baseline)
                    else pd.NA,
                }
            )
    eligibility = pd.DataFrame(rows)
    eligible_linked = dataset.merge(eligibility, left_on="source_patient_id", right_on="study_id", how="left")
    eligibility.to_csv(output_dir / "outcome_eligibility.csv", index=False)
    decision = "REQUIRES_CLINICAL_REVIEW"
    rationale = (
        "Six-month ETDRS candidates can be derived from week fields for some records, but treatment "
        "time zero and anti-VEGF exposure cannot be fully verified from the implemented public tables alone."
    )
    report = "\n".join(
        [
            "# Outcome Feasibility",
            "",
            f"- Decision: {decision}",
            f"- Linked baseline rows: {len(dataset)}",
            f"- Candidate source records with 150-210 day follow-up: {int(eligibility['eligible_followup_found'].sum())}",
            f"- Linked rows with candidate follow-up after conservative merge: {int(eligible_linked['eligible_followup_found'].fillna(False).sum())}",
            "",
            rationale,
            "",
            "Candidate labels are not promoted to modeling labels until clinical review confirms endpoint and exposure assumptions.",
        ]
    )
    (output_dir / "outcome_definition.md").write_text(report, encoding="utf-8")
    return decision
