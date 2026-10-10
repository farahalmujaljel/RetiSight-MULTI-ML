# Outcome Feasibility

- Decision: REQUIRES_CLINICAL_REVIEW
- Linked baseline rows: 56
- Candidate source records with 150-210 day follow-up: 0
- Linked rows with candidate follow-up after conservative merge: 0
- Worksheet cells with 150-210 day ETDRS values across all sheets: 165
- Worksheet cells with 150-210 day ETDRS values in ID-bearing sheets: 0

The TREX/GILA Vision sheets contain week-valued ETDRS trajectories, but no `StudyID` column. The ID-bearing worksheets contain the patient identifiers but do not provide usable 150-210 day week values in the current parsed structure.

Six-month ETDRS candidates can be derived from week fields for some records, but treatment time zero and anti-VEGF exposure cannot be fully verified from the implemented public tables alone.

Candidate labels are not promoted to modeling labels until clinical review confirms endpoint and exposure assumptions.