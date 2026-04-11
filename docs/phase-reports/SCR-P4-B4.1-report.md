# Batch Report: SCR-P4-B4.1

## Batch Metadata
- Batch ID: SCR-P4-B4.1
- Phase: Gold Layer and Analytics Engineering
- Status: Completed/Verified
- Date: 2026-04-11
- Environment: GitHub Codespace -> DuckDB (local)

## Scope Definition
- Chunk(s) in Scope:
  - Chunk 1: Supplier reliability SCD Type 2 history table build
  - Chunk 2: Route-to-supplier dimension mapping
  - Chunk 3: Point-in-time Gold fact join from Silver events
- Explicit Goal for This Batch:
  - Implement auditable SCD Type 2 reliability history and event-time-correct Gold joins.
- Out of Scope:
  - Rolling cold-chain breach windows and timezone-safe lead-time metrics (Batch 4.2)

## What Was Built
- Files Created/Modified:
  - `data/reference/supplier_reliability_history.csv`
  - `data/reference/route_supplier_mapping.csv`
  - `scripts/build_gold_phase_4_1.py`
  - `scripts/bootstrap_phase_4_1.sh`
  - `docs/command/phase-4-commands.md`
  - `docs/phase-reports/SCR-P4-B4.1-report.md`
- Snapshot Models Added/Updated:
  - `gold.dim_supplier_reliability_scd2`
- Gold Marts Added/Updated:
  - `gold.dim_route_supplier`
  - `gold.fact_iot_events_pit`
- Window Function/SLA Logic Implemented:
  - SCD2 `lead(valid_from)` windowing to compute `valid_to` boundaries.
  - Point-in-time join condition: `event_ts >= valid_from AND event_ts < valid_to`.

## Tool and Methodology Justifications
- SCD Type 2 design rationale:
  - Historical supplier reliability changes are tracked with non-overlapping validity intervals and explicit `is_current` marker.
- Point-in-time join strategy:
  - Events are mapped to suppliers by route, then joined to the supplier record valid at event time.
- Trade-off:
  - Script-first implementation used for reproducible local execution because a full dbt project scaffold is not yet in place.

## Commands Executed
- `bash -n scripts/bootstrap_phase_4_1.sh`
- `python3 -m py_compile scripts/build_gold_phase_4_1.py`
- `./scripts/bootstrap_phase_4_1.sh`

## Validation Evidence
- Build metrics:
  - `SCD2 rows: 9`
  - `Gold fact rows: 67`
  - `Rows with null supplier_id: 0`
  - `Events with multiple PIT matches: 0`
- SCD2 current-row checks:
  - One `is_current = TRUE` row per supplier (`SUP-001`, `SUP-002`, `SUP-003`).
- PIT join coverage checks:
  - `silver_rows: 67`
  - `gold_rows: 67`
  - `gold_rows_with_null_supplier: 0`

## Issues and Resolutions
- Incident:
  - None blocking during Batch 4.1 execution.
- Preventive Guardrails:
  - Build fails if supplier mapping is missing (`null supplier_id > 0`) or if overlapping intervals cause duplicate PIT matches.

## Acceptance Criteria Met
- [x] Supplier reliability history is tracked via SCD Type 2.
- [x] Gold joins use event-time-correct historical records.
- [ ] SLA breach logic is validated and reproducible (Batch 4.2).
- [x] Gold marts are ready for downstream analytics.

## Handover Notes
- What changed for the next batch:
  - Gold layer now includes historical supplier reliability and PIT-enriched event facts.
- Risks/Dependencies:
  - New routes or suppliers require updates to both Gold reference mapping CSVs.
- Next Batch Recommendation:
  - Execute SCR-P4-B4.2 to implement rolling cold-chain breach windows and timezone-safe lead-time metrics.
