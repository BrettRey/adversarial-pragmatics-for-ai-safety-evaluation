# Construct-domain coverage register

`construct-domain-matrix.csv` is a design register, not an item-count target or a prevalence estimate. Each row identifies one atomic contrast region: a primary family and subfamily, an explicit boundary relation, one source relation, one pragmatic-status relation, one surface relation, and one claim-relevant coverage requirement. Relations such as `document_to_user_message` are single contrast descriptors rather than compressed Cartesian products.

Coverage status has three values:

- `observed_seed`: the historical seed materials represent the cell, without implying a strict minimal pair or a projective result;
- `development_fixture`: a public Study B fixture represents the cell but remains ineligible for target inference; and
- `planned_gap`: the cell is a construction target with no current item-level evidence.

`claim_ids` links the cell to the declarations it can inform. `priority` and `priority_rationale` state why it matters. `required_base_count` and `represented_base_count` make shortfalls explicit; a row is not sufficient merely because its vocabulary appears once. Planned target cells use the stricter five-base taxonomic requirement. Behavioural claims still apply their separate four-base minimum and conjunctive family-by-surface gate.

`phenomenon_family` is the primary assignment. `phenomenon_subfamily` records the controlled subtype, and `boundary_relation` preserves a declared neighbouring or overlapping family. The matrix therefore does not force naturally multi-family cases into an exclusive partition.

The five criterion columns state the role each response dimension plays in the proposed cell. They preserve task success, policy compliance, safety risk, criterion-scoped uncertainty, and failure attribution rather than compressing them into one score. Criterion-scoped uncertainty may be secondary, diagnostic, or inapplicable; it is never a primary evaluator-performance estimand. `template_split` prevents historical, development, and untouched target material from being silently pooled.

Expansion is justified by a declared coverage gap or planned comparison. Counts are consequences of that design. They do not establish content validity, set benchmark weights, or estimate the prevalence of a phenomenon in deployments.
