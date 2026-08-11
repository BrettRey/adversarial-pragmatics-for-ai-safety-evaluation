# Foundational Authorization-Formalization Literature: Locate-and-Archive Report

Task: locate and archive primary sources for the six foundational authorization-formalization
works a security/access-control referee flagged as absent from the adversarial-pragmatics
manuscript. Locate-and-archive only; no bib entries or manuscript edits were made.

## Step 1 — Inward search (portfolio), performed before any outward search

Checked, all negative:

- `lit resolve` (tools/lit-catalog) tried against author strings, titles, and citation-key
  guesses for all six works (e.g. `lit resolve "Abadi Burrows Lampson Plotkin"`, `lit resolve
  "SPKI Certificate Theory"`, `lit resolve "Delegation Logic"`, `lit resolve SecPAL`, `lit
  resolve "Park Sandhu"`, `lit resolve XACML`). No match for any.
- `grep -in "abadi\|lampson\|burrows\|plotkin\|ellison\|spki\|sdsi\|grosof\|feigenbaum\|secpal\|
  sandhu\|xacml\|oasis"` against the central bibliography `.house-style/references.bib`
  (~2162 entries). Only false-positive hit: an unrelated `Burrows2008` (Anne M. Burrows,
  primatology).
- `find literature -iname "*abadi*" -o -iname "*lampson*" -o -iname "*burrows*" -o -iname
  "*spki*" -o -iname "*sdsi*" -o -iname "*secpal*" -o -iname "*xacml*" -o -iname "*sandhu*"
  -o -iname "*ucon*" -o -iname "*delegation*logic*" -o -iname "*grosof*" -o -iname "*2693*"`
  across `/Users/brettreynolds/projects/LLM-CLI-projects/literature/` (3,119 filenames).
  No hits, filename search alone is known-unreliable given inconsistent naming, so combined
  with the next two checks.
- Full-text grep (`grep -rliE "calculus for access control|SPKI|SDSI|SecPAL|XACML|usage
  control model|delegation logic|distributed authorization"`) across every `.md` sidecar
  in `literature/`. One hit: `literature/south2025authenticated.md` (South, Mahari &
  Pentland, "Authenticated Delegation and Authorized AI Agents", already in the portfolio
  as an existing citation). That paper's related-work section discusses XACML in passing
  and cites the OASIS XACML v3.0 spec directly (giving the exact canonical URL used below),
  but does **not** cite ABLP, SPKI/SDSI, Delegation Logic, SecPAL, or UCON.
- `qmd query` (semantic + lexical) against the 1,384-document literature markdown index for
  all five non-XACML works. No relevant hits (only a spurious low-relevance match on an
  unrelated Mill text).

**Conclusion: all six works are genuinely absent from the portfolio** (central bib, literature
archive by filename, literature archive by full text, and the qmd semantic index). This is an
evidenced negative, not a one-search absence claim.

## Step 2/3 — Verified citations and acquisition

Every DOI below was checked live against the Crossref API (`api.crossref.org/works/<doi>`),
not taken from search-result prose. Every PDF was downloaded, then verified by reading its
actual first page (`pdftotext`) and page count (`pdfinfo`) to confirm it is the real, complete
document (not a paywall stub, an abstract-only page, or the wrong paper).

All files copied into the central literature archive:
`/Users/brettreynolds/projects/LLM-CLI-projects/literature/`
(no name collisions existed before copying).

---

### 1. ABLP logic (Abadi, Burrows, Lampson & Plotkin 1993)

**Citation (Crossref-verified):**
Abadi, M., Burrows, M., Lampson, B., & Plotkin, G. (1993). A calculus for access control in
distributed systems. *ACM Transactions on Programming Languages and Systems*, 15(4), 706–734.
DOI: 10.1145/155183.155225

Portfolio status: **not previously held.**

