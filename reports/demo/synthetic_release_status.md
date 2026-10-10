# SYNTHETIC EXPERIMENT - NOT CLINICAL VALIDATION

## Synthetic Release Status

- MULTI-DEMO-01: PASSED_SYNTHETIC_DEMONSTRATION
- Real OLIVES/OCT-DME treatment-response modeling remains blocked pending verified linkage, visit timing, and treatment histories.
- No synthetic identifier crosswalk is used to verify genuine records.
- No generated probability is suitable for clinical decisions.

## Example Inference

```json
{
  "synthetic_patient_id": "SYN-P-00001",
  "synthetic_eye_id": "SYN-P-00001-E1-OS",
  "predicted_probability_ge_5_letter_gain": 0.5870083261275514,
  "model_identity": "Clinical + OCT synthetic logistic regression",
  "predictor_availability": {
    "age_years": true,
    "sex": true,
    "diabetes_duration_years": true,
    "hba1c_percent": true,
    "hypertension": true,
    "dyslipidemia": true,
    "renal_disease": true,
    "egfr_ml_min_1_73m2": true,
    "baseline_bcva_etdrs": true,
    "baseline_cst_um": true,
    "irf_present": true,
    "srf_present": true,
    "dril_present": true,
    "hrf_present": true,
    "ez_disruption_present": true
  },
  "is_synthetic": true,
  "clinical_validation_status": "NOT_VALIDATED",
  "warning": "Synthetic demonstration probability only; not suitable for clinical decisions or treatment recommendations."
}
```