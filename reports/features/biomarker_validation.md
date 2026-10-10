# Biomarker Validation

Baseline OCT biomarkers are aggregated from OLIVES `V1` B-scans only.
No post-baseline biomarker annotations are included in the baseline feature table.

## Linked Candidate Baseline Counts

- irf_present: positives=56/56; distribution={1: 56}
- srf_present: positives=24/56; distribution={0: 32, 1: 24}
- dril_present: positives=1/56; distribution={0: 55, 1: 1}
- hrf_present: positives=56/56; distribution={1: 56}
- ez_disruption_present: positives=19/56; distribution={0: 37, 1: 19}

## Predictor Suitability

- `irf_present` and `hrf_present` are constant positive in the linked candidate baseline cohort and should be excluded from comparative predictive models unless a later cohort introduces variation.
- `dril_present` is extremely rare in this cohort (1 positive eye) and is unstable as an individual predictive input in small-sample modeling.
- These warnings describe annotation distributions only; they are not clinical findings.