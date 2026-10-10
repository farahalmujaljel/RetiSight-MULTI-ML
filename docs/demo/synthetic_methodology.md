# Synthetic Methodology

All data generated for MULTI-DEMO-01 are fictitious and are used only to demonstrate software flow.

The simulator creates baseline systemic features, baseline eye-level OCT/vision features, anti-VEGF treatment events, longitudinal visits, and a noisy six-month visual-response process. The outcome is observed only when a synthetic visit exists from 150 to 210 days after treatment baseline, using the visit closest to day 180.

Response is defined as `follow-up ETDRS - baseline ETDRS >= 5 letters`. Simulation noise, missingness, and heterogeneous feature effects are included to avoid perfectly separable labels.
