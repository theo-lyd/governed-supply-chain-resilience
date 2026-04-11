# Batch Report: SCR-P2-B2.1

## Batch Metadata
- Batch ID: SCR-P2-B2.1
- Phase: Ingestion and Bronze Layer
- Status: Completed/Verified (Pivoted)
- Date: 2026-04-11
- Environment: GitHub Codespace -> DuckDB (local)

## Scope Definition
- Chunk(s) in Scope:
  - Chunk 1: Operational DB Simulation
  - Chunk 2: Source Sync Strategy (Core First)
  - Chunk 3: IoT Heartbeat Simulation
- Explicit Goal for This Batch:
  - Deliver a reproducible ingestion MVP with local source simulation and DuckDB Bronze loads.

## What Was Built
- Files Created/Modified:
  - `sql/postgres/init_source.sql`
  - `scripts/start_postgres_source.sh`
  - `scripts/stop_postgres_source.sh`
  - `scripts/iot_emitter.py`
  - `scripts/ingest_iot_to_duckdb.py`
  - `scripts/bootstrap_phase_2_1_duckdb.sh`
  - `docs/command/phase-2-commands.md`
  - `docs/phase-reports/SCR-P2-B2.1-report.md`

## Commands Executed
- `bash -n scripts/start_postgres_source.sh`
- `bash -n scripts/stop_postgres_source.sh`
- `bash -n scripts/bootstrap_phase_2_1_duckdb.sh`
- `./scripts/bootstrap_phase_2_1_duckdb.sh`

## Validation Evidence
- Postgres simulation:
  - ✅ container `scr_source_postgres` starts and is queryable
- IoT emitter:
  - ✅ JSONL event files are created in `data/iot_landing`
- DuckDB Bronze ingestion:
  - ✅ rows loaded into `bronze.iot_events_raw`
  - ✅ local database file updated at `data/duckdb/scr.duckdb`
  - ✅ baseline verification count before Batch 2.2 incremental test: `table_count: 30`, `source_file_count: 2`

## Acceptance Criteria Met
- [x] Postgres source simulation scripts created and validated
- [x] IoT heartbeat emitter produces repeatable schema contract
- [x] End-to-end local bootstrap executes successfully
- [x] Bronze evidence captured against DuckDB table (`bronze.iot_events_raw`)

## Handover Notes
- What changed for the next batch:
  - Batch 2.1 evidence now points to DuckDB Bronze instead of `workspace.bronze`.
- Next batch recommendation:
  - Proceed to Batch 2.2 incremental ingestion and verify only new files are loaded.
