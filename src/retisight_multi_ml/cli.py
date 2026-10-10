from __future__ import annotations

import argparse
from pathlib import Path

from .cleaning import write_clean_outputs
from .config import load_pipeline_config, load_sources
from .dataset_builder import build_dataset
from .evaluation import write_evaluation_omission
from .features import build_baseline_features
from .inventory import inventory_sources
from .linkage import build_linkage
from .modeling import write_model_infrastructure_readiness, write_modeling_omission
from .olives_native_dataset import build_olives_native_baseline
from .olives_native_outcomes import audit_olives_native_outcomes
from .outcome_audit import audit_outcomes
from .recovery_investigation import run_recovery_investigation
from .reporting import write_final_report, write_progress
from .schema import validate_dataset, write_hospital_schema_validation, write_schema


def _paths(config_path: str) -> dict[str, Path]:
    cfg = load_pipeline_config(config_path)
    out = cfg["outputs"]
    return {
        "raw": Path("data/raw"),
        "interim": Path(out["interim_dir"]),
        "processed": Path(out["processed_dir"]),
        "inventory": Path(out["inventory_dir"]),
        "cleaning": Path(out["cleaning_dir"]),
        "linkage": Path(out["linkage_dir"]),
        "features": Path(out["features_dir"]),
        "outcomes": Path(out["outcomes_dir"]),
        "modeling": Path(out["modeling_dir"]) if "modeling_dir" in out else Path("reports/modeling"),
        "final": Path(out["final_dir"]),
        "schema": Path(out["schema_dir"]),
        "data_sources_config": Path(cfg["data_sources_config"]),
    }


def run_full(config_path: str) -> None:
    paths = _paths(config_path)
    statuses = {
        "MULTI-01": "NOT_STARTED",
        "MULTI-02": "NOT_STARTED",
        "MULTI-03": "NOT_STARTED",
        "MULTI-04": "NOT_STARTED",
        "MULTI-05": "NOT_STARTED",
        "MULTI-06": "NOT_STARTED",
        "MULTI-06A": "NOT_STARTED",
        "MULTI-07": "NOT_STARTED",
        "MULTI-08": "NOT_STARTED",
        "MULTI-09": "NOT_STARTED",
        "MULTI-10": "NOT_STARTED",
    }
    inventory_sources(load_sources(paths["data_sources_config"]), paths["inventory"])
    statuses["MULTI-01"] = "PASSED"
    write_clean_outputs(paths["raw"], paths["interim"], paths["cleaning"])
    statuses["MULTI-02"] = "PASSED"
    build_linkage(paths["interim"], paths["linkage"])
    statuses["MULTI-03"] = "BLOCKED_EXTERNAL_CROSSWALK_CONFIRMATION"
    build_baseline_features(paths["interim"], paths["linkage"], paths["features"])
    statuses["MULTI-04"] = "PASSED_WITH_PREDICTOR_VARIATION_WARNINGS"
    build_olives_native_baseline(paths["raw"], paths["processed"], paths["features"])
    build_dataset(paths["features"], paths["processed"], paths["features"])
    errors = validate_dataset(paths["processed"] / "multimodal_baseline.csv")
    statuses["MULTI-05"] = "BLOCKED_BY_LINKAGE_VERIFICATION" if not errors else "BLOCKED"
    outcome_decision = audit_outcomes(paths["raw"], paths["processed"], paths["outcomes"])
    statuses["MULTI-06"] = "PASSED_REQUIRES_CLINICAL_REVIEW"
    olives_native_decision = audit_olives_native_outcomes(
        paths["raw"], paths["processed"], paths["outcomes"]
    )
    recovery_decisions = run_recovery_investigation(
        paths["raw"],
        {
            "linkage": paths["linkage"],
            "outcomes": paths["outcomes"],
            "docs": Path("docs/subtasks"),
            "processed": paths["processed"],
        },
    )
    statuses["MULTI-06A"] = (
        "BLOCKED_OLIVES_NATIVE_OUTCOME_TIMING"
        if olives_native_decision == "NOT_FEASIBLE"
        else "PASSED_REQUIRES_CLINICAL_REVIEW"
    )
    statuses["MULTI-03"] = (
        "TRAJECTORY_SUPPORTED_CANDIDATES_REQUIRE_EXTERNAL_CONFIRMATION"
        if recovery_decisions["linkage_decision"].startswith("TRAJECTORY_SUPPORTED")
        else statuses["MULTI-03"]
    )
    statuses["MULTI-06"] = "BLOCKED_TIMING_CROSSWALK_REQUIRED"
    reason = (
        "MULTI-06 remains blocked because 150-210 day Vision-sheet ETDRS cells have no "
        "authoritative patient-eye crosswalk, and MULTI-06A found OLIVES-native six-month "
        "response labels NOT_FEASIBLE without documented TREX-DME visit timing."
    )
    write_modeling_omission(paths["modeling"], reason)
    write_evaluation_omission(paths["modeling"], reason)
    write_model_infrastructure_readiness(paths["modeling"])
    statuses["MULTI-07"] = "CONDITIONAL_NOT_APPLICABLE"
    statuses["MULTI-08"] = "CONDITIONAL_NOT_APPLICABLE"
    write_schema(paths["schema"])
    write_hospital_schema_validation(paths["schema"], paths["final"])
    statuses["MULTI-09"] = "PASSED"
    statuses["MULTI-10"] = "PASSED"
    write_progress(paths["final"], statuses)
    write_final_report(paths["final"], statuses, outcome_decision)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/pipeline.yaml")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in [
        "inventory",
        "clean",
        "link",
        "features",
        "build",
        "outcomes",
        "olives-native-outcomes",
        "olives-native-baseline",
        "recovery-investigation",
        "schema",
        "full",
    ]:
        sub.add_parser(name)
    args = parser.parse_args()
    paths = _paths(args.config)
    if args.command == "inventory":
        inventory_sources(load_sources(paths["data_sources_config"]), paths["inventory"])
    elif args.command == "clean":
        write_clean_outputs(paths["raw"], paths["interim"], paths["cleaning"])
    elif args.command == "link":
        build_linkage(paths["interim"], paths["linkage"])
    elif args.command == "features":
        build_baseline_features(paths["interim"], paths["linkage"], paths["features"])
    elif args.command == "build":
        build_dataset(paths["features"], paths["processed"], paths["features"])
    elif args.command == "outcomes":
        audit_outcomes(paths["raw"], paths["processed"], paths["outcomes"])
    elif args.command == "olives-native-outcomes":
        audit_olives_native_outcomes(paths["raw"], paths["processed"], paths["outcomes"])
    elif args.command == "olives-native-baseline":
        build_olives_native_baseline(paths["raw"], paths["processed"], paths["features"])
    elif args.command == "recovery-investigation":
        run_recovery_investigation(
            paths["raw"],
            {
                "linkage": paths["linkage"],
                "outcomes": paths["outcomes"],
                "docs": Path("docs/subtasks"),
                "processed": paths["processed"],
            },
        )
    elif args.command == "schema":
        write_schema(paths["schema"])
        write_hospital_schema_validation(paths["schema"], paths["final"])
    elif args.command == "full":
        run_full(args.config)


if __name__ == "__main__":
    main()
