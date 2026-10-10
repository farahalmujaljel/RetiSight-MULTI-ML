from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

CLINICAL_FEATURES = [
    "baseline_bcva_etdrs",
    "baseline_cst_um",
]

OCT_FEATURES = [
    "irf_present",
    "srf_present",
    "dril_present",
    "hrf_present",
    "ez_disruption_present",
    "number_of_annotated_scans",
]


@dataclass(frozen=True)
class OutcomeValidationManifest:
    outcome_column: str
    group_column: str
    source_provenance: str
    endpoint_definition: str
    time_zero: str
    eligibility_criteria: str
    clinical_approval_status: str
    approved_by_role: str
    validation_status: str
    observed_label_count: int
    positive_count: int
    negative_count: int
    prohibits_synthetic_labels: bool = True


@dataclass(frozen=True)
class SyntheticFixtureAuthorization:
    fixture_name: str
    purpose: str = "software_test_only"


def authorize_synthetic_fixture_training(fixture_name: str) -> SyntheticFixtureAuthorization:
    if not fixture_name.startswith("synthetic_"):
        raise ValueError("Synthetic fixture names must start with `synthetic_`.")
    return SyntheticFixtureAuthorization(fixture_name=fixture_name)


def validate_outcome_manifest(dataset: pd.DataFrame, manifest: OutcomeValidationManifest) -> None:
    required_text_fields = {
        "source_provenance": manifest.source_provenance,
        "endpoint_definition": manifest.endpoint_definition,
        "time_zero": manifest.time_zero,
        "eligibility_criteria": manifest.eligibility_criteria,
        "approved_by_role": manifest.approved_by_role,
    }
    missing = [name for name, value in required_text_fields.items() if not str(value).strip()]
    if missing:
        raise ValueError(f"Outcome validation manifest is missing required fields: {missing}")
    if manifest.validation_status != "VALIDATED":
        raise ValueError("Outcome validation manifest must have validation_status='VALIDATED'.")
    if manifest.clinical_approval_status != "APPROVED":
        raise ValueError("Outcome validation manifest must have clinical_approval_status='APPROVED'.")
    if not manifest.prohibits_synthetic_labels:
        raise ValueError("Real training manifest must prohibit synthetic labels.")
    require_validated_outcome(dataset, manifest.outcome_column, manifest.group_column)
    observed = dataset[manifest.outcome_column].dropna().astype(int)
    positive = int(observed.sum())
    negative = int((1 - observed).sum())
    if int(manifest.observed_label_count) != int(len(observed)):
        raise ValueError("Outcome manifest label count does not match the dataset.")
    if int(manifest.positive_count) != positive or int(manifest.negative_count) != negative:
        raise ValueError("Outcome manifest class counts do not match the dataset.")


def require_validated_outcome(
    dataset: pd.DataFrame, outcome_column: str, group_column: str = "research_patient_id"
) -> None:
    if outcome_column not in dataset:
        raise ValueError(f"Outcome column `{outcome_column}` is required for model training.")
    if group_column not in dataset:
        raise ValueError(f"Group column `{group_column}` is required for patient-grouped evaluation.")
    observed = dataset[outcome_column].dropna()
    if observed.empty:
        raise ValueError("No observed outcome labels are available.")
    if observed.isna().any():
        raise ValueError("Outcome labels contain missing values.")
    if not observed.isin([0, 1, False, True]).all():
        raise ValueError("Outcome labels must be binary 0/1 values.")
    classes = set(pd.Series(observed).astype(int).unique())
    if classes != {0, 1}:
        raise ValueError("Outcome labels must contain both 0 and 1 classes.")
    if dataset[group_column].isna().any():
        raise ValueError("Patient group labels must not be missing.")


def make_grouped_folds(
    dataset: pd.DataFrame,
    outcome_column: str,
    group_column: str = "research_patient_id",
    n_splits: int = 3,
    random_seed: int = 20261010,
) -> list[tuple[np.ndarray, np.ndarray]]:
    require_validated_outcome(dataset, outcome_column, group_column)
    groups = dataset[group_column].to_numpy()
    y = dataset[outcome_column].astype(int).to_numpy()
    unique_groups = pd.Series(groups).nunique()
    if unique_groups < n_splits:
        raise ValueError("Not enough patient groups for requested grouped folds.")
    splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=random_seed)
    folds = list(splitter.split(dataset, y, groups))
    for train_idx, test_idx in folds:
        if set(groups[train_idx]).intersection(set(groups[test_idx])):
            raise ValueError("Patient group leakage detected across folds.")
        if len(set(y[train_idx].tolist())) < 2:
            raise ValueError("Training fold contains only one outcome class.")
    return folds


