from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import SourceConfig
from .data_access import excel_sheets, read_table, sha256


def inventory_sources(sources: list[SourceConfig], output_dir: Path) -> list[dict[str, Any]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    md_lines = ["# Initial Data Audit", ""]
    for source in sources:
        entry: dict[str, Any] = {
            "dataset_name": source.name,
            "source_key": source.key,
            "original_url": source.url,
            "local_source_path": str(source.path),
            "intended_use": source.intended_use,
            "inspection_status": "BLOCKED_MISSING_FILE",
        }
        if source.path.exists():
            entry.update(
                {
                    "inspection_status": "INSPECTED",
                    "file_format": source.path.suffix.lower().lstrip("."),
                    "file_size_bytes": source.path.stat().st_size,
                    "sha256": sha256(source.path),
                    "licensing_information": "Not verified from file metadata; requires source documentation review.",
                }
            )
            sheets = excel_sheets(source.path) or [None]
            sheet_entries = []
            for sheet in sheets:
                df = read_table(source.path, sheet_name=sheet)
                identifiers = [
                    c
                    for c in df.columns
                    if any(token in str(c).lower() for token in ["id", "eye", "patient", "study", "visit"])
                ]
                sheet_entries.append(
                    {
                        "sheet_name": sheet or source.path.name,
                        "row_count": int(df.shape[0]),
                        "column_count": int(df.shape[1]),
                        "columns": [str(c) for c in df.columns],
                        "identifier_fields": [str(c) for c in identifiers],
                        "duplicate_rows": int(df.duplicated().sum()),
                        "missing_values": {str(k): int(v) for k, v in df.isna().sum().items()},
                    }
                )
            entry["tables"] = sheet_entries
        manifest.append(entry)
        md_lines.extend(_manifest_entry_to_markdown(entry))
    (output_dir / "source_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (output_dir / "initial_data_audit.md").write_text("\n".join(md_lines), encoding="utf-8")
    return manifest


def _manifest_entry_to_markdown(entry: dict[str, Any]) -> list[str]:
    lines = [f"## {entry['dataset_name']}", "", f"- Status: {entry['inspection_status']}"]
    if entry["inspection_status"] == "INSPECTED":
        lines.extend(
            [
                f"- Size: {entry['file_size_bytes']} bytes",
                f"- SHA-256: `{entry['sha256']}`",
                f"- URL: {entry['original_url']}",
            ]
        )
        for table in entry["tables"]:
            lines.extend(
                [
                    "",
                    f"### {table['sheet_name']}",
                    f"- Rows: {table['row_count']}",
                    f"- Columns: {table['column_count']}",
                    f"- Identifier fields: {', '.join(table['identifier_fields']) or 'None detected'}",
                    f"- Duplicate full rows: {table['duplicate_rows']}",
                ]
            )
    lines.append("")
    return lines
