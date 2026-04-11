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
