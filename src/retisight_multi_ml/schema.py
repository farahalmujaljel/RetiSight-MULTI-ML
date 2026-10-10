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
        ("egfr_ml_min_1_73m2", "Future hospital renal function", "number", "mL/min/1.73m2", True, "future_hospital"),
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

