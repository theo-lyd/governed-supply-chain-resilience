# Repo Standing Instructions and Execution Governance: Supply Chain Resilience Engine

## Purpose
This document operationalizes implementation discipline for the phase-by-phase delivery of the **Supply Chain Resilience Engine**. It ensures that the transition from a local **GitHub Codespace** to a remote **Databricks** environment is governed, documented, and reproducible for a Master’s thesis defense.

## 1. Batch Execution Protocol
Every batch shall:
1. **Scope Announcement:** Be initiated with a clear definition of "Chunks" (e.g., "Batch 1.1, Chunk 3: Profiles.yml setup").
2. **Pre-Approval:** Receive explicit user approval before compute-heavy Databricks clusters are spun up.
3. **Atomic Commits:** Follow the `feat(scope): message` convention (e.g., `feat(ingest): add Autoloader logic for IoT heartbeats`).
4. **Environment Sync:** Verify that the Codespace local environment is in sync with the Databricks remote workspace before pushing.
5. **Validation:** Include a successful `dbt debug` or `dbt test` run result in the batch summary.
6. **Documentation Maintenance:** Update or modify all appropriate and necessary `.md` files as project implementation progresses.

## 2. Batch Documentation Report Template
Use this structure for every batch report in `docs/phase-reports/`:

### Batch Metadata
- **Batch ID:** (e.g., SCR-P1-B1.2)
- **Phase:** (e.g., Infrastructure)
- **Status:** (Draft/Completed/Verified)
- **Environment:** GitHub Codespace -> Databricks Cluster ID

### What Was Built
- **Files Created/Modified:** (e.g., `models/staging/stg_german_orders.sql`)
- **Infrastructure Changes:** (e.g., Creation of `BRONZE` schema in Unity Catalog)
- **Connectivity Check:** (e.g., PAT Token validation status)

### Tool and Methodology Justifications
- **Methodology:** (e.g., Why SCD Type 2 was used for Supplier Reliability)
- **German Constraint Handling:** (e.g., Logic applied for Umlaut normalization)
- **Trade-offs:** (e.g., Choosing Incremental dbt models over Full Refresh for IoT data)

### Issues & Resolutions
- **Incident:** (e.g., JDBC Connection Timeout)
- **Root Cause:** (e.g., Missing outbound port configuration in Codespace)
- **Resolution:** (e.g., Update `.devcontainer` to include port forwarding)

### Acceptance Criteria Met
- [ ] Logic passes German encoding tests.
- [ ] Databricks Autoloader detects new files in the landing zone.
- [ ] Great Expectations suite reports 100% success on schema validation.

## 3. Command Log Policy
Maintain and update command logs under `docs/command/`. This is critical for the "Runbook" deliverable:
- `databricks-commands.md` (CLI, Workspace, Cluster mgmt)
- `dbt-commands.md` (Seeds, Run, Test, Snapshots)
- `pyspark-commands.md` (Spark-shell, Job submissions)
- `airflow-commands.md` (DAG triggers, Task logs)
- `airbyte-commands.md` (Connection resets, Sync triggers)
- `docker-commands.md` (Codespace service orchestration)
- `git-commands.md` (Commit, Branching, LFS)
- `ge-commands.md` (Great Expectations suite initialization)
- `monte-carlo-commands.md` (Collector setup and monitors)
- `make-commands.md`
- `bash-shell-commands.md`
- `lint-commands.md`
- `streamlit-commands.md`
- `github-actions-commands.md`
- `python-commands.md`

## 4. Deliverables Index Policy
The `README.md` must serve as the **Thesis Portfolio Map**.

Required document set:
- **Thesis Defense Brief:** (The "Why" and "How" for examiners)
- **Technical Project Presentation:** (Architecture diagrams, Medallion flow)
- **Non-Technical Business Blueprint:** (Value prop, ROI, Business Questions)
- **Developer Inner Loop Walkthrough:** (Guide on connecting Codespace to Databricks)
- **German Data Normalization Appendix:** (Technical specs for AGS and Encoding)
- **Project Runbook:** (Step-by-step reproduction guide)
- **SLA & Observability Report:** (Monte Carlo incident logs)
- Beginner tutorial
- **Standard MSc thesis report:** (dissertation to be submitted. It should include 5 Chapters, namely Introduction, Literature Review, Methodology (just a summary because we already have 'Thesis Defense Brief'), Implementation & Evaluation, and finally Result, Summary, & Future Recommendation)

## 5. Issues and Incident Documentation (The "Incident Post-Mortem")
Maintain per-phase issue logs in `docs/incidents/`. Given the "Connectivity Pain," this section is vital:
- **Symptom:** What the developer saw.
- **Cause:** Cloud permissions, network latency, or credential mismatch.
- **Solution Implementation:** The specific CLI command or secret update that fixed it.
- How the solution was implemented
- How to avoid recurrence
- **Mastery Lesson:** How this prepares you for a real-world Senior Analytics Engineer role.

## 6. Data Governance & LFS Policy
- **Git LFS:** Strictly required for the **Kaggle Logistics CSVs**. However, if it is going to be problematic, we can avoid it.
- **Data Privacy:** Any PII (Personal Identifiable Information) in the Kaggle set must be hashed or masked in the **Bronze-to-Silver** transition.
- **Unity Catalog Policy:** All tables must have descriptions and tags (e.g., `PII`, `SCD_TYPE_2`, `GERMAN_DATA`).

## 7. Phase Checkpoint & Promotion Policy
Before "Promoting" a phase (e.g., moving from Ingestion to Transformation):
1. **SLA Validation:** Data Freshness SLAs must be met for 24 hours of simulated "heartbeats."
2. **Lineage Verification:** Monte Carlo must show a complete graph from Airbyte Source to Gold Marts.
3. **German Consistency Check:** A manual audit of 50 records to ensure "München" is not "Mnchen".
4. **Peer Review Simulation:** A documentation check to ensure a second engineer could take over the Codespace and continue.

## 8. "Developer Inner Loop" Enforcement
- All SQL/Python code **must** be written in the Codespace.
- Execution **must** happen on the Databricks Cluster via dbt/CLI.
- **Prohibition:** Manual editing of code via the Databricks Web UI (Notebooks) is forbidden to maintain Git as the "Single Source of Truth."

---

### Implementation Note
This document is the "Constitution" of your project. Following it ensures that when I enter an interview, I can prove not just that you *know* the tools, but that I know how to **govern** them at a production level.
