import pytest

from retisight_multi_ml.modeling import (
    OutcomeValidationManifest,
    authorize_synthetic_fixture_training,
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
    with pytest.raises(ValueError, match="exactly one"):
        compare_clinical_vs_oct_models(synthetic_modeling_dataset, "synthetic_outcome")


def test_synthetic_model_comparison_uses_same_fold_count(synthetic_modeling_dataset):
    results = compare_clinical_vs_oct_models(
        synthetic_modeling_dataset,
        "synthetic_outcome",
        n_splits=3,
        synthetic_authorization=authorize_synthetic_fixture_training("synthetic_modeling_fixture"),
    )
    assert set(results["model"]) == {"clinical_only", "clinical_plus_oct"}
    assert results.groupby("model")["fold"].nunique().to_dict() == {
        "clinical_only": 3,
        "clinical_plus_oct": 3,
    }
    assert set(results["auroc_status"]).issubset({"estimable", "not_estimable_single_class_test_fold"})
    assert results["synthetic_fixture_only"].all()


def test_synthetic_authorization_rejects_non_synthetic_fixture_name():
    with pytest.raises(ValueError, match="Synthetic fixture"):
        authorize_synthetic_fixture_training("real_olives")


def test_real_training_requires_valid_manifest(synthetic_modeling_dataset):
    bad_manifest = OutcomeValidationManifest(
        outcome_column="synthetic_outcome",
        group_column="research_patient_id",
        source_provenance="synthetic test",
        endpoint_definition="synthetic endpoint",
        time_zero="synthetic baseline",
        eligibility_criteria="synthetic only",
        clinical_approval_status="NOT_APPROVED",
        approved_by_role="none",
        validation_status="DRAFT",
        observed_label_count=len(synthetic_modeling_dataset),
        positive_count=int(synthetic_modeling_dataset["synthetic_outcome"].sum()),
        negative_count=int((1 - synthetic_modeling_dataset["synthetic_outcome"]).sum()),
    )
    with pytest.raises(ValueError, match="VALIDATED"):
        compare_clinical_vs_oct_models(
            synthetic_modeling_dataset,
            "synthetic_outcome",
            outcome_manifest=bad_manifest,
        )


def test_outcome_validation_rejects_missing_labels(synthetic_modeling_dataset):
    with pytest.raises(ValueError, match="required"):
        require_validated_outcome(synthetic_modeling_dataset, "missing_outcome")
