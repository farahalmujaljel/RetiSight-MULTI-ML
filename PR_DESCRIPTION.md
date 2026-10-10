# RetiSight MULTI-ML Engineering Release Audit

## Summary

This PR prepares the MULTI-ML feature branch for engineering review while preserving scientific restrictions around linkage and outcome modeling.

## Key Changes

- Replaced ambiguous synthetic model-training control with explicit synthetic fixture authorization and validated outcome manifests.
- Strengthened outcome, fold, baseline conflict, and leakage checks.
- Added OLIVES-native feature metadata and supported clinical feature manifest.
- Added clinical ML and OCT biomarker interface schemas with integration contracts.
- Added release audit documentation and CI protected-file checks.
- Added `MULTI-DEMO-01`, a fully fictitious synthetic end-to-end multimodal demo with separate cohort generation, six-month synthetic outcomes, grouped model comparison, reporting, figures, and inference output.

## Scientific Status

- OLIVES-native baseline cohort: 56 eyes, 47 patients, aggregate validation passed.
- Cross-dataset linkage: trajectory-supported candidate links only; not externally verified.
- Six-month response modeling: disabled.
- Real model training: disabled without validated outcome manifest.
- Synthetic demo metrics are explicitly labeled `SYNTHETIC EXPERIMENT - NOT CLINICAL VALIDATION` and are not clinical performance estimates.

## MULTI-DEMO-01 Synthetic Demo

- Generator: `src/retisight_multi_ml/synthetic_demo/generator.py`
- CLI: `python -m retisight_multi_ml.cli --config configs/pipeline.yaml synthetic-demo`
- Default generated cohort: 1,000 synthetic patients, 1,306 synthetic eyes, 1,274 outcome-eligible eyes.
- Models: Clinical-only and Clinical + OCT regularized logistic regression on identical eligible eyes and patient-grouped held-out splits.
- Safeguards: all rows carry synthetic provenance; baseline-only predictors are enforced; no synthetic crosswalk is used to validate genuine records.

## Validation

- Full pipeline passed locally with private raw files present.
- Test suite passed locally: 32 tests.
- Ruff was not available in the local shell used for this update; GitHub Actions installs the locked dependencies and runs `ruff check src tests`.
- GitHub Actions `ci` includes a synthetic CLI smoke test using `/tmp` output paths.

## Privacy

No raw datasets, row-level clinical exports, protected images, credentials, or model artifacts should be included. CI includes a protected tracked-file gate.
