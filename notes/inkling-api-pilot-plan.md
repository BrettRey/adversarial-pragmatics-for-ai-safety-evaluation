# Inkling Exploratory API Pilot Plan

**Status: parked on 2026-07-16.** Brett clarified that the intended next steps
were the project steps discussed before the model-release tangent. No API-runner
implementation should proceed from this plan unless the model work is explicitly
resumed.

## Decision sought

Build a separate, provider-aware exploratory runner for Inkling through NVIDIA
NIM, verify it with offline contract tests, then run one public seed item after
an `NVIDIA_API_KEY` is available. Do not change the frozen three-model local
pilot or ingest Inkling into Study A.

## Why this is the next step

NVIDIA currently exposes `thinkingmachines/inkling` through a free,
OpenAI-compatible endpoint for research, evaluation, development, and testing.
The project currently has only an Ollama runner. A separate API path lets us
test a frontier open-weights model without weakening the provenance or fixed
matrix of the historical 54-row pilot.

## Load-bearing assumptions

| Assumption | What would falsify it | Test |
|---|---|---|
| NVIDIA will issue Brett a free Developer Program key with Inkling access. | No key can be generated, or the endpoint returns a persistent 402/403 for Inkling. | Generate a key, then make one minimal authenticated request. |
| Inkling implements the advertised OpenAI chat-completions contract. | The endpoint rejects the documented model ID/request fields or returns an incompatible response shape. | Exercise the exact request against a local mock first, then one live seed item. |
| The public seed benchmark is suitable for the free hosted endpoint. | An input contains private, confidential, evaluator-identifying, or sensitive material. | Restrict the runner to the tracked seed file by default and hard-deny project `private/` and Study A run paths. |
| Free trial capacity is enough for a bounded 18-item exploratory cohort. | Provider rate or token limits prevent a resumable run. | Implement retry/backoff and resume; test one item before considering all 18. |
| Adding Inkling as a new exploratory cohort will not contaminate Study A. | New output is merged into the 54-row source matrix or current manuscript summaries. | Use a distinct run prefix and output directory; leave all Study A scripts, manifests, and model defaults untouched. |

The unstated requirement behind every successful version is provenance: a row
must identify both the model and the serving provider. `Inkling` alone is not a
reproducible condition because NVIDIA, Tinker, and other hosts can use different
quantization, templates, defaults, or revisions.

## Implementation

### 1. Add a small tracked API-model registry

Create `benchmark/api-models.json` with a versioned entry for
`inkling-nvidia-nim`:

- provider: NVIDIA NIM;
- API style: OpenAI chat completions;
- model ID: `thinkingmachines/inkling`;
- base URL: `https://integrate.api.nvidia.com/v1`;
- key environment variable: `NVIDIA_API_KEY`;
- verified access class and date;
- public-benign-only data boundary;
- documented request defaults.

The registry will contain no secret values.

### 2. Add a separate API runner

Create `scripts/run_api_pilot.py` using only the Python standard library. It
will:

- validate and read the existing seed CSV;
- resolve a named model from `benchmark/api-models.json`;
- read the API key only from the declared environment variable;
- POST to `/chat/completions` with a single user message;
- support `--limit`, `--run-id`, `--resume`, timeouts, and bounded retries;
- preserve response text, reasoning content when returned, finish reason,
  token usage, timing, request settings, endpoint host, provider, and model ID;
- reuse the existing diagnostic intent without presenting heuristic flags as
  gold labels;
- never serialize request headers, bearer tokens, or environment values;
- refuse protected project paths and require an explicit external-transfer
  acknowledgement for any non-default input file.

Results will use `api-pilot-<timestamp>/` under the already ignored
`benchmark/results/` directory. They will not enter tracked summaries
automatically.

### 3. Add offline contract tests

Add a `unittest` test module with a temporary local HTTP server. Tests will
cover:

- correct endpoint path and OpenAI request shape;
- response extraction and result-bundle files;
- key redaction from every generated file;
- missing-key failure;
- retry/resume behaviour;
- protected-path rejection;
- registry validation.

No live provider call will be part of `make test`.

### 4. Add bounded commands and documentation

Add Make targets for an offline API-runner test and a one-item live Inkling
smoke test. Update the benchmark and result-bundle documentation to distinguish:

- the frozen local Ollama pilot;
- the exploratory hosted-provider cohort;
- raw ignored outputs versus intentionally reviewed summaries.

### 5. Live checkpoint

After Brett generates an NVIDIA key:

1. export it locally as `NVIDIA_API_KEY` without writing it into the repo;
2. run exactly one benign seed item;
3. inspect provider metadata, output parsing, finish reason, and token usage;
4. verify the key is absent from the entire worktree and result bundle;
5. decide whether the full separate 18-item Inkling run is scientifically
   useful before consuming the remaining free quota.

## Explicit non-goals

- No change to `PILOT_MODELS`, `DEFAULT_MODELS`, or the frozen Study A matrix.
- No modification of Study A manifests, comparators, analysis, or paper claims.
- No API key creation, storage, or transmission by repository code beyond the
  authenticated request header.
- No private evaluator returns or interaction histories sent to NVIDIA.
- No full 18-item run before the one-item checkpoint is inspected.

## Verification gate

Implementation is complete only if all of the following pass:

```text
python3 -m unittest scripts/test_run_api_pilot.py
python3 scripts/validate_items.py benchmark/items/seed-items.csv
python3 scripts/check_private_boundaries.py
python3 scripts/check_pilot_integrity.py
git diff --check
```

The live smoke test is a separate credential-dependent gate.

---
comments:
  c1:
    body: no, I meant to refer to the steps we'd talked about before I brought up
      the new models. We'll just park the models for now
    by: user
    at: 2026-07-16T17:26:11.524Z
  c2:
    body: Understood. I have parked this plan and returned to the pre-model project sequence.
    by: Codex
    at: 2026-07-16T17:27:24.000Z
    re: c1