Acquired: free author copy from Gordon Plotkin's University of Edinburgh homepage
(`https://homepages.inf.ed.ac.uk/gdp/publications/Calculus_for_Access_Control.pdf`).
Verified as the genuine 29-page extended version (first page carries the correct title,
all four correct author names/affiliations, and the note "This is an extended version of a
paper presented at the Crypto '91 conference, August 1991").

- Archive path: `/Users/brettreynolds/projects/LLM-CLI-projects/literature/abadi1993calculus.pdf`
- SHA-256: `04b16c6305d400d0b802d4c2ec13e101de6a3780ebb25d02bd8510b9afb29827`

---

### 2. Lampson, Abadi, Burrows & Wobber (1992), "Authentication in Distributed Systems: Theory and Practice"

**Citation (Crossref-verified):**
Lampson, B., Abadi, M., Burrows, M., & Wobber, E. (1992). Authentication in distributed
systems: Theory and practice. *ACM Transactions on Computer Systems*, 10(4), 265–310.
DOI: 10.1145/138873.138874

Portfolio status: **not previously held.**

Acquired: free copy hosted for a graduate systems course at UT Austin
(`https://www.cs.utexas.edu/~witchel/380L/papers/lampson92tocs-auth-distributed.pdf`), which
is a straight PDF of the DEC SRC/ACM paper (Acrobat Distiller output, 1996). Verified as the
genuine 47-page paper: first page carries the correct title, all four correct authors, and
the "speaks for" abstract.

- Archive path: `/Users/brettreynolds/projects/LLM-CLI-projects/literature/lampson1992authentication.pdf`
- SHA-256: `694d90263c28275d760cf769eec99658c56bc57daa15a282fb3e90751e7e6711`

---

### 3. SPKI/SDSI — Ellison et al., RFC 2693 "SPKI Certificate Theory" (1999)

**Citation (Crossref-verified):**
Ellison, C., Frantz, B., Lampson, B., Rivest, R., Thomas, B., & Ylonen, T. (1999). *SPKI
Certificate Theory*. RFC 2693, IETF. DOI: 10.17487/RFC2693.
URL: https://www.rfc-editor.org/rfc/rfc2693

Portfolio status: **not previously held.**

Acquired directly from the RFC Editor (`https://www.rfc-editor.org/rfc/rfc2693.txt`), the
canonical publication form for an RFC. Verified complete: 43 pages of the standard RFC text
format, correct title/authors on the first page, ending in the standard IETF/Internet Society
copyright boilerplate. (Note: rfc-editor.org's PDF-rendering mirror for this specific RFC
returned 404 — `rfc2693.txt.pdf` does not exist there — so the archived copy is the plain-text
form, which is the RFC's authoritative format regardless.)

Rivest & Lampson's separate SDSI note ("SDSI — A Simple Distributed Security Infrastructure")
was **not separately pursued**: RFC 2693 is the SPKI/SDSI merger document and is the standard
citation target for "SPKI/SDSI" in the security literature; the task specification listed it
as the primary item. If Brett wants the standalone 1996 SDSI white paper as well (it circulates
as an MIT LCS technical report / web page, not a numbered RFC or DOI-bearing publication),
say so and it can be located separately.

- Archive path: `/Users/brettreynolds/projects/LLM-CLI-projects/literature/ellison1999spki.txt`
- SHA-256: `6822d668195c3d9b391f0c4f2b023341ba0e5a72e59d63c366a520de42c99098`

---

### 4. Delegation Logic — Li, Grosof & Feigenbaum (2003)

**Citation (Crossref-verified):**
Li, N., Grosof, B. N., & Feigenbaum, J. (2003). Delegation logic: A logic-based approach to
distributed authorization. *ACM Transactions on Information and System Security*, 6(1),
128–171. DOI: 10.1145/605434.605438

Portfolio status: **not previously held.**

Acquired: Ninghui Li's own author copy, hosted at his Stanford crypto-group page
(`https://crypto.stanford.edu/~ninghui/papers/dl_tissec03.pdf`). Verified as the genuine
42-page paper: correct title, all three correct authors and affiliations (Stanford, MIT,
Yale, matching their 2003 affiliations), correct abstract on trust-management/D1LP.

- Archive path: `/Users/brettreynolds/projects/LLM-CLI-projects/literature/li2003delegationlogic.pdf`
- SHA-256: `e046b9462d50ebe8a5dcf278d19ad36ecd3ef3be09ac71f1a793636fc4b025f5`

---

### 5. SecPAL — Becker, Fournet & Gordon (2010)

**Citation (Crossref-verified):**
Becker, M. Y., Fournet, C., & Gordon, A. D. (2010). SecPAL: Design and semantics of a
decentralized authorization language. *Journal of Computer Security*, 18(4), 619–665.
DOI: 10.3233/JCS-2009-0364

Portfolio status: **not previously held.** As flagged in the task brief, this is especially
important because *Journal of Computer Security* (IOS Press) is exactly the kind of venue
this manuscript targets — it's a directly comparable precedent, not just background theory.

Acquired: the full journal-length author copy from Microsoft Research's own site
(`https://www.microsoft.com/en-us/research/wp-content/uploads/2010/01/jcs-final.pdf`,
filename literally "jcs-final.pdf"). First attempt via `curl` with a generic user-agent was
served an HTML interstitial rather than the PDF; a normal browser-style user-agent string
retrieved the real file (confirmed independently via the Wayback Machine's snapshot of the
same URL returning `content-type: application/pdf`). Verified as the genuine 59-page full
journal version: correct "SecPAL: Design and Semantics..." title (matching the JCS title,
not the shorter 2006 PLAS workshop precursor title "Design and Semantics of a Decentralized
Authorization Language" without the "SecPAL:" prefix, which was also found and discarded
as the wrong, shorter version), correct authors/affiliation (Microsoft Research Cambridge).

- Archive path: `/Users/brettreynolds/projects/LLM-CLI-projects/literature/becker2010secpal.pdf`
- SHA-256: `fee113c49325bf27e9f28b8f0381443ddffb23aad02ca2b16c4d5aa17222c1ad`

---

### 6. UCON / usage control — Park & Sandhu (2004)

**Citation (Crossref-verified):**
Park, J., & Sandhu, R. (2004). The UCON_ABC usage control model. *ACM Transactions on
Information and System Security*, 7(1), 128–174. DOI: 10.1145/984334.984339

Portfolio status: **not previously held.**

Acquired: free author copy from Ravi Sandhu's own site
(`https://profsandhu.com/journals/tissec/ucon-abc.pdf`). Verified as the genuine 47-page
paper: correct title (rendered "The UCON_ABC Usage Control Model" in the PDF text layer),
correct authors and affiliations (George Mason University; NSD Security and George Mason),
correct abstract on Authorizations/oBligations/Conditions.

Sandhu & Park's other closely related UCON papers (e.g. the earlier position paper, or the
2005 formal-model TISSEC paper with Zhang/Parisi-Presicce) were **not** separately pursued —
the task named this specific paper as the UCON canonical citation. Flag if a broader UCON
citation set is wanted.

- Archive path: `/Users/brettreynolds/projects/LLM-CLI-projects/literature/park2004ucon.pdf`
- SHA-256: `af3c4e8af37e2278886d3d4b8acb618db241692ef2d0b919fe70c5f89a0dedcd`

---

### 7. XACML — OASIS eXtensible Access Control Markup Language, Version 3.0

**Citation:**
OASIS eXtensible Access Control Markup Language (XACML) TC. (2013). *eXtensible Access
Control Markup Language (XACML) Version 3.0*. OASIS Standard, 22 January 2013.
URL: http://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.pdf
(This is a standards document, not a journal article — it carries no DOI; the URL above,
taken from the specification's own title page as its authoritative URI, is the standard
citation target.)

Portfolio status: **not previously held as a standalone document.** (Only referenced
in passing, with this exact URL, inside the already-held `south2025authenticated.md`.)

Acquired directly from OASIS (`https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.pdf`).
Verified as the genuine, complete 154-page OASIS Standard: PDF metadata title field reads
"eXtensible Access Control Markup Language (XACML) Version 3.0", author field "OASIS
eXtensible Access Control Markup Language (XACML) TC", and the first page carries the full
correct front matter (specification URIs, TC chairs, editor, standard-track history).

- Archive path: `/Users/brettreynolds/projects/LLM-CLI-projects/literature/oasis2013xacml.pdf`
- SHA-256: `516743fc1c99d435744871f080b0f95f88d9679ee03388aab30e3808f013a2dd`

---

## Summary table

| # | Work | DOI/URL | Portfolio status before | Archive path | SHA-256 |
|---|---|---|---|---|---|
| 1 | Abadi, Burrows, Lampson & Plotkin 1993 (ABLP) | 10.1145/155183.155225 | absent | `literature/abadi1993calculus.pdf` | `04b16c63...29827` |
| 2 | Lampson, Abadi, Burrows & Wobber 1992 | 10.1145/138873.138874 | absent | `literature/lampson1992authentication.pdf` | `694d9026...e7e6711` |
| 3 | Ellison et al. 1999, RFC 2693 (SPKI) | 10.17487/RFC2693 | absent | `literature/ellison1999spki.txt` | `6822d668...c99098` |
| 4 | Li, Grosof & Feigenbaum 2003 (Delegation Logic) | 10.1145/605434.605438 | absent | `literature/li2003delegationlogic.pdf` | `e046b946...025f5` |
| 5 | Becker, Fournet & Gordon 2010 (SecPAL) | 10.3233/JCS-2009-0364 | absent | `literature/becker2010secpal.pdf` | `fee113c4...c1ad` |
| 6 | Park & Sandhu 2004 (UCON_ABC) | 10.1145/984334.984339 | absent | `literature/park2004ucon.pdf` | `af3c4e8a...dedcd` |
| 7 | OASIS XACML v3.0 (2013) | docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.pdf | absent standalone | `literature/oasis2013xacml.pdf` | `516743fc...3a2dd` |

## What was NOT done (out of scope per instructions)

- No bib entries were written to `references-local.bib` or any central bib.
- No `.tex` files in the project were edited.
- No `notes/source-verification.md` or `notes/cited-source-local-archive.md` entries were
  added — that recording step belongs to whoever integrates these citations into the
  manuscript, per the project's own Source Discipline section.

## Follow-up items for whoever integrates these

- The standalone Rivest & Lampson SDSI whitepaper (pre-RFC-2693 merger) and the broader
  Sandhu/Park UCON paper family were named as "also relevant" in the brief but not
  separately fetched, since RFC 2693 and the 2004 TISSEC paper are the standard citation
  anchors. Say the word if the broader sets are wanted too.
- `/push-bib` workflow and `references-local.bib` additions still need to happen inside the
  project before these can actually be cited in the manuscript; this pass only secured the
  primary-source files and citation metadata.
