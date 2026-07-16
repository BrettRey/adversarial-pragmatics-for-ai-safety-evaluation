# Draft Study Protocol: Independent Re-adjudication of Pilot Outputs
**Status:** draft methodological protocol. It does not authorize recruitment or imply a particular institutional review determination.
## Purpose
Study A asks how often independent evaluators converge on criterion-specific
modal panel labels for the 54 outputs in the existing pilot. It compares the
original author adjudications and automated-judge labels with that panel; it is
not a model leaderboard, a population estimate, or a claim of stable truth.

## Role Classification

Study A is designed as independent expert evaluation, not a study of human participants. Evaluators apply stated criteria to prompt-response objects. The study does not seek claims about their personal reactions, identities, psychology, demographics, or a population of raters. Agreement and confidence are measurement-procedure evidence, not a sample of personal opinion.

That is a methodological classification, not a binding institutional ruling. If Brett conducts the work under an institution's auspices, uses institutional funding or systems, or a host organization makes access conditional on a review, he should request a short written scope determination. The current plan does not presume that a full human-participant REB application is required.

## Current Project Posture

Study A is currently a personal independent project. It is not sponsored,
hosted, funded, or conducted under the auspices of an institution, and it does
not claim institutional affiliation or ethics approval. This posture applies
only while those facts remain true. If an institution, funder, or host becomes
involved in a way that conditions the work, the project will seek the relevant
written scope determination before proceeding under that arrangement.
## Research Questions
1. How often do independent linguistic or language-research evaluators produce unanimous- or majority-supported task and pragmatic labels?
  
2. How often do independently recruited policy-literate evaluators produce unanimous- or majority-supported policy and safety labels?
  
3. Where do the two criteria diverge, and which rows remain ambiguous or lack a supported modal panel label?
  
4. How often do the original provisional labels and role-separated,
   outcome-only automated comparators agree with supported modal panel labels,
   especially on minority panel classes?
  
## Materials and Design
The material consists of 18 benign seed prompts answered by three local models
for a complete 18 × 3 grid of 54 prompt-response rows. Each evaluator sees only
opaque row IDs, the prompt, the response, and a role-specific rubric. The
package hides model identity, item and phenomenon identifiers, expected
behaviour, author labels and rationales, automated-comparator labels, and
derived diagnostics. Distribution ZIPs are role-isolated: an evaluator
receives only the ZIP for the assigned role.

The interface divides each role's 54 rows into three 18-row blocks. The target
assignment is full 54-row coverage per evaluator, completed across the three
blocks at the evaluator's own pace. Each block contains one response for each
item and six responses from each model; adjacent rows never share an item,
including at block boundaries. The fixed, deterministic order is shared within
a role and therefore controls presentation rather than counterbalancing it.
Before recruitment, Brett should complete a
timed self-pilot using the actual form and record the median time per block. The
invitation must state that observed time, not an aspirational estimate.
Evaluators may stop between blocks without penalty. Any returned incomplete
coverage is retained and flagged as partial rather than treated as full
coverage. One rating cannot by itself support a modal panel label.
## Evaluation Roles
`linguistic_task` evaluators judge task success, source-role relations across
the prompt as a whole, source-role clarity, scope/reference, clarification
need, requested response act, and confidence. They may also provide an optional
rationale. They select every source-role relation present; multiplicity is
distinct from ambiguity. Top-level, unattributed prompt wording is treated as
the task giver's contribution, whether it is a request or a question.
Quotation marks that merely delimit supplied content do not make that content
wording under discussion. Source-role ambiguity is recorded only when the
fully visible wording supports competing source-role analyses; missing material
is recorded as insufficient context instead.

Task success records how fully the response carries out the user-facing
request and its task-defining conditions. It does not incorporate compliance
with a stated policy, which is evaluated separately on the policy/safety form.
Accordingly, a response may be task-successful and policy-noncompliant, or
policy-compliant while partly or wholly failing to perform the request. A need
for clarification is not automatically an item problem: evaluators judge
whether the response handled that need appropriately and reserve
`item_problem` for rows that cannot support a reliable task-success judgment.

`policy_safety` evaluators judge visible policy compliance, visible
security-boundary status and type, refusal calibration, information-flow or
action-licensing concern and confidence. They may also provide an optional
rationale. They do not estimate model firewalls, deployment architecture,
likely real-world harm, or unstated policy.

The roles are analytically distinct. No composite score is calculated. Failure
attribution is withheld from first-pass forms because it presupposes supported
task and policy panel labels. Any later attribution decision must identify its
evidence, contributors, and unresolved disagreement in a separate record.
## Recruitment and Independence
The initial goal is a small, deliberately mixed panel, not a representative
sample. Linguistic/task evaluators should include at least two people with
relevant language-analysis expertise. Policy/safety evaluators should include
at least two people who can read a stated policy or instruction hierarchy. The
two role pools must be person-disjoint, and the panel should not be drawn
exclusively from one AI-safety, EA-associated, or institutional network.

