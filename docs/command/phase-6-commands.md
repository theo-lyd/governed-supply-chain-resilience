# Phase 6 Commands

Batch-level operational controls and governance commands.

## 2026-04-11 - Batch 6.1 quality controls
Commands:
```bash
bash -n scripts/bootstrap_phase_6_1.sh
python3 -m py_compile scripts/build_ops_phase_6_1.py
./scripts/bootstrap_phase_6_1.sh
```
Purpose:
- Execute freshness checks, quality gates, and automated incident logging.
Result:
- Generated `ops.data_freshness_checks`, `ops.quality_gate_results`, and `ops.incident_log` artifacts.

## 2026-04-11 - Batch 6.2 PR validation and defense assets
Commands:
```bash
bash -n scripts/bootstrap_phase_6_1.sh
python3 -m py_compile scripts/build_ops_phase_6_1.py scripts/validate_phase_6_2_assets.py
python3 scripts/validate_phase_6_2_assets.py
./scripts/bootstrap_phase_6_1.sh
```
Purpose:
- Enforce PR validation checks for the defense-ready runbook, narrative assets, and Phase 6 roadmap alignment.
Result:
- Validated that defense-facing docs exist and that the local-first Phase 6 control loop remains reproducible.

## 2026-04-12 - Batch 6 execution rerun (environment compatibility)
Commands:
```bash
bash -n scripts/bootstrap_phase_6_1.sh
./scripts/bootstrap_phase_6_1.sh
python3 scripts/validate_phase_6_2_assets.py
```
Purpose:
- Re-execute Phase 6 controls and validation in the active virtualenv-backed workspace.
Result:
- Batch 6.1 control loop executes successfully after updating bootstrap script to auto-use `.venv/bin/python` when present.
- Batch 6.2 asset validation passed.

## 2026-04-12 - Controlled incident closure execution
Commands:
```bash
FRESHNESS_HOURS=1 CLOSE_RESOLVED_INCIDENTS=1 ./scripts/bootstrap_phase_6_1.sh
python3 - << 'PY'
import duckdb
conn = duckdb.connect("data/duckdb/scr.duckdb")
print("open", conn.execute("select count(*) from ops.incident_log where status='OPEN'").fetchone()[0])
print("resolved", conn.execute("select count(*) from ops.incident_log where status='RESOLVED'").fetchone()[0])
PY
```
Purpose:
- Perform a controlled resolution step that closes stale OPEN incidents after successful quality and freshness checks.
Result:
- Incident state transitioned to healthy baseline (`open=0`, `resolved=17`).
