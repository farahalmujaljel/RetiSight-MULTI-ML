from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field


class BaselineRecord(BaseModel):
    model_config = ConfigDict(extra="allow")

    source_dataset: str
    research_patient_id: str | None = None
    research_eye_id: str | None = None
    eye_laterality: str | None = Field(default=None, pattern="^(OD|OS)$")
    linkage_status: str
    age_years: float | None = None
    baseline_bcva_etdrs: float | None = None
    baseline_cst_um: float | None = None
    hba1c_percent: float | None = None
    hypertension: bool | None = None
    dyslipidemia: bool | None = None
    renal_disease: bool | None = None
    egfr_ml_min_1_73m2: float | None = None
    anti_vegf_injection_count_prior_12mo: int | None = None
    last_anti_vegf_agent: str | None = None
    followup_bcva_etdrs: float | None = None
    followup_cst_um: float | None = None


def schema_definition() -> dict[str, Any]:
    fields = [
        ("research_patient_id", "Stable de-identified patient key", "string", None, True, "identity"),
        ("research_eye_id", "Stable de-identified eye key", "string", None, True, "identity"),
        ("eye_laterality", "Eye laterality", "category", "OD/OS", True, "identity"),
        ("baseline_bcva_etdrs", "Baseline ETDRS visual acuity", "number", "letters", True, "baseline_predictor"),
        ("baseline_cst_um", "Baseline central subfield thickness", "number", "um", True, "baseline_predictor"),
        ("irf_present", "Any baseline scan annotated with intraretinal fluid", "integer", "0/1", True, "baseline_predictor"),
        ("srf_present", "Any baseline scan annotated with subretinal fluid", "integer", "0/1", True, "baseline_predictor"),
        ("hba1c_percent", "Future hospital HbA1c value", "number", "percent", True, "future_hospital"),
        ("hypertension", "Future hospital hypertension flag", "boolean", "true/false", True, "future_hospital"),
        ("dyslipidemia", "Future hospital dyslipidemia flag", "boolean", "true/false", True, "future_hospital"),
        ("renal_disease", "Future hospital renal disease flag", "boolean", "true/false", True, "future_hospital"),
        ("egfr_ml_min_1_73m2", "Future hospital renal function", "number", "mL/min/1.73m2", True, "future_hospital"),
        ("anti_vegf_injection_count_prior_12mo", "Future hospital anti-VEGF treatment history", "integer", "count", True, "future_hospital"),
        ("last_anti_vegf_agent", "Future hospital last anti-VEGF medication", "string", None, True, "future_hospital"),
        ("followup_bcva_etdrs", "Future hospital follow-up ETDRS visual acuity", "number", "letters", True, "follow_up"),
        ("followup_cst_um", "Future hospital follow-up central subfield thickness", "number", "um", True, "follow_up"),
    ]
    return {
        "entities": [
            "Patient",
            "Eye",
            "Visit",
            "ClinicalAssessment",
            "OCTExamination",
            "OCTBiomarkerObservation",
            "TreatmentAdministration",
            "TreatmentCourse",
            "FollowUpAssessment",
            "TreatmentResponse",
            "DataProvenance",
        ],
        "fields": [
            {
                "field_name": f,
                "clinical_meaning": meaning,
                "data_type": dtype,
                "unit_or_allowed_values": unit,
                "nullable": nullable,
                "temporal_role": role,
            }
            for f, meaning, dtype, unit, nullable, role in fields
        ],
    }


def write_schema(schema_dir: Path) -> None:
    schema_dir.mkdir(parents=True, exist_ok=True)
    definition = schema_definition()
    (schema_dir / "canonical_schema.json").write_text(json.dumps(definition, indent=2), encoding="utf-8")
    pd.DataFrame(definition["fields"]).to_csv(schema_dir / "feature_dictionary.csv", index=False)
    pd.DataFrame(
        [
            {"source": "OLIVES path", "canonical_field": "research_eye_id", "mapping": "Patient_ID + Eye_ID"},
            {"source": "OCT-DME StudyID", "canonical_field": "patient_id_norm", "mapping": "Exact StudyID"},
            {"source": "Hospital EHR", "canonical_field": "hba1c_percent", "mapping": "Future integration only"},
        ]
    ).to_csv(schema_dir / "source_mapping.csv", index=False)
    pd.DataFrame(
        [
            {"source_field": "Patient_ID", "canonical_field": "research_patient_id"},
            {"source_field": "Eye_ID", "canonical_field": "research_eye_id"},
            {"source_field": "StudyID", "canonical_field": "patient_id_norm"},
        ]
    ).to_csv(schema_dir / "source_to_canonical_mapping.csv", index=False)


def validate_dataset(path: Path) -> list[str]:
    df = pd.read_csv(path)
    errors = []
    for idx, record in df.iterrows():
        try:
            data = record.where(pd.notna(record), None).to_dict()
            BaselineRecord(**data)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"row {idx}: {exc}")
    if df["research_eye_id"].duplicated().any():
        errors.append("Duplicate research_eye_id values found.")
    return errors


def synthetic_hospital_records() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "source_dataset": "synthetic_hospital_fixture",
                "research_patient_id": "SYN-P-001",
                "research_eye_id": "SYN-E-001-OD",
                "eye_laterality": "OD",
                "linkage_status": "SYNTHETIC_SCHEMA_VALIDATION_ONLY",
                "age_years": 62,
                "baseline_bcva_etdrs": 68,
                "baseline_cst_um": 412,
                "hba1c_percent": 8.1,
                "hypertension": True,
                "dyslipidemia": True,
                "renal_disease": False,
                "egfr_ml_min_1_73m2": 72,
                "anti_vegf_injection_count_prior_12mo": 3,
                "last_anti_vegf_agent": "ranibizumab",
                "followup_bcva_etdrs": 75,
                "followup_cst_um": 331,
            },
            {
                "source_dataset": "synthetic_hospital_fixture",
                "research_patient_id": "SYN-P-002",
                "research_eye_id": "SYN-E-002-OS",
                "eye_laterality": "OS",
                "linkage_status": "SYNTHETIC_SCHEMA_VALIDATION_ONLY",
                "age_years": 58,
                "baseline_bcva_etdrs": 55,
                "baseline_cst_um": 505,
                "hba1c_percent": 7.4,
                "hypertension": False,
                "dyslipidemia": True,
                "renal_disease": True,
                "egfr_ml_min_1_73m2": 49,
                "anti_vegf_injection_count_prior_12mo": 0,
                "last_anti_vegf_agent": None,
                "followup_bcva_etdrs": 58,
                "followup_cst_um": 470,
            },
        ]
    )


def write_hospital_schema_validation(schema_dir: Path, report_dir: Path) -> list[str]:
    schema_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    fixture = synthetic_hospital_records()
    fixture_path = schema_dir / "synthetic_hospital_schema_fixture.csv"
    fixture.to_csv(fixture_path, index=False)
    errors = validate_dataset(fixture_path)
    lines = [
        "# Hospital Schema Validation",
        "",
        "Synthetic future-hospital records were validated against the canonical schema.",
        "This is not live hospital integration and does not use real hospital data.",
        "",
        f"- Synthetic records: {len(fixture)}",
        f"- Validation errors: {len(errors)}",
        "- Supported fields: HbA1c, hypertension, dyslipidemia, renal disease, eGFR, anti-VEGF treatment history, OCT/BCVA follow-up.",
    ]
    if errors:
        lines.extend(["", "## Errors", *[f"- {error}" for error in errors]])
    (report_dir / "hospital_schema_validation.md").write_text("\n".join(lines), encoding="utf-8")
    return errors
