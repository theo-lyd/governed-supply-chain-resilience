# Master Execution Backlog: Supply Chain Resilience Engine

## 1. Planning Baseline
This backlog is execution-ready and aligned to the DuckDB-native architecture decision:
- Core first: Codespace + DuckDB + dbt-duckdb + one reliable ingestion path.
- Extensions second: Airbyte and Airflow added only after MVP stability.
- Governance always on: documentation, tests, incident logs, and phase reports are mandatory.

Sprint model:
- Duration: 2 weeks per sprint
- Capacity assumption: 35 story points per sprint
- Point scale: Fibonacci (`1, 2, 3, 5, 8, 13`)
- Delivery objective: 8 sprints from infrastructure to defense-ready portfolio

Roles:
- Data Engineer (DE)
- Analytics Engineer (AE)
- ML Engineer (MLE)
- BI Analyst (BIA)
- Data Quality Engineer (DQE)
- Platform Engineer (PE)
- Product/Thesis Owner (PTO)

## 2. Definition of Ready and Done
Definition of Ready (DoR):
- Scope is written as a clear user story.
- Dependencies are identified.
- Acceptance criteria are testable.
- Required local tools are available.

Definition of Done (DoD):
- Code merged through PR with review.
- Validation evidence captured (`dbt debug`, tests, or equivalent).
- Batch/phase report updated in `docs/phase-reports/`.
- Command and incident logs updated where relevant.

## 3. Epic Overview
| Epic ID | Epic Name | Total Points | Primary Owner | Outcome |
| :--- | :--- | :---: | :--- | :--- |
| E1 | Inner Loop and Platform Foundation | 34 | DE + PE | Reproducible Codespace -> DuckDB workflow |
| E2 | Bronze Ingestion and Source Integration | 42 | DE | Reliable ingestion and incremental file processing |
| E3 | Silver Normalization (German Constraints) | 39 | AE | Trusted cleaned datasets and harmonized dimensions |
| E4 | Gold Analytics and SCD Type 2 | 34 | AE | Historical and SLA-ready marts |
| E5 | Predictive Intelligence | 29 | MLE + AE | Delay-risk scoring and segmentation |
| E6 | Quality, Observability, and CI/CD | 37 | DQE + PE | Production-style controls and guarded delivery |
| E7 | BI and Decision Experience | 21 | BIA | Risk map and scorecards for stakeholders |
| E8 | Thesis Packaging and Defense Assets | 24 | PTO + AE | Defense-ready documentation and narrative |

