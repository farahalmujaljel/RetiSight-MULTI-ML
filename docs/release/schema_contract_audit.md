# Schema Contract Audit

Audit date: 2026-10-11

## Canonical Schema

`schemas/canonical_schema.json` and `schemas/feature_dictionary.csv` define the current baseline record contract, including future hospital fields for HbA1c, hypertension, dyslipidemia, renal function, treatment history, and follow-up BCVA/CST.

## Clinical ML Interface

`schemas/clinical_interface.schema.json` defines one de-identified patient-eye baseline record. It requires explicit linkage state and does not permit silent promotion of candidate links to verified links.

## OCT Biomarker Interface

`schemas/oct_biomarker_interface.schema.json` defines one eye-level baseline biomarker record. `annotation_timepoint` is constrained to `baseline_only`.

## Feature Manifest

`schemas/supported_clinical_feature_manifest.csv` distinguishes:

- OLIVES-native baseline clinical/OCT predictors that are currently supported.
- OCT-DME or future-hospital systemic fields that require verified linkage or source approval.
- Treatment-history fields that are schema-supported but not currently eligible as predictors.

## Test Coverage

Schema tests validate canonical synthetic hospital records, clinical interface payloads, OCT biomarker interface payloads, and rejection of post-baseline OCT biomarker timepoints.

## Contract Decision

The public contracts are ready for downstream CLIN-ML and OCT-DL integration testing with synthetic or approved de-identified data. They do not establish real hospital integration or clinical outcome readiness.