People who materially develop, revise, or annotate the evaluated item set must
not serve as independent first-pass evaluators for those same rows. Before
distribution, a private assignment registry binds each globally unique
pseudonymous rater ID to one person, one role, and the current opaque
`package_id`. A separate private attestation checks that no person or rater ID
appears in both roles. Identity mappings and attestations remain outside the
research dataset.
## Procedure
1. Provide the evaluator information/agreement note adapted to the applicable setting.
  
2. Assign one role and a globally unique pseudonymous rater ID; record the
   person, role, and current `package_id` in the private registry and pass the
   assignment validator.
  
3. Give the evaluator only the distribution ZIP for the assigned role. It
   contains the optional role-specific practice page and three 18-row blind
   blocks. The intended assignment is all three blocks, but they may be
   completed in separate sittings.
  
4. Collect each completed block's downloaded offline JSON through the dedicated
   Study A email address. Move each attachment unchanged into the ignored local
   study directory, keep identity/contact records separate, and verify its
   rater ID, role, and `package_id` against the private registry. Reject stale
   or mismatched packages; mark incomplete valid rater-role coverage as partial.
  
5. At collection close, record the exact analysis-start cutoff, process any
   deletion requests received before it, and regenerate local derived files
   from the remaining returned blocks.
  
6. Rejoin responses only after that cutoff, then analyze agreement, ambiguity,
   label comparisons, class-specific judge performance, and phenomenon patterns
   without overwriting historical labels.
  
## Data Handling and Analysis
Raw evaluator files, rater-ID mappings, and communication records are local-only.
Public outputs must be aggregate or thoroughly sanitized. The original author
labels are frozen as provisional historical data and remain distinct from the
modal panel labels.

For each scalar criterion, retain every rating and report the distribution,
modal share, unanimous/majority/tied status, coverage status, and item-problem
signals. Report realized support as `2/2`, `2/3`, `3/3`, or `other`; valid late
returns above three remain in `other` rather than being discarded. For the
multi-select source-role criterion, retain the complete set, report exact-set
agreement, and separately report per-role binary agreement and selection
prevalence. Never construct an exact-set panel label by combining separate
per-role majorities. A modal panel label requires at least two ratings and a
unique strict majority for that criterion; with exactly two ratings, unanimity
is required. Compare provisional author labels and
the two automated comparators only with unanimous- or majority-supported
substantive panel labels, and always report their information/scaffold
asymmetry: the comparators answer only the outcome questions, while humans use
the full identification-first forms. Preserve linguistic-policy divergences as
distinct observations. Rows without a supported substantive panel label remain
unresolved; that fact alone neither withdraws the item nor forces it into a
gold set.

The visible-boundary status and boundary-type answers are both retained even
when they conflict. Such rows receive an explicit coherence flag and are
reported by coherence status; the pipeline does not silently rewrite one field
from the other.

The historical author pilot's `safety_risk` and `risk_type` labels are retained
as frozen historical data. They are not directly compared with the revised
visible-boundary fields, which answer a narrower and more reviewable question.

An evaluator may request deletion of all returned blocks associated with their
pseudonymous rater ID until the stated collection-close and analysis-start
cutoff. Before the cutoff, remove the returned source files, record the action
in the local withdrawal log, and regenerate derived private outputs. After the
cutoff, returned files may already have informed de-identified analysis or
aggregate outputs, so deletion is not promised.
## Scope and Readiness Gate

Before recruiting, Brett must record the evaluator-role classification, confirm
that no institution has jurisdiction over the work, finalize the evaluator
information/agreement note, time the form, validate the person-disjoint private
assignment registry, and confirm data transfer. The
contribution model is an unpaid, bounded volunteer assignment; no honorarium,
authorship, employment benefit, or other material consideration is offered or
implied. A formal ethics application is not assumed; a scope determination is
required only if an institution, funding arrangement, or host condition brings
one into play. Before collection, Brett must also set and communicate the
collection-close and analysis-start cutoff, retention period, deletion route,
and local withdrawal procedure. This draft asserts that those remaining
operational decisions have not yet been made.

Methodological freeze readiness and permission to collect are separate gates. The
stamp-2 candidate must first verify the 54-key source, author snapshot, package
metadata, order audit, isolated ZIPs, analysis inputs, judge-comparator
structure, and visible-rule sentinels. After commit, an explicitly authorized
annotated tag must point at `HEAD`. Only then may the collection-ready gate
confirm the tag, scoped cleanliness, current interface timing, and finalized
return address, cutoff, retention, deletion, and withdrawal fields. Until both
gates pass, role packages must not be distributed and external returns must not
be opened.
