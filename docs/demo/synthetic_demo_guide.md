# Synthetic Demo Guide

Run the default demonstration:

```bash
python -m retisight_multi_ml.cli --config configs/pipeline.yaml synthetic-demo
```

Run a faster smoke demonstration:

```bash
python -m retisight_multi_ml.cli --config configs/pipeline.yaml synthetic-demo --n-patients 80 --seed 20261011
```

Generated row-level synthetic data are written to `data/synthetic_demo/`. Aggregate reports are written to `reports/demo/`. Model artifacts are synthetic-only and written to `artifacts/synthetic_demo/`.
