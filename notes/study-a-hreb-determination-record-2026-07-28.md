# Study A HREB determination record

**Received:** 2026-07-28 at 17:42:18 UTC, from REB Coordinator Suzan Abdelkarim.
**Status:** partial determination received; one of the two scope questions answered, the other not asked and not addressed.

## What HREB determined

HREB determined that the proposed research does not require research ethics
review, because it does not involve conducting research with human
participants. The determination is grounded in the TCPS 2 Article 2.1
application notes: participants are individuals whose data, biological
materials, or responses to the researcher's interventions, stimuli, or
questions are relevant to answering the research question. HREB stated it is
satisfied that the design as described would not require the six experts to
provide their own data or respond to interventions from the researcher — i.e.,
the experts are evaluators of fixed AI-output objects, not a studied
population.

## What remains open

The sent inquiry (see `study-a-hreb-inquiry-record-2026-07-16.md`) asked only
whether the experts count as human participants. It did not separately ask
whether the off-duty, unfunded, no-Humber-resource project falls within
Humber's jurisdiction or auspices at all — the second question the pre-send
drafting record (`study-a-humber-scope-inquiry-2026-07-16.md`) identified as
independently necessary. HREB's reply answers only the first question. It
does not state that the project is outside Humber's jurisdiction, nor that
jurisdiction is moot; it simply doesn't address the point. Per the inquiry
record's own stated criterion, a response that does not make the jurisdiction
question inapplicable requires a follow-up before the collection-ready gate
can be treated as passed on the HREB dimension.

One soft signal worth weighing, not treating as a formal answer: HREB engaged
with and ruled on the substance from a Humber-account inquiry describing a
Humber-affiliated researcher's project, rather than declining to comment as
out of scope. That is consistent with HREB accepting jurisdiction, but it is
an inference from institutional behavior, not a written jurisdictional
determination, and should not be recorded as one.

## Private evidence

The byte-exact received-message export is stored at the ignored path
`private/study-a/production/evidence/hreb-scope-determination-received-2026-07-28.eml`.
Its SHA-256 digest is
`f5b3b04a17150763185c09e27ef946cc77b3f926c4740ef9fd16476855de1837`.
The export is mode `0600`. The message body, sender contact details, and
institutional signature block are not reproduced in this public record.

## Decision (2026-07-28, Brett)

No jurisdiction follow-up will be sent. Brett's rationale: as a Humber
Polytechnic employee, he considers himself never "off duty" for ethics
purposes — Humber's REB jurisdiction over his research applies regardless of
funding status or an "independent project" framing. This is not a new
position adopted to close this gap; it matches his own annotation on the
project posture question in `study-a-collection-launch-decisions-2026-07-16.md`
§1 ("as an employee at Humber, I can't do research with human participants
without REB approval, even with such a statement"). The jurisdiction question
was therefore never a live doubt on Brett's side — it dropped out of the sent
email by omission, not because the answer was unclear. HREB's participant-
status determination is treated as the operative answer: on his own view
jurisdiction was never in question, and HREB's engagement with the substance
is consistent with that.

**This resolves the HREB/ethics dimension of the collection gate. It does not
by itself make Study A collection-ready** — the other steps in
`study-a-collection-launch-decisions-2026-07-16.md` §8 (finalize the eight
evaluator-facing materials, build the operational config, complete the two
timing runs, populate and attest the assignment registry, regenerate and
verify the freeze stamp, get explicit authorization for the tag name, then tag
and run `make study-a-collection-ready`) are unaffected by this decision and
remain outstanding.