## 4. Prioritized Product Backlog
| ID | User Story | Epic | Points | Priority | Primary Owner | Supporting Roles | Dependencies | Acceptance Criteria |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- | :--- | :--- |
| BL-001 | As an engineer, I need local environment checks for DuckDB execution. | E1 | 5 | Must | PE | DE | None | `check_duckdb_env.sh` validates required local tools. |
| BL-002 | As an AE, I need dbt-duckdb configured so transformations run locally and reproducibly. | E1 | 5 | Must | AE | DE | BL-001 | `dbt debug` succeeds for `dev` target. |
| BL-003 | As a platform owner, I need local medallion schemas initialized (`bronze/silver/gold`). | E1 | 8 | Must | PE | DE | BL-002 | Schemas exist in DuckDB file and are queryable. |
| BL-004 | As a developer, I need a reproducible devcontainer for core tooling. | E1 | 5 | Must | PE | AE | BL-001 | Container builds with pinned versions and startup docs. |
| BL-005 | As a DE, I need source data landing conventions so ingestion is traceable. | E2 | 3 | Must | DE | AE | BL-003 | Landing path and naming policy documented and tested. |
| BL-006 | As a DE, I need IoT heartbeat simulation to produce incremental files. | E2 | 5 | Must | DE | AE | BL-005 | `iot_emitter.py` generates files with schema contract. |
| BL-007 | As a DE, I need incremental file-state ingestion to load only new IoT files. | E2 | 8 | Must | DE | AE | BL-006 | New files are detected and loaded exactly once. |
| BL-008 | As a DE, I need Postgres in Docker to simulate transactional source data. | E2 | 5 | Should | DE | PE | BL-004 | Postgres container seeded and queryable from Codespace. |
| BL-009 | As a DE, I need optional Airbyte sync from Postgres to Bronze for source heterogeneity. | E2 | 8 | Should | DE | PE | BL-008 | Initial + incremental sync validated and logged. |
| BL-010 | As an AE, I need Bronze quality checks to reject malformed records. | E2 | 8 | Must | AE | DQE | BL-007 | Schema/null checks pass and quarantined records documented. |
| BL-011 | As an AE, I need German text normalization macros in Silver. | E3 | 8 | Must | AE | DE | BL-010 | Umlaut normalization tests pass deterministically. |
| BL-012 | As an AE, I need AGS code harmonization for canonical geography. | E3 | 8 | Must | AE | DE | BL-011 | AGS mapping validated with reference lookups. |
| BL-013 | As an AE, I need incremental lookback logic for late-arriving IoT records. | E3 | 8 | Must | AE | DE | BL-010 | Backfill affects only impacted partitions and is reproducible. |
| BL-014 | As an AE, I need domain normalization (LKW, Mio. EUR) for business consistency. | E3 | 5 | Should | AE | BIA | BL-011 | Converted values pass semantic checks. |
| BL-015 | As an AE, I need supplier reliability snapshots (SCD Type 2). | E4 | 8 | Must | AE | DE | BL-012 | Snapshot history queryable with valid-from/to fields. |
| BL-016 | As an AE, I need point-in-time joins in Gold so historical correctness is preserved. | E4 | 8 | Must | AE | DE | BL-015 | Gold joins match event-time supplier state. |
| BL-017 | As an AE, I need cold-chain breach logic using rolling windows. | E4 | 8 | Must | AE | DQE | BL-013 | Breach flags reflect >120 minute out-of-range conditions. |
| BL-018 | As an AE, I need timezone-safe lead-time metrics for cross-border routes. | E4 | 5 | Must | AE | DE | BL-016 | Lead-time tests pass across timezone cases. |
| BL-019 | As an MLE, I need a local Python model for delay prediction using engineered DuckDB features. | E5 | 8 | Must | MLE | AE | BL-016 | Model trains and scores reproducibly from local data marts. |
| BL-020 | As an MLE, I need feature engineering for route and telemetry predictors. | E5 | 5 | Must | MLE | AE | BL-019 | Feature set documented and reproducible. |
| BL-021 | As an MLE, I need K-means route segmentation for risk zoning. | E5 | 5 | Should | MLE | AE | BL-020 | Route clusters produced and versioned. |
| BL-022 | As a DQE, I need drift/performance thresholds with alerting. | E5 | 8 | Should | DQE | MLE | BL-019 | Alert triggers when metric threshold is breached. |
| BL-023 | As a DQE, I need Great Expectations suites for key business rules. | E6 | 8 | Must | DQE | AE | BL-017 | GE suites pass for critical SLA and schema checks. |
| BL-024 | As a PE, I need observability for freshness and lineage incidents. | E6 | 8 | Must | PE | DQE | BL-023 | Freshness and lineage incidents are captured and routed. |
| BL-025 | As a PE, I need Slim CI for dbt validation on pull requests. | E6 | 8 | Must | PE | AE | BL-002 | PR pipeline blocks merge on test failure. |
| BL-026 | As a DE, I need Airflow DAG orchestration for scheduled execution. | E6 | 8 | Should | DE | PE | BL-025 | DAG runs end-to-end with retries and logging. |
| BL-027 | As a BIA, I need a live risk map app for dispatch operations. | E7 | 8 | Must | BIA | AE, MLE | BL-019 | Map displays active shipments and risk status. |
| BL-028 | As a BIA, I need supplier resilience scorecards for procurement review. | E7 | 8 | Must | BIA | AE | BL-016 | Scorecard published with monthly trend metrics. |
| BL-029 | As a BIA, I need SLA breach incident dashboard for governance reporting. | E7 | 5 | Should | BIA | DQE | BL-024 | Incident timeline and status available to stakeholders. |
| BL-030 | As a PTO, I need phase reports and command logs up to date for reproducibility. | E8 | 8 | Must | PTO | All | Cross-epic | Every sprint has completed report artifacts and evidence. |
| BL-031 | As a PTO, I need defense-ready thesis assets aligned to implementation evidence. | E8 | 8 | Must | PTO | AE, BIA | BL-030 | Brief, spec, architecture, and runbook cross-reference real outputs. |
| BL-032 | As a PTO, I need dry-run demo scripts for viva and interviews. | E8 | 8 | Should | PTO | BIA, AE | BL-027, BL-028 | Timed demo script validated end-to-end. |

## 5. Sprint-by-Sprint Milestones
- Sprint 1: Local platform foundations (`check_duckdb_env`, `dbt-duckdb`, devcontainer baseline).
- Sprint 2: Core ingestion MVP (IoT simulation + DuckDB Bronze + incremental file-state batch).
- Sprint 3-4: Silver normalization and historical modeling hardening.
- Sprint 5-6: Gold SLA logic and predictive intelligence.
- Sprint 7-8: CI/observability/BI, then defense packaging.

## 6. RAID Snapshot (Execution Risks)
| ID | Risk | Likelihood | Impact | Owner | Mitigation |
| :--- | :--- | :---: | :---: | :--- | :--- |
| R-01 | Local environment drift across Codespaces | Medium | High | PE | Pinned devcontainer, scripted bootstraps, regular validation |
| R-02 | Tooling overload from early Airbyte/Airflow adoption | Medium | High | PTO | Enforce MVP gate before phase-two additions |
| R-03 | German normalization defects | Medium | Medium | AE | Deterministic tests and sample audits each release |
| R-04 | Data drift lowers model utility | Medium | Medium | MLE | Monitor drift thresholds and retraining triggers |
| R-05 | Documentation lag vs implementation | Medium | High | PTO | Include documentation tasks in each sprint DoD |

## 7. Release Milestones
- Release M1 (end Sprint 2): Core MVP (DuckDB + dbt + reliable ingestion path)
- Release M2 (end Sprint 5): Gold analytics with SCD + SLA governance
- Release M3 (end Sprint 7): Production-style operations (CI, observability, orchestration, BI)
- Release M4 (end Sprint 8): Thesis defense package and portfolio readiness

## 8. Reporting and Governance Rhythm
- Daily: short standup update against sprint backlog.
- Weekly: risk review and dependency unblock.
- End of sprint: phase report, command log updates, acceptance evidence.
- End of release: architecture and requirement traceability check.

This backlog is a living control document. Scope changes must be reflected in sprint plans, phase reports, and requirement traceability artifacts.
