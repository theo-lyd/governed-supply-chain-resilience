# Batch Report: SCR-P5-B5.1

## Batch Metadata
- Batch ID: SCR-P5-B5.1
- Phase: Predictive Intelligence and AI
- Status: Completed/Verified
- Date: 2026-04-11
- Environment: GitHub Codespace -> DuckDB (local)

## Scope Definition
- Chunk(s) in Scope:
  - Chunk 1: Baseline feature engineering from Gold SLA outputs
  - Chunk 2: Baseline delay-risk scoring pipeline
  - Chunk 3: Reproducible metric capture for model baseline
- Explicit Goal for This Batch:
  - Build a reproducible local baseline model workflow that generates feature, prediction, and metrics outputs for delay risk.
- Out of Scope:
  - Route clustering and drift-threshold alerting (Batch 5.2)

## What Was Built
- Files Created/Modified:
  - `scripts/build_ml_phase_5_1.py`
  - `scripts/bootstrap_phase_5_1.sh`
  - `docs/command/phase-5-commands.md`
  - `docs/command/README.md`
  - `docs/phase-reports/SCR-P5-B5.1-report.md`
- Feature Engineering Components:
  - `analytics.ml_features_delay_baseline`
  - Feature set includes reliability score, temperature/humidity, breach flags, rolling breach counts, and contract value.
- Inference/Scoring Outputs:
  - `analytics.ml_delay_predictions_baseline`
  - Deterministic weighted baseline risk score with thresholded class predictions.
- Monitoring Hooks:
  - `analytics.ml_model_metrics_baseline` for confusion-matrix metrics and threshold tracking.

## Tool and Methodology Justifications
- Model choice rationale:
  - A weighted-rule baseline was selected to maximize reproducibility and explainability in a local-first environment before introducing heavier ML dependencies.
- Feature set rationale:
  - Features directly reflect Phase 4 operational signals linked to delay risk: sustained cold-chain breaches, reliability degradation, and shipment-value exposure.
- Threshold rationale:
  - Default threshold set to `0.50` for baseline sensitivity/precision trade-off and easy recalibration in Batch 5.2.

## Commands Executed
- `bash -n scripts/bootstrap_phase_5_1.sh`
- `python3 -m py_compile scripts/build_ml_phase_5_1.py`
- `./scripts/bootstrap_phase_5_1.sh`

## Validation Evidence
- Pipeline row checks:
  - `Feature rows: 67`
  - `Prediction rows: 67`
- Baseline metrics (`analytics.ml_model_metrics_baseline`):
  - `n=67, tp=11, tn=49, fp=7, fn=0`
  - `accuracy=0.8955`
  - `precision=0.6111`
  - `recall=1.0000`
  - `f1=0.7586`
- Score distribution:
  - `min_score=0.154`
  - `avg_score=0.3236`
  - `max_score=0.978`
  - `predicted_positive=18`

## Issues and Resolutions
- Incident:
  - None blocking during Batch 5.1 execution.
- Preventive Guardrails:
  - Pipeline fails fast if `gold.fact_iot_events_sla` is missing/empty.
  - Metrics and threshold values are persisted for future drift and threshold tuning.

## Acceptance Criteria Met
- [x] Delay prediction baseline runs successfully on the active DuckDB execution path.
- [x] Feature engineering pipeline is reproducible.
- [ ] Drift threshold and alert pathway are validated (Batch 5.2).
- [x] Outputs are documented for downstream consumption.

## Handover Notes
- What changed for the next batch:
  - Baseline predictive tables are now available under `analytics` schema for extension into clustering and drift controls.
- Risks/Dependencies:
  - Rule-weighted baseline may overfit current synthetic signal patterns; Batch 5.2 should add robustness checks and drift thresholds.
- Next Batch Recommendation:
  - Proceed to SCR-P5-B5.2 for route clustering and drift monitoring thresholds.
