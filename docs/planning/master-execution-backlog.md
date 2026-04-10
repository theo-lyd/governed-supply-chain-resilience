# Master Execution Backlog: Supply Chain Resilience Engine

## 1. Planning Baseline
This backlog is execution-ready and aligned to the thesis architecture decisions:
- Core first: Codespace + Databricks + dbt + one reliable ingestion path.
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
- Required access/secrets are available.

Definition of Done (DoD):
- Code merged through PR with review.
- Validation evidence captured (`dbt debug`, `dbt test`, or equivalent).
- Batch/phase report updated in `docs/phase-reports/`.
- Command and incident logs updated where relevant.

## 3. Epic Overview
| Epic ID | Epic Name | Total Points | Primary Owner | Outcome |
| :--- | :--- | :---: | :--- | :--- |
| E1 | Inner Loop and Platform Foundation | 34 | DE + PE | Secure Codespace -> Databricks workflow |
| E2 | Bronze Ingestion and Source Integration | 42 | DE | Reliable ingestion and Autoloader pipeline |
| E3 | Silver Normalization (German Constraints) | 39 | AE | Trusted cleaned datasets and harmonized dimensions |
| E4 | Gold Analytics and SCD Type 2 | 34 | AE | Historical and SLA-ready marts |
| E5 | Predictive Intelligence | 29 | MLE + AE | Delay-risk scoring and segmentation |
| E6 | Quality, Observability, and CI/CD | 37 | DQE + PE | Production-style controls and guarded delivery |
| E7 | BI and Decision Experience | 21 | BIA | Risk map and scorecards for stakeholders |
| E8 | Thesis Packaging and Defense Assets | 24 | PTO + AE | Defense-ready documentation and narrative |

## 4. Prioritized Product Backlog
| ID | User Story | Epic | Points | Priority | Primary Owner | Supporting Roles | Dependencies | Acceptance Criteria |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- | :--- | :--- |
| BL-001 | As an engineer, I need Codespace secrets configured for Databricks auth so execution is secure. | E1 | 5 | Must | PE | DE | None | Host/token/http path validated; no plaintext secrets in repo. |
| BL-002 | As an AE, I need dbt-databricks configured so transformations run remotely. | E1 | 5 | Must | AE | DE | BL-001 | `dbt debug` succeeds for `dev` target. |
| BL-003 | As a platform owner, I need Unity Catalog `dev` and `prod` initialized so environments are separated. | E1 | 8 | Must | PE | DE | BL-001 | Catalogs and baseline permissions verified. |
| BL-004 | As a developer, I need a reproducible devcontainer for core tooling. | E1 | 5 | Must | PE | AE | BL-001 | Container builds with pinned versions and startup docs. |
| BL-005 | As a DE, I need source data landing conventions so ingestion is traceable. | E2 | 3 | Must | DE | AE | BL-003 | Landing path and naming policy documented and tested. |
| BL-006 | As a DE, I need IoT heartbeat simulation to produce incremental files. | E2 | 5 | Must | DE | AE | BL-005 | `iot_emitter.py` generates scheduled files with schema contract. |
| BL-007 | As a DE, I need Databricks Autoloader to ingest new IoT files automatically. | E2 | 8 | Must | DE | AE | BL-006 | New files detected and loaded incrementally with checkpointing. |
| BL-008 | As a DE, I need Postgres in Docker to simulate transactional source data. | E2 | 5 | Should | DE | PE | BL-004 | Postgres container seeded and queryable from Codespace. |
| BL-009 | As a DE, I need Airbyte sync from Postgres to Bronze for source heterogeneity. | E2 | 8 | Should | DE | PE | BL-008 | Initial + incremental sync validated and logged. |
| BL-010 | As an AE, I need Bronze quality checks to reject malformed records. | E2 | 8 | Must | AE | DQE | BL-007 | Schema and null checks pass; quarantined records documented. |
| BL-011 | As an AE, I need German text normalization macros in Silver. | E3 | 8 | Must | AE | DE | BL-010 | Umlaut normalization tests pass deterministically. |
| BL-012 | As an AE, I need AGS code harmonization for canonical geography. | E3 | 8 | Must | AE | DE | BL-011 | AGS mapping validated with reference lookups. |
| BL-013 | As an AE, I need incremental lookback logic for late-arriving IoT records. | E3 | 8 | Must | AE | DE | BL-010 | Backfill affects only impacted partitions and is reproducible. |
| BL-014 | As an AE, I need domain normalization (LKW, Mio. EUR) for business consistency. | E3 | 5 | Should | AE | BIA | BL-011 | Converted values pass semantic checks. |
| BL-015 | As an AE, I need supplier reliability snapshots (SCD Type 2). | E4 | 8 | Must | AE | DE | BL-012 | Snapshot history queryable with valid-from/to fields. |
| BL-016 | As an AE, I need point-in-time joins in Gold so historical correctness is preserved. | E4 | 8 | Must | AE | DE | BL-015 | Gold joins match event-time supplier state. |
| BL-017 | As an AE, I need cold-chain breach logic using rolling windows. | E4 | 8 | Must | AE | DQE | BL-013 | Breach flags reflect >120 minute out-of-range conditions. |
| BL-018 | As an AE, I need timezone-safe lead-time metrics for cross-border routes. | E4 | 5 | Must | AE | DE | BL-016 | Lead-time tests pass across timezone cases. |
| BL-019 | As an MLE, I need a dbt Python model for delay prediction. | E5 | 8 | Must | MLE | AE | BL-016 | Model trains and scores in Databricks runtime. |
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

