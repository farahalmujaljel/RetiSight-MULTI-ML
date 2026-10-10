# MULTI-ML Closure Review

Review date: 2026-10-10

## MULTI-03 Linkage Verification

The pipeline reproduces 56 exact-match candidate TREX-DME/OLIVES eyes from 47 patients by matching the OLIVES image-path study folder to OCT-DME `StudyID`, with arm consistency where inferable.

Available project documentation states that only 56 TREX-DME eyes are included in OLIVES, which is consistent with the reproduced candidate count. However, no row-level source crosswalk or documentation was found that independently proves each exact identifier match is the same clinical study eye. Therefore:

- Reproducible candidate matching: yes.
- Independently verified identity: no.
- DoD status: `BLOCKED_EXTERNAL_CROSSWALK_CONFIRMATION`.

No model training or clinical interpretation should treat the candidate cohort as verified until the data owner, source documentation, or an explicit crosswalk confirms the mapping.

## MULTI-06 Outcome Feasibility

All eight OCT-DME worksheets were inspected.

- ID-bearing worksheets: `Monthly`, `TREX`, `GILA`, `Year 3 Monthly`, `Year 3 TREX`, `Year 3 GILA`.
- Week-valued ETDRS trajectory worksheets without `StudyID`: `TREX Vision`, `GILA Vision`.
- 150-210 day ETDRS cells across all sheets: 165.
- 150-210 day ETDRS cells in ID-bearing sheets: 0.

The conservative audit returns zero six-month linked outcome records because the sheets with usable week trajectories do not expose `StudyID`. Row-order linkage between Vision sheets and ID-bearing sheets is not assumed.

Outcome feasibility remains `REQUIRES_CLINICAL_REVIEW`.

## MULTI-04/05 Biomarker Validation

The linked candidate baseline cohort contains 56 eyes, each with 49 baseline `V1` annotated scans.

- `irf_present`: 56/56 positive.
- `hrf_present`: 56/56 positive.
- `dril_present`: 1/56 positive.
- `srf_present`: 24/56 positive.
- `ez_disruption_present`: 19/56 positive.

IRF and HRF are constant positive in this candidate cohort and should not be used as informative predictors in a comparative model unless a future verified cohort introduces variation. DRIL is extremely rare and unstable as a standalone predictor in a small cohort.

## Ophthalmology-Team Questions

1. Does the OLIVES TREX-DME path folder exactly encode the OCT-DME `StudyID` for every shared eye?
2. Is there an approved source crosswalk mapping OLIVES `Patient_ID`, `Eye_ID`, image path, and laterality to OCT-DME `StudyID` and study eye?
3. Are the `TREX Vision` and `GILA Vision` rows in the same order as the ID-bearing TREX/GILA worksheets, or is there another identifier/crosswalk for those sheets?
4. What is the clinically valid time zero for response prediction: screening, baseline/randomization, first ranibizumab injection, or another visit?
5. Is a 150-210 day window acceptable for an approximately six-month ETDRS endpoint in TREX-DME, or should protocol-defined visits be used instead?
6. Can treatment exposure be confirmed per eye before the candidate endpoint, including arm-specific injection/laser rules?
7. Should response be defined as at least 5, 10, or 15 ETDRS letters, and should worsening/stability be modeled separately?
8. Are baseline V1 OLIVES annotations the correct OCT biomarker time point for the intended prediction task?
9. Are IRF and HRF expected to be universally present in this DME subset, and should they be excluded as non-informative cohort constants?
10. Is DRIL's 1/56 prevalence clinically plausible for these annotations, or does it indicate an annotation-definition or label-export issue?

