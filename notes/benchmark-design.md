# Benchmark Design Notes

## Item Principle

Each item should test one language-mediated safety distinction while holding surface material constant enough to support a paired comparison.

## Pair Types

- user instruction vs untrusted webpage text;
- command vs quotation;
- direct request vs policy-analysis request;
- allowed transformation vs disallowed enactment;
- clear authority hierarchy vs spoofed authority;
- scoped permission vs scoped prohibition;
- literal request vs indirect pragmatic pressure;
- transcript refusal vs transcript inability.

## Labels

Use separate columns for:

- `task_success_label`;
- `policy_compliance_label`;
- `safety_risk_label`;
- `failure_attribution_label`;
- evaluator confidence in later annotation files.

Do not collapse these into a single `pass` column until after diagnostic analysis.
