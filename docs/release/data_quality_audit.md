# Data Quality Audit

Audit date: 2026-10-11

## Source State

Raw TREX-DME and OLIVES source files were inspected locally from `data/raw/`, which is ignored by Git. No raw workbook, row-level clinical export, protected image, or row-level derived CSV/JSON should be committed.

## OLIVES-Native Baseline Cohort

Aggregate validation from `reports/features/olives_native_dataset_validation.md`:

- Patient-eye rows: 56
- Unique patients: 47
- Unique eyes: 56
- Duplicate research eye IDs: 0
- Baseline V1 clinical eye count: 56
- Missing baseline BCVA: 0
- Missing baseline CST: 0
- Duplicate clinical scan paths: 0
- Clinical visit measurement conflicts: 0
- Baseline biomarker eye count: 56
- Biomarker duplicate scan records: 0
- Biomarker conflicting duplicate annotations: 0
- Post-baseline biomarker columns in baseline export: 0

## Baseline Biomarker Prevalence

Aggregate statistics from `reports/features/olives_native_biomarker_statistics.md`:

- IRF: 56/56 positive
- SRF: 24/56 positive
- DRIL: 1/56 positive
- HRF: 56/56 positive
- EZ disruption: 19/56 positive

IRF and HRF are constant positive in this cohort, and DRIL is extremely rare. They are preserved as observed annotations but require clinical/statistical review before use as predictive inputs.

## Linkage And Outcome Data Quality

- Cross-dataset links: 56 trajectory-supported candidates, not externally verified.
- Six-month timing: blocked; no authoritative patient/eye crosswalk for Vision timing rows.
- OLIVES-native visit-index endpoints: descriptive only; not six-month outcomes.

## Data Quality Decision

The OLIVES-native baseline dataset is scientifically usable for descriptive baseline-feature work. It is not sufficient for six-month treatment-response modeling.
