# MULTI-06A OLIVES-Native Longitudinal Outcome Recovery

This subtask investigates whether anti-VEGF response labels can be created entirely inside OLIVES, without promoting candidate cross-dataset links to verified OCT-DME links.

## Source Evidence

The OLIVES paper and supplement document that OLIVES includes native longitudinal clinical labels. The dataset summary reports 96 eyes with clinical labels, BCVA, CST, Patient ID, and Eye ID, and describes 56 center-involving DME eyes from TREX-DME. The supplement states that the ML-centric clinical file contains path names plus Eye ID, BCVA, CST, and Patient ID for all OCT scans, while the path encodes trial, TREX-DME arm, folder, visit, eye laterality, and image name.

Relevant public sources:

- Zenodo OLIVES record: https://zenodo.org/records/7105232
- OLIVES NeurIPS supplement: https://proceedings.neurips.cc/paper_files/paper/2022/file/3be60b4a739b95a07a944a1a2c41e05e-Supplemental-Datasets_and_Benchmarks.pdf
- VIP Cup OLIVES repository: https://github.com/olivesgatech/VIPCUP2023_OLIVES

## Internal OLIVES Reconstruction

Using only `Clinical_Data_Images.xlsx`, the pipeline reconstructs patient-eye-visit records from:

- `Patient_ID`
- `Eye_ID`
- OLIVES image path trial
- TREX-DME arm
- path visit label
- path laterality
- BCVA
- CST

Observed reconstruction:

- TREX-DME patients: 47
- TREX-DME eyes: 56
- TREX-DME eye-visits: 934
- Baseline V1 records: 56
- BCVA conflicts within patient-eye-visit: 0
- CST conflicts within patient-eye-visit: 0

This is an internally verified OLIVES cohort. It is distinct from candidate cross-dataset matches to `OCT-DME.xlsx`.

## Outcome Decision

Decision: `NOT_FEASIBLE`

Reason: TREX-DME OLIVES-native visits are labelled `V1` through `V27`, not as elapsed weeks or dates. The official documentation says TREX-DME visits occurred every 4-16 weeks, but does not map each `V` label to elapsed days for each eye. Therefore the pipeline cannot identify a 150-210 day endpoint from OLIVES-native TREX-DME labels without inventing timing.

Study arm is available from the path, but eye-level injection dates/counts before six months are not available in the ML-centric clinical table. Modeling remains disabled.

