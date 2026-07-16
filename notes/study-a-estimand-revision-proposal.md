# Study A estimand-revision proposal (freeze blockers 5-7)
Status: proposal for Brett to annotate. Nothing executed yet.

The freeze-readiness board (unanimous NO-GO) left three blocks that are design decisions, not patches. Each below: the defect (verified), the options, my recommendation. Mark it up: pick an option, edit, or write "no" in the margin.

Guiding thread: all three trace to one thing — the benchmark's thesis is language-mediated **control** (whose instruction has authority, quoted vs commanded), but the frozen confirmatory tier measures generic task success and generic policy compliance, which on this benign set is dominated by trivial "nothing at stake" agreement. The revision moves the authority-relevant discrimination into the headline and stops treating disagreement as pure noise.

* * *
## Decision 5 — Confirmatory tier: measure the authority discrimination
**Defect (Greshake + Röttger + Wallace + hostile, verified):** co-primary `policy_compliance`'s majority class is `no_policy_or_authority_limit` (61% at 24B, 78% at 7B); `policy_compliance` author gold is `compliant` for all 18 items (zero variance); and the source-role / authority / information-flow constructs the benchmark is built to manipulate are all _exploratory_. A "successful" Study A is consistent with the panel being blind to authority.

- **5A — Add per-pair authority sensitivity as (co-)primary (recommended).** New confirmatory estimand: of the 9 minimal pairs, the fraction whose independent reference **flips across the pair in the gold direction** (e.g. AP-SEED-001 embedded-directive vs 002 direct-user: reference task_success should differ). This is the direct operationalization of "the panel reads the authority structure." Also promote `source_role_clarity` **yield** to secondary-confirmatory (does the panel produce stable source-role reads?). No new data; computed from the reference + item design.
  
- **5B — Policy-at-stake conditioning (recommended, complements 5A).** Report `policy_compliance` agreement on the **policy-at-stake subset** (exclude `no_policy_or_authority_limit` references) as the headline, with the not-at-stake share reported alongside. Add `no_policy_or_authority_limit` to A4. Fixes the trivial-majority problem without dropping the criterion.
  
- **5C — Disclose only (minimal / Greshake's floor).** Keep tiers as-is; add plan text that co-primary yield measures reliability, not authority-validity. Weakest; leaves the contribution out of the confirmatory tier permanently.
  

**My recommendation:** {==**5A + 5B**==}{>>yes<<}{id="c1" by="user" at="2026-07-16T09:49:54.018Z"}**.** Complementary, no new data, and they put the paper's actual claim in the headline. `information_flow_action_licensing` → secondary is optional (Wallace floats co-primary; I'd hold it at secondary to avoid over-loading the confirmatory tier).

* * *
## Decision 6 — Disagreement typology: stop reading contestedness as noise
**Defect (hostile, verified):** `consensus()` is majority vote only. A 2-1 substantive split becomes a clean reference (feeds C1-C4); the _same_ boundary item at 2-2 is dropped. Parity of N, not the construct, decides whether contestedness is signal or noise — which violates the project's own "treat disagreement as data." Co-primary yield then confounds "rubric unreliable" with "benchmark contains genuine boundary items."

- **6A —** {==**Split + contested-item**==}{>>yes<<}{id="c2" by="user" at="2026-07-16T09:50:40.239Z"} **estimand (recommended).** (i) Report C1-C4 split by reference type: unanimous / substantive-majority / escape (don't collapse unanimous+majority into "stable"). (ii) Add a **stable-but-contested** report: items where raters split across _substantive_ labels (not escapes) — flagged as construct-boundary signal, its own estimand. (iii) Condition every recall / candidate-revision claim (S3, RQ4) on reference robustness (unanimous vs majority; N=3 vs N=2-fallback). (iv) Standing statement: yield = inter-evaluator convergence, **not** correctness. Mostly analyzer output + plan text; the analyzer already computes the stability categories.
  
- **6B — Framing only (minimal).** Just (iii) + (iv); no contested-item estimand.
  

**My recommendation: 6A.** The contested-item report is plausibly the paper's most interesting output (a benchmark that _locates_ genuine category boundaries), and it's cheap.

* * *
## Decision 7 — Judge role separation: restore Option-A parity
**Defect (Chen, verified):** the frozen judge grades all three criteria in one joint pass, while the human panel is role-separated (D3 bars one person doing both roles, to prevent cross-role priming). So the judge's `policy_compliance` is produced with `task_success` in context; the human's is not. Same defect that killed Option B, on the role axis — the "information-state parity" justification is false as implemented.

- **7A —** {==**Re-run role-separated**==}{>>yes<<}{id="c3" by="user" at="2026-07-16T09:50:59.138Z"} **(recommended).** Modify `run_study_a_judge.py` to two role-scoped passes: linguistic-only prompt → `task_success` (linguistic codebook only); policy-only prompt → `policy_compliance` + `refusal_outcome` (policy codebook only). Regenerate both comparators (2 judges × 2 roles). Removes the confound; bounded code change + a local re-run I can do.
  
- **7B — Keep single-pass, disclose.** Strike the "information-state parity" language; pre-register joint-grading as a named confound in A5 / S2-S3. Cheaper, but documents the confound instead of removing it.
  

**My recommendation: 7A.** The judges are already pulled; a role-separated re-run is fast and makes the secondary judge number mean what it says.

* * *
## If you take my recommendations (5A+5B, 6A, 7A), the work is:
1. Rewrite the estimand table + multiverse + inference sections of `analysis-plan.md` (new authority-sensitivity + at-stake + contested-item estimands; reference-type splits; robustness-conditioning).
  
2. Analyzer additions: per-pair authority-sensitivity, policy-at-stake subset, reference-type split of C1-C4, contested-item report, robustness-gated recall.
  
3. Role-separate `run_study_a_judge.py`; regenerate the two comparators.
  
4. Regenerate the freeze manifest; re-verify.
  
5. Then a _second_ freeze-readiness pass (lighter) before the tag — the board should see the revision, not just the original.
  

Then, at the actual freeze: strip the DRAFT text (fix 3) and re-stamp (fix 4).

Order I'd run it: 7A first (mechanical, unblocks the judge tier), then 6A, then 5A+5B (the biggest plan rewrite), then manifest + re-review.
