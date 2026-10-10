# Linkage Methodology

OLIVES image paths are parsed into trial, arm, study folder, visit, eye laterality, and image name. OCT-DME workbook records expose `StudyID`.

The implemented accepted rule is exact equality between the OLIVES study folder and OCT-DME `StudyID`, plus arm consistency where a worksheet-to-arm relationship is inferable.

String equality alone is recorded as a limitation requiring source-documentation confirmation before clinical interpretation.

