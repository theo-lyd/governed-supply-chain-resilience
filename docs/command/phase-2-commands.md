# Phase 2 Commands

This log captures commands for Batch 2.1 (Multi-Source Ingestion).

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

### Cost-constrained core path
- Primary path in this track: local source simulation + Databricks Bronze table load.
- Airbyte remains optional extension and is deferred until MVP stability.

### Bronze schema (Databricks SQL)
```sql
CREATE SCHEMA IF NOT EXISTS workspace.bronze;
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
chmod +x ./scripts/bootstrap_phase_2_1.sh
./scripts/bootstrap_phase_2_1.sh
```

## Run Summary
- Clean final run used 2 IoT files with 15 events per file, for 30 new records loaded.
- The Bronze table load targeted `workspace.bronze.iot_events_raw`.
- Because the landing directory had older files from earlier attempts, the cumulative table count reached 121 after the clean run.
- Earlier non-clean runs showed 35 rows loaded because prior JSONL files remained in `data/iot_landing`.

## Notes
- This batch implements a cost-constrained ingestion MVP path.
- Bronze ingestion SQL/table materialization is executed in Databricks after local generation, targeting `workspace.bronze` by default.
- Keep all command evidence synchronized with `docs/phase-reports/SCR-P2-B2.1-report.md`.
