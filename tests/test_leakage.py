from retisight_multi_ml.dataset_builder import CANONICAL_COLUMNS


def test_dataset_schema_excludes_future_outcome_predictors():
    forbidden = {"change_etdrs", "total_injections", "response_5_letters_6mo"}
    assert forbidden.isdisjoint({c.lower() for c in CANONICAL_COLUMNS})

