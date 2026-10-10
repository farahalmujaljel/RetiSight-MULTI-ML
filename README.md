# RetiSight MULTI-ML — Engineering Release & Scientific Validation

## Overview

This PR delivers the research-engineering implementation of **RetiSight MULTI-ML**, including OLIVES-native clinical/OCT data integration, baseline feature engineering, longitudinal linkage investigation, treatment-response feasibility auditing, model infrastructure, and integration contracts.

The pipeline is ready for engineering review, with scientific safeguards that prevent unsupported patient linkage or invalid treatment-response modeling.

## Release Status

| Flag | Status |
|---|---|
| `ENGINEERING_RELEASE_READY` | `true` |
| `CLINICAL_PREDICTION_READY` | `false` |
| `CROSS_DATASET_LINKAGE_EXTERNALLY_VERIFIED` | `false` |
| `SIX_MONTH_RESPONSE_MODELING_ENABLED` | `false` |

---

## Synthetic Demonstration

`MULTI-DEMO-01` adds a fully fictitious end-to-end multimodal proof of concept for hackathon demonstration only.

Run:

```bash
python -m retisight_multi_ml.cli --config configs/pipeline.yaml synthetic-demo
```

The command writes ignored synthetic row-level tables to `data/synthetic_demo/`, aggregate reports to `reports/demo/`, and synthetic-only artifacts to `artifacts/synthetic_demo/`.

All outputs are labeled `SYNTHETIC EXPERIMENT - NOT CLINICAL VALIDATION`. The real OLIVES/OCT-DME six-month treatment-response pathway remains blocked until verified linkage, visit timing, and treatment histories are available.

---

## 1. Data Integration & Processing

Implemented an end-to-end reproducible pipeline using three real research datasets:

- `Clinical_Data_Images.xlsx` — OLIVES clinical and image metadata
- `Biomarker_Clinical_Data_Images.csv` — expert-annotated OCT biomarkers
- `OCT-DME.xlsx` — TREX-DME longitudinal clinical workbook

### Implemented Capabilities

- Source inventory, provenance tracking, and file checksums
- Data cleaning, normalization, and patient/eye identifier standardization
- Patient-eye-visit reconstruction
- Baseline V1 clinical feature extraction
- Scan-level to eye-level OCT biomarker aggregation
- OLIVES-native baseline dataset generation independent of external OCT-DME linkage
- Canonical schema validation and aggregate reporting

### OLIVES-Native Cohort

| Metric | Result |
|---|---:|
| Unique patients | 47 |
| Unique eyes | 56 |
| Longitudinal eye-visits | 934 |
| Baseline eye records | 56 |
| Duplicate research-eye IDs | 0 |
| Missing baseline BCVA | 0 |
| Missing baseline CST | 0 |
| Detected clinical measurement conflicts | 0 |

### OCT Biomarker Statistics

| Biomarker | Positive eyes |
|---|---:|
| IRF | 56/56 |
| SRF | 24/56 |
| DRIL | 1/56 |
| HRF | 56/56 |
| EZ disruption | 19/56 |

> Research limitation: IRF and HRF presence are constant in the current baseline cohort, and DRIL prevalence is extremely low. These features require careful selection and interpretation in future modeling.

---

## 2. Cross-Dataset Linkage Investigation — MULTI-03/05

Investigated potential linkage between OLIVES patient-eye records and the OCT-DME clinical workbook using study identifiers and longitudinal clinical measurements.

### Findings

| Check | Result |
|---|---:|
| Candidate eye matches identified | 56 |
| Baseline BCVA agreement | 56/56 |
| Baseline CST agreement | 56/56 |
| Laterality agreement | 56/56 |
| Longitudinal BCVA/CST mismatches | 0 |

All 56 links remain classified as:

```text
TRAJECTORY_SUPPORTED_CANDIDATE
