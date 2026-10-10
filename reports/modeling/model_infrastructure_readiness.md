# Model Infrastructure Readiness

Reusable patient-grouped modeling infrastructure is implemented and tested with synthetic fixtures only.

## Ready Interfaces

- `require_validated_outcome(dataset, outcome_column, group_column)`
- `make_grouped_folds(dataset, outcome_column, group_column)`
- `compare_clinical_vs_oct_models(..., synthetic_authorization=...)` for software tests
- `compare_clinical_vs_oct_models(..., outcome_manifest=...)` for future validated research labels

## Safeguards

- Real model training remains disabled unless a machine-checkable validated outcome manifest is supplied.
- Clinical-only and clinical-plus-OCT models use identical eligible patients and folds.
- Synthetic tests are software validation only and are not clinical results.