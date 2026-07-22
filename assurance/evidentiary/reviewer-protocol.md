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
- **not established**: the record is adequate to evaluate the node, and it
  neither meets the support standard nor supplies affirmative evidence meeting
  the defeat standard. The showing falls short; the recording does not;
- **record gap**: evidence prospectively required to evaluate the node is
  missing, inaccessible, or inadequate as a record, so the node cannot be
  reached on its merits;
- **conflict**: material supporting and defeating records remain unresolved
  under the conflict rule.

The gap/not-established boundary matters because the two call for different
responses. A gap names material to preserve or produce; not established says the
record was there and the case still was not made. Ask whether you were unable to
evaluate the node, or evaluated it and found the showing short.

A **rebutting** defeater supports the negation of the node proposition and may
yield substantive defeat. An **undercutting** defeater attacks the reliability of
records cited in support, for example unauthenticated provenance or broken
custody. An undercutter can yield not established or conflict. It can never by
itself yield substantive defeat: removing a reason to believe something is not a
reason to believe the opposite.

Do not infer historical failure merely because the proponent has not met a
production burden. Cite the record IDs used. Authenticity and integrity
metadata are evidence to assess, not pre-entered node verdicts.

## Bearer and forum nodes are about a named candidate

Every `B_` node is evaluated of a particular candidate answerability bearer, and
every `C_` node of a particular object-level forum, as listed in the case's
bearer or forum registry. Enter one verdict per candidate per required node and
name the candidate in `entity_id`. Where the registry names no candidate at all,
enter the verdict with a null `entity_id`.

Then record `conjunction_resolution` for each of `J_B` and `J_C`: whether any
**single** candidate satisfies every required node of that family, and which. Do
not report a family as satisfied by combining nodes across candidates. A bearer
who is identified and dutied but unreachable, plus a second who is reachable but
carries no duty, is not an answerable bearer; it is two people neither of whom
can be made to answer. The same holds for a forum with access but no remedial
power alongside one with the power but no competence.

Identity and duty are assessed as at the time of the action. Reachability and
object-forum capacity are assessed as at the time of review.

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
