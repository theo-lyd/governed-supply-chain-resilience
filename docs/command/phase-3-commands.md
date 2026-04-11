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
- Batch 3.2 adds BL-013 lookback handling and domain normalization for `LKW`/`Mio. EUR`.

## Batch 3.2: Incremental Lookback + Domain Normalization

### One-command Batch 3.2 bootstrap
```bash
chmod +x ./scripts/bootstrap_phase_3_2.sh
./scripts/bootstrap_phase_3_2.sh
```

### Direct Batch 3.2 build command
```bash
python3 scripts/build_silver_phase_3_2.py \
  --db-path data/duckdb/scr.duckdb \
  --terms-csv data/reference/route_business_terms.csv \
  --lookback-hours 48
```

### Validate LKW and Mio. EUR normalization
```bash
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
print(conn.execute("""
select route_code, vehicle_type_raw, vehicle_type, contract_value_raw, contract_value_million_eur
from silver.route_business_terms_normalized
order by route_code
""").fetchall())
PY
```

### Validate lookback parity
```bash
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
max_ts = conn.execute("select max(event_ts) from silver.iot_events_normalized").fetchone()[0]
source_count = conn.execute(f"""
select count(*) from silver.iot_events_normalized
where event_ts >= (timestamp '{max_ts}' - interval '48 hours')
""").fetchone()[0]
curated_count = conn.execute("select count(*) from silver.iot_events_curated").fetchone()[0]
print(source_count, curated_count)
PY
```
