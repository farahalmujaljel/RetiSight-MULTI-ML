# Limitations

- Public file linkage is currently exact-match candidate linkage only; independently verified row-level identity requires source-documentation or data-owner confirmation.
- Treatment exposure and endpoint timing require clinical review.
- Vision trajectory sheets lack `StudyID`; using them for outcomes requires an approved crosswalk or source confirmation, not row-order assumptions.
- OLIVES-native TREX-DME visit labels are sequence labels (`V1`...`V27`) without documented elapsed days in the ML-centric table; these are not sufficient for a six-month response label.
- Longitudinal BCVA/CST agreement can strengthen candidate linkage evidence, but it is not a substitute for a source-owner crosswalk.
- The OLIVES-native baseline dataset is valid for internal descriptive analysis and feature engineering, but it does not contain validated six-month treatment-response labels.
- Constant or near-constant baseline biomarkers should be excluded or pre-specified carefully in any future model.
- Small cohort sizes may make grouped model evaluation statistically fragile.
- Generated row-level artifacts should remain untracked until redistribution permissions are confirmed.
