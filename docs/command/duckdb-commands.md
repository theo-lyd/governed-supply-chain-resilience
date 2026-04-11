# DuckDB Commands

This log captures commands for the DuckDB-native execution track in GitHub Codespaces.

## Local Preparation

### Install DuckDB Python package
```bash
pip install duckdb
```

### Optional: verify DuckDB installation
```bash
python3 -c "import duckdb; print(duckdb.__version__)"
```

## Batch 2.1 (DuckDB-Native Bronze Ingestion)

### One-command local bootstrap
```bash
chmod +x ./scripts/bootstrap_phase_2_1_duckdb.sh
./scripts/bootstrap_phase_2_1_duckdb.sh
```

### Manual ingestion command
```bash
python3 ./scripts/ingest_iot_to_duckdb.py \
  --input-pattern "data/iot_landing/*.jsonl" \
  --db-path data/duckdb/scr.duckdb \
  --schema bronze \
  --table iot_events_raw
```

### Quick row-count check
```bash
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
print(conn.execute("select count(*) from bronze.iot_events_raw").fetchone()[0])
PY
```

## Notes
- DuckDB file path default: `data/duckdb/scr.duckdb`
- Bronze table default: `bronze.iot_events_raw`
- This path is fully local and does not require Databricks compute.
