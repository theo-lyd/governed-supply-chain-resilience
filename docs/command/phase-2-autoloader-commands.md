# Phase 2 Autoloader Commands

This log captures commands for Batch 2.2 (Databricks Autoloader Logic).

## Chunk 4: Incremental Landing with cloudFiles

### Local authoring and dry-run validation
```bash
python3 scripts/autoloader_bronze.py \
  --dry-run \
  --input-path dbfs:/tmp/scr/iot_landing \
  --checkpoint-path dbfs:/tmp/scr/checkpoints/iot_events_raw
```

### Databricks runtime execution
```bash
python3 scripts/autoloader_bronze.py \
  --input-path dbfs:/tmp/scr/iot_landing \
  --checkpoint-path dbfs:/tmp/scr/checkpoints/iot_events_raw
```

### Optional continuous mode for debugging only
```bash
python3 scripts/autoloader_bronze.py \
  --input-path dbfs:/tmp/scr/iot_landing \
  --checkpoint-path dbfs:/tmp/scr/checkpoints/iot_events_raw \
  --continuous
```

## Run Summary
- Cost-aware execution uses `availableNow` by default, so the stream processes currently available files and stops.
- The stream target is `workspace.bronze.iot_events_raw` in the cost-constrained track.
- Checkpointing should remain stable across reruns so only newly arrived files are processed.

## Notes
- Autoloader requires a Databricks runtime and a Databricks-accessible landing path.
- This batch is intentionally bounded to avoid always-on cluster cost.
- Keep all command evidence synchronized with `docs/phase-reports/SCR-P2-B2.2-report.md`.
