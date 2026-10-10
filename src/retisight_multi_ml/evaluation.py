from __future__ import annotations

from pathlib import Path


def write_evaluation_omission(output_dir: Path, reason: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "evaluation_report.md").write_text(
        "\n".join(
            [
                "# Evaluation Report",
                "",
                "Status: CONDITIONAL_NOT_APPLICABLE",
                "",
                reason,
                "",
                "Metrics are NOT_ESTIMABLE because validated response modeling was not performed.",
            ]
        ),
        encoding="utf-8",
    )

