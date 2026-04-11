# Master Thesis Execution Roadmap: Supply Chain Resilience Engine

This roadmap treats connectivity challenges as evidence of engineering maturity, not project friction. The objective is to prove end-to-end capability in a professional Developer Inner Loop: code authored in GitHub Codespace, executed on Databricks, validated with reproducible controls, and documented for thesis defense and industry review.

## Strategic Objective
Deliver a thesis-grade platform that demonstrates:
- Secure local-to-remote engineering workflow (Codespace -> Databricks)
- Strong data governance and observability practices
- Analytics engineering depth (SCD Type 2, incremental modeling, data quality)
- Production-oriented AI/ML integration and monitoring

---

## Phase 1: Infrastructure and Developer Inner Loop Foundation
Goal: Establish secure, reproducible connectivity between Codespace and Databricks.

### Batch 1.1: Connectivity and Security Setup
- Chunk 1: Databricks Access Control
  - Generate a scoped Databricks PAT.
  - Create a Service Principal (example: `dbt_runner`) for production-like identity isolation.
- Chunk 2: Secret Management in Codespace
  - Store `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, and `DATABRICKS_HTTP_PATH` in GitHub Codespace Secrets.
  - Enforce no hard-coded credentials in repository files.
- Chunk 3: dbt `profiles.yml` Configuration
  - Configure `dbt-databricks` from Codespace.
  - Validate authentication and target resolution with `dbt debug`.
  - Use modern metadata access patterns compatible with current dbt-databricks capabilities.

#### Execution Status (2026-04-10)
- Implemented in repository:
  - `dbt/profiles.yml.example`
  - `scripts/check_databricks_env.sh`
  - `docs/command/databricks-commands.md`
  - `docs/command/dbt-commands.md`
  - `docs/phase-reports/SCR-P1-B1.1-report.md`
- Batch 1.1 Status:
  - ✅ COMPLETED/VERIFIED (2026-04-11)
  - dbt debug passed, Databricks connectivity verified, adapter installed

### Batch 1.2: Environment Containerization
- Chunk 4: `.devcontainer` Engineering
  - Build a Codespace image that pre-installs `dbt-databricks`, Databricks CLI, and Airflow dependencies.
  - Pin versions for reproducibility.
  - ✅ COMPLETED: `.devcontainer/devcontainer.json` with pinned tools, VS Code extensions, Python settings
  - ✅ COMPLETED: `.devcontainer/postCreateCommand.sh` with 7-step automated setup
- Chunk 5: Unity Catalog Initialization
  - Create separate `dev` and `prod` catalogs.
  - Apply baseline naming conventions and permission boundaries.
  - ✅ COST-CONSTRAINED FALLBACK: proceed with `workspace` catalog defaults when UC storage root is unavailable
  - 🔁 OPTIONAL UPGRADE: enable Unity Catalog later with `ENABLE_UNITY_CATALOG=1` and `UNITY_CATALOG_STORAGE_ROOT`
- Batch 1.2 Status:
  - ✅ COMPLETED/VERIFIED (Cost-Constrained Track) (2026-04-11)
  - Containerization verified; non-UC execution path active without paid cloud setup

#### Architecture Decision Note (Phase 1.2)
- Standard/target architecture remains Unity Catalog with dedicated environment boundaries and governed metadata.
- Temporary implementation track uses the `workspace` catalog fallback due explicit user cost constraint: no paid cloud account setup and no card-linked account creation.
- This is an intentional scope adaptation, not a technical preference reversal.

#### Why Excluding Unity Catalog Now
- Unity Catalog provisioning in this workspace requires a metastore storage root or managed location.
- A storage root requires external cloud object storage setup, which is out of scope for the current cost boundary.
- Proceeding without UC avoids blocking Phase 2 execution while preserving a documented upgrade path.

#### Implementation and Performance Implications Without Unity Catalog
- Implementation model:
  - Continue with Databricks + dbt using `workspace` catalog fallback and schema-level separation.
  - Keep naming conventions and medallion progression unchanged.
  - Maintain governance evidence through repository controls, dbt tests, and phase reports.
- Performance expectations:
  - Core query and transformation performance for thesis-scale datasets remains suitable.
  - No expected degradation for current batch goals based solely on catalog layer selection.
  - Main trade-off is governance depth and enterprise permission granularity, not compute throughput.
- Risk profile:
  - Reduced fine-grained governance and lineage controls compared with full UC.
  - Acceptable for current cost-constrained implementation track.
  - Tracked as optional uplift in later hardening.

#### Hive Metastore Clarification
- Hive Metastore is the legacy catalog namespace; it is not the abandoned trio of `storage_root`, metastore, and Unity Catalog.
- In this workspace, Hive Metastore access is disabled at the workspace level, which is why direct `hive_metastore` execution failed.
- The failure is therefore caused by workspace policy, not by the decision to skip paid cloud storage setup.
- The operational fallback used by this project is `workspace`, not `hive_metastore`.

### Phase 1 Exit Criteria
- ✅ Codespace can run `dbt debug` successfully against Databricks. (Batch 1.1)
- ✅ Secrets are injected securely with no plaintext credentials in Git. (Batch 1.1)
- ✅ Catalog strategy is operational for implementation track (Batch 1.2 cost-constrained fallback)
- ✅ **PHASE 1 COMPLETE (COST-CONSTRAINED TRACK)**

### Phase 1 Handoff Notes
- Execution path: Batch 1.1 (Connectivity) → Batch 1.2 (Containerization, Catalogs)
- Reports: [SCR-P1-B1.1-report.md](../phase-reports/SCR-P1-B1.1-report.md), [SCR-P1-B1.2-report.md](../phase-reports/SCR-P1-B1.2-report.md)
- Ready to proceed: Phase 2 Batch 2.1 (Multi-Source Ingestion)
- Estimated Phase 2 duration: 4-6 hours initial, includes Docker Postgres, IoT emitter, Bronze loads

---

## Phase 2: Ingestion and Bronze Layer
Goal: Ingest multi-modal logistics data (IoT and ERP-like records) reliably and incrementally.

### Batch 2.1: Multi-Source Ingestion
- Chunk 1: Operational DB Simulation
  - Run Postgres in Docker for route and supplier metadata.
- Chunk 2: Source Sync Strategy (Core First, Extension Ready)
  - Core path: implement one reliable ingestion path into Databricks Bronze and validate repeatability.
  - Extension path: configure Airbyte sync from Postgres to Databricks Bronze when source heterogeneity needs explicit demonstration.
  - Validate initial full load plus incremental sync behavior for the chosen path.
- Chunk 3: IoT Heartbeat Simulation
  - Implement `iot_emitter.py` to emit event files at a fixed interval to a landing zone.

#### Execution Status (2026-04-11)
- Implemented in repository:
  - `sql/postgres/init_source.sql`
  - `scripts/start_postgres_source.sh`
  - `scripts/stop_postgres_source.sh`
  - `scripts/iot_emitter.py`
  - `scripts/bootstrap_phase_2_1.sh`
  - `docs/command/phase-2-commands.md`
  - `docs/phase-reports/SCR-P2-B2.1-report.md`
- Batch 2.1 Status:
  - ✅ COMPLETED/VERIFIED (2026-04-11)
  - Local Postgres simulation, IoT emitter, and Databricks Bronze ingestion validated.
  - Bronze evidence: `workspace.bronze.iot_events_raw` loaded with reproducible command path.

### Batch 2.2: Databricks Autoloader Logic
- Chunk 4: Incremental Landing with `cloudFiles`
  - Configure Autoloader to detect and process newly arrived IoT files.
  - Demonstrate cost-aware streaming-lite ingestion versus always-on streaming clusters.

### Phase 2 Exit Criteria
- Bronze ingestion works through at least one reliable path and is reproducible.
- Late file arrivals are detectable and processed.
- Pipeline run logs show successful repeated incremental loads.

### MVP Gate and Extension Track
Before proceeding to later-phase complexity, confirm the MVP gate:
- Databricks + dbt pipeline runs end-to-end with documented validation.
- One ingestion path is stable and repeatable.

After MVP gate approval, add extension capabilities as needed:
- Airbyte for explicit multi-source synchronization patterns.
- Airflow for scheduled orchestration, dependency management, and operational automation.

---

## Phase 3: Silver Layer and German Data Normalization
Goal: Apply rigorous cleaning with explicit support for German-language and regional constraints.

### Batch 3.1: String and Encoding Normalization
- Chunk 1: Umlaut Transliteration Macro
  - Build a dbt macro to normalize German characters consistently (for example: `ae`, `oe`, `ue`, `ss`).
- Chunk 2: Administrative Harmonization
  - Map AGS codes to canonical city/region entities via lookup tables.
  - Preserve source values for traceability.

Example dbt expression pattern:

```sql
lower(
  replace(
    replace(
      replace(
        replace(
          replace(city_name, 'ae', 'ae'),
          'oe', 'oe'
        ),
        'ue', 'ue'
      ),
      'ss', 'ss'
    ),
    '  ', ' '
  )
)
```

### Batch 3.2: Financial and Metric Scaling
- Chunk 3: Domain Abbreviation and Currency Normalization
  - Standardize terms such as `LKW` -> `truck`.
  - Convert strings such as `Mio. EUR` into numeric columns.
- Chunk 4: Late-Arriving Data Buffer
  - Implement incremental model logic with a lookback window for delayed telemetry.
  - Backfill only impacted partitions to balance correctness and cost.

### Phase 3 Exit Criteria
- German text normalization passes deterministic tests.
- AGS-to-city mapping is consistent and auditable.
- Incremental backfill logic handles delayed IoT events correctly.

---

## Phase 4: Gold Layer and Analytics Engineering
Goal: Build business-grade historical modeling and SLA logic.

### Batch 4.1: Supplier Reliability SCD Type 2
- Chunk 1: dbt Snapshots
  - Create `snapshots/supplier_reliability.sql` for historized supplier scoring.
- Chunk 2: Historical Integrity in Gold Models
  - Ensure joins use the score version valid at event time, not current-state values.

### Batch 4.2: Cold Chain SLA Logic
- Chunk 3: Rolling Temperature Breach Windows
  - Use SQL window logic to flag shipments above 8 C for more than 120 minutes.
- Chunk 4: Lead-Time Calculation Across Time Zones
  - Compute `actual_arrival - estimated_arrival` with explicit timezone handling.

### Phase 4 Exit Criteria
- SCD Type 2 snapshots pass point-in-time correctness checks.
- Cold-chain breach rules are test-covered and reproducible.
- Gold marts expose trusted SLA and performance metrics.

---

## Phase 5: Predictive Intelligence and ML
Goal: Move from descriptive reporting to reliable risk prediction.

### Batch 5.1: Delay Prediction with Random Forest
- Chunk 1: dbt Python Model
  - Implement a `type: python` model in dbt running on Databricks.
- Chunk 2: Feature Engineering and Training
  - Train a Random Forest classifier for `is_late`.
  - Candidate features: `scheduled_days`, `shipping_mode`, `iot_avg_temp`, and route context.

### Batch 5.2: Route Risk Segmentation and Drift Monitoring
- Chunk 3: K-Means Risk Clusters
  - Segment routes into operational risk zones.
- Chunk 4: Model Performance Monitoring
  - Define a drift/quality threshold (example: accuracy < 0.75) and trigger alerts.

### Phase 5 Exit Criteria
- Prediction pipeline produces stable, explainable outputs.
- Drift monitoring is active with alert routing documented.
- Risk segmentation is consumable by downstream dashboarding.

---

## Phase 6: CI/CD, Observability, and SLA Operations
Goal: Prove production readiness with automation, lineage, and incident response.

### Batch 6.1: Data Quality and Observability
- Chunk 1: Great Expectations Checkpoints
  - Validate non-negative `lead_time` and valid geo bounds.
- Chunk 2: Lineage and Freshness Monitoring
  - Integrate Monte Carlo with Databricks.
  - Alert when telemetry freshness breaches thresholds (example: no update for 4 hours).

### Batch 6.2: CI/CD and Product Narrative
- Chunk 3: Pull Request Slim CI
  - Run dbt tests on PRs against isolated test data/clone strategy.
- Chunk 4: Streamlit Risk Monitor
  - Deploy a live risk map with operator-focused workflows.
  - Include natural-language query support for dispatcher decisions.

### Phase 6 Exit Criteria
- CI blocks unsafe merges on test failure.
- Observability stack captures freshness, quality, and lineage incidents.
- Demo application presents actionable risk insights for stakeholders.

---

## Why This Structure Wins
1. Complexity Control
- The Phase -> Batch -> Chunk hierarchy enables iterative delivery while reducing execution risk.

2. Industry Signal
- The workflow demonstrates product-minded engineering, governance, and operational ownership.

3. Thesis Rigor
- The combination of German-market normalization, historized modeling, and applied ML satisfies academic and practical evaluation standards.

## Implementation Guidance
- Treat each batch as a governed unit: define scope, execute, validate, and document outcomes.
- Record incidents and remediations as evidence of engineering maturity.
- Keep all logic in Git-managed sources and execute remotely via Databricks to preserve reproducibility and auditability.
