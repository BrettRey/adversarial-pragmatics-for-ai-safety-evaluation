# Draft Statement: Private Interaction Histories as a Discovery Corpus

**Status:** active private-discovery boundary. On 16 July 2026, Brett explicitly
authorized a local Codex/Claude Code corpus build. The active derivative is a
privacy-minimized, pseudonymized v2 corpus with a separate owner-only linkage
vault. The original histories and vault remain ignored and local; no episode
has been adjudicated, released, or added to Study A. The deleted raw-derivative
starting state and the v2 transformation are recorded in
`notes/naturalistic-corpus-privatization-record.md`.

Private ChatGPT, Codex, and Claude Code histories may be useful for discovering
candidate cases in which a model's interpretation required repair. They are not
a representative corpus, a benchmark, a sample of ordinary users, or evidence
that an original request had only one reasonable interpretation.

The discovery unit is a bounded local episode. The expanded corpus also admits
positive-uptake episodes when success evidence coincides with high pragmatic
load:

```text
preceding context -> target prompt -> model interpretation or action -> repair turn
```

A repair turn may show Brett's intended interpretation after the fact. It does
not, by itself, establish model error. Candidate review must distinguish: clear
model misinterpretation; clarification required; reasonable competing readings;
relevant context lost; user changed the request; non-pragmatic capability or
factual error; and insufficient evidence.

The original histories and exact source linkage remain under separate ignored
`private/` boundaries. The candidate index contains no conversation text or
direct provenance; the review layer contains only bounded, sanitized excerpts
and generalized tool metadata. The local miner uses lexical retrieval signals
and bounded windows only; it makes no external API call and does not upload
text. Signals such as "I mean," "that is not what I asked," "resume," or "the
other one" are ranking cues, not annotations or gold labels.

No raw episode should be released, cited, or converted directly into a
benchmark item. A public item must be a synthetic or thoroughly sanitized
controlled contrast, with a separate transformation record and privacy review.
Candidate counts are retrieval diagnostics, not failure/success rates or a
Codex--Claude comparison.
