# OCT DL Contract

Status: interface ready for structured biomarkers and future OCT-DL outputs.

The OCT biomarker interface is one row per de-identified eye at the baseline timepoint. Required fields are defined in `schemas/oct_biomarker_interface.schema.json`.

## Required Fields

- `research_eye_id`: stable eye key matching the clinical interface.
- `baseline_visit_id`: baseline visit label.
- `biomarker_source`: structured annotation, future OCT-DL output, or synthetic fixture.
- `irf_present`, `srf_present`, `dril_present`, `hrf_present`, `ez_disruption_present`: binary baseline biomarkers.
- `number_of_annotated_scans`: number of baseline scans contributing to aggregation.
- `annotation_timepoint`: must be `baseline_only`.

## Aggregation Rule

Current OLIVES-native biomarkers use eye-level any-positive aggregation across baseline `V1` annotated scans. Post-baseline OCT findings are not eligible as predictors for response modeling.

## Modeling Restriction

These features can be passed to model infrastructure only with synthetic software-test labels or with a validated outcome manifest. The interface does not itself establish a six-month treatment-response endpoint.
