# Study A Interface Self-Pilot Runbook

This runbook is for Brett's interface and workload self-pilot. It is not an
independent evaluation pass, and its ratings must never enter Study A analysis.

## Prepare

1. Run `make study-a-self-pilot`.
2. Open the practice page for a role, then the first blind block under
   `private/study-a/self-pilot/package/`.
3. Use pseudonymous self-pilot IDs such as `SELF-LING` and `SELF-POL`.
4. Keep downloaded JSON files local. Do not email or ingest them.

## Complete

For each role, complete all three 18-row blocks in the form:

1. `linguistic_task`: blocks 01, 02, and 03.
2. `policy_safety`: blocks 01, 02, and 03.

The form records its own elapsed time. Complete the blocks in realistic
sittings, including a break between blocks if that is how an evaluator would
reasonably work. Do not use historical author labels, expected-behaviour fields,
or the old unblinded review app while completing the self-pilot.

## Record Timing Only

Move the six downloaded JSON files to:

```text
private/study-a/self-pilot/responses/
```

Then run:

```bash
make study-a-self-pilot-report
```

The report writes only completion and timing metadata to:

```text
private/study-a/self-pilot/report/self-pilot-readout.md
```

It deliberately does not inspect or report the ratings themselves.

## Usability Notes

After each block, record only interface observations in a local note:

- unclear question wording or option labels;
- missing help or confusing progression;
- the point at which fatigue becomes noticeable;
- whether the practice material prepared you adequately; and
- any reason the observed time may not transfer to an external evaluator.

Do not revise items, labels, or rubrics mid-self-pilot. Capture the concern and
decide on revisions afterward in a documented pass.
