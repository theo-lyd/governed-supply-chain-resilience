# Batch Report: SCR-P3-B3.2

## Batch Metadata
- Batch ID: SCR-P3-B3.2
- Phase: Silver Layer and German Data Normalization
- Status: Completed/Verified
- Date: 2026-04-11
- Environment: GitHub Codespace -> DuckDB (local)

## Scope Definition
- Chunk(s) in Scope:
  - Chunk 4: Incremental lookback refresh for late-arriving telemetry
  - Chunk 5: Domain normalization for `LKW` and `Mio. EUR` business terms
- Explicit Goal for This Batch:
  - Implement a reproducible Silver curated layer that refreshes a lookback window and standardizes German domain terms.
- Out of Scope:
  - Gold-layer SCD2 and SLA logic (Phase 4)

## What Was Built
- Files Created/Modified:
  - `data/reference/route_business_terms.csv`
  - `scripts/build_silver_phase_3_2.py`
  - `scripts/bootstrap_phase_3_2.sh`
  - `docs/command/phase-3-commands.md`
  - `docs/phase-reports/SCR-P3-B3.2-report.md`
- Transformations Added:
  - `normalize_vehicle_type` to canonicalize vehicle label variants to `LKW`.
  - `parse_contract_value_million` to normalize `Mio. EUR`/`million eur` strings into numeric million-EUR and EUR fields.
- Silver Models Updated:
  - `silver.route_business_terms_normalized`
  - `silver.iot_events_curated` (lookback refresh table)

## Tool and Methodology Justifications
- Incremental lookback design:
  - Rebuild the latest 48-hour event window by deleting and reinserting only affected rows.
  - This limits refresh scope while allowing deterministic correction for late-arriving data.
- Domain normalization approach:
  - Use explicit, versioned route-level reference terms and deterministic parsing/normalization logic in code.

## Commands Executed
- `bash -n scripts/bootstrap_phase_3_2.sh`
- `python3 -m py_compile scripts/build_silver_phase_3_2.py`
- `./scripts/bootstrap_phase_3_2.sh`

## Validation Evidence
- Batch build output:
  - `Lookback source rows: 67`
  - `Curated table total rows: 67`
  - `Rows with null vehicle_type: 0`
  - `Rows with null contract_value_million_eur: 0`
- Domain normalization output sample:
  - `('CGN-STR', 'lastkraftwagen', 'LKW', '2.0 million eur', 2.0)`
  - `('HAM-BER', 'Lkw', 'LKW', '1,2 Mio. EUR', 1.2)`
  - `('MUC-FRA', 'LKW', 'LKW', '0.85 Mio EUR', 0.85)`
- Lookback parity check:
  - `lookback_source_rows_48h: 67`
  - `curated_total_rows: 67`

## Issues and Resolutions
- Incident:
  - None blocking in Batch 3.2 execution.
- Preventive Guardrails:
  - Batch 3.2 bootstrap validates Phase 3.1 output existence before running.
  - Build fails fast if normalization outputs include null `vehicle_type` or null contract value metrics.

## Acceptance Criteria Met
- [x] German encoding/transliteration logic remains deterministic.
- [x] AGS mappings remain auditable from Batch 3.1 outputs.
- [x] Late-arriving data lookback handling is implemented and validated.
- [x] Domain normalization for `LKW` and `Mio. EUR` is implemented and validated.

## Handover Notes
- What changed for the next batch:
  - Phase 3 Silver layer now includes curated lookback refresh and normalized business-domain metrics.
- Risks/Dependencies:
  - New route codes require updates in both `route_ags_mapping.csv` and `route_business_terms.csv`.
- Next Batch Recommendation:
  - Start Phase 4 Batch 4.1 for SCD Type 2 supplier reliability snapshots and point-in-time correctness.
