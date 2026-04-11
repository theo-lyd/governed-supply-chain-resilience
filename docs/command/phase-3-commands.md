# Phase 3 Commands

This log captures commands for Batch 3.1 (Silver normalization and AGS harmonization).

## Chunk 1: Silver Build Inputs

### Ensure reference mapping exists
```bash
ls -lh data/reference/route_ags_mapping.csv
```

### Ensure Bronze baseline exists
```bash
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
print(conn.execute("select count(*) from bronze.iot_events_raw").fetchone()[0])
PY
```

## Chunk 2: Batch 3.1 Execution

### One-command Batch 3.1 bootstrap
```bash
chmod +x ./scripts/bootstrap_phase_3_1.sh
./scripts/bootstrap_phase_3_1.sh
```

### Direct Silver build command
```bash
python3 scripts/build_silver_phase_3_1.py \
  --db-path data/duckdb/scr.duckdb \
  --mapping-csv data/reference/route_ags_mapping.csv
```

## Chunk 3: Validation Queries

### Validate AGS completeness and route coverage
```bash
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
print("null_ags", conn.execute("""
  select count(*)
  from silver.iot_events_normalized
  where origin_ags is null or destination_ags is null
""").fetchone()[0])
print("distinct_routes_silver", conn.execute("select count(distinct route_code) from silver.iot_events_normalized").fetchone()[0])
print("distinct_routes_bronze", conn.execute("select count(distinct route_code) from bronze.iot_events_raw").fetchone()[0])
PY
```

### Sample canonical city outputs
```bash
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
for row in conn.execute("""
  select route_code, origin_city, destination_city
  from silver.dim_route_geo
  order by route_code
""").fetchall():
    print(row)
PY
```

## Notes
- This batch implements BL-011 and BL-012 scope for deterministic city normalization and AGS harmonization.
- Incremental lookback (BL-013) remains in Batch 3.2 scope.
