# Naturalistic Corpus Privatization Record

## Outcome and boundary

On 2026-07-16, the naturalistic Codex/Claude discovery derivative was replaced with
version 2: a privacy-minimized, pseudonymized internal corpus plus a separate owner-only
linkage vault. This is called _privatization_ here as shorthand for data minimization,
pseudonymization, access separation, and inert rendering. It is not anonymization and does
not authorize publication, quotation, sharing, or use as Study A data.

The original local chat histories were not altered. They remain private source records.
The restricted vault also remains identifying by design because it contains the linkage
needed to trace a keyed candidate back to its source. Only the v2 discovery derivative is
described as privacy-minimized.

## Recorded starting state

The principal v1 derivative contained 480 sessions, 482 candidates, and 300 review rows in
12 files totalling 66,627,455 bytes. Its exact pre-deletion file inventory—relative names,
SHA-256 hashes, byte sizes, and modes—has digest
`6987a8bbdf5d47f70199af05adec9c4fc8056715473f9420d8e5e1e04a4bc61e`.
Immediately before deletion, that recorded inventory matched the directory byte-for-byte;
there were no symlinks.

The aggregate scanner found 113,426 direct-identifier-pattern matches across 32,443
affected values and 494 active-markup/network-primitive matches across 113 affected values.
These are conservative pattern counts, not counts of distinct people or confirmed
identifiers. The scanner returned zero matches to its then-configured high-confidence
secret patterns; this was a pattern result, not a test of whether any credential was live.
A deterministic, stratified 60-row contextual audit found the following overlapping row
counts:

| V1 contextual risk | Rows |
|---|---:|
| Absolute or home path | 54 |
| Owner direct identifier | 12 |
| Third-party personal data | 9 |
| Employer identity or context | 8 |
| Reidentifying combination | 35 |
| Unpublished manuscript or research material | 54 |
| Source-code or data material | 57 |
| Correspondence-related material | 29 |

Nine sampled rows required exclusion or reconstruction from an abstract event; 51 required
contextual rewriting and trace minimization. None was safe through simple token redaction.

The v1 reviewer was structurally unsafe. HTML parsing found 30 script elements, 32 closing
script sequences, 45 external-resource-like attributes, 37 event-handler attributes, and no
CSP-authorized script. A separate literal scan counted 35 opening script tags, 32 closing
tags, 50 external-resource-like attributes, and 11 browser-storage markers. The difference
between the script/resource counts reflects the two stated counting methods.

The cleanup scan also found a second, older naturalistic derivative. It contained nine files
totalling 8,841,061 bytes, all mode `0644`, including a byte-identical derivative pair. Its
aggregate audit found 16,174 direct-identifier-pattern matches across 5,441 affected values
and 123 active-markup matches across three affected values. It returned zero matches to the
scanner's then-configured high-confidence secret patterns. Its inventory and hashes were
recorded before it too was deleted.

## Transformation protocol

The v2 build used the sampling window 2026-01-01 through 2026-07-15 and made no external API
calls. A 60-minute source-age floor excluded 22 recently modified files before session-mode
classification, reducing the risk that active or still-changing histories entered the derivative.
The initial build recorded no whole-session exceptions, but its then-current JSONL reader could
skip malformed lines and replace invalid UTF-8. That field therefore does not establish zero
line-level parse errors across all 479 parsed sessions. After the reader was made strict, final
validation re-read all 683,556 nonblank records in the 155 candidate-bearing source files as
UTF-8 JSON objects (130 Codex files/644,703 objects; 25 Claude files/38,853 objects), found no
blank lines or parse failures, and rechecked each retained source fingerprint after parsing.
Candidate-free sessions have no retained source-path inventory and cannot be retrospectively
given the same line-level certification.

The builder then applied these transformations:

1. Candidate, session, and source references were replaced with HMAC-SHA-256 pseudonyms
   generated with a random 32-byte key. The key is stored only in the restricted vault;
   unsalted path hashes are not used.
2. The candidate index was made text-free. It retains only keyed references, coarse month,
   source/mode class, retrieval class and scores, canonical evidence labels, generalized
   tool metadata, and privacy/reconstruction status.
3. Exact timestamps, model and software identifiers, project and branch metadata, prompt
   provenance, raw paths, session/node IDs, governing context, full compaction summaries,
   tool arguments, tool output, file contents, quoted documents, correspondence bodies, and
   attachment text were removed from the review layer.
4. Tool traces were reduced to generalized action classes, bounded event counts, and
   compaction booleans. No tool-result text was retained.
5. Review text was limited to four direct conversational fields plus, only where retrieval
   required it, at most two preceding turns. Direct fields are capped at 1,600 characters,
   each preceding role at 900, and the whole episode at 7,000.
6. Deterministic rules replaced paths, email addresses, URLs, handles, phone/address forms,
   dates, file names, long identifiers, and person/organization patterns with episode-local
   typed placeholders. Any credential context, correspondence header, active content, raw
   tool marker, large pasted material, or residual forbidden pattern caused the entire field
   to be empty and marked withheld. If either role in preceding context failed, the complete
   context window was removed.
