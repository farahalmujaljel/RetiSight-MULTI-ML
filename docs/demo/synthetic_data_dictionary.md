# Synthetic Data Dictionary

## Tables

- `synthetic_patients.csv`: one row per fictitious patient.
- `synthetic_eyes.csv`: one row per fictitious enrolled eye.
- `synthetic_visits.csv`: synthetic baseline and follow-up measurements.
- `synthetic_treatments.csv`: simulated anti-VEGF injection events.
- `synthetic_oct_biomarkers.csv`: baseline OCT biomarker flags.
- `synthetic_modeling_dataset.csv`: endpoint-eligible eye-level modeling rows.

## Required Provenance Fields

- `is_synthetic`: always `true`.
- `synthetic_provenance`: always `SYNTHETIC_DEMO_MULTI_DEMO_01`.
- `clinical_validation_status`: `NOT_VALIDATED` on modeling outputs.
