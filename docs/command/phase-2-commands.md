# Phase 2 Commands

This log captures commands for Batch 2.1 (Multi-Source Ingestion, DuckDB-native).

## Chunk 1: Operational DB Simulation (Postgres in Docker)

### Start source simulation
```bash
chmod +x ./scripts/start_postgres_source.sh
./scripts/start_postgres_source.sh
```

### Validate source container
```bash
docker ps --filter "name=scr_source_postgres"
```

### Stop and cleanup source simulation
```bash
chmod +x ./scripts/stop_postgres_source.sh
./scripts/stop_postgres_source.sh
```

## Chunk 2: Source Sync Strategy (Core First)

### Active core path
- Primary path: local source simulation + DuckDB Bronze table load.
- Airbyte remains optional extension and is deferred until MVP stability.

### Bronze schema (DuckDB)
```sql
CREATE SCHEMA IF NOT EXISTS bronze;
```

## Chunk 3: IoT Heartbeat Simulation

### Emit heartbeat files (JSONL)
```bash
python3 ./scripts/iot_emitter.py \
  --output-dir data/iot_landing \
  --iterations 3 \
  --interval-seconds 5 \
  --events-per-file 20
```

### Verify emitted files
```bash
ls -lh data/iot_landing
head -n 3 data/iot_landing/*.jsonl
```

## Batch Bootstrap

### One-command Batch 2.1 local bootstrap
```bash
chmod +x ./scripts/bootstrap_phase_2_1_duckdb.sh
./scripts/bootstrap_phase_2_1_duckdb.sh
```

## Run Summary
- Clean final run baseline: 2 IoT files x 15 events per file = 30 rows.
- Bronze target: `bronze.iot_events_raw` in `data/duckdb/scr.duckdb`.
- Re-runs are additive unless landing files are cleaned.

## Notes
- This batch is fully local and does not require remote compute.
- Keep evidence synchronized with `docs/phase-reports/SCR-P2-B2.1-report.md`.
