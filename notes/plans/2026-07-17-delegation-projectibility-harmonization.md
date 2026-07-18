# Delegation Assurance / AGI Evaluation Harmonization
## Aim
Align _Delegation Assurance_ with the live projectibility-first _AGI Evaluation_ paper while preserving their division of labour. The AGI paper supplies the discipline governing extrapolation from evaluation evidence. Delegation assurance supplies an action-level authorization claim and the evidence architecture used to assess it.

No change to the AGI paper is proposed in this pass. Delegation assurance will remain an assurance-case framework, not a new score.
## Manuscript changes
### 1. Make the output noncompensatory
State that delegation assurance is not a latent variable or composite numerical score. Its subclaims remain separately reportable, and failure or missing evidence on a required subclaim cannot be offset by success elsewhere. An action-level conclusion may be _supported_, _not supported_, or _indeterminate_.

Replace the statement that different deployments “weight” evidence families differently with a statement that they require different applicable subsets and depths of evidence.
### 2. Separate two evidential endpoints
Distinguish:

- retrospective reconstruction of one concrete action; and

- prospective projection to other actions, task families, systems, configurations, or future deployments.


A trace may support the first without supporting the second. A prospective claim will require a declared bearer, authority regime or policy snapshot, task and system populations, intervention range, time horizon, decision criterion, and matching holdout or independent outcome. The existing authority minimal pairs will be described as discrimination and construct tests, not by themselves as evidence of projectibility.
### 3. Fix the tail terminology
Replace “harmful-tail degradation” with “worst-tail change” or “worst-tail degradation” where the statistic concerns change under context. Add absolute worst-tail loss only when an authorization- or consequence-sensitive loss has been declared. This prevents Zhang-style change statistics from being treated as direct measures of harm.
### 4. Keep behavioural classification separate from internal mechanism
Replace phrases such as “status the system assigned” and “misfit recognition” with observable or recorded status classifications, uptake decisions, and classification--action fit. State that these records support behavioural attribution; claims about internal recognition or representation require additional causal or mechanistic evidence.
### 5. Fix the bearer and attribution level
Require each assurance claim to identify whether its bearer is a base model, stateful agent, deployed model--tool--retrieval composite, or wider socio-technical deployment. Preserve the existing model / scaffold / gate / evaluator decomposition.

Clarify that the trace can support operational and institutional attribution but does not by itself decide legal liability.
### 6. Narrow universal and ontological-sounding formulations
- Restrict the necessity of status, priority, and licensing to delegated actions in which authority is carried, modified, or contested through language.

- Present the failure mapping as candidate delegation diagnoses rather than reclassifying every listed AI-security failure.

- Replace “This middle layer has no classical analogue” with the narrower claim that the classical confused-deputy example lacks a language-interpretation step.

- State monotonic authority relative to a fixed grant: downstream nodes may narrow an inherited grant, while later authority can enter only through a separately recorded source with standing.

### 7. Preserve explicit defeat conditions
Keep and sharpen the existing demotion rule: status and priority lose their predictive or reconstructive role when capabilities, per-call authorization, causal attribution, or generic context instability explain the results equally well. Demotion from that role need not erase a descriptively or normatively useful audit field.
## Files in scope
- `delegation-assurance.tex` only if the abstract needs a compact no-score clarification

- `sections-delegation/01-introduction.tex`

- `sections-delegation/03-framework.tex`

- `sections-delegation/04-failure-evidence-mapping.tex`

- `sections-delegation/05-language-mediated-authority.tex`

- `sections-delegation/06-implications.tex`

- `sections-delegation/07-compositional-delegation.tex`

- `sections-delegation/07-conclusion.tex`


No benchmark instrument, Study A design, AGI-paper source, or empirical result will change.
## Verification
1. Re-read the complete revised argument against the live AGI manuscript.

2. Search for the retired formulations and accidental score language.

3. Build `delegation-assurance.pdf` with XeLaTeX and Biber.

4. Run the house-style checker on every edited TeX file.

5. Check for undefined citations/references, paragraph-length regressions, and uncommitted-file overlap.
