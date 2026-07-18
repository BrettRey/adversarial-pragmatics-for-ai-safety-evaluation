# Synthetic Fixtures

`naturalistic-corpus/` contains one synthetic primary session for each of the
Codex and Claude Code adapters, excluded subagent records for both sources, and
an excluded programmatic Claude SDK session. The Claude fixture also exercises
branch selection, repeated UUIDs, fragmented assistant messages, tool results,
file-history sidecars, meta/task-notification filtering, compaction, and
synthetic API-error suppression. The paired episodes exercise a likely
pragmatic failure and a surprising-success candidate without importing private
interaction history.

Files in this directory are fabricated solely to test local workflow code. They
are not pilot data, naturalistic corpus evidence, evaluator records, or
benchmark items. In particular, `synthetic-repair-history.jsonl` contains no
real user, organization, contact, file path, model output, or private history.

The normalized JSONL format used by the repair miner requires:

```json
{"conversation_id":"opaque-local-id","turn_index":1,"role":"user","content":"text"}
```

Optional fields are retained only in the original local input. The miner writes
an opaque episode ID and a private provenance index; it does not upload data or
call an external API.

`synthetic-study-a-self-pilot-response.json` is a fabricated single-block form
response used only to test the self-pilot timing summarizer. It contains no
rating labels or real pilot content.
