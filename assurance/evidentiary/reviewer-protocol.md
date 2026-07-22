# Evidentiary-assurance calibration protocol

This package contains harmless synthetic action records. It is a calibration
substrate, not a completed validation study and not legal advice.

For each case, read the bound authorization regime, applicability map, action
record, inventory, and record objects. For every **required** node, select
exactly one verdict:

- **support**: the cited records meet the declared standard for the node
  proposition;
- **substantive defeat**: affirmative cited records meet the declared standard
  for failure of the proposition;
- **record gap**: prospectively required evidence is unavailable or inadequate;
- **conflict**: material supporting and defeating records remain unresolved
  under the conflict rule.

Do not infer historical failure merely because the proponent has not met a
production burden. Cite the record IDs used. Authenticity and integrity
metadata are evidence to assess, not pre-entered node verdicts.

Nodes marked **not applicable** in the map are locked and do not appear in a
response. They are not evidentiary states. An **optional** node may be omitted
without creating a gap; if visible records directly bear on it, the reviewer
may enter a verdict, but it cannot compensate for another node.

The forum applying this calibration protocol is `F_review`. Records about
complaint, appeal, regulator, or remedy bodies are object-level evidence for
`J_C`; the two roles must not be conflated.

Reviewer responses conform to `reviewer-response.schema.json`. No completed or
simulated reviewer responses are included in the repository. A response is
marked `genuine_reviewer`, records active-review burden and any privacy or
security incident, and carries presentation metadata assigned by the package
builder. An opaque `blinded_replicate_group_id` is used only for prospectively
scheduled repeat presentations and is not shown to the reviewer as a repeat
cue. Across-case variation is not a test--retest estimate.

The hidden reference-key file is immutable and committed by SHA-256 in both
the frozen case manifest and reviewer package. It remains separate until the
declared boundary. After that time, the opening event is recorded in a separate
`unblinding-record.json` conforming to `unblinding-record.schema.json`; that
record names the committed key hash and does not modify the key. The analyzer
will not compare responses with the key without a valid post-boundary opening
record.

Each declared use also fixes numeric minimum reach: at least four distinct
cases, twelve genuine responses, and three distinct reviewers per action
class, with at least two reviewers on every observed case. Meeting error
tolerances on fewer observations is reported as `NOT_ESTIMATED`, not as a
pass. A use must also cover every construct tag it declares and both members
of each required controlled pair, with the per-case reviewer minimum on each
member. Error and omission tolerances apply noncompensatorily at each
estimable required node and at action-class level.
