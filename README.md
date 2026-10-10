# RetiSight MULTI-ML

Research engineering pipeline for creating a traceable multimodal DME baseline dataset from OCT-DME and OLIVES tabular sources, then auditing whether real anti-VEGF response modeling is scientifically feasible.

This repository is for exploratory research only. It is not a clinical decision-support device.

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
```

Place authorized source files in `data/raw/`:
- `OCT-DME.xlsx`
- `Biomarker_Clinical_Data_Images.csv`
- `Clinical_Data_Images.xlsx`

Raw data and row-level outputs are ignored by Git.

## Synthetic Demonstration

`MULTI-DEMO-01` adds a fully fictitious end-to-end multimodal proof of concept for hackathon demonstration only.

Run:

```bash
python -m retisight_multi_ml.cli --config configs/pipeline.yaml synthetic-demo
```

The command writes ignored synthetic row-level tables to `data/synthetic_demo/`, aggregate reports to `reports/demo/`, and synthetic-only artifacts to `artifacts/synthetic_demo/`.

All outputs are labeled `SYNTHETIC EXPERIMENT - NOT CLINICAL VALIDATION`. The real OLIVES/OCT-DME six-month treatment-response pathway remains blocked until verified linkage, visit timing, and treatment histories are available.

---

## Run

```bash
PYTHONPATH=src .venv/bin/python -m retisight_multi_ml.cli --config configs/pipeline.yaml full
PYTHONPATH=src .venv/bin/python -m retisight_multi_ml.cli --config configs/pipeline.yaml olives-native-outcomes
PYTHONPATH=src .venv/bin/python -m pytest
.venv/bin/ruff check src tests
```

The full command regenerates inventory, cleaned tables, linkage reports, baseline features, the canonical multimodal dataset, outcome feasibility audit, schema files, and final status reports.

## Limitations

The implemented linkage uses exact agreement between OLIVES image-path study folders and OCT-DME `StudyID`, with arm consistency where inferable. This produces candidate exact matches, not independently verified identity. Source documentation or clinical data-owner confirmation is required before treating the link as definitive.

Response modeling is intentionally omitted when the outcome audit requires clinical review.

The OLIVES-native longitudinal recovery audit reconstructs patient-eye-visit records internally, but does not infer elapsed days from TREX-DME `V` visit labels.

The recovery investigation can be regenerated with:

```bash
PYTHONPATH=src .venv/bin/python -m retisight_multi_ml.cli --config configs/pipeline.yaml recovery-investigation
```

The independent OLIVES-native baseline export can be regenerated with:

```bash
PYTHONPATH=src .venv/bin/python -m retisight_multi_ml.cli --config configs/pipeline.yaml olives-native-baseline
```