7. Exact raw-path/session/line linkage and source fingerprints were moved to the owner-only
   vault. The reviewer never loads that vault.
8. The reviewer payload was encoded as inert base64 in a template element. Rendering uses
   text nodes, one nonce-authorized script, one nonce-authorized style, a restrictive CSP,
   no network/resource attributes, no event-handler attributes, and no browser storage.
   Decisions stay in memory. The page can display decision-only JSON as inert text, but it has
   no download, clipboard, file-write, or other automatic export path; any deliberate save must
   be performed manually inside the restricted private boundary.

### Exact automatic action counts

Counts below are field-level events and can exceed the number of review rows.

| Automatic action | Count |
|---|---:|
| Acronym replacement | 1,531 |
| Large pasted material withheld | 736 |
| Local path replacement | 557 |
| File-name replacement | 332 |
| Person-pattern replacement | 290 |
| Owner-identifier replacement | 257 |
| Proper-token replacement | 229 |
| Proper-name replacement | 218 |
| Code-block replacement | 34 |
| Markup replacement | 28 |
| Long-identifier replacement | 28 |
| Private-context replacement | 28 |
| URL replacement | 25 |
| Credential-context field withheld | 13 |
| Organization replacement | 9 |
| Correspondence field withheld | 7 |
| Exact-date replacement | 4 |
| Handle replacement | 2 |
| Phone replacement | 2 |
| Email replacement | 1 |
| Residual-risk field withheld | 1 |
| Tool events reduced to metadata | 16,420 |

Every review row omits governing context, prompt provenance, raw tool text, and full
compaction summaries. In addition, preceding context was withheld in 233 rows; visible model
response in 169; immediate model response in 167; triggering request in 59; and user follow-up
in 34. Counts overlap.

## Final v2 state

The final build parsed 479 primary sessions. Of these, 155 candidate-bearing sessions/source
files produced 477 keyed candidates:

| Source and retrieval class | Candidates |
|---|---:|
| Codex likely pragmatic failure | 106 |
| Codex surprising-success candidate | 332 |
| Claude likely pragmatic failure | 11 |
| Claude surprising-success candidate | 28 |

The selected review layer contains 300 rows and 331,984 retained text characters; the largest
episode is 4,433 characters. Automatic minimization left 28 rows internally reviewable as
stored. The other 272 are marked `manual_controlled_reconstruction_required`.

The final inventory contains 12 hashed corpus files plus the self-referential privatization
audit, and three restricted-vault files. The canonical corpus-inventory digest is
`b19a23c0ab49eda96134813b80c5ef60f82e4894a920f16f8dfb824adf0ec8a7`;
the restricted-inventory digest is
`316c0a915166affaabd22c19f0b1d9fdc74007e5a6a8e9db672206ccecd20424`.
Each is SHA-256 over the compact, key-sorted JSON serialization of the corresponding records,
sorted by `relative_path`; the records contain relative name, file SHA-256, byte size, and mode.
The digests do not disclose raw source fingerprints.

Strict validation found:

- zero prohibited residual-identifier, credential, active-markup, or network-primitive
  pattern matches, raw tool text, or direct provenance in the candidate index, review corpus,
  or reviewer payload;
- 477 restricted linkage rows and 155 restricted source-fingerprint rows, with keyed
  references reproducing correctly;
- one inert reviewer payload decoding to 300 rows, one authorized script, one authorized
  style, and zero external attributes, event handlers, or decode failures;
- owner-only modes (`0700` directories and `0600` files), zero symlinks, zero wrong-owner
  files, zero byte-identical derivative groups, and zero hardlink groups;
- all 13 corpus files and all three vault files are ignored and untracked, and no decision
  file exists in the project.

The combined corpus-plus-vault aggregate scanner reports 638 conservative identifier-pattern
matches: 632 expected raw paths confined to the two restricted linkage tables and six
title-case/proper-name-pattern false positives in fixed explanatory prose. The candidate
index, review corpus, and decoded reviewer payload each have zero such hits. The scanner also
reports zero matches to pattern-policy-v2 high-confidence secret patterns, including Hugging
Face token syntax, and zero active/network primitives. It does not test credential liveness.

## Contextual residual-risk audit

A second deterministic 60-row audit ranked keyed pseudonyms by SHA-256 within source/class
strata. The sorted sample-manifest digest is
`f6bf60e550a429e09458c426504797a804a8b9c880a272f7f712c633f884156b`.
No sampled row retained a direct identifier or third-party PII, and no authentication
material was identified in the sampled retained text. The overlapping contextual counts were:

| V2 contextual signal | Rows |
|---|---:|
| Generic employer/institution context | 1 |
| Conservative identifying combination | 16 |
| Unpublished research context | 27 |
| Source/data/code context | 27 |
| Correspondence context | 9 |
| Generic access/security context | 6 |

