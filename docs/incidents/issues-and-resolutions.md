# Issues and Resolutions Log

This log tracks concrete implementation issues encountered during execution, plus root cause and corrective action.

## 2026-04-12 - Databricks connector import error in legacy ingest script
Symptom:
- `scripts/ingest_iot_to_bronze.py` reported import errors (`Unable to import 'databricks'`).

Root cause:
- Static module import (`from databricks import sql`) was enforced at parse time in an environment where the connector may be optional.

Resolution:
- Replaced static import with dynamic loading via `importlib.import_module("databricks.sql")`.
- Added clear fail-fast message: install `databricks-sql-connector` when connector is required.

Prevention:
- Keep optional platform dependencies dynamically imported in legacy-path scripts.

## 2026-04-12 - Phase 6.1 bootstrap failed with missing `duckdb`
Symptom:
- `ModuleNotFoundError: No module named 'duckdb'` when running `bootstrap_phase_6_1.sh`.

Root cause:
- Script used `python3` directly, which did not resolve to the project `.venv` interpreter.

Resolution:
- Updated `scripts/bootstrap_phase_6_1.sh` to auto-select `.venv/bin/python` when available.
- Installed `duckdb` in the configured virtualenv.

Prevention:
- Use interpreter-selection guards in shell scripts where Python package dependencies are required.

## 2026-04-12 - Fresh telemetry regeneration blocked by unavailable Docker
Symptom:
- `bootstrap_phase_2_1_duckdb.sh` failed at source simulation step: `Docker is not installed or not on PATH`.

Root cause:
- Current runtime environment does not provide Docker CLI/daemon.

Resolution:
- Executed Docker-free refresh path:
  - generated new telemetry via `iot_emitter.py`
  - ingested via `autoloader_bronze.py`
  - rebuilt downstream Silver/Gold/Analytics batches.

Prevention:
- Maintain a documented no-Docker fallback path for telemetry refresh and ops-validation continuity.

## 2026-04-12 - Silver 3.1 build failed due missing NumPy
Symptom:
- DuckDB UDF registration raised: `Invalid Input Error: 'numpy' is required for this operation`.

Root cause:
- Active virtualenv lacked `numpy`, required by DuckDB Python UDF internals in this setup.

Resolution:
- Installed `numpy` in project virtualenv and reran downstream batches.

Prevention:
- Include `numpy` in baseline local dependency setup for UDF-enabled transforms.

## 2026-04-12 - Gold 4.1 false positive on PIT duplicate validation
Symptom:
- Batch 4.1 failed with `Events with multiple PIT matches` after data refresh.

Root cause:
- Validation query treated repeated event keys as a join-overlap failure, which is not equivalent to SCD2 interval overlap.

Resolution:
- Updated `scripts/build_gold_phase_4_1.py` to validate overlap directly on SCD2 interval definitions.

Prevention:
- Keep data duplication checks separate from temporal-interval overlap checks in PIT validation.

## 2026-04-12 - Controlled incident closure added
Change:
- Added `--close-resolved-incidents` option to `scripts/build_ops_phase_6_1.py`.
- Added bootstrap toggle `CLOSE_RESOLVED_INCIDENTS=1` (default on) in `scripts/bootstrap_phase_6_1.sh`.

Behavior:
- When current freshness/quality checks pass, matching historical `OPEN` incidents are marked `RESOLVED` with `resolved_at` timestamp.

Operational note:
- Closure is controlled and auditable; set `CLOSE_RESOLVED_INCIDENTS=0` to disable automated resolution.
