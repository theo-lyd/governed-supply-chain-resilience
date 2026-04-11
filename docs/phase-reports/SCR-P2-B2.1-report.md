# Batch Report: SCR-P2-B2.1

## Batch Metadata
- Batch ID: SCR-P2-B2.1
- Phase: Ingestion and Bronze Layer
- Status: Completed/Verified
- Date: 2026-04-11
- Environment: GitHub Codespace -> Databricks (cost-constrained track)

## Scope Definition
- Chunk(s) in Scope:
  - Chunk 1: Operational DB Simulation
  - Chunk 2: Source Sync Strategy (Core First)
  - Chunk 3: IoT Heartbeat Simulation
- Explicit Goal for This Batch:
  - Deliver a reproducible ingestion MVP path by simulating source systems and producing Bronze-ready raw data artifacts.
- Out of Scope:
  - Batch 2.2 Autoloader checkpointing and streaming-lite polish.
  - Airbyte connector setup (extension path only).

## Pre-Execution Approval
- Approval Required for Compute-Heavy Run: No
- Approval Received From: Direct execution approved
- Approval Timestamp: 2026-04-11

## What Was Built
- Files Created/Modified:
  - `sql/postgres/init_source.sql`
  - `scripts/start_postgres_source.sh`
  - `scripts/stop_postgres_source.sh`
  - `scripts/iot_emitter.py`
  - `scripts/bootstrap_phase_2_1.sh`
  - `docs/command/phase-2-commands.md`
  - `docs/phase-reports/SCR-P2-B2.1-report.md`
- Ingestion Building Blocks:
  - Local Postgres source simulation (Docker) for transactional source emulation.
  - IoT heartbeat emitter producing newline-delimited JSON files.
  - Batch bootstrap orchestration script for reproducible local setup.

## Tool and Methodology Justifications
- Why this approach was chosen:
  - Delivers a low-cost, reproducible MVP ingestion path aligned with current budget constraints.
- Alternatives considered:
  - Early Airbyte setup for full connector path (deferred to extension track).
- Trade-offs accepted:
  - Local-first simulation precedes full Databricks Autoloader implementation (Batch 2.2).

## Commands Executed
- `bash -n scripts/start_postgres_source.sh`
- `bash -n scripts/stop_postgres_source.sh`
- `bash -n scripts/bootstrap_phase_2_1.sh`
- `python3 scripts/iot_emitter.py --output-dir data/iot_landing --iterations 1 --interval-seconds 1 --events-per-file 5`
- `./scripts/bootstrap_phase_2_1.sh`
- `rm -f data/iot_landing/*.jsonl && ./scripts/bootstrap_phase_2_1.sh`
- `docker exec scr_source_postgres psql -U source_user -d supply_chain_source -c "\\dt"`
- `docker exec scr_source_postgres psql -U source_user -d supply_chain_source -c "select count(*) as routes from routes;"`
- `docker exec scr_source_postgres psql -U source_user -d supply_chain_source -c "select count(*) as suppliers from suppliers;"`

## Validation Evidence
- Postgres simulation scripts:
  - Syntax: ✅ validated with `bash -n`
  - Runtime: ✅ container `scr_source_postgres` started successfully on port `5433`
  - Seed validation:
    - Tables present: `routes`, `suppliers`, `shipments`
    - Row counts: `routes=3`, `suppliers=3`
- IoT emitter:
  - ✅ Script writes JSONL event files to `data/iot_landing`
  - Schema fields generated: `event_ts`, `sensor_id`, `route_code`, `temperature_c`, `humidity_pct`, `battery_mv`
  - Evidence files generated:
    - `iot_20260411T012933Z.jsonl`
    - `iot_20260411T012955Z.jsonl`
    - `iot_20260411T012956Z.jsonl`
- Bootstrap flow:
  - ✅ Environment check passed for `DATABRICKS_HOST`, `DATABRICKS_HTTP_PATH`, `DATABRICKS_TOKEN`
  - ✅ Source simulation start, IoT file emission, landing verification, and Bronze SQL hints completed.
- Databricks Bronze ingestion runtime:
  - ✅ Ingestion command executed from bootstrap step [5/5]
  - ✅ Clean run load result: `Loaded 30 rows into workspace.bronze.iot_events_raw`
  - ✅ Clean run post-load count: `Current row_count: 121`
  - ✅ Target table: `workspace.bronze.iot_events_raw`

## Issues and Resolutions
- Incident:
  - None blocking during local execution.
- Root Cause:
  - N/A
- Resolution:
  - N/A
- Recurrence Prevention:
  - Keep startup and teardown scripts idempotent and log-driven.
- Mastery Lesson:
  - A local-first ingestion path can keep delivery moving under strict cost boundaries.

## Acceptance Criteria Met
- [x] Postgres source simulation scripts created.
- [x] IoT heartbeat emitter implemented with repeatable output contract.
- [x] Batch bootstrap script created and executed for end-to-end local setup.
- [x] Bronze ingestion evidence captured from Databricks runtime.
- [x] Source-to-Bronze reconciliation logged (30 local rows loaded in clean run).

## Handover Notes
- What changed for the next batch:
  - Batch 2.1 is complete with local simulation and Databricks Bronze load proof.
- Risks/Dependencies:
  - Docker runtime availability in Codespace may vary.
  - Airbyte extension path remains deferred until MVP gate confirmation.
- Next Batch Recommendation:
  - Proceed to Batch 2.2 Autoloader logic and incremental checkpointing validation.
