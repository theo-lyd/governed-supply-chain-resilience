# Command Logs Index

This folder is the lifecycle command register for the project.

Policy:
- No command category is excluded.
- As implementation progresses, append new commands to the relevant file.
- Keep commands reproducible: include context, exact command, and observed result.
- Preserve historical tracks (Databricks) and active tracks (DuckDB) with clear labels.

## Active Track
- [DuckDB Commands](duckdb-commands.md)
- [dbt Commands](dbt-commands.md)
- [Phase 2 Commands](phase-2-commands.md)
- [Phase 2 Incremental Loader Commands](phase-2-autoloader-commands.md)

## Legacy Track
- [Databricks Commands](databricks-commands.md)

## Cross-Cutting Command Logs
- [Bash and Shell Commands](bash-shell-commands.md)
- [Make Commands](make-commands.md)
- [Git Commands](git-commands.md)
- [GitHub Actions Commands](github-actions-commands.md)
- [Python Commands](python-commands.md)
- [Airflow Commands](airflow-commands.md)
- [Airbyte Commands](airbyte-commands.md)
- [Docker Commands](docker-commands.md)

## Entry Template
Use this entry block when adding commands:

```markdown
## YYYY-MM-DD - Context Title

Environment:
- Local Codespace / CI / Other

Command:
```bash
<exact command>
```

Purpose:
- Why this command was run.

Result:
- Key output and outcome.

Evidence:
- Reference to phase report or file where outcome is captured.
```
