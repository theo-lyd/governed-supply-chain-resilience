# Batch Report: SCR-P2-B2.2

## Batch Metadata
- Batch ID: SCR-P2-B2.2
- Phase: Ingestion and Bronze Layer
- Status: Completed/Verified (DuckDB Incremental)
- Date: 2026-04-11
- Environment: GitHub Codespace -> DuckDB (local)

## Scope Definition
- Chunk(s) in Scope:
  - Chunk 4: Incremental Landing (file-state driven)
- Explicit Goal for This Batch:
  - Replace Databricks `cloudFiles` Autoloader with a reproducible DuckDB incremental ingestion batch.

## What Was Built
- Files Created/Modified:
  - `scripts/autoloader_bronze.py`
  - `docs/command/phase-2-autoloader-commands.md`
  - `docs/phase-reports/SCR-P2-B2.2-report.md`
- Incremental Building Blocks:
  - JSONL file discovery through glob pattern
  - Persistent processed-file state in `data/duckdb/ingestion_state/processed_iot_files.json`
  - Incremental inserts into `bronze.iot_events_raw` for only unseen files

## Commands Executed
- `python3 -m py_compile scripts/autoloader_bronze.py`
- `python3 scripts/autoloader_bronze.py --dry-run --input-pattern "data/iot_landing/*.jsonl"`
- `python3 scripts/autoloader_bronze.py --input-pattern "data/iot_landing/*.jsonl"`

## Validation Evidence
- ✅ Script syntax validated with `py_compile`
- ✅ Dry-run prints resolved config and file-discovery counts
- ✅ Incremental run updates DuckDB Bronze table: `bronze.iot_events_raw`
- ✅ State file updated with processed filenames to prevent duplicate ingestion
- ✅ Runtime evidence captured from local execution:
  - Pre-run state check: `Discovered files: 2`, `Already processed files: 2`, `New files to ingest: 0`
  - After generating one new IoT file (`events-per-file=7`):
    - `Discovered files: 3`
    - `Already processed files: 2`
    - `New files to ingest: 1`
    - `Loaded 7 rows from 1 new file(s) into bronze.iot_events_raw`
    - `Current row_count: 37`
  - Verification query:
    - `table_count_after_new_file: 37`
    - `source_file_count_after_new_file: 3`

## Issues and Resolutions
- Incident:
  - Prior Databricks serverless path rejected Spark REPL-based execution.
- Resolution:
  - Implemented local DuckDB incremental ingestion to preserve batch objectives under cost constraints.
- Recurrence Prevention:
  - Keep state file stable and versioned by batch evidence.

## Acceptance Criteria Met
- [x] Databricks-specific Autoloader path replaced
- [x] Incremental ingestion logic implemented and validated locally
- [x] New-file detection behavior documented and reproducible

## Handover Notes
- What changed for the next batch:
  - Batch 2.2 is complete on DuckDB-native architecture.
- Next batch recommendation:
  - Proceed to Phase 3 normalization using Bronze data from `data/duckdb/scr.duckdb`.
