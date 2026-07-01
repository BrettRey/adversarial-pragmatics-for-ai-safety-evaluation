# LLM-Judge Validation: local-pilot-20260630-185417

- Judge run: `judge-validation-glm-compact-20260701`
- Judge model: `glm-4.7-flash:q4_K_M`
- Prompt variant: `compact`
- Rows judged: 54
- Raw judge bundle: `benchmark/results/local-pilot-20260630-185417/judge_validation/judge-validation-glm-compact-20260701`

## Label Accuracy

| Label family | Matched | Total | Invalid | Accuracy |
| --- | --- | --- | --- | --- |
| task_success | 36 | 54 | 0 | 66.7% |
| policy_compliance | 48 | 54 | 0 | 88.9% |
| safety_risk | 39 | 54 | 0 | 72.2% |
| risk_type | 45 | 54 | 0 | 83.3% |
| refusal_outcome | 53 | 54 | 0 | 98.1% |
| failure_attribution | 42 | 54 | 0 | 77.8% |

## Primary Diagnostic Axes

| Axis | Accuracy |
| --- | --- |
| task_success | 66.7% |
| policy_compliance | 88.9% |
| failure_attribution | 77.8% |

## Lowest Phenomenon/Axis Cells

| Phenomenon | Label family | Matched | Total | Accuracy |
| --- | --- | --- | --- | --- |
| policy_boundary_ambiguity | task_success | 2 | 6 | 33.3% |
| policy_boundary_ambiguity | failure_attribution | 2 | 6 | 33.3% |
| embedded_command | safety_risk | 4 | 9 | 44.4% |
| agent_transcript_interpretation | task_success | 3 | 6 | 50.0% |
| agent_transcript_interpretation | failure_attribution | 3 | 6 | 50.0% |
| deixis_reference_hijack | policy_compliance | 3 | 6 | 50.0% |
| deixis_reference_hijack | safety_risk | 3 | 6 | 50.0% |
| deixis_reference_hijack | risk_type | 3 | 6 | 50.0% |
| policy_boundary_ambiguity | safety_risk | 3 | 6 | 50.0% |
| embedded_command | task_success | 5 | 9 | 55.6% |
| indirect_speech_act | task_success | 4 | 6 | 66.7% |
| indirect_speech_act | failure_attribution | 4 | 6 | 66.7% |

## Parse Errors

0 of 54 rows had a parse error or invalid judge response.
