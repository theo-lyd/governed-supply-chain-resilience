# Master Thesis Execution Roadmap: Supply Chain Resilience Engine

This roadmap defines the active execution strategy for the thesis portfolio after the compute-constraint pivot.

## Architecture Decision (2026-04-11)
- Active execution target: DuckDB-native architecture in GitHub Codespaces.
- Reason: current no-paid-cloud constraint and unavailable Spark-capable Databricks compute.
- Principle: keep governance, reproducibility, medallion layering, and evidence quality unchanged.

## Strategic Objective
Deliver a thesis-grade platform that demonstrates:
- Reproducible local engineering workflow (Codespace + DuckDB)
- Strong data governance and observability practices
- Analytics engineering depth (SCD Type 2, incremental modeling, data quality)
- Production-oriented AI/ML integration and monitoring

---

## Phase 1: Infrastructure and Developer Inner Loop Foundation
Goal: establish secure, reproducible local execution in Codespaces.

### Batch 1.1: Local Baseline and dbt Profile
- Validate local toolchain prerequisites (`python3`, `pip`).
- Configure `dbt/profiles.yml.example` for `dbt-duckdb`.
- Verify with `dbt debug` on local target.

Status:
- ✅ Completed/Verified (pivoted)
- Key artifacts:
  - `dbt/profiles.yml.example`
  - `scripts/check_duckdb_env.sh`
  - `scripts/bootstrap_phase_1_1.sh`
  - `docs/command/dbt-commands.md`
  - `docs/phase-reports/SCR-P1-B1.1-report.md`

### Batch 1.2: Containerization and Local Medallion Schema Setup
- Keep reproducible devcontainer baseline.
- Initialize `bronze`, `silver`, `gold`, `analytics` schemas in local DuckDB.
- Validate schema availability for downstream batches.

Status:
- ✅ Completed/Verified (DuckDB-native)
- Key artifacts:
  - `.devcontainer/devcontainer.json`
  - `.devcontainer/postCreateCommand.sh`
  - `scripts/bootstrap_phase_1_2.sh`
  - `docs/phase-reports/SCR-P1-B1.2-report.md`

### Phase 1 Exit Criteria
- ✅ `dbt debug` succeeds on local DuckDB target.
- ✅ Reproducible bootstrap scripts are executable in Codespaces.
- ✅ Local medallion schemas are available for ingestion and modeling.

---

## Phase 2: Ingestion and Bronze Layer
Goal: ingest multi-modal logistics data reliably and incrementally.

### Batch 2.1: Multi-Source Ingestion (DuckDB Bronze)
- Run Postgres in Docker for source-system simulation.
- Emit IoT JSONL files using `iot_emitter.py`.
- Load events into `bronze.iot_events_raw` in local DuckDB.

Status:
- ✅ Completed/Verified (pivoted)
- Key artifacts:
  - `scripts/ingest_iot_to_duckdb.py`
  - `scripts/bootstrap_phase_2_1_duckdb.sh`
  - `docs/command/phase-2-commands.md`
  - `docs/phase-reports/SCR-P2-B2.1-report.md`

### Batch 2.2: Incremental Landing (DuckDB File-State)
- Replace Databricks `cloudFiles` Autoloader with local incremental ingestion.
- Track processed filenames in a persistent state file.
- Ingest only unseen files into `bronze.iot_events_raw`.

Status:
- ✅ Completed/Verified (DuckDB incremental)
- Key artifacts:
  - `scripts/autoloader_bronze.py`
  - `docs/command/phase-2-autoloader-commands.md`
  - `docs/phase-reports/SCR-P2-B2.2-report.md`

### Phase 2 Exit Criteria
- ✅ Bronze ingestion is reproducible and command-driven.
- ✅ Late file arrivals are detected as new inputs.
- ✅ Incremental runs avoid duplicate file ingestion through state tracking.

---

## Phase 3: Silver Layer and German Data Normalization
Goal: apply deterministic normalization with German-market constraints.

### Batch 3.1
- Implement umlaut transliteration and text standardization macros.
- Harmonize AGS codes and canonical geography entities.

Status:
- ✅ Completed/Verified (DuckDB Silver normalization)
- Key artifacts:
  - `data/reference/route_ags_mapping.csv`
  - `scripts/build_silver_phase_3_1.py`
  - `scripts/bootstrap_phase_3_1.sh`
  - `docs/command/phase-3-commands.md`
  - `docs/phase-reports/SCR-P3-B3.1-report.md`

