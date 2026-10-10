from __future__ import annotations

import pandas as pd

BIOMARKER_COLUMNS = {
    "irf": "fluid_irf",
    "srf": "fluid_srf",
    "dril": "dril",
    "hrf": "ir_hrf",
    "ez_disruption": "disruption_of_ez",
}


def aggregate_baseline_oct(biomarker: pd.DataFrame) -> pd.DataFrame:
    baseline = biomarker[biomarker["visit"].eq("V1")].copy()
    rows = []
    group_cols = ["study_folder", "patient_id_norm", "eye_id_norm", "eye_laterality"]
    for keys, group in baseline.groupby(group_cols, dropna=False):
        row = dict(zip(group_cols, keys, strict=False))
        row["number_of_annotated_scans"] = int(group["scan_number"].notna().sum())
        for name, col in BIOMARKER_COLUMNS.items():
            values = pd.to_numeric(group[col], errors="coerce") if col in group else pd.Series(dtype=float)
            usable = values.dropna()
            row[f"{name}_positive_scan_count"] = int((usable == 1).sum()) if len(usable) else pd.NA
            row[f"{name}_positive_scan_proportion"] = float((usable == 1).mean()) if len(usable) else pd.NA
            row[f"{name}_present"] = int((usable == 1).any()) if len(usable) else pd.NA
        rows.append(row)
    return pd.DataFrame(rows)

