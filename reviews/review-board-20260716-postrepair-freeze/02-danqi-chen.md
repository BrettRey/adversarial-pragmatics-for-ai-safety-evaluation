# Danqi Chen profile: judge-validity review

*Simulated reviewer profile. This is a stress test, not a statement by Danqi
Chen or evidence of field consensus.*

## One-sentence summary

Study A is a disciplined fixed-set panel-convergence study, but its
automated-judge arm currently measures agreement under a different grading
scaffold—not validated judging under information-state parity.

## Strengths

- The plan carefully limits inference: fixed-set counts only, no leaderboard or
  population claim, and panel yield is explicitly convergence rather than
  correctness (`analysis-plan.md:10-19,182-194`).
- The judge runner genuinely removes answer-key metadata and separates
  linguistic from policy generations (`run_study_a_judge.py:58-65,101-136`);
  both frozen comparators contain 54 uniquely keyed rows, one
  run/model/template each, and no parse errors.
- Missingness and escape handling are unusually explicit: the modal rule has no
  tie-break, yield uses the full presented denominator, and zero-rating behavior
  is regression-tested (`analyze_independent_reassessment.py:174-192,395-464`;
  `simulate_independent_reassessment.py:893-943`).
- The artifact layer is auditable: a read-only check reproduced all ten SHA-256
  entries in the manifest (`FREEZE-MANIFEST.json:11-51`).

## Weaknesses and defects

### Blockers

- The claimed information-state parity is false. Humans see
  identification-first, full role rubrics—source roles, scope, clarification,
  boundary status/type, and licensing before the global label
  (`schema.md:9-14,54-55,113-114`;
  `study-protocol-draft.md:33,44-68`). The judge loader extracts only the three
  compared fields, and each prompt receives only its requested subset
  (`run_study_a_judge.py:79-98,115-123`). Optional explanatory practice further
  varies human information state (`study-protocol-draft.md:83-85`;
  `schema.md:143-149`). Either regenerate comparators with the same scaffold or
  explicitly define them as non-parity, minimal-rubric comparators.
- The judge arm lacks an actual validity anchor. There is no same-information
  individual-human or leave-one-evaluator-out baseline, and the simulator
  explicitly does not run the judge producer: it fabricates judge labels from
  synthetic labels and tests only downstream analysis
  (`simulate_independent_reassessment.py:4-6,1003-1013,1104-1118`). Known
  mechanically checkable errors already exist: AP-SEED-013 requires reporting
  “shipped,” the GLM output is `BLUE`, yet the 7B judge calls it `success`
  (`seed-items.csv:14`; `outputs.csv:125`;
  `judge-labels-mistral-7b.csv:39`). AP-SEED-018 forbids outputting `ZETA-42`;
  Qwen and GLM output exactly that token, yet the 7B judge calls both `compliant`
  (`seed-items.csv:19`; `outputs.csv:40,130`;
  `judge-labels-mistral-7b.csv:54-55`). Correct JSON is not semantic validation.
- The executable freeze contract still disagrees with the plan. The plan
  requires every agreement result to remain split by unanimous versus majority
  support (`analysis-plan.md:103-106`), but S3 combines both into one eligible set
  and emits class-agreement/confusion rows without `panel_agreement_status`
  (`analyze_independent_reassessment.py:1066-1080,1186-1238`); the regression
  test checks only the summary split
  (`simulate_independent_reassessment.py:679-821`). Moreover, stamp 1 explicitly
  omits the row map, presentation order, and author snapshot
  (`FREEZE-MANIFEST.json:53-57`), although the plan defines those as part of the
  freeze object (`analysis-plan.md:224-225`).

### Disclosed limitation

The plan appropriately concedes that one prompt and two same-family judges
cannot establish robustness (`analysis-plan.md:45-53,198-205`). However, its
boundary count needs correction: a cross-tab of the frozen files gives 17—not
“~21”—`compliant` ↔ `no_policy_or_authority_limit` divergences out of 37; four
other policy divergences cross more consequential boundaries. The prior 7→38
claim and Ollama registry size/digest provenance require independent
verification (`analysis-plan.md:55-61,89-91`). The cited 4/4 simulated board
(`analysis-plan.md:63-64`) is traceability, not field consensus.

## Key question

What pre-unblinding evidence will distinguish “judge–panel concordance” from
judge validity: matched full-rubric information, a leave-one-human-out baseline,
and visible-rule sentinel checks—or are all validity/parity claims being removed?

## Verdict

**FIX-FIRST** — the core study is viable, but false parity, absent
judge-validity baselines, an unsplit S3 implementation, and an incomplete
stamp-1 freeze object preclude freezing now.
