# MULTI-DEMO-01 Synthetic Implementation Plan

## Objective

Build a reproducible, fully fictitious multimodal anti-VEGF response demonstration without weakening the real OLIVES/OCT-DME safeguards.

## Safety Plan

- Keep synthetic records in `data/synthetic_demo/`, which is ignored by Git except `.gitkeep`.
- Mark every row with `is_synthetic=true` and `synthetic_provenance=SYNTHETIC_DEMO_MULTI_DEMO_01`.
- Preserve `OutcomeValidationManifest` requirements for real model training.
- Do not modify genuine OLIVES, OCT-DME, or generated real-pipeline datasets.
- Report all synthetic model metrics under `SYNTHETIC EXPERIMENT - NOT CLINICAL VALIDATION`.

## Implementation

- Generate separate Patient, Eye, Visit, Treatment, OCT Biomarker, Outcome, and modeling tables.
- Define time zero as the synthetic treatment baseline.
- Select outcomes from the 150-210 day endpoint window, closest to day 180 with deterministic tie-breaking.
- Train Clinical-only and Clinical + OCT logistic-regression models on identical eligible eyes and patient-grouped splits.
- Exclude follow-up BCVA, follow-up CST, future injection totals, selected endpoint day, and outcome-derived fields from predictors.
- Produce aggregate quality, model comparison, release-status, and figure artifacts.

## Validation

- Deterministic generator tests.
- Cardinality, foreign-key, chronology, endpoint, leakage, and authorization tests.
- CI smoke test that runs without raw clinical data.
