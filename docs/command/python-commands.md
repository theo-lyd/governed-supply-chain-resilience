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
