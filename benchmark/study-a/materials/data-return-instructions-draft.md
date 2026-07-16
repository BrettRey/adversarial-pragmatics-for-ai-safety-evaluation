# Study A Data-Return Instructions (Draft)

**Draft only. Fill in the access-controlled return channel, collection-close
cutoff, and contact route only after Humber supplies a written scope
determination and any required data-handling conditions. This procedure claims
neither institutional approval nor an exemption.**

## Investigator Setup Before Collection

1. Select the access-controlled return channel permitted by the final written
   scope determination and data plan. Record its description and access control
   in the private operational configuration.
2. Limit return-channel and local-file access to the investigator.
3. Prepare an ignored local directory for returned JSON files and a separate
   private contact/identity mapping and assignment registry.
4. State the collection-close and analysis-start cutoff in the final evaluator
   information note.
5. Validate that every globally unique rater ID is assigned to exactly one
   person, one role, and the current package ID, and that the two role pools are
   person-disjoint. The registry attestation detects later file changes; the
   investigator's roster check, not the attestation alone, establishes that the
   real people are disjoint.

## Evaluator Return Instructions

1. Use only the role-specific ZIP assigned to you. Complete one 18-row block
   and download its JSON file without editing it.
2. Return only that JSON file through **[approved Study A return channel]**.
3. Identify the return as `Study A / [rater ID] / [block ID]` using the method
   stated in the final channel-specific instructions.
4. Do not put a real name, employer, institution, private task details, or
   unrelated material in the JSON file or accompanying message.
5. Return one completed block at a time. The investigator will acknowledge
   receipt using the study rater ID.

## Investigator Handling After Receipt

1. Confirm that the attachment is a JSON response file and that the filename
   contains only the assigned rater ID and block ID.
2. Save it unchanged under the ignored local study directory.
3. Before ingestion, verify the embedded package ID, role, and rater ID against
   the private assignment registry. Reject stale, unregistered, wrong-role, or
   duplicate-identifier submissions rather than repairing them by hand. The
   separate identity-side roster review, not ingestion, establishes whether the
   identifiers denote distinct eligible people.
4. Record receipt using the study rater ID, not a public project file.
5. Remove the returned file from the transfer channel after the unchanged local
   copy and receipt record are confirmed, subject to the final retention rule.
6. Do not forward the returned file or merge it with identity/contact records.

## If Something Goes Wrong

If an evaluator sends private material, a real interaction history, or a
misdirected file, do not ingest it. Contact the evaluator through the approved
contact route, remove the material from the study working directory, and record
the handling action privately. If a withdrawal request arrives before the stated
cutoff, follow `withdrawal-procedure-draft.md`.

## Rationale

The design minimizes collection, keeps real identity/contact records separate
from ratings, limits access, and applies safeguards proportionate to the small,
pseudonymous, benign study record. It does not assert that a particular privacy
statute applies to this project. For the general proportionality
principle, see the [Office of the Privacy Commissioner of Canada safeguards
guidance](https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/p_principle/principles/p_safeguards/).
