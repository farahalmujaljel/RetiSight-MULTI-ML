# Privacy And Safe-Commit Audit

Audit date: 2026-10-11

## Git Ignore Coverage

`.gitignore` excludes:

- `data/raw/*`
- `data/interim/*`
- `data/processed/*`
- `reports/**/*.csv`
- `reports/**/*.json`
- `artifacts/models/*`
- `artifacts/metadata/*`

Intentional `.gitkeep` placeholders and synthetic fixtures are allowed.

## Tracked Data Review

Tracked CSV files are schema/data-dictionary or synthetic validation artifacts under `schemas/`. No raw workbook, row-level OLIVES export, row-level OCT-DME export, model artifact, image, credential file, or private report CSV/JSON is intended for commit.

## Secret Scan

Local keyword scan for common key/secret/token patterns returned no tracked source-code findings outside documentation and `.env.example` exclusions.

## CI Privacy Gate

CI now fails if protected raw/interim/processed paths, model artifacts, metadata artifacts, or row-level report CSV/JSON files are tracked, while permitting `.gitkeep`.

## Privacy Decision

Safe for public PR if the staged set remains limited to source code, schemas, synthetic fixtures, CI, aggregate Markdown reports, and documentation.
