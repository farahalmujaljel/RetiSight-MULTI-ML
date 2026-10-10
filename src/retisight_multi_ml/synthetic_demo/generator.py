from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedGroupKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TITLE = "SYNTHETIC EXPERIMENT - NOT CLINICAL VALIDATION"
PROVENANCE = "SYNTHETIC_DEMO_MULTI_DEMO_01"
CLINICAL_FEATURES = [
    "age_years",
    "sex",
    "diabetes_duration_years",
    "hba1c_percent",
    "hypertension",
    "dyslipidemia",
    "renal_disease",
    "egfr_ml_min_1_73m2",
    "baseline_bcva_etdrs",
    "baseline_cst_um",
]
OCT_FEATURES = [
    "irf_present",
    "srf_present",
    "dril_present",
    "hrf_present",
    "ez_disruption_present",
]
OUTCOME_COLUMN = "six_month_response_ge_5_letters"
GROUP_COLUMN = "synthetic_patient_id"


@dataclass(frozen=True)
class SyntheticDemoConfig:
    n_patients: int = 1000
    random_seed: int = 20261011
    output_dir: str = "data/synthetic_demo"
    reports_dir: str = "reports/demo"
    artifacts_dir: str = "artifacts/synthetic_demo"
    start_date_min: str = "2024-01-01"
    start_date_max: str = "2024-12-31"
    two_eye_probability: float = 0.28
    endpoint_window_min_days: int = 150
    endpoint_window_max_days: int = 210
    endpoint_target_days: int = 180


