# Study A Withdrawal Procedure (Draft)

**Draft only. This procedure does not launch collection or establish a legal
retention rule until the final evaluator information/agreement note supplies an
exact cutoff, contact route, and retention period.**

## Rule

An evaluator may request deletion of all returned files associated with their
pseudonymous rater ID until the published collection-close and analysis-start
cutoff. The request should identify only the rater ID; it need not disclose a
name in a rating file.

After the cutoff, returned blocks may already have informed de-identified
analysis, aggregate counts, or a validation package. Deletion is therefore not
promised after that point. The final information note must state this plainly.

## Before Analysis Begins

1. Record the request in the local-only withdrawal log.
2. Identify the returned source JSON files using the pseudonymous rater ID.
3. Delete the requested source files and any direct local copies.
4. Re-run ingestion and analysis from the remaining returned files.
5. Record completion without adding evaluator identity to public project files.

## Cutoff Procedure

Before the first response rejoin or analysis run, Brett records the collection
close and analysis-start time in the local-only study administration record.
After processing any requests received before that moment, the analysis set is
frozen for the study pass. Any later change requires a documented revision and
reanalysis rather than silent table edits.

## Local Log

Use `withdrawal-log-template.csv` only as a schema. Any populated log belongs
under ignored `private/` paths and must not be committed.
