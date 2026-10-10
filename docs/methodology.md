# Methodology

The pipeline inventories source files, normalizes identifiers and image-path structure, derives candidate patient-eye links, aggregates baseline OCT biomarkers from B-scan annotations, and constructs one row per verified research eye.

The observation unit is patient-eye at baseline. Image rows and B-scans are never treated as independent patient observations.

MULTI-06A reconstructs OLIVES-native patient-eye-visit records from the ML-centric clinical file. These records are internally valid for longitudinal description, but TREX-DME `V` labels are not converted into elapsed days without documented timing.

The independent completion track exports a separate OLIVES-native baseline dataset that does not require OCT-DME candidate links. It uses native OLIVES patient, eye, visit, BCVA, CST, arm, laterality, and baseline biomarker annotations.
