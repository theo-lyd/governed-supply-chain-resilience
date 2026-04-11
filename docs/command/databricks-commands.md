# Databricks Commands

This log captures commands for Batch 1.1 (Connectivity and Security Setup).

## Required Parameters and Where to Get Them

### `DATABRICKS_HOST`
- Source: Databricks workspace URL.
- Example: `https://dbc-12345678-abcd.cloud.databricks.com`
- How to get it: open Databricks workspace in browser and copy the base URL.

### `DATABRICKS_HTTP_PATH`
- Source: SQL Warehouse or cluster connection details.
- How to get it:
	- Databricks -> SQL Warehouses -> select warehouse -> Connection details.
	- Copy the HTTP Path value.

### `DATABRICKS_TOKEN`
- Source: Personal Access Token (PAT).
- How to get it:
	- Databricks -> User Settings -> Developer -> Access tokens -> Generate new token.
	- Copy token once and store it in GitHub Codespaces Secrets.

### Add values to GitHub Codespaces Secrets
- GitHub repository -> Settings -> Secrets and variables -> Codespaces.
- Add:
	- `DATABRICKS_HOST`
	- `DATABRICKS_HTTP_PATH`
	- `DATABRICKS_TOKEN`

## Access Control and Identity

### Create/verify CLI profile
```bash
databricks auth login --host "$DATABRICKS_HOST"
databricks auth profiles
```

### Service Principal lifecycle (template)
```bash
# Create service principal
databricks service-principals create --display-name dbt_runner

# List service principals
databricks service-principals list

# Grant workspace access or permissions (adjust to your workspace policy)
# databricks permissions set ...
```

## Connectivity Checks

### Validate environment variables
```bash
./scripts/check_databricks_env.sh
```

### One-command Batch 1.1 bootstrap
```bash
chmod +x ./scripts/bootstrap_phase_1_1.sh
./scripts/bootstrap_phase_1_1.sh
```

### Confirm workspace reachability
```bash
databricks current-user me
```

## Notes
- Do not commit PAT values.
- PAT, host, and HTTP path must be sourced from Codespaces Secrets.
- Commands above may vary slightly by Databricks CLI version.
