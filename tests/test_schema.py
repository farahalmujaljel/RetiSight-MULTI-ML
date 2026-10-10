from pathlib import Path

import pandas as pd

from retisight_multi_ml.schema import validate_dataset, write_schema


def test_schema_files_and_validation(tmp_path: Path):
    write_schema(tmp_path)
    assert (tmp_path / "canonical_schema.json").exists()
    dataset = tmp_path / "dataset.csv"
    pd.DataFrame(
        {
            "source_dataset": ["synthetic"],
            "research_patient_id": ["RP-1"],
            "research_eye_id": ["RE-1"],
            "eye_laterality": ["OD"],
            "linkage_status": ["VERIFIED"],
            "age_years": [60],
            "baseline_bcva_etdrs": [70],
            "baseline_cst_um": [300],
        }
    ).to_csv(dataset, index=False)
    assert validate_dataset(dataset) == []

