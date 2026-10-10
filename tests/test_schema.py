from pathlib import Path

import pandas as pd

from retisight_multi_ml.schema import (
    synthetic_hospital_records,
    validate_dataset,
    write_hospital_schema_validation,
    write_schema,
)


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


def test_synthetic_hospital_schema_fixture_validates(tmp_path: Path):
    fixture = tmp_path / "hospital.csv"
    synthetic_hospital_records().to_csv(fixture, index=False)
    assert validate_dataset(fixture) == []
    assert write_hospital_schema_validation(tmp_path / "schemas", tmp_path / "reports") == []
    assert (tmp_path / "reports" / "hospital_schema_validation.md").exists()
