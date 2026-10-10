# Clinical ML Contract

Status: interface ready for synthetic validation; not live hospital integration.

The clinical ML layer accepts one row per de-identified patient-eye baseline record. Required fields are defined in `schemas/clinical_interface.schema.json`.

## Required Identity And Baseline Fields

- `research_patient_id`: stable de-identified patient key.
- `research_eye_id`: stable de-identified eye key.
- `eye_laterality`: `OD` or `OS`.
- `baseline_visit_id`: visit identifier for the baseline measurement.
- `baseline_bcva_etdrs`: observed baseline ETDRS letters.
- `baseline_cst_um`: observed baseline central subfield thickness in micrometers.
- `linkage_status`: explicit cohort/linkage state.

## Linkage States

- `INTERNALLY_VERIFIED_OLIVES_PATIENT_EYE`: internally consistent OLIVES-native record.
- `CANDIDATE_CROSS_DATASET_MATCH`: candidate cross-dataset match; not externally verified.
- `EXTERNALLY_VERIFIED_CROSS_DATASET_LINK`: reserved for source-owner or documented crosswalk confirmation.
- `SYNTHETIC_SCHEMA_VALIDATION_ONLY`: software-test fixture.

## Guardrails

Systemic predictors from `OCT-DME.xlsx` must not be joined onto OLIVES-native rows unless the linkage state is externally verified or otherwise accepted through documented review. Future hospital predictors are schema-supported but require a real integration, source approval, and prediction-time definitions before modeling.
