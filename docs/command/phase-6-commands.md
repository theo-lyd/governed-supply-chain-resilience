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
