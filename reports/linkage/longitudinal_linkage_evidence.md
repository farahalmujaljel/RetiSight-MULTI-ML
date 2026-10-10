# Longitudinal Linkage Evidence

This investigation compares OLIVES-native TREX-DME patient-eye-visit BCVA/CST trajectories with primary OCT-DME ID-bearing worksheets.

## Source-Backed Inputs

- OLIVES ML-centric clinical labels: path, BCVA, CST, Eye_ID, Patient_ID for all 78,185 OCT scans.
- OLIVES paths encode trial, treatment arm, folder, visit, eye laterality, and image name.
- OCT-DME primary worksheets provide StudyID, arm-specific workbook sheet, baseline and longitudinal ETDRS/OCT values.
- OLIVES source references: Zenodo DOI 10.5281/zenodo.7105232 and the NeurIPS 2022 OLIVES supplement.
- TREX-DME timing source reference: protocol/publication descriptions of monthly loading and treat-and-extend schedules.

## Results

- Candidate exact path-folder/StudyID eyes evaluated: 56
- Baseline BCVA exact matches: 56/56
- Baseline CST exact matches: 56/56
- Laterality suffix matches: 56/56
- BCVA mismatches across overlapping visits: 0
- CST mismatches across overlapping visits: 0
- Classification counts: {'TRAJECTORY_SUPPORTED_CANDIDATE': 56}
- Exact competing trajectory counts: {1: 56}

## Scientific Decision

The 56 links are upgraded from simple identifier matches to trajectory-supported candidates because arm, laterality, baseline BCVA/CST, and overlapping longitudinal BCVA/CST values agree. They are still not externally verified links because no authoritative row-level crosswalk or data-owner confirmation was found.