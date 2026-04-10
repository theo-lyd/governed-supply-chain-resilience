# Phase Reports Index

This folder contains standardized report templates for each implementation phase of the Supply Chain Resilience Engine.

## How to Use
1. Select the template matching the current phase.
2. Copy it to a new report file for the batch being executed.
3. Complete all sections, including approval, validation evidence, and acceptance criteria.
4. Commit the report with the batch code changes.

## Template Files
- [Phase 1 Template](phase-1-infrastructure-and-inner-loop-template.md)
- [Phase 2 Template](phase-2-ingestion-and-bronze-template.md)
- [Phase 3 Template](phase-3-silver-and-german-normalization-template.md)
- [Phase 4 Template](phase-4-gold-and-analytics-engineering-template.md)
- [Phase 5 Template](phase-5-predictive-intelligence-template.md)
- [Phase 6 Template](phase-6-cicd-observability-and-sla-template.md)

## Naming Convention for Real Batch Reports
Use a consistent file naming format:

`SCR-P{phase}-B{batch}.x-report.md`

Examples:
- `SCR-P1-B1.1-report.md`
- `SCR-P3-B1.2-report.md`
- `SCR-P6-B2.1-report.md`

## Recommended Report Storage Pattern
- Keep templates unchanged.
- Create completed reports in the same folder using the naming convention above.
- If phase report volume grows, optionally create subfolders per phase:
  - `phase-1/`
  - `phase-2/`
  - `phase-3/`
  - `phase-4/`
  - `phase-5/`
  - `phase-6/`
