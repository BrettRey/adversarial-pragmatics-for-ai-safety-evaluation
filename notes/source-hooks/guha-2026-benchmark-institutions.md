# Source hook: Guha et al. 2026, institutional view of legal AI benchmarking
<!-- SUMMARY: PNAS Perspective on benchmark design dimensions, capture, and legibility; hooks into AP's inference-bearer argument and EA's record-adequacy layer · status: uncited, metadata complete · updated: 2026-07-26 -->

- **Central note:** `literature/guha_etal_2026_no_free_benchmark_legal_ai.notes.md`
- **Cite as:** Guha, Zhang, Tsang, Manning, Nyarko & Ho (2026), "There is no free benchmark: An institutional view of legal AI benchmarking," *PNAS* 123(30), published 2026-07-20, CC BY. DOI `10.1073/pnas.2509757122`, Crossref-verified 2026-07-26.

**Why these papers care.** AP argues that a single benchmark label conceals four different inference bearers, and that what a score licenses depends on which target you declare. Guha et al. make the institutional version of the same argument: benchmarking involves six discretionary design choices (task definition, construction, evaluation protocol, measurements, choice of systems, transparency), and who makes them determines what the resulting number can support. Same structure, different level of explanation, which is worth being explicit about rather than eliding.

**Where it plugs in.**

- `sections/02-pass-fail.tex`, in the meta-evaluation paragraphs added 2026-07-25 alongside Reuel, Haimes, Dehghani, and Landesberg. This is the strongest available citation for the claim that benchmark construction determines what a score can be used for, and it's a PNAS Perspective rather than a preprint, which matters for the JAIR submission.
- The Paxton AI case is the best real-world instance of AP's central claim I've seen: a vendor advertising "94%+ accuracy on Stanford Hallucination Benchmark" where the benchmark tested explicit overruling, easy enough that bag-of-words models score near-perfectly. A true score, reported against a target that can't support the advertised use. If AP wants one concrete non-toy illustration of an inference-licence failure, this is it.
- The Thomson Reuters 33%-versus-10% dispute illustrates that two benchmarks for one task yield different estimates and can't be adjudicated without construction details. Adjacent to AP's argument for validator-enforced item metadata.
- Hidden stratification (chest X-ray, 0.87 overall against 0.77 on the clinically critical subgroup) supports AP's separation of aggregate judge performance from minority-class recovery, which is exactly the six-cell judge finding.

**Explanation-level caution.** Guha et al. work at the institutional level: incentives, capacity, ownership. AP works at the measurement and pragmatic level. Don't let the citation slide between them. AP's claim is about what a label licenses given how items were built; theirs is about which labels get built at all, given who pays. They're complementary, and saying so is more useful than treating them as the same point.

**Verify before citing:** the vendor claims are Guha et al.'s characterisations, so attribute them rather than asserting the vendor behaviour directly. Note also the declared competing interests (Manning advises LLM companies; Guha has consulted for CaseText and Snorkel AI), which matters if the paper is used as evidence about vendor conduct rather than about benchmarking design.
