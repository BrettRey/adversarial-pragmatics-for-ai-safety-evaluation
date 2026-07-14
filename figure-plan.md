# Figure Plan: Delegation Assurance
<!-- SUMMARY: Figure menu for the delegation-assurance paper; Brett kept #1 and #3, both built and audited 2026-07-13 · status: built · updated: 2026-07-13 -->

Menu proposed 2026-07-13 in response to Brett's question whether a causal-normative
graph (in the style of Effective without warrant's typed-edge figures) belongs in
the paper. Current state: one TikZ figure (delegation-assurance stack) and five
tables. Build survivors in TikZ matching the stack figure's idiom (box styles,
`black!55` strokes, `linkmaroon` accent); audit with `/check-chart-style`.

Design constraint for any typed-edge graph: two edge types only, causal and
authority. Don't import EwW's full node/edge typology (status, recognition,
response, correlative, conferral); a security reader needs the dissociation, not
the ontology.

| # | Fig | Kind | Makes clearer | Type | Source | Keep |
|---|-----|------|---------------|------|--------|------|
| 1 | Authority minimal pair: two panels, identical causal path, one differing authority edge; verdict labels under each panel (attribution flags / matrix licenses; attribution passes / matrix blocks) | conceptual | what the comparative test varies vs holds fixed; where causal attribution and authority status disagree | TikZ typed-edge graph, small multiples | conceptual | must |
| 2 | Verdict-dissociation 2×2: attribution (flag/pass) × authority (licensed/blocked), four quadrants populated (classic injection; ordinary licensed call; the two dissociation cases) | conceptual | the two verdicts are independent axes | TikZ quadrant diagram | conceptual | nice |
| 3 | Compositional authority path: constraint preserved vs dropped at a summarization hop between coordinator and specialist | conceptual | monotonic authority as a path property (§ compositional) | TikZ two-panel graph | conceptual | nice |
| 4 | Recognition gap: classical permission-to-execution wiring vs LLM agent with interposed uptake step | conceptual | why the language-mediated middle layer exists (intro argument) | TikZ two-panel schematic | conceptual | stretch: intro already has the stack figure |
| 5 | Procurement trace as annotated authority graph | conceptual | where each evidence record attaches along the action path | TikZ annotated graph | conceptual | stretch: overlaps #1 and the trace table |
| 6 | Comparative-test outcome matrix: three pair families × five outcome dimensions (attempted action, execution, authorization verdict, audit attribution, defence) × two accounts | data | whether the accounts actually diverge when run | dot matrix or heatmap | `DATA NEEDED`: executable delegation-assurance harness, sequenced after Study A | stretch |

Outcome (2026-07-13): Brett kept the recommended pair. #1 is built as
`fig:authority-minimal-pair` in `sections-delegation/03-framework.tex` and #3 as
`fig:authority-path-pair` in `sections-delegation/07-compositional-delegation.tex`;
both pass `/check-chart-style`. #2, #4, and #5 are cut. #6 stays parked until the
executable harness exists (sequenced after Study A).
