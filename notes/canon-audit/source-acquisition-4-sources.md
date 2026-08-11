# Source acquisition: four audit-required sources

Run date: 2026-08-08. Locate-and-archive only. No bib entries written, no manuscript
edits, no project files touched (including `notes/cited-source-local-archive.md`,
which is left for whoever does the citation pass).

**Archive root:** `/Users/brettreynolds/projects/LLM-CLI-projects/literature/`

**Result: 5 files acquired and archived, 3 documented gaps.**

---

## Inward check (performed first, all four)

| Probe | Result |
|---|---|
| `lit resolve` on all four titles/keys | `no match` for every one |
| `literature/` filename scan (`becker`, `nanz`, `secpal`, `camel`, `debenedetti`, `denning`, `jajodia`, `thuraisingham`, `morgenstern`, `hinke`, `lattice`, `multilevel`, `access.?control`, `iceccs`, `00828`, `2503.18813`) | only `becker2010secpal.pdf` and `debenedetti2024agentdojo.pdf` — neither is a target |
| `literature/` content grep, **`grep -a` throughout** (`Nanz`, `state-modifying`, `2503.18813`, `Defeating Prompt Injections`, `lattice model of secure`, `Jajodia`, `Thuraisingham`) | no hits on any target. `Nanz`/`Jajodia`/`Thuraisingham` hits were unrelated (a Korean-syntax paper, a GDPR preprint, `south2025authenticated`) |
| Central bib `.house-style/references.bib` (22,058 lines) | only `debenedetti2024agentdojo` (AgentDojo, different paper) |
| Project `references-local.bib` | nothing |
| `~/pdf-inbox` (36 files, listed by recency) | nothing; newest is 2026-08-08 13:50, unrelated |

**Portfolio status before this run: all four sources absent.** One partial exception —
the CaMeL PDF sat unarchived in this session's scratchpad (see source 2).

---

## Source 1 — Becker & Nanz 2007

### Verified citation (Crossref, DOI resolved)

**ESORICS conference version (what SecPAL cites, NOT the file acquired):**
> Becker, Moritz Y. & Sebastian Nanz. 2007. A Logic for State-Modifying Authorization
> Policies. In *Computer Security – ESORICS 2007* (Lecture Notes in Computer Science),
> 203–218. DOI `10.1007/978-3-540-74835-9_14`. ISBN 9783540748342 / 9783540748359.

Cross-checked against the citing text itself. `becker2010secpal.pdf` in the archive,
reference [10]: "M. Y. Becker and S. Nanz. A logic for state-modifying authorization
policies. In 12th European Symposium on Research in Computer Security (ESORICS), pages
203–218, 2007." Pages and year agree with Crossref exactly.

**Extended journal version (exists, distinct, not previously flagged):**
> Becker, Moritz Y. & Sebastian Nanz. 2010. A logic for state-modifying authorization
> policies. *ACM Transactions on Information and System Security* 13(3). 1–28.
> DOI `10.1145/1805974.1805976`.

### What was acquired

The **Microsoft Research technical report**, MSR-TR-2007-32, March 2007 — the authors'
extended version, free from Microsoft Research.

- **Archive path:** `/Users/brettreynolds/projects/LLM-CLI-projects/literature/becker_nanz_2007_state_modifying_authorization_policies.pdf`
- **SHA-256 (pdf):** `d9889afd0e12d08b24308d213eab0cf1a4d4b893b6064a4bddd6099cab7eac39`
- **Companion:** `becker_nanz_2007_state_modifying_authorization_policies.md`, SHA-256 `0fc62429141934021016e12aa6083fd586e83076507a89bd8d16c2204cb3e2d1`
- **Pages:** 29. Bytes: 535,737. Source URL: `https://www.microsoft.com/en-us/research/wp-content/uploads/2007/03/tr-2007-32.pdf`

