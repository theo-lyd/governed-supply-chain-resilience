# Python Commands

Python invocations used for ingestion, verification, and diagnostics.

## Entries

### 2026-04-11 - Python script compilation check
Command:
```bash
python3 -m py_compile scripts/autoloader_bronze.py
```
Purpose:
- Validate incremental loader syntax before runtime execution.
Result:
- Compilation completed without errors.

### 2026-04-11 - IoT event emitter generation
Command:
```bash
python3 ./scripts/iot_emitter.py \
	--output-dir data/iot_landing \
	--iterations 3 \
	--interval-seconds 5 \
	--events-per-file 20
```
Purpose:
- Generate JSONL heartbeat files for Bronze ingestion tests.
Result:
- IoT landing files were created and used in Batch 2.1 validation.

### 2026-04-11 - Bronze ingest script run
Command:
```bash
python3 ./scripts/ingest_iot_to_duckdb.py \
	--input-pattern "data/iot_landing/*.jsonl" \
	--db-path data/duckdb/scr.duckdb \
	--schema bronze \
	--table iot_events_raw
```
Purpose:
- Load emitted IoT JSONL files into DuckDB Bronze table.
Result:
- Bronze target table row count advanced to baseline used by Batch 2.2.

### 2026-04-11 - Incremental loader execution
Commands:
```bash
python3 scripts/autoloader_bronze.py --input-pattern "data/iot_landing/*.jsonl" --db-path data/duckdb/scr.duckdb --state-file data/duckdb/ingestion_state/processed_iot_files.json
```
Purpose:
- Run incremental file ingestion into DuckDB bronze table.
Result:
- Only unseen files ingested; prior files skipped based on state.

### 2026-04-11 - Incremental dry-run and post-run verification
Commands:
```bash
python3 scripts/autoloader_bronze.py \
	--dry-run \
	--input-pattern "data/iot_landing/*.jsonl" \
	--db-path data/duckdb/scr.duckdb

python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
print(conn.execute("select count(*) from bronze.iot_events_raw").fetchone()[0])
print(conn.execute("select count(distinct source_file) from bronze.iot_events_raw").fetchone()[0])
PY
```
Purpose:
- Validate incremental file detection and resulting table/source-file counts.
Result:
- Confirmed no-op behavior without new files and expected count growth after new file arrival.

### 2026-04-11 - Phase 3.1 Silver build implementation
Commands:
```bash
python3 -m py_compile scripts/build_silver_phase_3_1.py
python3 scripts/build_silver_phase_3_1.py --db-path data/duckdb/scr.duckdb --mapping-csv data/reference/route_ags_mapping.csv
```
Purpose:
- Build and validate Silver normalization outputs with route-level AGS harmonization.
Result:
- Produced `silver.dim_route_geo` and `silver.iot_events_normalized` with zero null AGS values and full route coverage.

### 2026-04-11 - Phase 3.2 lookback and domain normalization build
Commands:
```bash
python3 -m py_compile scripts/build_silver_phase_3_2.py
python3 scripts/build_silver_phase_3_2.py \
	--db-path data/duckdb/scr.duckdb \
	--terms-csv data/reference/route_business_terms.csv \
	--lookback-hours 48
```
Purpose:
- Build curated Silver outputs using lookback refresh logic and normalize `LKW`/`Mio. EUR` domain fields.
Result:
- Produced `silver.route_business_terms_normalized` and refreshed `silver.iot_events_curated` with zero null normalization fields.

### 2026-04-11 - Phase 4.1 Gold SCD2 and PIT build
Commands:
```bash
python3 -m py_compile scripts/build_gold_phase_4_1.py
python3 scripts/build_gold_phase_4_1.py \
	--db-path data/duckdb/scr.duckdb \
	--supplier-history-csv data/reference/supplier_reliability_history.csv \
	--route-supplier-csv data/reference/route_supplier_mapping.csv
```
Purpose:
- Build Gold SCD2 supplier history and point-in-time joined fact events.
Result:
- Produced `gold.dim_supplier_reliability_scd2` and `gold.fact_iot_events_pit` with zero null supplier assignments and no duplicate PIT matches.

### 2026-04-11 - Phase 4.2 Gold SLA and lead-time build
Commands:
```bash
python3 -m py_compile scripts/build_gold_phase_4_2.py
python3 scripts/build_gold_phase_4_2.py \
	--db-path data/duckdb/scr.duckdb \
	--tz-csv data/reference/route_timezone_offsets.csv \
	--breach-threshold-c 8.0 \
	--rolling-window-rows 3
```
Purpose:
- Build Gold SLA event fact with rolling breach flags and route-level timezone-safe lead-time mart.
Result:
- Produced `gold.fact_iot_events_sla` and `gold.mart_route_performance` with zero null timezone mappings.

### 2026-04-11 - Phase 5.1 baseline feature engineering and scoring
Commands:
```bash
python3 -m py_compile scripts/build_ml_phase_5_1.py
python3 scripts/build_ml_phase_5_1.py --db-path data/duckdb/scr.duckdb --threshold 0.50
```
Purpose:
- Build reproducible baseline ML features, risk scores, and evaluation metrics from Gold SLA outputs.
Result:
- Produced `analytics.ml_features_delay_baseline`, `analytics.ml_delay_predictions_baseline`, and `analytics.ml_model_metrics_baseline`.
