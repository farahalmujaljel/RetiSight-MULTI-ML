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
