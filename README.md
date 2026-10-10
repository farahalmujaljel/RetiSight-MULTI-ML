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

## Run

```bash
PYTHONPATH=src .venv/bin/python -m retisight_multi_ml.cli --config configs/pipeline.yaml full
PYTHONPATH=src .venv/bin/python -m pytest
.venv/bin/ruff check src tests
```

The full command regenerates inventory, cleaned tables, linkage reports, baseline features, the canonical multimodal dataset, outcome feasibility audit, schema files, and final status reports.

## Limitations

The implemented linkage uses exact agreement between OLIVES image-path study folders and OCT-DME `StudyID`, with arm consistency where inferable. This produces candidate exact matches, not independently verified identity. Source documentation or clinical data-owner confirmation is required before treating the link as definitive.

Response modeling is intentionally omitted when the outcome audit requires clinical review.