Fifty-three sampled rows were marked for manual controlled reconstruction and seven passed
automatic minimization for internal review. None is public-safe without a new controlled
reconstruction. The 16-row combination count is a conservative reidentification warning, not
confirmed PII.

## Deletion and residue verification

After the finalized v2 corpus passed both the root validator and an independent validator
run, the recorded 12-file v1 derivative and the recorded nine-file older derivative were
deleted. A post-deletion scan found zero legacy naturalistic episode files and zero unsafe
naturalistic reviewer files under `private/discovery/`. V2 then passed strict validation
again. The original local histories and the three-file restricted vault were not deleted.

The aggregate v1, older-derivative, and contextual audit reports remain inside the ignored v2
corpus. They contain counts, bounded field labels, opaque file references, modes, sizes, and
hashes, but no excerpts or matched values.

## Reproducibility record

The worktree was based on Git commit
`b8d6086a2543f4f25a42dbb532d0fddb0d78df8e`. Because the remediation was not yet committed,
the controlling source hashes are:

| Artifact | SHA-256 |
|---|---|
| Corpus payload generation builder | `a4665bc9127d93b31091ccf234fa5803a2a1efcf80dfe6d2a878f45f156a3db5` |
| Post-generation hardened corpus builder | `2585328d449d0999ee882e4875beb1e5f9acea378cddf289d2d479cd38d44088` |
| Final reviewer builder | `bb0c69b62d2a32311ba52cf87f1458bcff1a7892a020c16b3cd2c8e11e5d6d66` |
| Final aggregate auditor/finalizer | `fe86f19c2cf14616846889757b675c799c159002782e150a1cbf5dd00316b77c` |
| Final fail-closed validator | `24c2296e79117a6c428f014b4ae79fbbd56b06feace573e13490f16e43b15cf2` |
| Principal-v1 aggregate audit | `60f79823d563eb7c8f51313c9ef29fea5298f33b45ccc60c2b45987bbbcb73e7` |
| Older-derivative aggregate audit | `16f2695383c27d8ffecb9498f9ee6a9723165070333c4db174c4707ac14478a4` |
| V2 contextual audit | `4eacf5b7aa1cff136883f48ab6ffa9fd57fd8ddce9e06a5803b8a49539d2ccf9` |
| Final privatization audit | `e38a2c30a0241a98722761303bccb53504c46d8f45f93682416f8f237f07cfb5` |

The candidate-index and review-corpus payloads were generated with the first builder hash in
the table. They were not regenerated after the legacy derivatives were deleted. The hardened
builder is the controlling implementation for any future rebuild; it adds strict UTF-8/object-
only JSONL parsing, hashes the exact bytes consumed during discovery and parsing, requires the
discovery digest/state, parser digest, post-parse fingerprint, and final fingerprint to agree,
enforces fixed metadata vocabularies and legacy-audit schemas, and uses fail-closed output and
vault boundaries. The final reviewer and aggregate audit were regenerated with their final
hashes, and the final validator checked the retained payload against the unchanged source
fingerprints and strict source parse described above.

The machine-readable privatization audit was generated at
`2026-07-16T23:43:20.405326+00:00` and last finalized at
`2026-07-17T00:38:28.582022+00:00`. The final audit intentionally excludes its own bytes from
the hashed inventory to avoid a self-referential digest.

Post-finalization verification compiled all four workflow scripts; passed 45 focused tests
(ten builder, ten reviewer, seven auditor, and eighteen validator tests); passed the complete
synthetic build/reviewer/auditor/validator workflow; passed the real-v2 validator; and passed
the repository privacy, public-artifact, benchmark, and whitespace checks. The independent
storage audit separately reproduced the exact allowlists, inventories, modes, ownership,
ignore status, renderer restrictions, and absence of legacy residue.

## Limitations and permitted use

Deterministic pattern checks can produce both false positives and false negatives, and the
contextual audit covers a reproducible sample rather than every retained episode. HMAC
pseudonyms are linkable by anyone who obtains the restricted key and linkage tables. The
original histories, vault, and internal excerpts therefore remain sensitive local data.
The original payload-generation builder did not cryptographically bind the exact bytes consumed
while parsing to the fingerprint written later. The unchanged recorded fingerprints and later
strict parse provide strong current-integrity evidence but cannot exclude a source change in
that historical interval; exact byte-level replay of the initial candidate extraction is therefore
not claimed. The hardened future-build implementation closes this interval with parsed-byte,
discovery, post-parse, and final digest/state equality.
Reviewer execution was checked through static parsing, hostile rendering fixtures, and
structural CSP tests. In-app browser automation was unavailable and local headless-browser
attempts yielded no runtime result, so this record does not claim a live-browser execution
test.

V2 may be used for private candidate triage and for deciding which cases merit a newly written,
benign controlled reconstruction. It must not be described as anonymous, representative,
independently adjudicated, publication-ready, or covered by the pending Study A HREB inquiry.
