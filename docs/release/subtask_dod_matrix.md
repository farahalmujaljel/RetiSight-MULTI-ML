# Subtask DoD Matrix

Audit date: 2026-10-11

| subtask | release status | evidence | blocker |
| --- | --- | --- | --- |
| MULTI-01 | PASSED | Source inventory and checksums generated locally. | None for local raw-file execution. |
| MULTI-02 | PASSED | Cleaning and normalization reports generated. | None. |
| MULTI-03 | PARTIAL | 56 trajectory-supported candidate links with 56/56 baseline BCVA, CST, laterality, and overlapping trajectory agreement. | No authoritative crosswalk or source-owner confirmation. |
| MULTI-04 | PASSED_WITH_WARNINGS | Baseline OCT biomarkers aggregated without post-baseline leakage. | IRF/HRF constant positive; DRIL rare. |
| MULTI-05 | BLOCKED | Candidate linked baseline table exists. | External linkage verification missing. |
| MULTI-06 | BLOCKED | Timing audit found 165 Vision ETDRS cells in 150-210 day window. | Vision sheets lack patient/eye identifiers and crosswalk. |
| MULTI-06A | BLOCKED | OLIVES-native visit sequences inspected. | Visit labels cannot be mapped to elapsed days without source documentation. |
| MULTI-07 | CONDITIONAL_NOT_APPLICABLE | Modeling omission and infrastructure readiness reports generated. | Validated outcome manifest required. |
| MULTI-08 | CONDITIONAL_NOT_APPLICABLE | No clinical model metrics claimed. | Same validated outcome blocker. |
| MULTI-09 | PASSED | Reports and reproducible CLI available. | Raw-data pipeline requires private local files. |
| MULTI-10 | PASSED | Hospital schema synthetic validation implemented. | No live hospital integration. |
| MULTI-DEMO-01 | PASSED_SYNTHETIC_DEMONSTRATION | Fully fictitious cohort generator, six-month synthetic outcomes, grouped synthetic model comparison, inference demo, and CI smoke test. | Not clinical validation; real response modeling remains blocked. |

## Parent Task Decision

The engineering and descriptive-data deliverables are ready for review. The parent scientific task is not complete for cross-dataset verified modeling or six-month treatment-response prediction.
