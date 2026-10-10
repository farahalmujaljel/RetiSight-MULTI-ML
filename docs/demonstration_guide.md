# Demonstration Guide

This guide demonstrates completed, independently valid MULTI-ML deliverables without requiring unresolved cross-dataset verification or six-month response labels.

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
```

Place authorized source files in `data/raw/`:

- `Clinical_Data_Images.xlsx`
- `Biomarker_Clinical_Data_Images.csv`
- `OCT-DME.xlsx`

## Rebuild Outputs

```bash
PYTHONPATH=src .venv/bin/python -m retisight_multi_ml.cli --config configs/pipeline.yaml full
```

## Independent OLIVES-Native Outputs

- Row-level export, ignored by Git: `data/processed/olives_native_baseline.csv`
- Aggregate validation: `reports/features/olives_native_dataset_validation.md`
- Aggregate biomarkers: `reports/features/olives_native_biomarker_statistics.md`

## Modeling Status

Real model training remains disabled. Model infrastructure is tested with synthetic fixtures only and is summarized in `reports/modeling/model_infrastructure_readiness.md`.

## Validation

```bash
PYTHONPATH=src .venv/bin/python -m pytest
.venv/bin/ruff check src tests
```

