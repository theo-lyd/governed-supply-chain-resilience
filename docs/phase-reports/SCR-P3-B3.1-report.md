# Batch Report: SCR-P3-B3.1

## Batch Metadata
- Batch ID: SCR-P3-B3.1
- Phase: Silver Layer and German Data Normalization
- Status: Completed/Verified
- Date: 2026-04-11
- Environment: GitHub Codespace -> DuckDB (local)

## Scope Definition
- Chunk(s) in Scope:
  - Chunk 1: Route-to-AGS reference mapping bootstrap
  - Chunk 2: Deterministic German text normalization implementation
  - Chunk 3: Silver enrichment build and validation
- Explicit Goal for This Batch:
  - Deliver Silver normalization for city names and AGS harmonization with reproducible local execution.
- Out of Scope:
  - Incremental lookback handling for late-arriving telemetry (moved to Batch 3.2)

## What Was Built
- Files Created/Modified:
  - `data/reference/route_ags_mapping.csv`
  - `scripts/build_silver_phase_3_1.py`
  - `scripts/bootstrap_phase_3_1.sh`
  - `docs/command/phase-3-commands.md`
  - `docs/phase-reports/SCR-P3-B3.1-report.md`
- Macros/Transformations Added:
  - Deterministic city normalization function `normalize_german_text` embedded in Silver build script.
- AGS/Reference Mapping Changes:
  - Route-code reference mapping introduced for `HAM-BER`, `MUC-FRA`, and `CGN-STR` with canonical AGS values.
- Silver Models Updated:
  - `silver.dim_route_geo`
  - `silver.iot_events_normalized`

## Tool and Methodology Justifications
- German normalization logic rationale:
  - Canonical city mapping is deterministic and explicit (`Muenchen`, `Koeln`) to avoid inconsistent transliteration outcomes.
- AGS harmonization approach:
  - AGS codes sourced from a versioned reference CSV, then joined by `route_code` during Silver enrichment.
- Trade-off:
  - A script-first implementation was used because a full dbt project scaffold is not yet present in the repository.

## Commands Executed
- `bash -n scripts/bootstrap_phase_3_1.sh`
- `python3 -m py_compile scripts/build_silver_phase_3_1.py`
- `./scripts/bootstrap_phase_2_1_duckdb.sh`
- `./scripts/bootstrap_phase_3_1.sh`

## Validation Evidence
- Silver build output:
  - `Built silver.dim_route_geo rows: 3`
  - `Built silver.iot_events_normalized rows: 67`
  - `Missing route mappings: 0`
  - `Rows with null AGS: 0`
- Canonical route normalization sample:
  - `('CGN-STR', 'Koeln', 'Stuttgart', '05315000', '08111000')`
  - `('HAM-BER', 'Hamburg', 'Berlin', '02000000', '11000000')`
  - `('MUC-FRA', 'Muenchen', 'Frankfurt am Main', '09162000', '06412000')`
- Row parity check:
  - `silver.iot_events_normalized row_count: 67`
  - `bronze.iot_events_raw row_count: 67`

## Issues and Resolutions
- Incident:
  - First Batch 3.1 run failed because `bronze.iot_events_raw` did not include `source_file` for older non-incremental loads.
- Root Cause:
  - Bronze table schema differed between Batch 2.1 direct loader and Batch 2.2 incremental loader paths.
- Resolution:
  - Added schema-compatibility logic in `build_silver_phase_3_1.py` to auto-add `source_file` when absent.
- Recurrence Prevention:
  - Keep Bronze schema evolution checks in all Silver build scripts before selecting optional columns.

## Acceptance Criteria Met
- [x] German encoding/transliteration normalization implemented deterministically.
- [x] AGS mapping is consistent and auditable.
- [ ] Late-arriving data lookback handling (scheduled for Batch 3.2).
- [x] Silver outputs meet schema and quality expectations for current scope.

## Handover Notes
- What changed for the next batch:
  - Silver baseline now exists and is queryable with canonical city and AGS enrichments.
- Risks/Dependencies:
  - Future route codes require reference mapping updates before ingestion.
- Next Batch Recommendation:
  - Execute SCR-P3-B3.2 for incremental lookback and domain normalization (`LKW`, `Mio. EUR`) across Silver outputs.
