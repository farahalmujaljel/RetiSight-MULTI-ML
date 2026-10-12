# RetiSight MULTI-ML — Engineering Release & Synthetic Training Demonstration

## Summary

This PR delivers the RetiSight MULTI-ML engineering release for the anti-VEGF response-prediction pipeline. It establishes the reproducible project structure, clinical/OCT schema contracts, feature engineering layer, model-training guardrails, CI validation, and release documentation.

Important scientific note: the training result shown below is from **synthetic data only**. It is included to demonstrate that the pipeline can execute end-to-end. It is **not** a validated clinical result and must not be presented as real patient performance.

## Synthetic Training Demonstration Result

| Item | Result |
| --- | ---: |
| Synthetic patients | 1,000 |
| Synthetic eyes | 1,306 |
| Eligible synthetic outcome eyes | 1,274 |
| Outcome-missing eyes | 32 |
| Data type | Synthetic only |
| Clinical interpretation | Not allowed |

This training result is based on **synthetic data only**. It demonstrates that the ML pipeline can run end-to-end, but it is **not** a real clinical performance result and should not be interpreted as validated anti-VEGF response prediction.

## Data Pathways

| Pathway | Data | Pipeline step | Status | Clinical meaning |
| --- | --- | --- | --- | --- |
| Synthetic data | Fictitious DME patients | Generation → Training → Evaluation | Locally tested | Not clinically validated |
| Real data | OLIVES + OCT-DME | Cleaning → Biomarkers → Validation | Engineering ready | Clinical response modeling blocked |

## Synthetic Model Comparison

| Model | Synthetic score |
| --- | ---: |
| Random ranking baseline | 0.5000 |
| Clinical-only | 0.5629 |
| Clinical + OCT | 0.5698 |
| Difference between clinical-only and clinical + OCT | 0.0069 |
| Perfect ranking reference | 1.0000 |

The synthetic comparison shows that the Clinical + OCT demo model scored slightly higher than the Clinical-only demo model by `0.0069`. Because this is synthetic data, the result only validates pipeline behavior. It does **not** prove that OCT improves prediction for real patients.

## Implementation Methodology

```mermaid
flowchart TD
    A[Source data audit] --> B[Clinical and OCT schema contracts]
    B --> C[Baseline feature engineering]
    C --> D[Outcome feasibility checks]
    D --> E{Validated real outcome labels?}
    E -- No --> F[Disable real clinical model training]
    E -- Yes, future only --> G[Patient-grouped model evaluation]
    F --> H[Synthetic demo training only]
    G --> I[Clinical metrics report]
    H --> J[Engineering readiness report]
