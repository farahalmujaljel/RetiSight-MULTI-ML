from __future__ import annotations

import json
from pathlib import Path


def write_progress(final_dir: Path, statuses: dict[str, str]) -> None:
    final_dir.mkdir(parents=True, exist_ok=True)
    (final_dir / "progress.json").write_text(json.dumps(statuses, indent=2), encoding="utf-8")
    lines = ["# MULTI-ML Status", ""]
    lines.extend(f"- {task}: {status}" for task, status in statuses.items())
    (final_dir / "status.md").write_text("\n".join(lines), encoding="utf-8")


def write_final_report(final_dir: Path, statuses: dict[str, str], outcome_decision: str) -> None:
    lines = [
        "# Final MULTI-ML Report",
        "",
        "This report records executed pipeline status. It does not claim clinical validity.",
        "",
        "## Subtask Status",
        "",
        *[f"- {task}: {status}" for task, status in statuses.items()],
        "",
        "## Outcome Feasibility",
        "",
        f"- Decision: {outcome_decision}",
        "",
        "## Parent Definition of Done",
        "",
        "- Genuine source files loaded: PASS when local raw files are present and inventory was run.",
        "- Cross-source linkage: BLOCKED; exact StudyID/path-folder candidates were generated, but no independent source crosswalk was found.",
        "- Unified dataset: candidate exact-match baseline table exists, but it is not a verified linked research cohort until crosswalk confirmation.",
        "- Modeling: CONDITIONAL_NOT_APPLICABLE until response endpoint and exposure assumptions are clinically approved.",
    ]
    (final_dir / "final_report.md").write_text("\n".join(lines), encoding="utf-8")
