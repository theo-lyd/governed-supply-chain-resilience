# Jira Cloud Import Guide: Master Backlog

## Purpose
This guide explains how to safely import the project backlog CSV files into Jira Cloud with correct field mapping, minimal data loss risk, and predictable sprint placement.

## Supported CSV Files
- docs/jira-import-master-backlog.csv
- docs/jira-import-master-backlog-team-managed.csv
- docs/jira-import-master-backlog-board-exact-sample.csv

## Recommended Import Order
1. Import Epics first.
2. Import Stories second.
3. Verify parent linkage and sprint assignments.
4. Reconcile custom fields and role placeholders.

If you import all issue types in one pass, linkage may still work, but two-pass import is safer when your Jira configuration differs from the CSV schema.

## Pre-Import Safety Checklist
- Confirm the target Jira project key exists and matches the CSV value.
- Confirm issue types exist: Epic and Story.
- Confirm Sprint field is enabled for the target board.
- Confirm Story Points field is available for the project type.
- Confirm Components and Labels are enabled.
- Confirm Parent linkage is supported for your project mode.
- Confirm you have permission to create issues and manage sprints.
- Start with a small pilot import of 3 to 5 rows in a temporary project.

## Which CSV to Use
- Use docs/jira-import-master-backlog.csv for company-managed projects that use Epic Link.
- Use docs/jira-import-master-backlog-team-managed.csv for team-managed projects that use Parent.
- Use docs/jira-import-master-backlog-board-exact-sample.csv when you want broader field coverage and board-style metadata.

## Jira Cloud Importer Screens: Safe Field Mapping Checklist
When mapping fields in Jira Cloud importer screens, use this checklist.

### Required Core Mappings
- Issue Type -> Issue Type
- Summary -> Summary
- Description -> Description
- Priority -> Priority

### Planning and Estimation Mappings
- Story Points -> Story Points
- Sprint -> Sprint

If Sprint mapping fails on first import, proceed without sprint mapping and bulk-assign sprint later from backlog view.

### Taxonomy Mappings
- Labels -> Labels
- Components -> Components

### Hierarchy and Epic Mappings
For company-managed imports:
- Epic Name -> Epic Name
- Epic Link -> Epic Link

For team-managed imports:
- Epic Name -> Epic Name
- Parent -> Parent

For board-exact sample imports:
- Parent -> Parent
- Epic Name -> Epic Name

### Optional Metadata Mappings
- Project Key -> Project (or set project in importer wizard)
- Assignee Role -> map to a custom text field, or skip
- Team -> map to Team custom field if available, or skip
- Environment -> map to Environment if available, or skip

If a custom field does not exist, skip the mapping instead of forcing it into an unrelated Jira field.

## Two-Pass Import Method (Safest)
### Pass 1: Epics
- Filter CSV to Epic rows only.
- Import with Epic Name and required core fields.
- Confirm all epics are created.

### Pass 2: Stories
- Filter CSV to Story rows only.
- Import with Parent or Epic Link mapping.
- Confirm each story is linked to the intended epic.

## Post-Import Validation Checklist
- Epic count matches expected values.
- Story count matches expected values.
- No issues are created without Summary or Issue Type.
- Story Points imported correctly on random samples.
- Sprint values are populated or intentionally deferred.
- Components and Labels populated correctly.
- Parent or Epic linkage is correct for sampled stories.
- No import errors remain unresolved in Jira import logs.

## Recovery Plan if Import Goes Wrong
- Delete imported issues in bulk using a JQL filter scoped by labels and import timestamp.
- Correct mapping in CSV importer.
- Re-run pilot import.
- Re-run full import after pilot validation passes.

## Suggested JQL for Validation
- project = SCR AND issuetype = Epic
- project = SCR AND issuetype = Story
- project = SCR AND labels in (thesis)
- project = SCR AND sprint is EMPTY
- project = SCR AND "Story Points" is EMPTY AND issuetype = Story

## Common Mapping Pitfalls
- Mixing Parent and Epic Link in the same import strategy.
- Mapping Assignee Role into Assignee when values are role names, not user accounts.
- Expecting Sprint values to create new sprints automatically.
- Forgetting to enable Story Points in team-managed projects.
- Importing all rows without validating custom field availability.

## Final Recommendation
Use a pilot-first approach, then full import:
1. Pilot import 5 rows in a sandbox project.
2. Validate field mapping outcomes.
3. Import full epics.
4. Import full stories.
5. Validate hierarchy, sprint, and estimation fields.

This sequence minimizes rework and protects board integrity.