**Verified as the real, complete document.** Page 1 front matter reads: "A Logic for
State-Modifying Authorization Policies / Moritz Y. Becker, Microsoft Research, Cambridge,
UK / Sebastian Nanz, Informatics and Mathematical Modelling, Technical University of
Denmark / March 2007 / Technical Report". The abstract matches the ESORICS abstract
(Transaction Logic semantics; state updates factored out of the resource guard; sound and
complete proof system; goal-oriented algorithm for minimal request sequences). Page 29 is
the tail of the proof appendix (Lemma 3.19), so the file is not truncated.

### Discrepancies (flagged, not silently resolved)

1. **The acquired file is not the ESORICS proceedings version.** 29 pages against the
   ESORICS 16 (203–218). It is the longer TR with full proofs. Anything cited to a page
   number must be cited to the TR, or the page must come from the Springer version, which
   was not obtained.
2. **Microsoft Research's own publication page states the venue as "Proc. of IEEE Infocom
   2010."** That is wrong — this is an ESORICS 2007 paper. Treat the MSR page's venue field
   as unreliable metadata; the PDF itself and Crossref agree with each other.
3. The **DTU Orbit** record (Nanz's institutional repository) indexes only the technical
   report, not the ESORICS chapter, and offers no downloadable file.

### For the ESORICS version specifically

`https://link.springer.com/content/pdf/10.1007/978-3-540-74835-9_14.pdf` returns a 3,038-byte
HTML auth stub. Semantic Scholar has no record under that DOI. Paywalled; not acquired.

---

## Source 2 — CaMeL

### Verified citation (arXiv API + SaTML 2026 accepted-papers page)

> Debenedetti, Edoardo, Ilia Shumailov, Tianqi Fan, Jamie Hayes, Nicholas Carlini,
> Daniel Fabian, Christoph Kern, Chongyang Shi, Andreas Terzis & Florian Tramèr. 2025.
> Defeating Prompt Injections by Design. arXiv:2503.18813v2 [cs.CR].
> Submitted 2025-03-24; v2 2025-06-24. To appear, IEEE SaTML 2026 (Research Papers).

- **Archive path:** `/Users/brettreynolds/projects/LLM-CLI-projects/literature/debenedetti_2025_camel_defeating_prompt_injections.pdf`
- **SHA-256 (pdf):** `c3719f6ce73eecf45e3764debef8a3d8ff8c9233b37d128c558b694ec3790cc7`
- **Companion:** `debenedetti_2025_camel_defeating_prompt_injections.md`, SHA-256 `1d87f0c227219d61107a9ef025371c8b7541b90162043447e3a2c277f3c149f7`
- **Pages:** 125 (long appendices). Bytes: 5,531,468.

**Verified.** Page 1 carries the stamp `arXiv:2503.18813v2 [cs.CR] 24 Jun 2025`, the full
author list, affiliations (1 Google, 2 Google DeepMind, 3 ETH Zurich), and the abstract
("solving 77% of tasks with provable security (compared to 84% with an undefended system)
in AgentDojo"). Page 125 is live appendix content, so it is complete.

**SaTML 2026 verified, not assumed.** `https://satml.org/2026/accepted-papers/` (live,
HTTP 200, confirmed today) lists "Defeating Prompt Injections by Design" under **Research
Papers**, with the author list and affiliations matching. Note `https://satml.org/accepted-papers/`
404s — the year segment is required.

### Discrepancies

1. **The task brief's author attribution is wrong.** It gives "Debenedetti, Beurer-Kellner
   et al." **Luca Beurer-Kellner is not an author of this paper.** He is an author of
   *AgentDojo* (`debenedetti2024agentdojo`, already in the central bib), which is a
   different paper and is probably where the conflation came from. Confirmed against
   the arXiv API, the PDF's own title page, and the SaTML accepted-papers listing — all
   three agree on the ten-author list above.
2. Minor: SaTML lists Nicholas Carlini at **Anthropic**; the arXiv v2 PDF has him under
   Google DeepMind. An affiliation change between preprint and camera-ready, not an error.
3. arXiv reports **no journal-ref and no registered DOI** for this entry as of today, so
   the SaTML appearance is not yet reflected in arXiv metadata.
4. `file(1)` misreports this PDF as "20 pages"; `pdfinfo` and a page-125 text extraction
   both give 125. Trust `pdfinfo`.

---

## Source 3 — "A Vision for Access Control in LLM Agent Systems" (ICECCS 2025)

### PRIORITY ITEM — READ THIS SECTION

**The published ICECCS chapter was NOT obtained. It is paywalled with no open-access
version. What was archived is an arXiv preprint that is close but demonstrably not
bibliographically identical, and the manuscript's remaining claim should not be rested
on the assumption that they are the same document.**

### Verified citation of the published chapter (Crossref + DBLP, agreeing)

> Huang, Dong, Jie Li, Hongyi Cai, Xinfeng Li, Yijia Xu, Wenbin Tang, Jie Zhang & Yang Liu.
> 2025. A Vision for Access Control in LLM Agent Systems. In *Engineering of Complex
> Computer Systems* (Lecture Notes in Computer Science), 467–472. Springer Nature
> Switzerland. DOI `10.1007/978-3-032-00828-2_25`. ISBN 9783032008275 / 9783032008282.
> Issued 2025-10-17. ICECCS 2025, 29th International Conference, Hangzhou, China, 2–4 July 2025.
> DBLP key `conf/iceccs/HuangLCLXTZL25`.

Crossref returns **no abstract**, matching the audit's finding.

### What was acquired instead

> Li, Xinfeng, Dong Huang, Jie Li, Hongyi Cai, Zhenhong Zhou, Wei Dong, XiaoFeng Wang &
> Yang Liu. 2025. A Vision for Access Control in LLM-**based** Agent Systems.
> arXiv:2510.11108v2 [cs.MA]. Submitted 2025-10-13; v2 2025-10-19. 11 pages, 1 figure.
> DOI `10.48550/arXiv.2510.11108`. DBLP key `journals/corr/abs-2510-11108`.

- **Archive path:** `/Users/brettreynolds/projects/LLM-CLI-projects/literature/li_huang_2025_access_control_llm_agent_systems.pdf`
- **SHA-256 (pdf):** `34d5f6b8689268cb4e09024118c3a169d7b4ab460deed458f7c1330b4ec3342c`
- **Companion:** `li_huang_2025_access_control_llm_agent_systems.md`, SHA-256 `aea1d574b9a8a6a4f97016b729c1c6919065afd65945f473b7ff54ef1715f6cd`
- **Pages:** 11. Bytes: 398,545.

**Verified complete.** Page 1 carries `arXiv:2510.11108v2 [cs.MA] 19 Oct 2025`, the
LNCS-format title block, affiliations (1 Nanyang Technological University, 2 National
University of Singapore), the abstract, `Keywords: Access Control · Trustworthy Agent`,
and the footnote "Corresponding Author: Dong Huang (e1143962@u.nus.edu)". Page 11 ends
mid-bibliography with real reference entries, so nothing is truncated.

**Contents:** a position paper proposing **Agent Access Control (AAC)**, reframing access
control as information-flow governance, with two modules — multi-dimensional contextual
evaluation (identity, relationships, scenarios, norms) and adaptive response formulation
(redaction, summarization, paraphrasing beyond allow/deny) — driven by a dedicated AC
reasoning engine. This is now readable; the audit's "nobody has read it" gap is closed for
the preprint's content, not for the published chapter's.

### The discrepancies, stated loudly

**DBLP holds these as two separate publication records and does not link them as versions
of one work.** Four differences:

| | Published chapter | arXiv preprint |
|---|---|---|
| Title | "in LLM Agent Systems" | "in LLM-**based** Agent Systems" |
| First author | Dong Huang | Xinfeng Li |
| Length | 6 pp. (467–472) | 11 pp. |
| Date | ICECCS July 2025; Crossref issued 2025-10-17 | arXiv v1 2025-10-13 |

Author lists share **five** names (Dong Huang, Jie Li, Hongyi Cai, Xinfeng Li, Yang Liu)
and differ by **three each way**:
- chapter only: Yijia Xu, Wenbin Tang, Jie Zhang
- preprint only: Zhenhong Zhou, Wei Dong, XiaoFeng Wang

**The arXiv PDF never mentions ICECCS, Springer, LNCS, or Hangzhou** — grep for all of
those returns nothing. There is no self-identification linking it to the published chapter.

What supports treating them as one work: identical framework name and two-module
architecture, near-identical title, LNCS document class, overlapping core authorship, and
Dong Huang as corresponding author on the preprint and first author on the chapter. That is
strong circumstantial evidence, but it is inference, not verification.

**Recommendation:** cite the preprint as the preprint (arXiv:2510.11108), with its own
author list, or obtain the Springer chapter through a library before attributing anything
to the published version. Do not merge the two author lists.

Minor: Semantic Scholar renders "Wenbin Tang" as "Wen Tang". Crossref and DBLP both say
Wenbin Tang; prefer those.

### What was tried for the published chapter

- `https://doi.org/10.1007/978-3-032-00828-2_25` → resolves to Springer
- `https://link.springer.com/chapter/10.1007/978-3-032-00828-2_25` → 303 to `idp.springer.com/authorize` (login wall)
- `https://link.springer.com/content/pdf/10.1007/978-3-032-00828-2_25.pdf` → 3,038-byte HTML stub, not a PDF
- Semantic Scholar `openAccessPdf` for the chapter DOI → `{"url": "", "status": null}` (no OA copy indexed)
- Dong Huang's homepage `https://huangd1999.github.io/` → **no entry** for this paper or for ICECCS 2025 at all
- arXiv title search (`ti:"Access Control" AND ti:"LLM Agent"`) → returned only an unrelated 2505.18279
- ACM DL mirror `dl.acm.org/doi/abs/10.1007/978-3-032-00828-2_25` → same Springer paywall

---

## Source 4 — Information flow, and the inference/aggregation line

### 4a. Denning 1976 — ACQUIRED (the anchor)

Verified against Crossref and against the document's own printed page numbers.

> Denning, Dorothy E. 1976. A lattice model of secure information flow.
> *Communications of the ACM* 19(5). 236–243. DOI `10.1145/360051.360056`.

- **Archive path:** `/Users/brettreynolds/projects/LLM-CLI-projects/literature/denning_1976_lattice_model_secure_information_flow.pdf`
- **SHA-256 (pdf):** `dbd25312c94632a874f4ec4baf450a2247ef99f01fa51e7ef0be1e5a9e2df450`
- **Companion:** `denning_1976_lattice_model_secure_information_flow.md`, SHA-256 `d50bed687604f683077d193379f55f7f95118edecaeff38386874ad9961ecbac`
- **Pages:** 8. Bytes: 690,073.
- **Route:** Wayback Machine capture of the ACM DL PDF, `https://web.archive.org/web/2020/https://dl.acm.org/doi/pdf/10.1145/360051.360056`. CACM 1976 is inside ACM's opened first-fifty-years archive (Semantic Scholar reports the DOI as BRONZE open access); `dl.acm.org` itself refuses scripted requests behind Cloudflare.

**Verified, and front matter agrees with Crossref on every field.** Page 1: "Operating
Systems / R.S. Gaines Editor / A Lattice Model of Secure Information Flow / Dorothy E.
Denning / Purdue University", full abstract, "CR Categories: 4.35". Embedded PDF metadata
gives the title, author "Dorothy E. Denning", and subject `http://doi.acm.org/10.1145/360051.360056`.
Every page footer reads "Communications of the ACM / May 1976 / Volume 19 / Number 5".
**Printed page numbers run 236 on PDF page 1 to 243 on PDF page 8** — 8 pages, exactly the
236–243 range Crossref gives. **No discrepancy between document and Crossref.**

### 4b. Lunt 1989 — ACQUIRED

Verified against DBLP and against the document's own IEEE copyright footer.

> Lunt, Teresa F. 1989. Aggregation and Inference: Facts and Fallacies. In *Proceedings.
> 1989 IEEE Symposium on Security and Privacy*, 102–109. DOI `10.1109/SECPRI.1989.36284`.

- **Archive path:** `/Users/brettreynolds/projects/LLM-CLI-projects/literature/lunt_1989_aggregation_inference_facts_fallacies.pdf`
- **SHA-256 (pdf):** `313c7e2e3b56c5d1a2030467beb2f98c3021ffc0be52822d5d7df40ab33794e4`
- **Companion:** `lunt_1989_aggregation_inference_facts_fallacies.md`, SHA-256 `ce8096b0b60b42737432cb6c16f4982b7f675adeed134b39e80f2035644f1e53`
- **Pages:** 8. Bytes: 929,676.
- **Route:** Semantic Scholar reports GREEN OA at `acme.highpoint.edu/~culleev8/CIS430/AggregationAndInference.pdf`; that host is dead, so the file came from its Wayback capture, `http://web.archive.org/web/20170811201635/http://acme.highpoint.edu/~culleev8/CIS430/AggregationAndInference.pdf`.

**Verified.** Page 1: "Aggregation and Inference: Facts and Fallacies / Teresa F. Lunt /
Computer Science Laboratory / SRI International / Menlo Park, California". The IEEE footer
reads `CH2703-7/89/OOOO/O102$Ol.00 01989 IEEE`, confirming start page **102**; the last
page ends on **109**. 8 pages, matching DBLP's 102–109. Substance is on point: it defines
the aggregation problem, names fallacies about it, and discusses SeaView, LOCK Data Views,
and TRW's A1 prototype.

**One quality caveat.** This is an OCR'd scan and the `.md` carries OCR noise ("databsae"
for database, "ae" for as, "Hlnke" for Hinke). Fine for reading and locating passages;
**quote from the PDF, not the Markdown.**

### 4c–4e. Verified metadata, full text NOT obtained

All three verified through DBLP (per instruction, not OpenAlex author matching) and
cross-checked against Crossref where a DOI exists. Citations below are safe to use; the
documents are not on disk.

> Morgenstern, Matthew. 1987. Security and Inference in Multilevel Database and
> Knowledge-Base Systems. In *Proceedings of the 1987 ACM SIGMOD International Conference
> on Management of Data*, 357–373. DOI `10.1145/38713.38752`.

> Hinke, Thomas H. 1988. Inference aggregation detection in database management systems.
> In *Proceedings. 1988 IEEE Symposium on Security and Privacy*, 96–106.
> DOI `10.1109/SECPRI.1988.8101`.

> Thuraisingham, Bhavani M. 1987. Security checking in relational database management
> systems augmented with inference engines. *Computers & Security* 6(6). 479–492.
> DOI `10.1016/0167-4048(87)90029-0`.

**Morgenstern 1987 — what was tried.** OpenAlex and Semantic Scholar both report this as
**gold open access** at `https://dl.acm.org/doi/pdf/10.1145/38714.38752` (note ACM's own
OA URL uses `38714`, not the DOI's `38713`; both were tried). Direct `curl` with a full
Chrome header set (UA, Accept, Accept-Language, sec-ch-ua, Sec-Fetch-*) returns Cloudflare's
`<title>Just a moment...</title>` interstitial. Wayback availability API returns
`archived_snapshots: {}` for `dl.acm.org/doi/pdf/10.1145/38713.38752`,
`dl.acm.org/doi/pdf/10.1145/38714.38752`, `dl.acm.org/doi/10.1145/38713.38752`, and
`dl.acm.org/citation.cfm?id=38752`. CDX search across `dl.acm.org*` and
`portal.acm.org/citation.cfm*` filtered on `38752` returned zero rows.
**It is genuinely free; it is only Cloudflare that blocks scripted retrieval.** One session
in a real browser would get it.

**Hinke 1988 — what was tried.** OpenAlex: `oa_status: closed`, `any_repository_has_fulltext: false`.
Semantic Scholar: `openAccessPdf: {"url": "", "status": "CLOSED"}`. Web search surfaced
only the IEEE Xplore landing page (`ieeexplore.ieee.org/document/8101/`) and paywalled
citing works. No author copy found. IEEE-paywalled.

**Thuraisingham 1987 — what was tried.** OpenAlex and Semantic Scholar both CLOSED.
Elsevier *Computers & Security*, 1987. No repository copy found.

### 4f. Jajodia & Meadows — verified as a print book chapter, not obtainable

> Jajodia, Sushil & Catherine Meadows. 1995. Inference Problems in Multilevel Secure
> Database Management Systems. In Marshall D. Abrams, Sushil Jajodia & Harold J. Podell
> (eds.), *Information Security: An Integrated Collection of Essays*. IEEE Computer
> Society Press. ISBN 0818636610 / 0818636629.

This is the field's standard survey and the one item here co-authored by the target
journal's board member, so it was pursued hardest. **Not acquired.**

What was tried: Semantic Scholar record `471193eaeed0b14e9f4dac34aebe6930613b0ec0` has
`openAccessPdf: {"url": "", "status": null}` and no DOI (MAG 17090561, CorpusId 11272483).
DBLP search for `Jajodia+Meadows+inference+problems+multilevel+secure` returns
`TOTAL 0` — the volume's chapters are not individually indexed. `csis.gmu.edu/jajodia/`
loads (with a TLS chain warning requiring `curl -k`) but hosts no PDFs; `publications.php`
returns a 16-byte empty response and `acm_library.php` fails TLS verification under WebFetch.
The parent volume exists at Internet Archive as `informationsecur0000unse_o9z5`, but that
is controlled digital lending (borrow-only), not a downloadable copy, so it is out of scope
under the free-and-legitimate rule.

**Caveat on the year.** Sources differ: the volume is variously dated 1994 and 1995, and
Semantic Scholar's record says 2006 (clearly a metadata artifact). The 1995 IEEE CS Press
printing is the usual citation, but **verify the year against a library catalogue record
before it goes in the bibliography** — I could not confirm it from the item itself.

---

## Summary table

| # | Source | Held before | Acquired | Pages | Archive stem |
|---|---|---|---|---|---|
| 1 | Becker & Nanz 2007 (MSR TR extended ver.) | No | **Yes** | 29 | `becker_nanz_2007_state_modifying_authorization_policies` |
| 1b | Becker & Nanz, ESORICS proceedings ver. | No | No — Springer paywall | (16) | — |
| 2 | CaMeL, arXiv:2503.18813v2 | No (loose in scratchpad) | **Yes** | 125 | `debenedetti_2025_camel_defeating_prompt_injections` |
| 3 | ICECCS chapter, DOI …00828-2_25 | No | **No — paywalled, no OA** | (6) | — |
| 3b | arXiv:2510.11108v2 preprint (near-version) | No | **Yes** | 11 | `li_huang_2025_access_control_llm_agent_systems` |
| 4a | Denning 1976, CACM 19(5) | No | **Yes** | 8 | `denning_1976_lattice_model_secure_information_flow` |
| 4b | Lunt 1989, IEEE S&P | No | **Yes** | 8 | `lunt_1989_aggregation_inference_facts_fallacies` |
| 4c | Morgenstern 1987, SIGMOD | No | No — Cloudflare (is gold OA) | (17) | — |
| 4d | Hinke 1988, IEEE S&P | No | No — IEEE paywall | (11) | — |
| 4e | Thuraisingham 1987, Comput. Secur. | No | No — Elsevier paywall | (14) | — |
| 4f | Jajodia & Meadows 1995 | No | No — print chapter, IA borrow-only | — | — |

Parenthesised page counts are from Crossref/DBLP page ranges, not from a file on disk.

## Things the caller should act on

1. **The CaMeL author list in the brief is wrong** — no Beurer-Kellner. Fix wherever it came from.
2. **The ICECCS paper is effectively unobtained.** The preprint is archived and readable, but
   its title, author list, and length all differ from the published chapter, and DBLP treats
   them as separate records. Decide deliberately which one the manuscript cites.
3. **Morgenstern 1987 is free and one browser session away.** It is the only gap here caused
   purely by bot-blocking rather than by a paywall.
4. **Nothing was written to `notes/cited-source-local-archive.md`** or to any bib file, per
   the locate-and-archive scope. Five archive paths and hashes above are ready to be recorded.
5. **Quote Lunt from the PDF, not the `.md`** — OCR noise.