def generate_synthetic_cohort(config: SyntheticDemoConfig) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(config.random_seed)
    patient_rows: list[dict[str, Any]] = []
    eye_rows: list[dict[str, Any]] = []
    visit_rows: list[dict[str, Any]] = []
    treatment_rows: list[dict[str, Any]] = []
    biomarker_rows: list[dict[str, Any]] = []
    outcome_rows: list[dict[str, Any]] = []
    start_min = pd.Timestamp(config.start_date_min)
    start_span = (pd.Timestamp(config.start_date_max) - start_min).days

    for patient_idx in range(1, config.n_patients + 1):
        patient_id = f"SYN-P-{patient_idx:05d}"
        age = int(np.clip(rng.normal(63, 10), 35, 90))
        sex = rng.choice(["Female", "Male"], p=[0.48, 0.52])
        diabetes_duration = float(np.round(np.clip(rng.gamma(4.0, 3.2), 1, 42), 1))
        hba1c = float(np.round(np.clip(rng.normal(7.8 + diabetes_duration / 35, 1.15), 5.3, 12.8), 1))
        hypertension = bool(rng.random() < _sigmoid(-2.2 + 0.045 * age + 0.025 * diabetes_duration))
        dyslipidemia = bool(rng.random() < _sigmoid(-1.2 + 0.025 * age))
        renal_disease = bool(rng.random() < _sigmoid(-3.0 + 0.035 * age + 0.08 * (hba1c - 7.0)))
        egfr = float(np.round(np.clip(rng.normal(88 - 0.55 * (age - 45) - 15 * renal_disease, 12), 18, 120), 1))
        patient_rows.append(
            {
                "synthetic_patient_id": patient_id,
                "age_years": age,
                "sex": sex,
                "diabetes_duration_years": diabetes_duration,
                "hba1c_percent": hba1c,
                "hypertension": hypertension,
                "dyslipidemia": dyslipidemia,
                "renal_disease": renal_disease,
                "egfr_ml_min_1_73m2": egfr,
                "is_synthetic": True,
                "synthetic_provenance": PROVENANCE,
            }
        )
        lateralities = ["OD", "OS"] if rng.random() < config.two_eye_probability else [str(rng.choice(["OD", "OS"]))]
        for laterality in lateralities:
            eye_number = len([row for row in eye_rows if row["synthetic_patient_id"] == patient_id]) + 1
            eye_id = f"{patient_id}-E{eye_number}-{laterality}"
            baseline_date = start_min + pd.Timedelta(days=int(rng.integers(0, start_span + 1)))
            baseline_bcva = int(np.clip(np.round(rng.normal(62 - 0.28 * (hba1c - 7.0) - 0.08 * diabetes_duration, 11)), 20, 88))
            baseline_cst = int(np.clip(np.round(rng.normal(430 + 13 * (hba1c - 7.0), 72)), 245, 760))
            irf = int(rng.random() < _sigmoid(-1.0 + 0.008 * (baseline_cst - 350)))
            srf = int(rng.random() < _sigmoid(-2.2 + 0.005 * (baseline_cst - 350)))
            dril = int(rng.random() < _sigmoid(-3.0 + 0.02 * (70 - baseline_bcva) + 0.004 * (baseline_cst - 400)))
            hrf = int(rng.random() < _sigmoid(-0.8 + 0.006 * (baseline_cst - 350)))
            ez = int(rng.random() < _sigmoid(-2.4 + 0.018 * (68 - baseline_bcva) + 0.7 * dril))
            agent = str(rng.choice(["aflibercept", "bevacizumab", "ranibizumab"], p=[0.42, 0.38, 0.20]))
            ltf = bool(rng.random() < _sigmoid(-3.2 + 0.04 * (hba1c - 7.0) + 0.012 * (age - 65)))
            planned_injections = int(np.clip(np.round(rng.normal(5.7 - 0.9 * ltf, 1.15)), 1, 8))
            latent_change = (
                4.0
                + 0.12 * (65 - baseline_bcva)
                + 0.010 * (baseline_cst - 380)
                - 1.15 * dril
                - 0.9 * ez
                - 0.45 * (hba1c - 7.5)
                + 0.35 * planned_injections
                + rng.normal(0, 6.0)
            )
            eye_rows.append(
                {
                    "synthetic_eye_id": eye_id,
                    "synthetic_patient_id": patient_id,
                    "laterality": laterality,
                    "baseline_date": baseline_date.date().isoformat(),
                    "baseline_bcva_etdrs": baseline_bcva,
                    "baseline_cst_um": baseline_cst,
                    "treatment_start_date": baseline_date.date().isoformat(),
                    "synthetic_anti_vegf_agent": agent,
                    "is_synthetic": True,
                    "synthetic_provenance": PROVENANCE,
                }
            )
            biomarker_rows.append(
                {
                    "synthetic_eye_id": eye_id,
                    "synthetic_patient_id": patient_id,
                    "biomarker_timepoint": "baseline",
                    "irf_present": irf,
                    "srf_present": srf,
                    "dril_present": dril,
                    "hrf_present": hrf,
                    "ez_disruption_present": ez,
                    "is_synthetic": True,
                    "synthetic_provenance": PROVENANCE,
                }
            )
            injection_days = sorted(int(day) for day in np.clip(rng.normal(np.arange(planned_injections) * 30 + 3, 6), 0, 205))
            for injection_idx, elapsed in enumerate(injection_days, start=1):
                treatment_rows.append(
                    {
                        "synthetic_treatment_id": f"{eye_id}-TX-{injection_idx:02d}",
                        "synthetic_eye_id": eye_id,
                        "synthetic_patient_id": patient_id,
                        "anti_vegf_agent": agent,
                        "treatment_date": (baseline_date + pd.Timedelta(days=elapsed)).date().isoformat(),
                        "elapsed_days_from_baseline": elapsed,
                        "is_synthetic": True,
                        "synthetic_provenance": PROVENANCE,
                    }
                )
            visit_schedule = [0, 30, 60, 90, 120, 150, 180, 210, 240]
            if ltf:
                visit_schedule = [day for day in visit_schedule if day < int(rng.choice([120, 150, 180]))]
            for elapsed in visit_schedule:
                if elapsed > 0 and rng.random() < (0.10 if elapsed not in {150, 180, 210} else 0.07):
                    continue
                progress = min(elapsed / config.endpoint_target_days, 1.25)
                bcva = int(np.clip(np.round(baseline_bcva + latent_change * progress + rng.normal(0, 3.0)), 0, 100))
                cst = int(np.clip(np.round(baseline_cst - (45 + 7 * planned_injections + 22 * irf + 18 * srf) * progress + rng.normal(0, 28)), 180, 850))
                visit_rows.append(
                    {
                        "synthetic_visit_id": f"{eye_id}-V-{elapsed:03d}",
                        "synthetic_eye_id": eye_id,
                        "synthetic_patient_id": patient_id,
                        "visit_date": (baseline_date + pd.Timedelta(days=elapsed)).date().isoformat(),
                        "elapsed_days_from_baseline": elapsed,
                        "followup_bcva_etdrs": bcva,
                        "followup_cst_um": cst,
                        "visit_missingness_flag": False,
                        "loss_to_followup_flag": ltf,
                        "is_synthetic": True,
                        "synthetic_provenance": PROVENANCE,
                    }
                )
            outcome_rows.append(_derive_eye_outcome(eye_id, baseline_bcva, visit_rows, config))

    patients = pd.DataFrame(patient_rows)
    eyes = pd.DataFrame(eye_rows)
    visits = pd.DataFrame(visit_rows)
    treatments = pd.DataFrame(treatment_rows)
    biomarkers = pd.DataFrame(biomarker_rows)
    outcomes = pd.DataFrame(outcome_rows)
    treatment_counts = (
        treatments[treatments["elapsed_days_from_baseline"].between(0, config.endpoint_target_days)]
        .groupby("synthetic_eye_id")
        .size()
        .rename("cumulative_injections_before_endpoint")
        .reset_index()
    )
    eyes = eyes.merge(treatment_counts, on="synthetic_eye_id", how="left")
    eyes["cumulative_injections_before_endpoint"] = eyes["cumulative_injections_before_endpoint"].fillna(0).astype(int)
    modeling = (
        eyes.merge(patients, on=["synthetic_patient_id", "is_synthetic", "synthetic_provenance"])
        .merge(biomarkers, on=["synthetic_eye_id", "synthetic_patient_id", "is_synthetic", "synthetic_provenance"])
        .merge(outcomes, on=["synthetic_eye_id", "is_synthetic", "synthetic_provenance"])
    )
    modeling = modeling[modeling["outcome_status"] == "OBSERVED"].copy()
    modeling[OUTCOME_COLUMN] = modeling[OUTCOME_COLUMN].astype(int)
    modeling["clinical_validation_status"] = "NOT_VALIDATED"
    modeling["experiment_title"] = TITLE
    return {
        "patients": patients,
        "eyes": eyes,
        "visits": visits,
        "treatments": treatments,
        "oct_biomarkers": biomarkers,
        "outcomes": outcomes,
        "modeling_dataset": modeling,
    }


