# SYNTHETIC EXPERIMENT - NOT CLINICAL VALIDATION

## Synthetic Model Comparison

These metrics are software demonstration results from a fully fictitious cohort. They are not clinical performance estimates.

| title | model | eligible_eyes | eligible_patients | heldout_eyes | response_prevalence | auroc | average_precision | sensitivity | specificity | balanced_accuracy | brier_score | true_negative | false_positive | false_negative | true_positive | non_constant_predictors | synthetic_fixture_only | clinical_validation_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SYNTHETIC EXPERIMENT - NOT CLINICAL VALIDATION | Clinical-only | 1274 | 984 | 319 | 0.5989 | 0.5629 | 0.6152 | 0.8315 | 0.2074 | 0.5195 | 0.2472 | 28 | 107 | 31 | 153 | age_years, sex, diabetes_duration_years, hba1c_percent, hypertension, dyslipidemia, renal_disease, egfr_ml_min_1_73m2, baseline_bcva_etdrs, baseline_cst_um | True | NOT_VALIDATED |
| SYNTHETIC EXPERIMENT - NOT CLINICAL VALIDATION | Clinical + OCT | 1274 | 984 | 319 | 0.5989 | 0.5698 | 0.6213 | 0.8315 | 0.2074 | 0.5195 | 0.2471 | 28 | 107 | 31 | 153 | age_years, sex, diabetes_duration_years, hba1c_percent, hypertension, dyslipidemia, renal_disease, egfr_ml_min_1_73m2, baseline_bcva_etdrs, baseline_cst_um, irf_present, srf_present, dril_present, hrf_present, ez_disruption_present | True | NOT_VALIDATED |

## Paired Cases

Clinical-only and Clinical + OCT models use identical eligible eyes, identical held-out patients, and fitted preprocessing inside each training fold/split.