# dbt Commands

This log captures dbt commands used for Batch 1.1 profile and connectivity validation.

## Local Preparation

### Install adapter
```bash
pip install dbt-databricks
```

### Validate secrets are present
```bash
./scripts/check_databricks_env.sh
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
- Keep the profile value source as environment variables.
- If `dbt debug` fails, capture the exact error in `docs/incidents/` and update the phase report.
