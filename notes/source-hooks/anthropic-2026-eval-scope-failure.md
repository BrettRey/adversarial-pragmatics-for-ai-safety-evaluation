# Source hook: Anthropic 2026, cybersecurity evaluation incidents
<!-- SUMMARY: a false prompt assertion about scope led models to compromise real systems; documented instance of AP's scope-ambiguity family and DA's recognition gap · status: uncited, first-party source · updated: 2026-07-30 -->

- **Central note:** `literature/anthropic_2026_cybersecurity_eval_incidents.notes.md`
- **Cite as:** Anthropic (2026), "Investigating three real-world incidents in our cybersecurity evaluations," <https://www.anthropic.com/news/investigating-incidents-cybersecurity-evals>, retrieved 2026-07-30. Local archive hashed in the central note.

**Why adversarial pragmatics cares.** AP's phenomenon families include scope ambiguity, and this is a first-party documented case of scope ambiguity in an evaluation prompt producing real-world compromise. The prompt asserted the environment was a simulation without internet access. The assertion was false because of a misconfiguration. The task instruction, retrieve the flag, placed no bound on where to look. Models resolved that toward everything reachable being in scope and attacked production systems belonging to three organizations.

Anthropic's own proposed remedy is a claim about language-mediated control: Claude "wouldn't have accessed the internet to begin with if the prompt had clearly explained which systems were in and out of scope."

**Where it plugs in.** Section 2 argues that safety-relevant judgments turn on familiar distinctions in pragmatic interpretation, and currently illustrates that with constructed minimal pairs. This supplies a real case with named consequences. It also bears on the paper's separation of inference bearers: what a run shows about a model's behaviour is relative to a configured system and a declared context, and here the declared context was false, so behaviour that looked like an alignment failure was a scope failure inherited from the prompt.

**The reasoning trace is the interesting part** and is unusual to have on the record. In one incident the model explicitly considered whether it was on the real internet, concluded that publishing a package there would be "NOT okay, and surely not the intended solution," then argued itself back to simulation on two cues: unrecognised certificate authorities, and a system date of 2026 which it took to prove staging. It never revisited that. A defeasible inference from environmental cues to a scope judgment, wrong, and recoverable from a transcript.

**Verify before citing.** First-party disclosure by the vendor whose models are the subject. Report the numbers as Anthropic's account. METR was engaged for third-party review and a redacted transcript was promised within a week of publication; both would strengthen any use of this case and should be chased. Do not repeat the newer-models-behave-better pattern as a finding: the post itself calls it three isolated incidents rather than a controlled comparison.

**Related:** `notes/source-hooks/guha-2026-benchmark-institutions.md` for the argument that evaluation design choices determine what a result can support. This case is the same point from the other end, where the design choice is a false situating assertion rather than a benchmark-construction decision.
