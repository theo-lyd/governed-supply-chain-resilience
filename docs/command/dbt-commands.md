# dbt Commands

This log captures dbt commands for the DuckDB-native execution track.

## Local Preparation

### Install adapter
```bash
pip install dbt-duckdb duckdb
```

### Validate local prerequisites
```bash
./scripts/check_duckdb_env.sh
```

## Profile Setup

### Copy profile template
```bash
mkdir -p ~/.dbt
cp dbt/profiles.yml.example ~/.dbt/profiles.yml
```

### Validate profile target
```bash
dbt debug --profile governed_supply_chain_resilience --target dev
```

## Notes
- Keep profile values environment-driven where useful (`DUCKDB_PATH`, schema vars).
- Default DuckDB path is `data/duckdb/scr.duckdb`.
- Capture dbt errors in phase reports and incidents documentation.
