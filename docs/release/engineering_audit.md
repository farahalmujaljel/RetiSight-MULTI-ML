# Engineering Release Audit

Audit date: 2026-10-11

## Verdict

Engineering release is locally testable and reproducible for source-code, schema, synthetic-fixture, and aggregate-report deliverables. Clinical prediction release remains blocked because six-month response labels and externally verified cross-dataset linkage are not established.

## P0/P1 Findings

| finding | severity | status | evidence |
| --- | --- | --- | --- |
| Ambiguous `allow_synthetic=True` could obscure real versus synthetic training authorization. | P0 | Fixed | Replaced with `SyntheticFixtureAuthorization` and `OutcomeValidationManifest` in `src/retisight_multi_ml/modeling.py`. |
| Outcome validation allowed weak manifests and did not record AUROC estimability. | P1 | Fixed | Real training requires validated manifest, approved clinical status, observed label counts, class counts, binary labels, patient groups, and fold train-class checks. |
| Baseline clinical aggregation used `first` after grouping. | P1 | Fixed | `_baseline_clinical` now fails on conflicting baseline BCVA/CST values before aggregation. |
| Leakage checks relied mainly on feature-name tokens. | P1 | Fixed | Added explicit feature metadata and predictor allowlist checks. |
| Clinical feature availability was ambiguous for OLIVES-native data. | P1 | Fixed | Added `schemas/supported_clinical_feature_manifest.csv`; OCT-DME/future-hospital systemic fields are not eligible for OLIVES-native modeling without verified provenance. |
| CI did not inspect tracked protected files. | P1 | Fixed locally | GitHub workflow now installs package, runs import smoke test, lint, tests, protected-file check, and schema CLI smoke test. |

## Code Areas Reviewed

- Source package: `src/retisight_multi_ml/`
- Tests: `tests/`
- Schemas and interface contracts: `schemas/`
- CI: `.github/workflows/ci.yml`
- Reports and documentation: `reports/`, `docs/`

## Local Verification

- `pytest`: 27 passed on Python 3.13.5 and 27 passed on Python 3.14.5 virtualenv.
- `python -m retisight_multi_ml.cli --config configs/pipeline.yaml full`: passed with local raw source files present.
- Protected tracked-file check: passed after excluding intentional `.gitkeep` sentinels.

## Remaining Engineering Gaps

- Hosted GitHub Actions result must be confirmed after push.
- Python 3.11 CI is configured but was not locally available in this workspace.
- The lockfile is pinned to Python 3.11-compatible package versions for CI.
- Real model training remains intentionally disabled until a validated outcome manifest exists.
