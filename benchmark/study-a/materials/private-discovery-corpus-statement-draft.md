# Draft Statement: Private Interaction Histories as a Discovery Corpus

**Status:** draft only. No private history has been imported through this
workflow.

Private ChatGPT, Codex, and Claude Code histories may be useful for discovering
candidate cases in which a model's interpretation required repair. They are not
a representative corpus, a benchmark, a sample of ordinary users, or evidence
that an original request had only one reasonable interpretation.

The discovery unit is a bounded local episode:

```text
preceding context -> target prompt -> model interpretation or action -> repair turn
```

A repair turn may show Brett's intended interpretation after the fact. It does
not, by itself, establish model error. Candidate review must distinguish: clear
model misinterpretation; clarification required; reasonable competing readings;
relevant context lost; user changed the request; non-pragmatic capability or
factual error; and insufficient evidence.

Raw exports, provenance maps, candidate episodes, and reviewer decisions remain
under ignored `private/` paths. The local miner uses lexical retrieval signals
and bounded windows only; it makes no external API call and does not upload
text. Signals such as "I mean," "that is not what I asked," "resume," or "the
other one" are ranking cues, not annotations or gold labels.

No raw episode should be released, cited, or converted directly into a
benchmark item. A public item must be a synthetic or thoroughly sanitized
controlled contrast, with a separate transformation record and privacy review.
