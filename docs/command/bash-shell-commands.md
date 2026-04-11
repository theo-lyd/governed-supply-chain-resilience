# Bash and Shell Commands

Cross-cutting shell commands used during implementation, validation, and cleanup.

## Logging Rule
For each command, record date, purpose, exact command, and result.

## Entries

### 2026-04-11 - Bootstrap and validation shell checks
Command:
```bash
bash -n scripts/bootstrap_phase_1_1.sh
bash -n scripts/bootstrap_phase_1_2.sh
```
Purpose:
- Validate script syntax before execution.
Result:
- No syntax errors.

### 2026-04-11 - Phase 2.1 shell execution flow
Commands:
```bash
bash -n scripts/start_postgres_source.sh
bash -n scripts/stop_postgres_source.sh
bash -n scripts/bootstrap_phase_2_1_duckdb.sh
chmod +x ./scripts/start_postgres_source.sh
./scripts/start_postgres_source.sh
chmod +x ./scripts/stop_postgres_source.sh
./scripts/stop_postgres_source.sh
chmod +x ./scripts/bootstrap_phase_2_1_duckdb.sh
./scripts/bootstrap_phase_2_1_duckdb.sh
ls -lh data/iot_landing
head -n 3 data/iot_landing/*.jsonl
```
Purpose:
- Validate script structure and execute the Phase 2.1 local ingestion path end to end.
Result:
- Source simulation, IoT file generation checks, and bootstrap execution completed for Bronze ingestion evidence.

### 2026-04-11 - dbt local profile validation
Commands:
```bash
./scripts/check_duckdb_env.sh
dbt debug --profile governed_supply_chain_resilience --target dev
```
Purpose:
- Validate local prerequisites and dbt profile connectivity to DuckDB.
Result:
- dbt local target validation passed.
