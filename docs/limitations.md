# Limitations

- Public file linkage is currently exact-match candidate linkage only; independently verified row-level identity requires source-documentation or data-owner confirmation.
- Treatment exposure and endpoint timing require clinical review.
- Vision trajectory sheets lack `StudyID`; using them for outcomes requires an approved crosswalk or source confirmation, not row-order assumptions.
- Constant or near-constant baseline biomarkers should be excluded or pre-specified carefully in any future model.
- Small cohort sizes may make grouped model evaluation statistically fragile.
- Generated row-level artifacts should remain untracked until redistribution permissions are confirmed.
