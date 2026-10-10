import json
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


def test_clinical_interface_schema_accepts_synthetic_payload():
    schema = _read_schema("clinical_interface.schema.json")
    payload = {
        "source_dataset": "synthetic_hospital_fixture",
        "research_patient_id": "SYN-P-001",
        "research_eye_id": "SYN-E-001-OD",
        "eye_laterality": "OD",
        "baseline_visit_id": "V1",
        "baseline_bcva_etdrs": 68,
        "baseline_cst_um": 412,
        "hba1c_percent": 8.1,
        "hypertension": True,
        "dyslipidemia": True,
        "renal_disease": False,
        "egfr_ml_min_1_73m2": 72,
        "anti_vegf_injection_count_prior_12mo": 3,
        "last_anti_vegf_agent": "ranibizumab",
        "linkage_status": "SYNTHETIC_SCHEMA_VALIDATION_ONLY",
        "provenance_note": "synthetic software-test fixture",
    }
    assert _minimal_schema_errors(payload, schema) == []


def test_oct_biomarker_interface_schema_accepts_synthetic_payload():
    schema = _read_schema("oct_biomarker_interface.schema.json")
    payload = {
        "research_eye_id": "SYN-E-001-OD",
        "baseline_visit_id": "V1",
        "biomarker_source": "SYNTHETIC_SCHEMA_VALIDATION_ONLY",
        "irf_present": 1,
        "srf_present": 0,
        "dril_present": 0,
        "hrf_present": 1,
        "ez_disruption_present": 0,
        "number_of_annotated_scans": 49,
        "annotation_timepoint": "baseline_only",
        "aggregation_rule": "any-positive across baseline scans",
        "provenance_note": "synthetic software-test fixture",
    }
    assert _minimal_schema_errors(payload, schema) == []


def test_oct_biomarker_interface_rejects_post_baseline_timepoint():
    schema = _read_schema("oct_biomarker_interface.schema.json")
    payload = {
        "research_eye_id": "SYN-E-001-OD",
        "baseline_visit_id": "V1",
        "biomarker_source": "SYNTHETIC_SCHEMA_VALIDATION_ONLY",
        "irf_present": 1,
        "srf_present": 0,
        "dril_present": 0,
        "hrf_present": 1,
        "ez_disruption_present": 0,
        "number_of_annotated_scans": 49,
        "annotation_timepoint": "V22",
    }
    assert "annotation_timepoint must be one of ['baseline_only']." in _minimal_schema_errors(payload, schema)


def _read_schema(file_name: str) -> dict:
    return json.loads((Path(__file__).parents[1] / "schemas" / file_name).read_text(encoding="utf-8"))


def _minimal_schema_errors(payload: dict, schema: dict) -> list[str]:
    errors = []
    for field in schema.get("required", []):
        if field not in payload:
            errors.append(f"{field} is required.")
    if schema.get("additionalProperties") is False:
        extra = sorted(set(payload) - set(schema["properties"]))
        errors.extend([f"{field} is not allowed." for field in extra])
    for field, value in payload.items():
        spec = schema["properties"].get(field, {})
        if value is None and _allows_null(spec):
            continue
        allowed = spec.get("enum")
        if allowed is not None and value not in allowed:
            errors.append(f"{field} must be one of {allowed}.")
        minimum = spec.get("minimum")
        if minimum is not None and value < minimum:
            errors.append(f"{field} must be >= {minimum}.")
        maximum = spec.get("maximum")
        if maximum is not None and value > maximum:
            errors.append(f"{field} must be <= {maximum}.")
    return errors


def _allows_null(spec: dict) -> bool:
    expected_type = spec.get("type")
    return expected_type == "null" or (isinstance(expected_type, list) and "null" in expected_type)
