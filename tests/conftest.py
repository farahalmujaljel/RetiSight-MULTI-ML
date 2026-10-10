from __future__ import annotations

import pandas as pd
import pytest


@pytest.fixture
def synthetic_biomarkers() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "study_folder": ["0101GOD", "0101GOD", "0102TOS"],
            "patient_id_norm": ["101", "101", "102"],
            "eye_id_norm": ["1", "1", "2"],
            "eye_laterality": ["OD", "OD", "OS"],
            "visit": ["V1", "V1", "V2"],
            "scan_number": [1, 2, 1],
            "fluid_irf": [0, 1, 1],
            "fluid_srf": [0, 0, 1],
            "dril": [0, 0, 1],
            "ir_hrf": [1, 1, 0],
            "disruption_of_ez": [0, 0, 1],
        }
    )


@pytest.fixture
def synthetic_modeling_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "research_patient_id": [f"P{i}" for i in range(12)],
            "baseline_bcva_etdrs": [50, 55, 60, 65, 52, 58, 62, 67, 51, 57, 63, 69],
            "baseline_cst_um": [500, 480, 450, 430, 510, 470, 440, 420, 505, 465, 435, 415],
            "irf_present": [1] * 12,
            "srf_present": [0, 1] * 6,
            "dril_present": [0, 0, 1, 0] * 3,
            "hrf_present": [1] * 12,
            "ez_disruption_present": [0, 1, 0, 1] * 3,
            "number_of_annotated_scans": [49] * 12,
            "synthetic_outcome": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        }
    )
