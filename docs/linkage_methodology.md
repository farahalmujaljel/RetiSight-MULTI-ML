# Linkage Methodology

OLIVES image paths are parsed into trial, arm, study folder, visit, eye laterality, and image name. OCT-DME workbook records expose `StudyID`.

The implemented candidate rule is exact equality between the OLIVES study folder and OCT-DME `StudyID`, plus arm consistency where a worksheet-to-arm relationship is inferable.

String equality alone is not independently verified identity. Available project documentation says 56 TREX-DME eyes are included in OLIVES, but no row-level source crosswalk was found during the closure review. MULTI-03 remains blocked until the data owner, study documentation, or an explicit crosswalk confirms the mapping.
