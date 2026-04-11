# Databricks Commands

> Legacy track notice (2026-04-11): This document is retained as historical evidence from the Databricks execution track. The active execution path for this repository is now DuckDB-native in Codespaces. Use `docs/command/duckdb-commands.md` for current commands.

This log captures commands for Batch 1.1 and Batch 1.2 (Connectivity, Security Setup, and Environment Containerization).

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

### PAT scope guidance
- Minimum for Batch 1.1: `workspace`
- Recommended for Batch 1.2 and beyond: `workspace`, `unity-catalog`, `access-management`
- If you rotate the token, reopen the terminal after refreshing Codespaces Secrets so the new PAT is loaded.

### Unity Catalog storage root guidance
- Batch 1.2 catalog creation also needs a metastore storage root or managed location.
- Provide `UNITY_CATALOG_STORAGE_ROOT` as a cloud storage path approved for your workspace, or create the catalog from the Databricks UI using the metastore's default storage if your admin has enabled it.
- If this value is missing, catalog creation will fail even when the PAT scopes are correct.

### Cost-constrained mode (no AWS account required)
- If you cannot create a paid cloud account, run Batch 1.2 with Unity Catalog provisioning disabled.
- This keeps the project moving with Databricks + dbt using `workspace` as default catalog fallback.
- Command:
```bash
ENABLE_UNITY_CATALOG=0 ./scripts/bootstrap_phase_1_2.sh
```
- Optional env vars for explicit non-UC catalog/schema naming:
	- `DATABRICKS_CATALOG_DEV` (default: `workspace`)
	- `DATABRICKS_SCHEMA_DEV` (default: `analytics`)
	- `DATABRICKS_CATALOG_PROD` (default: `workspace`)
	- `DATABRICKS_SCHEMA_PROD` (default: `analytics`)

### Why Hive Metastore failed here
- `hive_metastore` is the legacy Databricks metastore namespace, not the same thing as Unity Catalog storage root or the metastore record itself.
- In this workspace, Hive Metastore legacy access is disabled, so any direct `hive_metastore` reference throws `UC_HIVE_METASTORE_DISABLED_EXCEPTION`.
- That failure is not caused by “abandoning” Unity Catalog, storage root, or the metastore; it is caused by the workspace policy disabling legacy Hive Metastore access.
- For this project, the working fallback is `workspace` catalog, which lets the cost-constrained track continue without paid cloud setup.
- If Unity Catalog is later enabled with a managed location, you can switch back to the UC path without changing the local source generation flow.

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
- If you regenerate the PAT with broader scopes, rerun `./scripts/bootstrap_phase_1_2.sh` to verify Unity Catalog access with the new token.
- If catalog creation still fails after token rotation, verify the Unity Catalog storage root or managed location next.
