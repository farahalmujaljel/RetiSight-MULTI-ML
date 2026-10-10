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

