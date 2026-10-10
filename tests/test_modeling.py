import pytest

from retisight_multi_ml.modeling import (
    compare_clinical_vs_oct_models,
    make_grouped_folds,
    require_validated_outcome,
)


def test_grouped_folds_keep_patients_separate(synthetic_modeling_dataset):
    folds = make_grouped_folds(synthetic_modeling_dataset, "synthetic_outcome", n_splits=3)
    groups = synthetic_modeling_dataset["research_patient_id"].to_numpy()
    for train_idx, test_idx in folds:
        assert set(groups[train_idx]).isdisjoint(set(groups[test_idx]))


def test_model_training_requires_explicit_synthetic_flag(synthetic_modeling_dataset):
    with pytest.raises(ValueError, match="disabled"):
        compare_clinical_vs_oct_models(synthetic_modeling_dataset, "synthetic_outcome")


def test_synthetic_model_comparison_uses_same_fold_count(synthetic_modeling_dataset):
    results = compare_clinical_vs_oct_models(
        synthetic_modeling_dataset,
        "synthetic_outcome",
        n_splits=3,
        allow_synthetic=True,
    )
    assert set(results["model"]) == {"clinical_only", "clinical_plus_oct"}
    assert results.groupby("model")["fold"].nunique().to_dict() == {
        "clinical_only": 3,
        "clinical_plus_oct": 3,
    }
    assert results["synthetic_fixture_only"].all()


def test_outcome_validation_rejects_missing_labels(synthetic_modeling_dataset):
    with pytest.raises(ValueError, match="required"):
        require_validated_outcome(synthetic_modeling_dataset, "missing_outcome")
