# Linkage Methodology

OLIVES image paths are parsed into trial, arm, study folder, visit, eye laterality, and image name. OCT-DME workbook records expose `StudyID`.

The implemented candidate rule is exact equality between the OLIVES study folder and OCT-DME `StudyID`, plus arm consistency where a worksheet-to-arm relationship is inferable.

String equality alone is not independently verified identity. The recovery investigation additionally compares baseline and longitudinal BCVA/CST trajectories and finds trajectory-supported candidates, but no row-level source crosswalk was found. MULTI-03 remains blocked until the data owner, study documentation, or an explicit crosswalk confirms the mapping.
