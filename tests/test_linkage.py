from pathlib import Path

import pandas as pd

from retisight_multi_ml.linkage import build_linkage


def test_linkage_rejects_unmatched_and_verifies_exact_match(tmp_path: Path):
    interim = tmp_path / "interim"
    reports = tmp_path / "reports"
    interim.mkdir()
    pd.DataFrame(
        {
            "study_folder": ["0101GOD", "0999BAD"],
            "patient_id_norm": ["101", "999"],
            "eye_id_norm": ["1", "9"],
            "eye_laterality": ["OD", "OD"],
            "arm": ["GILA", "GILA"],
            "path_trial_arm_folder_visit_eye_image_name": ["a", "b"],
            "visit": ["V1", "V1"],
        }
    ).to_pickle(interim / "olives_biomarkers_clean.pkl")
    pd.DataFrame({"study_id": ["0101GOD"], "source_sheet": ["GILA"]}).to_pickle(
        interim / "oct_dme_baseline.pkl"
    )
    out = build_linkage(interim, reports)
    assert set(out["linkage_status"]) == {"VERIFIED", "UNMATCHED"}

