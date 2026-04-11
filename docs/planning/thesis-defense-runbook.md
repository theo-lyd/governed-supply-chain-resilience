# Thesis Defense Runbook

## Purpose
This runbook is the step-by-step reproduction guide for the Supply Chain Resilience Engine in its current DuckDB-first, local-first implementation.

## Operating Model
- Development happens in Git-managed files inside GitHub Codespaces.
- Primary execution target is DuckDB in the local workspace.
- Airflow and Databricks remain optional extension tracks, not required for the defense path.
- Every phase is reproducible from the command logs and phase reports.

## Primary Validation Commands
Run these in order when reproducing the thesis evidence:

```bash
./scripts/check_duckdb_env.sh
./scripts/bootstrap_phase_1_1.sh
./scripts/bootstrap_phase_1_2.sh
./scripts/bootstrap_phase_2_1_duckdb.sh
./scripts/bootstrap_phase_3_1.sh
./scripts/bootstrap_phase_3_2.sh
./scripts/bootstrap_phase_4_1.sh
./scripts/bootstrap_phase_4_2.sh
./scripts/bootstrap_phase_5_1.sh
./scripts/bootstrap_phase_5_2.sh
./scripts/bootstrap_phase_6_1.sh
```

## Evidence Checklist
- Phase reports exist for every batch from 1.1 through 6.2.
- Command logs capture the exact commands and outcomes.
- Freshness, quality, and incident controls are visible in `ops` tables.
- ML outputs are traceable to a frozen baseline and monitored drift snapshot.
- Business narrative and architecture narrative remain consistent with the DuckDB-first decision.

## Demo Storyline
1. Start with the business need: protect logistics service levels and supplier trust.
2. Show the architecture pivot to DuckDB-first and explain why it improves reproducibility.
3. Walk through Bronze, Silver, Gold, and Analytics outputs.
4. Demonstrate the Phase 6 controls: freshness checks, quality gates, incident logging, and PR validation.
5. Close with how the project supports defense-ready evidence and future extension paths.

## Reproducibility Notes
- Use the command logs in `docs/command/` as the single source of command evidence.
- Use the phase reports in `docs/phase-reports/` as the batch-level outcome record.
- Keep local environment changes minimal and documented.

## Escalation Notes
If a command fails:
- Check the corresponding phase report for the last known-good output.
- Validate the schema and the latest command log entry.
- Treat missing freshness or quarantine data as a controlled incident, not as an implicit pass.

## Closing Position
The repository is ready for a thesis defense when the runbook, narrative assets, command logs, and phase reports tell the same story: governed analytics engineering under a local-first architecture.
