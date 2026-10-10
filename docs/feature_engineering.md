# Feature Engineering

Baseline features include available systemic fields, ophthalmic fields, and aggregated baseline OCT biomarkers.

OCT biomarkers are aggregated from `V1` annotated scans. Presence is `1` when at least one usable baseline scan is positive, `0` when usable scans exist and none are positive, and missing when no usable annotation exists.

Observed scan proportions are descriptive annotation summaries, not calibrated probabilities.

