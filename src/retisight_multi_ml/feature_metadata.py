from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class FeatureMetadata:
    feature_name: str
    source_dataset: str
    observation_time: str
    temporal_role: str
    unit: str | None
    data_type: str
    allowed_as_baseline_predictor: bool
    linkage_requirement: str


OLIVES_NATIVE_FEATURE_METADATA = [
    FeatureMetadata(
        "baseline_bcva_etdrs",
        "OLIVES Clinical_Data_Images.xlsx",
        "V1 baseline visit label",
        "baseline_predictor",
        "ETDRS letters",
        "number",
        True,
        "OLIVES-native Patient_ID/Eye_ID only",
    ),
    FeatureMetadata(
        "baseline_cst_um",
        "OLIVES Clinical_Data_Images.xlsx",
        "V1 baseline visit label",
        "baseline_predictor",
        "um",
        "number",
        True,
        "OLIVES-native Patient_ID/Eye_ID only",
    ),
    FeatureMetadata(
        "irf_present",
        "OLIVES Biomarker_Clinical_Data_Images.csv",
        "V1 baseline visit label",
        "baseline_predictor",
        "0/1",
        "integer",
        True,
        "OLIVES-native Patient_ID/Eye_ID only",
    ),
    FeatureMetadata(
        "srf_present",
        "OLIVES Biomarker_Clinical_Data_Images.csv",
        "V1 baseline visit label",
        "baseline_predictor",
        "0/1",
        "integer",
        True,
        "OLIVES-native Patient_ID/Eye_ID only",
    ),
    FeatureMetadata(
        "dril_present",
        "OLIVES Biomarker_Clinical_Data_Images.csv",
        "V1 baseline visit label",
        "baseline_predictor",
        "0/1",
        "integer",
        True,
        "OLIVES-native Patient_ID/Eye_ID only",
    ),
    FeatureMetadata(
        "hrf_present",
        "OLIVES Biomarker_Clinical_Data_Images.csv",
        "V1 baseline visit label",
        "baseline_predictor",
        "0/1",
        "integer",
        True,
        "OLIVES-native Patient_ID/Eye_ID only",
    ),
    FeatureMetadata(
        "ez_disruption_present",
        "OLIVES Biomarker_Clinical_Data_Images.csv",
        "V1 baseline visit label",
        "baseline_predictor",
        "0/1",
        "integer",
        True,
        "OLIVES-native Patient_ID/Eye_ID only",
    ),
    FeatureMetadata(
        "number_of_annotated_scans",
        "OLIVES Biomarker_Clinical_Data_Images.csv",
        "V1 baseline visit label",
        "baseline_predictor",
        "scan count",
        "integer",
        True,
        "OLIVES-native Patient_ID/Eye_ID only",
    ),
    FeatureMetadata(
        "endpoint_bcva",
        "OLIVES Clinical_Data_Images.xlsx",
        "post-baseline visit-index endpoint",
        "outcome_candidate",
        "ETDRS letters",
        "number",
        False,
        "not a baseline predictor",
    ),
    FeatureMetadata(
        "anti_vegf_injection_count_prior_12mo",
        "future hospital integration",
        "requires dated treatment history",
        "treatment_history",
        "count",
        "integer",
        False,
        "requires approved hospital source and prediction-time definition",
    ),
]


def feature_metadata_frame() -> pd.DataFrame:
    return pd.DataFrame([m.__dict__ for m in OLIVES_NATIVE_FEATURE_METADATA])


def validate_baseline_predictor_allowlist(feature_columns: list[str]) -> list[str]:
    metadata = {m.feature_name: m for m in OLIVES_NATIVE_FEATURE_METADATA}
    errors = []
    for feature in feature_columns:
        item = metadata.get(feature)
        if item is None:
            errors.append(f"No feature metadata for `{feature}`.")
            continue
        if not item.allowed_as_baseline_predictor:
            errors.append(f"`{feature}` is not allowed as a baseline predictor.")
        if item.temporal_role != "baseline_predictor":
            errors.append(f"`{feature}` has temporal role `{item.temporal_role}`.")
    return errors
