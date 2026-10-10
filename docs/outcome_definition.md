# Outcome Definition

The candidate endpoint is visual-acuity improvement of at least five ETDRS letters approximately six months after baseline, using 150-210 days where supported.

The closure review found that the ID-bearing OCT-DME worksheets do not expose usable 150-210 day week/date timing in the parsed workbook, while the TREX/GILA Vision worksheets contain week-valued ETDRS trajectories but no `StudyID` column. Row-order linkage between those sheets is not assumed.

The current pipeline audits candidate follow-up availability but does not promote labels for modeling unless anti-VEGF exposure, time zero, endpoint interpretation, and any worksheet crosswalk are clinically reviewed.

MULTI-06A adds an OLIVES-native recovery audit from `Clinical_Data_Images.xlsx`. It reconstructs native patient-eye-visit BCVA/CST records, but TREX-DME OLIVES visits are labelled as `V1` through `V27` rather than documented elapsed weeks or dates. Therefore, a 150-210 day endpoint is not calculated from OLIVES-native data.