def build_model_pipeline(feature_columns: list[str]) -> Pipeline:
    numeric_features = feature_columns
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_features,
            )
        ],
        remainder="drop",
    )
    return Pipeline(
        [
            ("preprocess", preprocessor),
            ("classifier", LogisticRegression(max_iter=1000, solver="liblinear")),
        ]
    )


def compare_clinical_vs_oct_models(
    dataset: pd.DataFrame,
    outcome_column: str,
    clinical_features: list[str] | None = None,
    oct_features: list[str] | None = None,
    group_column: str = "research_patient_id",
    n_splits: int = 3,
    random_seed: int = 20261010,
    outcome_manifest: OutcomeValidationManifest | None = None,
    synthetic_authorization: SyntheticFixtureAuthorization | None = None,
) -> pd.DataFrame:
    synthetic_mode = synthetic_authorization is not None
    real_mode = outcome_manifest is not None
    if synthetic_mode == real_mode:
        raise ValueError("Provide exactly one training authorization: synthetic fixture or validated outcome manifest.")
    if synthetic_mode:
        if synthetic_authorization.purpose != "software_test_only":
            raise ValueError("Synthetic authorization is limited to software_test_only.")
    else:
        if outcome_manifest is None:
            raise ValueError("A validated outcome manifest is required for real model training.")
        validate_outcome_manifest(dataset, outcome_manifest)
        outcome_column = outcome_manifest.outcome_column
        group_column = outcome_manifest.group_column
    clinical = clinical_features or CLINICAL_FEATURES
    oct_cols = oct_features or OCT_FEATURES
    model_specs = {
        "clinical_only": clinical,
        "clinical_plus_oct": clinical + oct_cols,
    }
    folds = make_grouped_folds(dataset, outcome_column, group_column, n_splits, random_seed)
    rows: list[dict[str, Any]] = []
    y = dataset[outcome_column].astype(int)
    for model_name, feature_columns in model_specs.items():
        missing = [c for c in feature_columns if c not in dataset.columns]
        if missing:
            raise ValueError(f"Missing feature columns for {model_name}: {missing}")
        for fold_id, (train_idx, test_idx) in enumerate(folds, start=1):
            pipeline = build_model_pipeline(feature_columns)
            pipeline.fit(dataset.iloc[train_idx][feature_columns], y.iloc[train_idx])
            probabilities = pipeline.predict_proba(dataset.iloc[test_idx][feature_columns])[:, 1]
            y_true = y.iloc[test_idx].to_numpy()
            rows.append(
                {
                    "model": model_name,
                    "fold": fold_id,
                    "n_test": int(len(test_idx)),
                    "test_positive": int(y_true.sum()),
                    "test_negative": int((1 - y_true).sum()),
                    "auroc": _safe_auroc(y_true, probabilities),
                    "average_precision": float(average_precision_score(y_true, probabilities)),
                    "auroc_status": _auroc_status(y_true),
                    "synthetic_fixture_only": synthetic_mode,
                    "training_authorization": "synthetic_fixture" if synthetic_mode else "validated_manifest",
                }
            )
    return pd.DataFrame(rows)


def _safe_auroc(y_true: np.ndarray, probabilities: np.ndarray) -> float | None:
    if len(set(y_true.tolist())) < 2:
        return None
    return float(roc_auc_score(y_true, probabilities))


def _auroc_status(y_true: np.ndarray) -> str:
    if len(set(y_true.tolist())) < 2:
        return "not_estimable_single_class_test_fold"
    return "estimable"


def write_modeling_omission(output_dir: Path, reason: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "modeling_not_performed.md").write_text(
        "\n".join(
            [
                "# Modeling Not Performed",
                "",
                "Status: CONDITIONAL_NOT_APPLICABLE",
                "",
                reason,
                "",
                "No model artifacts or performance tables were generated.",
            ]
        ),
        encoding="utf-8",
    )


def write_model_infrastructure_readiness(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Model Infrastructure Readiness",
        "",
        "Reusable patient-grouped modeling infrastructure is implemented and tested with synthetic fixtures only.",
        "",
        "## Ready Interfaces",
        "",
        "- `require_validated_outcome(dataset, outcome_column, group_column)`",
        "- `make_grouped_folds(dataset, outcome_column, group_column)`",
        "- `compare_clinical_vs_oct_models(..., synthetic_authorization=...)` for software tests",
        "- `compare_clinical_vs_oct_models(..., outcome_manifest=...)` for future validated research labels",
        "",
        "## Safeguards",
        "",
        "- Real model training remains disabled unless a machine-checkable validated outcome manifest is supplied.",
        "- Clinical-only and clinical-plus-OCT models use identical eligible patients and folds.",
        "- Synthetic tests are software validation only and are not clinical results.",
    ]
    (output_dir / "model_infrastructure_readiness.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
