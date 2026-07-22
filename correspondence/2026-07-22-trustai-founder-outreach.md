# TrustAI founder outreach
## The YC framing
Do not pitch an idea, a framework, or three papers. Pitch one product-relevant failure mode, evidence that you can already work on it, and a bounded paid experiment.

The useful asymmetry is not merely that TrustAI has money and Brett does not. TrustAI has a newly public claim it must make defensible: that its Permission Compliance verdicts show an agent stayed within what it was permitted to do. Brett has a developed way to detect cases in which the agent, policy reference, or evaluator appears to pass for the wrong reason.

The founder should be able to classify the message in under thirty seconds:

- specific to TrustAI, not generic AI-safety outreach;
  
- capable of improving the product or a customer report;
  
- low-cost to investigate;
  
- backed by an existing artifact rather than a request to fund open-ended research; and
  
- sent by someone who understands what TrustAI already does well.
  
## Recommended first email
**Subject:** A false-green stress test for TrustAI's Permission Compliance evals

Hi Hannah and Medha,

Congratulations on the launch. I looked closely at the Permission Compliance and reconstruction-local parts of your public assessment. The preregistered criteria, confidence intervals, explicit not-assessed states, and limits on transfer from a reconstructed agent are unusually careful.

I've been working on the philosophical foundations of AI safety and compliance, especially what makes an agent action authorized and what evidence warrants that conclusion. One resulting failure mode may be useful to TrustAI: a Permission Compliance test can turn green because the agent tracked the governing authority, but also because it refused everything, followed recency or policy-looking language, or was scored against the wrong permitted-action reference. Those routes can look identical in a report but behave very differently when a role, policy, prompt, model, or integration changes.

I've built machine-checked development fixtures and analysis code for testing whether a system distinguishes operative authority changes from inert and quoted lookalikes. Each case preserves a separately authorized control action, which catches apparent success produced by blanket refusal or indiscriminate resistance to later instructions.

A narrow pilot could adapt that design to one harmless shadow ERP/MCP workflow and compare TrustAI's verdicts with a prospectively specified action reference. I would handle the test design, analysis, and evaluation memo; your team would expose and operate the relevant part of the harness. The first pass would require neither customer data nor production actions.

Would you be open to a 20-minute call? If the problem looks relevant, we could then scope a fixed, paid two-week pilot.

Best,

Brett Reynolds

Professor, Humber Polytechnic

[https://github.com/BrettRey/adversarial-pragmatics-for-ai-safety-evaluation](https://github.com/BrettRey/adversarial-pragmatics-for-ai-safety-evaluation)
## Why this version works
The message credits their real strengths before identifying the gap. It does not claim that their implementation actually suffers from the failure mode; it says the public evaluation proposition makes the test material. It names a deliverable and asks for a call, not for unpaid access, general mentorship, or an undefined collaboration.

The key sentence is the offer of a **small paid pilot**. Do not hide payment until after producing bespoke work. Conversely, do not lead with your financial situation or put a fee in the cold email. The business reason for paying is that the pilot tests a claim on which their product and customer reports depend.
## What not to send initially
- No full benchmark, private corpus, complete schema bundle, or detailed implementation recipe.
  
- No three-paper literature tour.
  
- No claim that TrustAI has confused authorization, evidence, or compliance without inspecting the product.
  
- No suggestion that the idea alone deserves compensation.
  
- No offer to prepare a bespoke pilot specification for free beyond a genuinely one-page scope.
  
- No NDA request in the opening message; discuss confidentiality before receiving customer or proprietary harness material.
  
## If they take the call
Use twenty minutes as follows:

1. Ask them to describe one Permission Compliance test and how its permitted-action reference is established.
  
2. Ask what triggers reassessment: model, prompt, role, policy, tool, interface, and evaluator changes.
  
3. Show one harmless counterexample in which the same green output can arise from authority sensitivity or indiscriminate refusal.
  
4. Propose one action family, one reconstruction, fixed inputs, fixed deliverables, and a short schedule.
  
5. Confirm that any adaptation beyond the exploratory call is paid.
  

The first pilot should deliver:

- a test adapter for one harmless action family;
  
- controlled operative, non-operative, nuisance, and placebo cases;
  
- a false-green and judge-disagreement report;
  
- a reference/behaviour/measurement/change-impact classification;
  
- recommended additions to their trace or report schema; and
  
- a decision about whether a larger customer-facing validation project is warranted.
  
## Commercial posture
The product-language version of Brett's contribution is:

> TrustAI tests whether an agent stays within a permission envelope. I test whether the envelope, its interpretation, and the green verdict remain correct when policy language, authority, and deployment configuration change.

That is a paid product-validation capability. The papers establish depth and credibility after interest exists; they are not the opening product.
