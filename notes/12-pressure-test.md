# Pressure Test

## Load-Bearing Assumptions

| Assumption | What would make it false? | Design response |
|------------|----------------------------|-----------------|
| The benchmark measures language-mediated safety control, not generic reasoning. | Items can be solved without tracking authority, quotation, scope, deixis, or speech-act force. | Use minimal pairs where the surface string stays constant and only the linguistic embedding changes. |
| Rater disagreement is informative, not just noise. | Disagreement disappears after clearer instructions or reflects random inattentiveness. | Record confidence, rater role, and adjudication reason; distinguish unstable constructs from bad items. |
| The taxonomy improves eval construction. | Categories do not predict model behaviour, grader disagreement, or error attribution. | Report performance and disagreement by phenomenon family; revise taxonomy if families do no work. |
| LLM judges fail in predictable linguistic ways. | LLM-judge errors are unstructured or no worse on adversarial-pragmatic contrasts than ordinary items. | Include judge validation as an empirical question, not a premise. |
| The project is hireable because it is operational. | It reads as a conceptual essay with benchmark language added late. | Keep benchmark schema, seed items, validator, and metrics central from the first draft. |

## Strongest Anti-Thesis

The proposed benchmark may simply relabel already-known prompt-injection and policy-evaluation problems with linguistic terminology, without improving measurement, reliability, or safety documentation.

## Failure Conditions

The project should be demoted or redesigned if:

- minimal-pair contrasts do not change model or rater behaviour;
- labels cannot be made reliable after protocol revision;
- taxonomy categories fail to predict any pattern of model failure, grader failure, or adjudication;
- benchmark items depend on bespoke wording rather than reusable construction principles;
- the paper's empirical result is only a leaderboard.

## Early Tests

1. Build 50 seed items.
2. Have at least two rater roles annotate a subset.
3. Run at least one LLM judge on the same subset.
4. Identify whether disagreements cluster by phenomenon family.
5. Revise the taxonomy before scaling.
