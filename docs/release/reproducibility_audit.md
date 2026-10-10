# Reproducibility Audit

Audit date: 2026-10-11

## Commands

```bash
PYTHONPATH=src .venv/bin/python -m retisight_multi_ml.cli --config configs/pipeline.yaml full
.venv/bin/pytest
.venv/bin/python -m ruff check src tests
python -m pytest
```

## Results

- Full pipeline: passed locally with private raw files present.
- Test suite: 27 passed on Python 3.13.5 system environment.
- Test suite: 27 passed on Python 3.14.5 virtual environment.
- Ruff: passed after one import-order issue found during the audit was fixed.
- GitHub Actions `ci` run 38088312519 passed on Ubuntu/Python 3.11 for commit `77e60a9`.

## Generated Outputs

The pipeline generates row-level exports under ignored directories and aggregate Markdown reports under `reports/`. Row-level CSV/JSON outputs are intentionally ignored.

## Environment Notes

- CI targets Python 3.11 on Ubuntu.
- Local virtualenv uses Python 3.14.5.
- Local system Python is 3.13.5.
- Python 3.11 was not locally available; GitHub Actions is the authoritative Python 3.11 execution environment.
- `requirements-lock.txt` is pinned to versions with Python 3.11 manylinux wheels verified by pip's platform resolver.

## Reproducibility Decision

The repository is reproducible for public code, schemas, synthetic fixtures, and aggregate reports. Full raw-data pipeline execution requires private local source files.
