# Synthetic Fixtures

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
