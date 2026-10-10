from __future__ import annotations

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
    classes = set(pd.Series(observed).astype(int).unique())
    if classes != {0, 1}:
        raise ValueError("Outcome labels must contain both 0 and 1 classes.")


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
    allow_synthetic: bool = False,
) -> pd.DataFrame:
    if not allow_synthetic:
        raise ValueError("Model training is disabled unless a caller explicitly provides validated labels.")
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
                    "synthetic_fixture_only": True,
                }
            )
    return pd.DataFrame(rows)


def _safe_auroc(y_true: np.ndarray, probabilities: np.ndarray) -> float | None:
    if len(set(y_true.tolist())) < 2:
        return None
    return float(roc_auc_score(y_true, probabilities))


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
        "- `compare_clinical_vs_oct_models(..., allow_synthetic=True)` for software tests",
        "",
        "## Safeguards",
        "",
        "- Real model training remains disabled unless validated outcomes are explicitly supplied.",
        "- Clinical-only and clinical-plus-OCT models use identical eligible patients and folds.",
        "- Synthetic tests are software validation only and are not clinical results.",
    ]
    (output_dir / "model_infrastructure_readiness.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
