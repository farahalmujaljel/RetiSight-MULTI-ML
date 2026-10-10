from __future__ import annotations

from pathlib import Path


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

