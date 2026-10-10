# RetiSight MULTI-ML Engineering Release Audit

## Summary

This PR prepares the MULTI-ML feature branch for engineering review while preserving scientific restrictions around linkage and outcome modeling.

## Key Changes

- Replaced ambiguous synthetic model-training control with explicit synthetic fixture authorization and validated outcome manifests.
- Strengthened outcome, fold, baseline conflict, and leakage checks.
- Added OLIVES-native feature metadata and supported clinical feature manifest.
- Added clinical ML and OCT biomarker interface schemas with integration contracts.
- Added release audit documentation and CI protected-file checks.

## Scientific Status

- OLIVES-native baseline cohort: 56 eyes, 47 patients, aggregate validation passed.
- Cross-dataset linkage: trajectory-supported candidate links only; not externally verified.
- Six-month response modeling: disabled.
- Real model training: disabled without validated outcome manifest.

## Validation

- Full pipeline passed locally with private raw files present.
- Test suite passed locally: 27 tests.
- Ruff passed locally.

## Privacy

No raw datasets, row-level clinical exports, protected images, credentials, or model artifacts should be included. CI includes a protected tracked-file gate.