### Sprint 1: Platform Foundations (Target 34 points)
Planned backlog:
- BL-001, BL-002, BL-004, BL-005, BL-030 (partial)

Milestones:
- Secure Databricks connectivity from Codespace is proven.
- dbt-databricks environment is operational.
- Devcontainer and baseline command logs are in place.

Exit Evidence:
- Successful `dbt debug` output captured.
- Sprint report committed in `docs/phase-reports/`.

### Sprint 2: Core Ingestion MVP (Target 34 points)
Planned backlog:
- BL-006, BL-007, BL-010, BL-003, BL-030 (partial)

Milestones:
- IoT file simulation and Autoloader ingestion are stable.
- Bronze quality checks are running.
- Core Databricks + dbt + one ingestion path MVP is achieved.

Exit Evidence:
- Repeatable incremental ingestion run logs.
- Bronze validation checks passing.

### Sprint 3: Source Heterogeneity Extension (Target 34 points)
Planned backlog:
- BL-008, BL-009, BL-011, BL-012, BL-030 (partial)

Milestones:
- Postgres source simulation and Airbyte connector path implemented.
- German normalization macro and AGS harmonization baseline delivered.

Exit Evidence:
- Airbyte initial and incremental sync logs.
- Deterministic German normalization test outputs.

### Sprint 4: Silver Hardening (Target 32 points)
Planned backlog:
- BL-013, BL-014, BL-015, BL-018, BL-030 (partial)

Milestones:
- Late-arriving data buffer works in incremental runs.
- SCD Type 2 snapshot baseline in place.
- Timezone-safe lead-time calculations validated.

Exit Evidence:
- Incremental backfill test report.
- Snapshot history correctness checks.

### Sprint 5: Gold Analytics and SLA Logic (Target 34 points)
Planned backlog:
- BL-016, BL-017, BL-023, BL-024, BL-030 (partial)

Milestones:
- Gold layer is historically correct and SLA-aware.
- Observability and quality checks cover critical business rules.

Exit Evidence:
- Cold-chain breach rule validations.
- Freshness and lineage monitoring proof.

### Sprint 6: Predictive Intelligence (Target 31 points)
Planned backlog:
- BL-019, BL-020, BL-021, BL-022, BL-030 (partial)

Milestones:
- Delay prediction model runs in Databricks.
- Feature pipeline and risk segmentation are reproducible.
- Drift thresholds and alerts are operational.

Exit Evidence:
- Model metrics and threshold alert test logs.
- Scoring outputs available in analytics layer.

### Sprint 7: Orchestration and Decision Experience (Target 34 points)
Planned backlog:
- BL-025, BL-026, BL-027, BL-028, BL-029

Milestones:
- CI safeguards active for PR validation.
- Airflow orchestration added as phase-two extension.
- Risk map and supplier scorecards available to stakeholders.

Exit Evidence:
- CI run logs with pass/fail gate.
- Airflow DAG success run and retry log.
- BI outputs validated by sample stakeholder questions.

### Sprint 8: Portfolio Hardening and Defense Readiness (Target 24 points)
Planned backlog:
- BL-031, BL-032, BL-030 (final closure)

Milestones:
- End-to-end narrative aligned across architecture, spec, and evidence.
- Defense demo script and interview narrative validated.

Exit Evidence:
- Final thesis portfolio map updated.
- End-to-end demo dry run completed and documented.

## 6. RAID Snapshot (Execution Risks)
| ID | Risk | Likelihood | Impact | Owner | Mitigation |
| :--- | :--- | :---: | :---: | :--- | :--- |
| R-01 | Codespace -> Databricks connectivity instability | Medium | High | PE | Secret hygiene, connection tests each sprint, fallback runbook |
| R-02 | Tooling overload from early Airbyte/Airflow adoption | Medium | High | PTO | Enforce MVP gate before phase-two additions |
| R-03 | German normalization defects | Medium | Medium | AE | Deterministic tests and sample audits each release |
| R-04 | Data drift lowers model utility | Medium | Medium | MLE | Monitor drift thresholds and retraining triggers |
| R-05 | Documentation lag vs implementation | Medium | High | PTO | Include documentation tasks in each sprint DoD |

## 7. Release Milestones
- Release M1 (end Sprint 2): Core MVP (Databricks + dbt + reliable ingestion path)
- Release M2 (end Sprint 5): Gold analytics with SCD + SLA governance
- Release M3 (end Sprint 7): Production-style operations (CI, observability, orchestration, BI)
- Release M4 (end Sprint 8): Thesis defense package and portfolio readiness

## 8. Reporting and Governance Rhythm
- Daily: short standup update against sprint backlog.
- Weekly: risk review and dependency unblock.
- End of sprint: phase report, command log updates, acceptance evidence.
- End of release: architecture and requirement traceability check.

This backlog should be treated as a living control document. Scope changes must be reflected in sprint plans, phase reports, and requirement traceability artifacts.