### Batch 3.2
- Normalize domain abbreviations and currency forms.
- Add incremental lookback logic for late-arriving telemetry.

Status:
- ✅ Completed/Verified (DuckDB Silver curated)
- Key artifacts:
  - `data/reference/route_business_terms.csv`
  - `scripts/build_silver_phase_3_2.py`
  - `scripts/bootstrap_phase_3_2.sh`
  - `docs/phase-reports/SCR-P3-B3.2-report.md`

Exit criteria:
- ✅ Deterministic normalization tests pass.
- ✅ AGS mappings are auditable and reproducible.
- ✅ Incremental lookback handling validated.
- ✅ Domain normalization for `LKW` and `Mio. EUR` validated.

---

## Phase 4: Gold Layer and Analytics Engineering
Goal: build historical and SLA-aware analytics models.

### Batch 4.1
- Implement supplier reliability SCD Type 2 snapshots.
- Enforce point-in-time correctness in Gold joins.

Status:
- ✅ Completed/Verified (DuckDB Gold SCD2 + PIT)
- Key artifacts:
  - `data/reference/supplier_reliability_history.csv`
  - `data/reference/route_supplier_mapping.csv`
  - `scripts/build_gold_phase_4_1.py`
  - `scripts/bootstrap_phase_4_1.sh`
  - `docs/command/phase-4-commands.md`
  - `docs/phase-reports/SCR-P4-B4.1-report.md`

### Batch 4.2
- Implement rolling cold-chain breach detection.
- Compute timezone-safe lead-time metrics.

Status:
- ✅ Completed/Verified (DuckDB Gold SLA + lead-time)
- Key artifacts:
  - `data/reference/route_timezone_offsets.csv`
  - `scripts/build_gold_phase_4_2.py`
  - `scripts/bootstrap_phase_4_2.sh`
  - `docs/phase-reports/SCR-P4-B4.2-report.md`

Exit criteria:
- ✅ Snapshot integrity verified.
- ✅ SLA logic and lead-time metrics validated.

---

## Phase 5: Predictive Intelligence
Goal: produce explainable and monitored risk predictions.

### Batch 5.1
- Build delay prediction baseline (Python/dbt-integrated workflow).
- Establish reproducible feature engineering from Bronze/Silver/Gold outputs.

Status:
- ✅ Completed/Verified (DuckDB baseline scoring)
- Key artifacts:
  - `scripts/build_ml_phase_5_1.py`
  - `scripts/bootstrap_phase_5_1.sh`
  - `docs/command/phase-5-commands.md`
  - `docs/phase-reports/SCR-P5-B5.1-report.md`

### Batch 5.2
- Add route risk clustering and model drift thresholds.
- Define response playbook for degraded model performance.

Status:
- ✅ Completed/Verified (DuckDB clustering + drift status)
- Key artifacts:
  - `scripts/build_ml_phase_5_2.py`
  - `scripts/bootstrap_phase_5_2.sh`
  - `docs/phase-reports/SCR-P5-B5.2-report.md`

Exit criteria:
- ✅ Stable scoring outputs with documented quality thresholds.
- ✅ Monitoring and drift-threshold triggers defined.

---

## Phase 6: CI/CD, Observability, and SLA Operations
Goal: prove production readiness in a controlled local-first architecture.

### Batch 6.1
- Implement quality gates and observability checks.
- Add freshness and incident logging controls.

Status:
- ✅ Completed/Verified (DuckDB controls + incident logging)
- Key artifacts:
  - `scripts/build_ops_phase_6_1.py`
  - `scripts/bootstrap_phase_6_1.sh`
  - `docs/command/phase-6-commands.md`
  - `docs/phase-reports/SCR-P6-B6.1-report.md`

### Batch 6.2
- Enforce PR validation pipeline.
- Finalize defense-ready runbook and narrative assets.

Status:
- ✅ Completed/Verified (PR validation + defense package)
- Key artifacts:
  - `.github/workflows/ci-quality-gates.yml`
  - `scripts/validate_phase_6_2_assets.py`
  - `docs/planning/thesis-defense-runbook.md`
  - `docs/planning/thesis-defense-narrative.md`
  - `docs/phase-reports/SCR-P6-B6.2-report.md`

Exit criteria:
- ✅ CI gates enforce quality standards.
- ✅ Documentation and evidence are defense-ready.

---

## Governance Rules
- All code lives in Git-managed files.
- All batch runs produce command and validation evidence.
- Every scope change updates roadmap, command logs, and phase reports.
- Legacy Databricks artifacts are retained only as historical context.
