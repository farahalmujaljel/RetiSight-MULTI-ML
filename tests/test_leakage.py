from retisight_multi_ml.dataset_builder import CANONICAL_COLUMNS


def test_dataset_schema_excludes_future_outcome_predictors():
    forbidden = {"change_etdrs", "total_injections", "response_5_letters_6mo"}
    assert forbidden.isdisjoint({c.lower() for c in CANONICAL_COLUMNS})


def test_olives_native_features_do_not_include_post_baseline_patterns():
    from retisight_multi_ml.olives_native_dataset import BIOMARKER_FEATURES

    forbidden_tokens = ("post", "follow", "change", "response")
    assert all(not any(token in feature for token in forbidden_tokens) for feature in BIOMARKER_FEATURES)


def test_feature_metadata_rejects_misleading_post_baseline_name():
    from retisight_multi_ml.feature_metadata import validate_baseline_predictor_allowlist

    errors = validate_baseline_predictor_allowlist(["baseline_bcva_etdrs", "endpoint_bcva"])
    assert any("not allowed" in error for error in errors)
