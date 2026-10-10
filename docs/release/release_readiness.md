# Release Readiness

Audit date: 2026-10-11

## Verdict Flags

- `ENGINEERING_RELEASE_READY`: true for engineering review; merge still requires human PR review.
- `CLINICAL_PREDICTION_READY`: false.
- `SIX_MONTH_RESPONSE_MODELING_ENABLED`: false.
- `CROSS_DATASET_LINKAGE_EXTERNALLY_VERIFIED`: false.

## Completed For This Release

- OLIVES-native baseline dataset construction and aggregate validation.
- Explicit model-training authorization split between synthetic software tests and future validated real outcomes.
- Outcome manifest validation for future real model training.
- Patient-grouped fold checks and AUROC estimability status.
- Baseline clinical conflict failure before aggregation.
- Explicit feature metadata and baseline predictor allowlist.
- Clinical and OCT-DL interface schemas.
- Hospital-schema synthetic validation.
- CI protected-file gate.

## Final Local Checks

- `.venv/bin/python -m ruff check src tests`: passed.
- `.venv/bin/pytest`: 27 passed.
- `PYTHONPATH=src .venv/bin/python -m retisight_multi_ml.cli --config configs/pipeline.yaml full`: passed with private local raw files present.
- `.venv/bin/python -m pip install -e .`: passed.
- `.venv/bin/python -m retisight_multi_ml.cli --config configs/pipeline.yaml schema`: passed.
- GitHub Actions `ci` run 38088312519 on commit `77e60a9`: passed on Ubuntu with Python 3.11.

## Not Released As Complete

- Externally verified OLIVES to OCT-DME linkage.
- Six-month treatment-response labels.
- Real clinical model training or metrics.
- Live hospital integration.

## Required Before Clinical Modeling

1. Authoritative OLIVES Patient_ID/Eye_ID/path to OCT-DME StudyID/study-eye crosswalk, or source-owner confirmation of the current candidate links.
2. Actual visit dates or elapsed study days for candidate eyes.
3. Eye-level treatment exposure and time-zero definition.
4. Clinically approved outcome definition and signed-off validation manifest.
5. Re-run patient-grouped model evaluation only on the approved eligible cohort.
