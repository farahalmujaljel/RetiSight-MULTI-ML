import pandas as pd

from retisight_multi_ml.olives_native_dataset import validate_olives_native_baseline


def test_olives_native_validation_detects_duplicate_eye_and_no_leakage():
    dataset = pd.DataFrame(
        {
            "research_eye_id": ["E1", "E1"],
            "research_patient_id": ["P1", "P1"],
            "baseline_bcva_etdrs": [70, 70],
            "baseline_cst_um": [300, 300],
        }
    )
    clinical = pd.DataFrame(
        {
            "trial": ["TREX DME", "TREX DME"],
            "patient_id_norm": ["1", "1"],
            "eye_id_norm": ["1", "1"],
            "visit": ["V1", "V1"],
            "file_path": ["a", "a"],
            "bcva": [70, 70],
            "cst": [300, 300],
        }
    )
    biomarkers = pd.DataFrame(
        {
            "trial": ["TREX DME"],
            "patient_id_norm": ["1"],
            "eye_id_norm": ["1"],
            "visit": ["V1"],
            "eye_laterality": ["OD"],
            "scan_number": [1],
            "fluid_irf": [1],
            "fluid_srf": [0],
            "dril": [0],
            "ir_hrf": [1],
            "disruption_of_ez": [0],
        }
    )
    validation = validate_olives_native_baseline(dataset, clinical, biomarkers)
    assert validation["duplicate_research_eye_ids"] == 1
    assert validation["post_baseline_biomarker_columns"] == 0

