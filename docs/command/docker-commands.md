# Docker Commands

Container lifecycle commands used for local source simulation and services.

## Entries

### 2026-04-11 - Validate source simulation container
Command:
```bash
docker ps --filter "name=scr_source_postgres"
```
Purpose:
- Confirm the Postgres source simulation container is running.
Result:
- Container health and visibility confirmed during Batch 2.1 checks.

### 2026-04-11 - Remove generated local artifacts during cleanup
Command:
```bash
rm -f data/duckdb/scr.duckdb data/duckdb/ingestion_state/processed_iot_files.json
```
Purpose:
- Clean generated runtime artifacts from workspace.
Result:
- Files removed successfully.
