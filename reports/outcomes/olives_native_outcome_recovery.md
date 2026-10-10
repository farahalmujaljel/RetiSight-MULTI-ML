# MULTI-06A OLIVES-Native Longitudinal Outcome Recovery

- Decision: NOT_FEASIBLE
- Internally verified OLIVES TREX-DME patients: 47
- Internally verified OLIVES TREX-DME eyes: 56
- TREX-DME eye-visit records: 934
- Baseline V1 TREX-DME records: 56
- TREX-DME records with documented 150-210 day timing: 0
- BCVA conflicts within patient-eye-visit: 0
- CST conflicts within patient-eye-visit: 0
- Non-49-scan patient-eye-visits: 5

## Cohort States

- Internally verified OLIVES patient-eye records: reconstructed from OLIVES-native `Patient_ID`, `Eye_ID`, path visit, BCVA, and CST.
- Candidate cross-dataset matches with OCT-DME.xlsx: exact path-folder/StudyID matches only.
- Externally verified cross-dataset links: 0.

## Scientific Decision

The OLIVES-native longitudinal table is suitable for descriptive patient-eye-visit reconstruction, but it does not support a scientifically defensible six-month anti-VEGF response label without additional timing and treatment documentation.

Reasons:

- TREX-DME OLIVES-native visit labels are sequence labels (V1-V27), not elapsed weeks or dates.
- No TREX-DME OLIVES-native records have documented elapsed days in the 150-210 day window.
- Study arm is available from the OLIVES path, but eye-level injection dates/counts before six months are not available in the ML-centric clinical table.
- The official documentation supports TREX-DME treatment cohorts and visits every 4-16 weeks, but does not map each V-label to an elapsed day.

Modeling remains disabled. Do not assume that `V22` or any other TREX-DME `V` label equals six months.