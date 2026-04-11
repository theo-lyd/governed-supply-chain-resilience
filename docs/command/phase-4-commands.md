# Phase 4 Commands

This log captures commands for Batch 4.1 (Gold SCD Type 2 and point-in-time joins).

## Chunk 1: Input Baseline Checks

### Verify Phase 3 curated data exists
```bash
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
print(conn.execute("select count(*) from silver.iot_events_curated").fetchone()[0])
PY
```

### Verify reference mappings
```bash
ls -lh data/reference/route_supplier_mapping.csv data/reference/supplier_reliability_history.csv
```

## Chunk 2: Batch 4.1 Execution

### One-command bootstrap
```bash
chmod +x ./scripts/bootstrap_phase_4_1.sh
./scripts/bootstrap_phase_4_1.sh
```

### Direct build command
```bash
python3 scripts/build_gold_phase_4_1.py \
  --db-path data/duckdb/scr.duckdb \
  --supplier-history-csv data/reference/supplier_reliability_history.csv \
  --route-supplier-csv data/reference/route_supplier_mapping.csv
```

## Chunk 3: Validation Queries

### Validate SCD2 structure
```bash
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
print(conn.execute("""
select supplier_id, count(*) as versions, sum(case when is_current then 1 else 0 end) as current_rows
from gold.dim_supplier_reliability_scd2
group by 1
order by 1
""").fetchall())
PY
```

### Validate PIT join integrity
```bash
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
print('gold_rows', conn.execute("select count(*) from gold.fact_iot_events_pit").fetchone()[0])
print('null_supplier', conn.execute("select count(*) from gold.fact_iot_events_pit where supplier_id is null").fetchone()[0])
print('multi_matches', conn.execute("""
  select count(*) from (
    select event_ts, sensor_id, route_code, count(*) c
    from gold.fact_iot_events_pit
    group by 1,2,3
    having c > 1
  ) x
""").fetchone()[0])
PY
```

## Notes
- Batch 4.1 implements BL-015 (SCD2 snapshots) and BL-016 (point-in-time joins).
- SLA rolling-breach and timezone-safe lead-time logic are in Batch 4.2 scope.
