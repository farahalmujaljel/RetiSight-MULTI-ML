from __future__ import annotations

import pandas as pd

from retisight_multi_ml.synthetic_demo.generator import (
    CLINICAL_FEATURES,
    OCT_FEATURES,
    OUTCOME_COLUMN,
    SyntheticDemoConfig,
    generate_synthetic_cohort,
    run_synthetic_demo,
    train_and_evaluate,
    validate_synthetic_tables,
)


def test_synthetic_generation_is_deterministic():
    config = SyntheticDemoConfig(n_patients=40, random_seed=123)
    first = generate_synthetic_cohort(config)
    second = generate_synthetic_cohort(config)
    pd.testing.assert_frame_equal(first["patients"], second["patients"])
    pd.testing.assert_frame_equal(first["eyes"], second["eyes"])
    pd.testing.assert_frame_equal(first["modeling_dataset"], second["modeling_dataset"])


def test_synthetic_cardinality_links_and_chronology():
    tables = generate_synthetic_cohort(SyntheticDemoConfig(n_patients=75, random_seed=456))
    assert tables["patients"]["synthetic_patient_id"].nunique() == 75
    assert tables["eyes"]["synthetic_patient_id"].isin(tables["patients"]["synthetic_patient_id"]).all()
    assert tables["visits"]["synthetic_eye_id"].isin(tables["eyes"]["synthetic_eye_id"]).all()
    assert tables["treatments"]["synthetic_eye_id"].isin(tables["eyes"]["synthetic_eye_id"]).all()
    assert tables["visits"]["elapsed_days_from_baseline"].ge(0).all()
    assert tables["treatments"]["elapsed_days_from_baseline"].ge(0).all()
    assert tables["patients"]["is_synthetic"].all()
    assert tables["eyes"]["is_synthetic"].all()


def test_six_month_outcomes_and_missingness_rules():
    config = SyntheticDemoConfig(n_patients=80, random_seed=789)
    tables = generate_synthetic_cohort(config)
    outcomes = tables["outcomes"]
    observed = outcomes[outcomes["outcome_status"] == "OBSERVED"]
    unavailable = outcomes[outcomes["outcome_status"] == "OUTCOME_UNAVAILABLE"]
    assert not observed.empty
    assert not unavailable.empty
    assert observed["outcome_visit_elapsed_days"].between(150, 210).all()
    assert (observed[OUTCOME_COLUMN] == (observed["bcva_letter_change"] >= 5).astype(int)).all()


def test_leakage_prevention_and_grouped_evaluation():
    config = SyntheticDemoConfig(n_patients=90, random_seed=111)
    tables = generate_synthetic_cohort(config)
    quality = validate_synthetic_tables(tables, config)
    assert quality["status"] == "PASSED"
    forbidden = {"followup_bcva_etdrs", "followup_cst_um", "cumulative_injections_before_endpoint", "bcva_letter_change"}
    assert not set(CLINICAL_FEATURES + OCT_FEATURES).intersection(forbidden)
    metrics, _, predictions = train_and_evaluate(tables["modeling_dataset"], config.random_seed)
    assert set(metrics["model"]) == {"Clinical-only", "Clinical + OCT"}
    assert predictions.groupby("model")["synthetic_eye_id"].nunique().nunique() == 1


def test_synthetic_demo_writes_outputs(tmp_path):
    summary = run_synthetic_demo(
        SyntheticDemoConfig(
            n_patients=60,
            random_seed=222,
            output_dir=str(tmp_path / "data"),
            reports_dir=str(tmp_path / "reports"),
            artifacts_dir=str(tmp_path / "artifacts"),
        )
    )
    assert summary["patient_count"] == 60
    assert summary["eligible_eye_count"] > 0
    assert summary["example_inference"]["is_synthetic"] is True
    assert (tmp_path / "data" / "synthetic_modeling_dataset.csv").exists()
    assert (tmp_path / "reports" / "synthetic_model_comparison.md").exists()
    assert (tmp_path / "artifacts" / "synthetic_clinical_plus_oct_model.joblib").exists()