def run_synthetic_demo(config: SyntheticDemoConfig, example_inference: bool = True) -> dict[str, Any]:
    tables = generate_synthetic_cohort(config)
    output_dir = Path(config.output_dir)
    reports_dir = Path(config.reports_dir)
    artifacts_dir = Path(config.artifacts_dir)
    figures_dir = reports_dir / "figures"
    for directory in [output_dir, reports_dir, artifacts_dir, figures_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    filenames = {
        "patients": "synthetic_patients.csv",
        "eyes": "synthetic_eyes.csv",
        "visits": "synthetic_visits.csv",
        "treatments": "synthetic_treatments.csv",
        "oct_biomarkers": "synthetic_oct_biomarkers.csv",
        "modeling_dataset": "synthetic_modeling_dataset.csv",
    }
    for key, filename in filenames.items():
        tables[key].to_csv(output_dir / filename, index=False)
    quality = validate_synthetic_tables(tables, config)
    metrics, fitted, test_predictions = train_and_evaluate(tables["modeling_dataset"], config.random_seed)
    inference = build_example_inference(tables["modeling_dataset"], fitted) if example_inference else {}
    _write_reports(tables, quality, metrics, inference, config, reports_dir)
    _write_figures(metrics, test_predictions, tables["modeling_dataset"], figures_dir)
    joblib.dump(
        {
            "title": TITLE,
            "clinical_validation_status": "NOT_VALIDATED",
            "is_synthetic": True,
            "feature_columns": CLINICAL_FEATURES + OCT_FEATURES,
            "model": fitted["clinical_plus_oct"],
        },
        artifacts_dir / "synthetic_clinical_plus_oct_model.joblib",
    )
    summary = {
        "title": TITLE,
        "config": asdict(config),
        "patient_count": int(tables["patients"]["synthetic_patient_id"].nunique()),
        "eye_count": int(tables["eyes"]["synthetic_eye_id"].nunique()),
        "eligible_eye_count": int(len(tables["modeling_dataset"])),
        "outcome_unavailable_eye_count": int((tables["outcomes"]["outcome_status"] == "OUTCOME_UNAVAILABLE").sum()),
        "metrics": metrics.to_dict(orient="records"),
        "quality": quality,
        "example_inference": inference,
    }
    (reports_dir / "synthetic_demo_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def validate_synthetic_tables(tables: dict[str, pd.DataFrame], config: SyntheticDemoConfig) -> dict[str, Any]:
    errors: list[str] = []
    patients = tables["patients"]
    eyes = tables["eyes"]
    visits = tables["visits"]
    treatments = tables["treatments"]
    modeling = tables["modeling_dataset"]
    outcomes = tables["outcomes"]
    if patients["synthetic_patient_id"].duplicated().any():
        errors.append("Duplicate synthetic patient identifiers.")
    if eyes["synthetic_eye_id"].duplicated().any():
        errors.append("Duplicate synthetic eye identifiers.")
    if not set(eyes["synthetic_patient_id"]).issubset(set(patients["synthetic_patient_id"])):
        errors.append("Invalid patient-eye relationship.")
    if visits["elapsed_days_from_baseline"].lt(0).any() or treatments["elapsed_days_from_baseline"].lt(0).any():
        errors.append("Negative elapsed day detected.")
    if eyes["cumulative_injections_before_endpoint"].lt(0).any():
        errors.append("Negative treatment count detected.")
    observed = outcomes[outcomes["outcome_status"] == "OBSERVED"]
    if not observed["outcome_visit_elapsed_days"].between(config.endpoint_window_min_days, config.endpoint_window_max_days).all():
        errors.append("Observed outcome outside endpoint window.")
    forbidden_predictors = {"followup_bcva_etdrs", "followup_cst_um", "cumulative_injections_before_endpoint", "outcome_visit_elapsed_days", "bcva_letter_change"}
    used = set(CLINICAL_FEATURES + OCT_FEATURES)
    if used.intersection(forbidden_predictors):
        errors.append("Future or outcome-derived feature selected for modeling.")
    folds = _make_holdout_split(modeling, config.random_seed)
    train_groups = set(modeling.iloc[folds[0]][GROUP_COLUMN])
    test_groups = set(modeling.iloc[folds[1]][GROUP_COLUMN])
    if train_groups.intersection(test_groups):
        errors.append("Patient leakage detected in grouped holdout.")
    return {
        "status": "PASSED" if not errors else "FAILED",
        "errors": errors,
        "baseline_only_predictors": CLINICAL_FEATURES + OCT_FEATURES,
        "patient_overlap_in_holdout": len(train_groups.intersection(test_groups)),
        "observed_outcomes": int(len(observed)),
        "unavailable_outcomes": int((outcomes["outcome_status"] == "OUTCOME_UNAVAILABLE").sum()),
    }


def train_and_evaluate(dataset: pd.DataFrame, random_seed: int) -> tuple[pd.DataFrame, dict[str, Pipeline], pd.DataFrame]:
    train_idx, test_idx = _make_holdout_split(dataset, random_seed)
    train = dataset.iloc[train_idx].copy()
    test = dataset.iloc[test_idx].copy()
    models = {
        "Clinical-only": CLINICAL_FEATURES,
        "Clinical + OCT": CLINICAL_FEATURES + OCT_FEATURES,
    }
    rows: list[dict[str, Any]] = []
    fitted: dict[str, Pipeline] = {}
    prediction_frames: list[pd.DataFrame] = []
    for model_name, features in models.items():
        non_constant = [feature for feature in features if train[feature].nunique(dropna=False) > 1]
        pipeline = _build_pipeline(non_constant)
        pipeline.fit(train[non_constant], train[OUTCOME_COLUMN])
        probabilities = pipeline.predict_proba(test[non_constant])[:, 1]
        predictions = (probabilities >= 0.5).astype(int)
        y_true = test[OUTCOME_COLUMN].to_numpy()
        tn, fp, fn, tp = confusion_matrix(y_true, predictions, labels=[0, 1]).ravel()
        rows.append(
            {
                "title": TITLE,
                "model": model_name,
                "eligible_eyes": int(len(dataset)),
                "eligible_patients": int(dataset[GROUP_COLUMN].nunique()),
                "heldout_eyes": int(len(test)),
                "response_prevalence": float(dataset[OUTCOME_COLUMN].mean()),
                "auroc": _safe_auroc(y_true, probabilities),
                "average_precision": float(average_precision_score(y_true, probabilities)),
                "sensitivity": float(tp / (tp + fn)) if (tp + fn) else None,
                "specificity": float(tn / (tn + fp)) if (tn + fp) else None,
                "balanced_accuracy": float(balanced_accuracy_score(y_true, predictions)),
                "brier_score": float(brier_score_loss(y_true, probabilities)),
                "true_negative": int(tn),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "true_positive": int(tp),
                "non_constant_predictors": ", ".join(non_constant),
                "synthetic_fixture_only": True,
                "clinical_validation_status": "NOT_VALIDATED",
            }
        )
        fitted[_slug(model_name)] = pipeline
        prediction_frames.append(
            pd.DataFrame(
                {
                    "synthetic_eye_id": test["synthetic_eye_id"].to_numpy(),
                    "synthetic_patient_id": test[GROUP_COLUMN].to_numpy(),
                    "model": model_name,
                    "observed": y_true,
                    "probability": probabilities,
                    "prediction": predictions,
                }
            )
        )
    return pd.DataFrame(rows), fitted, pd.concat(prediction_frames, ignore_index=True)


def build_example_inference(dataset: pd.DataFrame, fitted: dict[str, Pipeline]) -> dict[str, Any]:
    row = dataset.iloc[0].copy()
    features = CLINICAL_FEATURES + OCT_FEATURES
    model = fitted["clinical_plus_oct"]
    probability = float(model.predict_proba(pd.DataFrame([row[features].to_dict()]))[:, 1][0])
    return {
        "synthetic_patient_id": row["synthetic_patient_id"],
        "synthetic_eye_id": row["synthetic_eye_id"],
        "predicted_probability_ge_5_letter_gain": probability,
        "model_identity": "Clinical + OCT synthetic logistic regression",
        "predictor_availability": {feature: bool(pd.notna(row[feature])) for feature in features},
        "is_synthetic": True,
        "clinical_validation_status": "NOT_VALIDATED",
        "warning": "Synthetic demonstration probability only; not suitable for clinical decisions or treatment recommendations.",
    }


def _derive_eye_outcome(eye_id: str, baseline_bcva: int, visit_rows: list[dict[str, Any]], config: SyntheticDemoConfig) -> dict[str, Any]:
    eye_visits = [row for row in visit_rows if row["synthetic_eye_id"] == eye_id]
    eligible = [
        row
        for row in eye_visits
        if config.endpoint_window_min_days <= int(row["elapsed_days_from_baseline"]) <= config.endpoint_window_max_days
    ]
    base = {"synthetic_eye_id": eye_id, "is_synthetic": True, "synthetic_provenance": PROVENANCE}
    if not eligible:
        return {
            **base,
            "outcome_status": "OUTCOME_UNAVAILABLE",
            "outcome_visit_id": None,
            "outcome_visit_elapsed_days": None,
            "bcva_letter_change": None,
            OUTCOME_COLUMN: None,
        }
    selected = sorted(
        eligible,
        key=lambda row: (
            abs(int(row["elapsed_days_from_baseline"]) - config.endpoint_target_days),
            int(row["elapsed_days_from_baseline"]),
            row["synthetic_visit_id"],
        ),
    )[0]
    change = int(selected["followup_bcva_etdrs"]) - int(baseline_bcva)
    return {
        **base,
        "outcome_status": "OBSERVED",
        "outcome_visit_id": selected["synthetic_visit_id"],
        "outcome_visit_elapsed_days": int(selected["elapsed_days_from_baseline"]),
        "bcva_letter_change": change,
        OUTCOME_COLUMN: int(change >= 5),
    }


def _build_pipeline(feature_columns: list[str]) -> Pipeline:
    categorical = [feature for feature in feature_columns if feature == "sex"]
    numeric = [feature for feature in feature_columns if feature not in categorical]
    return Pipeline(
        [
            (
                "preprocess",
                ColumnTransformer(
                    [
                        ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric),
                        ("categorical", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
                    ],
                    remainder="drop",
                ),
            ),
            ("classifier", LogisticRegression(max_iter=1000, solver="liblinear", random_state=20261011)),
        ]
    )


def _make_holdout_split(dataset: pd.DataFrame, random_seed: int) -> tuple[np.ndarray, np.ndarray]:
    patient_outcomes = dataset.groupby(GROUP_COLUMN)[OUTCOME_COLUMN].max().reset_index()
    train_patients, test_patients = train_test_split(
        patient_outcomes[GROUP_COLUMN],
        test_size=0.25,
        random_state=random_seed,
        stratify=patient_outcomes[OUTCOME_COLUMN],
    )
    train_idx = np.flatnonzero(dataset[GROUP_COLUMN].isin(set(train_patients)).to_numpy())
    test_idx = np.flatnonzero(dataset[GROUP_COLUMN].isin(set(test_patients)).to_numpy())
    _check_grouped_cv(dataset.iloc[train_idx], random_seed)
    return train_idx, test_idx


def _check_grouped_cv(train: pd.DataFrame, random_seed: int) -> None:
    splitter = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=random_seed)
    for inner_train, inner_test in splitter.split(train, train[OUTCOME_COLUMN], train[GROUP_COLUMN]):
        if set(train.iloc[inner_train][GROUP_COLUMN]).intersection(set(train.iloc[inner_test][GROUP_COLUMN])):
            raise ValueError("Patient leakage detected inside grouped validation.")


def _write_reports(
    tables: dict[str, pd.DataFrame],
    quality: dict[str, Any],
    metrics: pd.DataFrame,
    inference: dict[str, Any],
    config: SyntheticDemoConfig,
    reports_dir: Path,
) -> None:
    outcomes = tables["outcomes"]
    modeling = tables["modeling_dataset"]
    quality_lines = [
        f"# {TITLE}",
        "",
        "## Synthetic Data Quality",
        "",
        f"- Synthetic patients: {tables['patients']['synthetic_patient_id'].nunique()}",
        f"- Synthetic eyes: {tables['eyes']['synthetic_eye_id'].nunique()}",
        f"- Outcome-observed eyes: {(outcomes['outcome_status'] == 'OBSERVED').sum()}",
        f"- Outcome-unavailable eyes: {(outcomes['outcome_status'] == 'OUTCOME_UNAVAILABLE').sum()}",
        f"- Validation status: {quality['status']}",
        f"- Patient overlap in held-out split: {quality['patient_overlap_in_holdout']}",
        f"- Baseline-only predictors: {', '.join(quality['baseline_only_predictors'])}",
    ]
    if quality["errors"]:
        quality_lines.extend(["", "## Errors", *[f"- {error}" for error in quality["errors"]]])
    (reports_dir / "synthetic_data_quality.md").write_text("\n".join(quality_lines), encoding="utf-8")
    metric_lines = [
        f"# {TITLE}",
        "",
        "## Synthetic Model Comparison",
        "",
        "These metrics are software demonstration results from a fully fictitious cohort. They are not clinical performance estimates.",
        "",
        _markdown_table(metrics),
        "",
        "## Paired Cases",
        "",
        "Clinical-only and Clinical + OCT models use identical eligible eyes, identical held-out patients, and fitted preprocessing inside each training fold/split.",
    ]
    (reports_dir / "synthetic_model_comparison.md").write_text("\n".join(metric_lines), encoding="utf-8")
    release_lines = [
        f"# {TITLE}",
        "",
        "## Synthetic Release Status",
        "",
        "- MULTI-DEMO-01: PASSED_SYNTHETIC_DEMONSTRATION" if quality["status"] == "PASSED" else "- MULTI-DEMO-01: FAILED_VALIDATION",
        "- Real OLIVES/OCT-DME treatment-response modeling remains blocked pending verified linkage, visit timing, and treatment histories.",
        "- No synthetic identifier crosswalk is used to verify genuine records.",
        "- No generated probability is suitable for clinical decisions.",
        "",
        "## Example Inference",
        "",
        "```json",
        json.dumps(inference, indent=2),
        "```",
    ]
    (reports_dir / "synthetic_release_status.md").write_text("\n".join(release_lines), encoding="utf-8")
    assumption_lines = [
        "# Synthetic Assumptions",
        "",
        f"Title: {TITLE}",
        "",
        "The generator uses broad, literature-informed DME demonstration ranges for age, ETDRS visual acuity, central subfield thickness, "
        "diabetes duration, HbA1c, renal function, OCT fluid and structural biomarkers, anti-VEGF injection schedules, and six-month visual response.",
        "",
        "These are illustrative engineering assumptions, not estimated clinical parameters. "
        "Stochastic noise and missingness are intentionally included so labels are not perfectly separable.",
        "",
        f"Endpoint window: {config.endpoint_window_min_days}-{config.endpoint_window_max_days} days; target day: {config.endpoint_target_days}.",
        f"Eligible modeling eyes: {len(modeling)}.",
    ]
    (reports_dir / "synthetic_assumptions_snapshot.md").write_text("\n".join(assumption_lines), encoding="utf-8")


def _write_figures(metrics: pd.DataFrame, predictions: pd.DataFrame, dataset: pd.DataFrame, figures_dir: Path) -> None:
    plt.figure(figsize=(5, 4))
    dataset[OUTCOME_COLUMN].value_counts().sort_index().plot(kind="bar", color=["#4c78a8", "#f58518"])
    plt.title(TITLE)
    plt.xlabel("Response >=5 letters")
    plt.ylabel("Eyes")
    plt.tight_layout()
    plt.savefig(figures_dir / "class_distribution.png", dpi=150)
    plt.close()
    plt.figure(figsize=(6, 4))
    plt.bar(metrics["model"], metrics["auroc"], color=["#54a24b", "#b279a2"])
    plt.ylim(0, 1)
    plt.title(TITLE)
    plt.ylabel("Held-out AUROC")
    plt.tight_layout()
    plt.savefig(figures_dir / "clinical_vs_multimodal_performance.png", dpi=150)
    plt.close()
    for model_name, frame in predictions.groupby("model"):
        cm = confusion_matrix(frame["observed"], frame["prediction"], labels=[0, 1])
        plt.figure(figsize=(4, 4))
        plt.imshow(cm, cmap="Blues")
        plt.title(f"{TITLE}\n{model_name}")
        plt.xticks([0, 1], ["No", "Yes"])
        plt.yticks([0, 1], ["No", "Yes"])
        for (i, j), value in np.ndenumerate(cm):
            plt.text(j, i, str(value), ha="center", va="center")
        plt.xlabel("Predicted")
        plt.ylabel("Observed")
        plt.tight_layout()
        plt.savefig(figures_dir / f"confusion_matrix_{_slug(model_name)}.png", dpi=150)
        plt.close()
    plt.figure(figsize=(5, 4))
    for model_name, frame in predictions.groupby("model"):
        bins = pd.cut(frame["probability"], bins=np.linspace(0, 1, 6), include_lowest=True)
        calibration = frame.groupby(bins, observed=False).agg(mean_probability=("probability", "mean"), observed_rate=("observed", "mean")).dropna()
        plt.plot(calibration["mean_probability"], calibration["observed_rate"], marker="o", label=model_name)
    plt.plot([0, 1], [0, 1], color="black", linestyle="--", linewidth=1)
    plt.title(TITLE)
    plt.xlabel("Mean predicted probability")
    plt.ylabel("Observed synthetic response rate")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figures_dir / "calibration.png", dpi=150)
    plt.close()


def _safe_auroc(y_true: np.ndarray, probabilities: np.ndarray) -> float | None:
    if len(set(y_true.tolist())) < 2:
        return None
    return float(roc_auc_score(y_true, probabilities))


def _sigmoid(value: float) -> float:
    return float(1 / (1 + np.exp(-value)))


def _slug(value: str) -> str:
    return value.lower().replace(" + ", "_plus_").replace("-", "_").replace(" ", "_")


def _markdown_table(frame: pd.DataFrame) -> str:
    columns = list(frame.columns)
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in frame.iterrows():
        values = []
        for column in columns:
            value = row[column]
            if isinstance(value, float):
                values.append(f"{value:.4f}")
            else:
                values.append("" if pd.isna(value) else str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)
