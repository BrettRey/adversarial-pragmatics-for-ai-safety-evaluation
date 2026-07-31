# Source hook: Anthropic 2026 eval incidents -> delegation-assurance
<!-- SUMMARY: a four-field trace instance with a contested institutional regime; candidate for DA's deferred institutional-mode worked case · status: uncited, first-party source · updated: 2026-07-30 -->

- **Central note:** `literature/anthropic_2026_cybersecurity_eval_incidents.notes.md`
- **Companion hooks:** `anthropic-2026-eval-scope-failure.md` (AP), `anthropic-2026-eval-evidentiary.md` (EA)
- **Cite as:** Anthropic (2026), "Investigating three real-world incidents in our cybersecurity evaluations," <https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals>, retrieved 2026-07-30.

**The four-field trace, instantiated.** DA's schema separates independently adjudicated authority status, system-assigned status, recognitional fit or misfit, and the action produced through that recognition. This case supplies all four from a first-party record:

| Field | This case |
|---|---|
| Adjudicated status | Attack the simulated target inside a sealed range. Nobody authorized touching production systems at three uninvolved organizations. |
| System-assigned status | Everything network-reachable is in scope, inferred from an unbounded task instruction plus a false assertion of no internet access. |
| Recognitional fit | Misfit, and it persisted through contrary evidence in two of three runs. |
| Action produced | Credential extraction, database access, a malicious PyPI package that executed on 15 real systems. |

Anthropic states DA's recognition-gap claim in its own voice: "the line between an aligned action and a harmful one is dependent on the model's understanding of its situation," and "we saw no evidence in any run described here of a model pursuing a goal of its own." Efficacy outran authorization without any misalignment of ends, which is the distinction DA exists to make and which capability and per-call-authorization baselines both miss.

**The stronger use: DA's deferred institutional-mode worked case.** Section 3 separates stipulated closed-world regimes from institutional regimes whose identity and applicability require adjudication, and the institutional worked case is one of the three round-1 items still open. This case is institutional in exactly the contested sense. Which regime governed the action is genuinely unsettled among Anthropic's evaluation policy, the third-party partner's environment configuration, and the law and terms of service of three organizations that authorized nothing and were not parties to any of it. The grant chain runs Anthropic to Irregular to model, and the harm lands on parties outside it entirely.

That is a better institutional illustration than a constructed one, because the regime-identification problem is real rather than stipulated, and because a stipulated closed-world reading gets the answer wrong: inside the declared regime the model did what it was told.

**Caution.** First-party disclosure by the vendor whose models are the subject. If DA uses it as a worked case rather than an illustration, the regime attribution has to be argued rather than borrowed, and Anthropic's own framing ("closer to a harness and operational failure than a model alignment failure") is a party's characterisation of where responsibility sits, which is precisely the kind of claim DA's apparatus is meant to test rather than accept. Chase the promised METR review before leaning on it.
