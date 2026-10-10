# RetiSight MULTI-ML Agent Instructions

Objective: maintain a reproducible multimodal DME research pipeline linking systemic/baseline clinical data, OCT-DME longitudinal measurements, and OLIVES structured OCT biomarker annotations.

Scientific integrity rules:
- Do not fabricate clinical records, labels, treatments, dates, identifiers, or model metrics.
- Accept patient-eye linkage only when a traceable rule and evidence are recorded.
- Keep predictors baseline-only; never use future visits, treatment totals, or outcome-derived fields as model inputs.
- Keep both eyes from the same patient in the same validation group.
- Train response models only after `reports/outcomes/outcome_definition.md` records a feasible endpoint.

Repository structure:
- `configs/`: reproducible configuration.
- `src/retisight_multi_ml/`: importable pipeline package and CLI.
- `schemas/`: canonical schema and feature dictionaries.
- `data/raw/`: local protected source files, ignored by Git.
- `data/interim/`, `data/processed/`, `reports/`, `artifacts/`: generated outputs, ignored by default where row-level.

Primary commands:
- `python -m retisight_multi_ml.cli --config configs/pipeline.yaml full`
- `pytest`
- `ruff check src tests`

Progress tracking:
- Machine-readable: `reports/final/progress.json`
- Human-readable: `reports/final/status.md` and `reports/final/final_report.md`

Privacy:
- This is a public repository. Do not commit raw data, row-level derived data, secrets, tokens, protected OCT images, or generated reports containing redistributable-sensitive rows unless permissions are confirmed.

