# Phase 2 Incremental Commands

This log captures commands for Batch 2.2 (DuckDB incremental ingestion).

## Chunk 4: Incremental Landing (File-State Driven)

### Dry-run validation
```bash
python3 scripts/autoloader_bronze.py \
  --dry-run \
  --input-pattern "data/iot_landing/*.jsonl" \
  --db-path data/duckdb/scr.duckdb
```

### Incremental ingestion run
```bash
python3 scripts/autoloader_bronze.py \
  --input-pattern "data/iot_landing/*.jsonl" \
  --db-path data/duckdb/scr.duckdb \
  --schema bronze \
  --table iot_events_raw
```

### Verify newly ingested records
```bash
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
print(conn.execute("select count(*) from bronze.iot_events_raw").fetchone()[0])
print(conn.execute("select count(distinct source_file) from bronze.iot_events_raw").fetchone()[0])
PY
```

## Run Summary
- Incremental behavior is controlled by `data/duckdb/ingestion_state/processed_iot_files.json`.
- Only files not present in the state file are ingested on each run.
- Target table is `bronze.iot_events_raw`.
- Validation results:
  - Initial check with no new files: `new files to ingest = 0`, table remained at 30 rows.
  - After emitting one new file with 7 events: loader ingested exactly 7 new rows.
  - Post-run verification: `table_count = 37`, `source_file_count = 3`.

## Notes
- This replaces the Databricks `cloudFiles` path for the DuckDB-native track.
- Keep all command evidence synchronized with `docs/phase-reports/SCR-P2-B2.2-report.md`.
