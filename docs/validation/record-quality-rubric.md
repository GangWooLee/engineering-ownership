# Record quality rubric

Status: Current
Checked: 2026-07-29

How the engineering records in `docs/engineering/**` are measured. This document
is the standard; it does not contain scores. Results are recorded separately so
that a bad result cannot be fixed by quietly editing the standard that produced
it.

## Why three layers

Grading "is this well written" as one question makes every answer a judgement
call, and judgement is the expensive input. Splitting by what the question
actually needs keeps the cheap checks cheap:

| Layer | Question | Cost | Cadence |
| --- | --- | --- | --- |
| 1 — guards | Is a mechanical property violated? | zero | every commit |
| 2 — scored dimensions | Can a stranger use this record? | judge call | quarterly |
| 3 — reach | How many steps to the answer? | manual walk | quarterly |

Layer 1 answers questions with no interpretation in them. Layer 2 answers what
no counter can. Layer 3 measures the structure around the records rather than
the records themselves, which is why it is not folded into layer 2.

## The four rules every item obeys

Inherited from the skill-evaluation guards, which exist because this project's
first efficacy claim was retracted for breaking them.

1. **No private vocabulary.** An item a stranger cannot judge — "did it apply
   R0–R3 correctly?" — cannot appear in a rubric that claims to measure
   comprehensibility. Measuring understandability while requiring insider
   knowledge is self-contradictory.
2. **Silence never passes.** "Has no unexplained terms" is satisfied by an empty
   document. Every layer-2 expectation is phrased as *state* or *list*, so a
   response that says nothing scores nothing.
3. **Discrimination is required — of layer 2.** An item every record passes or
   fails is a constant, and a constant in a scored denominator dilutes the
   result. `eval-9`'s fourth expectation passed 0 of 8 times across every run
   ever recorded, holding 20% of that denominator fixed. That is the failure this
   rule prevents.
4. **No aggregation.** A mean of 0.72 cannot distinguish "everything is 0.72"
   from "half are 1.0 and half are 0.44". Results are reported per record and
   per dimension; a mean, if given at all, comes after and never alone.

**Rule 3 applies to layer 2 only, and this is a deliberate exception.** A layer-1
guard is a tripwire, not a score. It contributes to no denominator, so a guard
that nothing currently violates dilutes nothing — it prevents a regression. The
index guard passed on the day it was written and is still worth having. The test
for keeping a layer-1 item is therefore *"would a realistic mistake trip it?"*,
not *"does something violate it today?"*

## Layer 1 — guards

Every item was measured against all 56 records before being admitted. Violation
counts are as of `Checked` above and are recorded so that a later reader can
tell a tripwire from a discriminator.

| # | Guard | Violations today | Why it is here |
| --- | --- | --- | --- |
| G1 | A record containing a correction carries a marker in its header block | **3 / 56** | A correction at the bottom means a skimming reader absorbs the withdrawn claim first. Three records carry `(Corrected …)` annotations at 65–93% depth. |
| G2 | `Status: In progress` does not survive the change closing | **4 / 56** | Four records say in progress while all 22 evidence records are closed. The markdown status is parsed by nothing, so nothing corrects it. |
| G3 | Relative links resolve from the record's own directory | 0 / 56 | Tripwire. Only five real links exist across the corpus, so this guards a surface that is about to grow, not one that is currently broken. |
| G4 | The artifacts the risk tier requires exist and are non-empty | 0 / 56 | Already enforced by `evidence_gaps`; listed here so the layer is complete rather than to add a second implementation. |

**Rejected during design, with the measurement that rejected it:**

- *`fill-required` markers remain* — **0 / 56**, and unlike G3 no realistic
  mistake reaches a commit with one, because `check` already blocks it. Proposed
  in the original design; deleted by rule 3's own logic.
- *Empty template sections* — **0 / 56**, same reasoning.
- *A term's first use links to its definition* — **52 / 56 would fail.** A guard
  almost everything violates blocks all work rather than catching a mistake.
  Retained as a forward-only expectation in layer 2 (D3) instead, and as a rule
  for new records rather than a gate on old ones.

**One caveat, learned the hard way.** G3's first implementation flagged
`declare-english-canonical` for a dead `README.md` link. The link was inside
backticks — prose quoting another file's content, not a link at all. A guard
that does not respect code spans manufactures defects. Every layer-1 item must
be run against the whole corpus and its hits inspected before it is automated;
that is what layer 1's admission process is for.

## Layer 2 — scored dimensions

Four dimensions. Each expectation is phrased so a reader who has never seen this
project can judge it, and so that silence fails.

| Dimension | Expectation |
| --- | --- |
| **D1 Point first** | Read only the first three paragraphs, then state in one sentence what was done and why. Then read the rest: if the summary contradicts the record, or the record's most consequential fact appears only after the halfway mark, this fails. |
| **D2 Completeness** | State what this record claims was verified, and say whether someone could repeat that verification from what is written here. Name the specific step that could not be repeated, if any. |
| **D3 Comprehensibility** | List every term you had to look up outside this document to follow it, and where you had to go. A record requiring no external lookup passes; one requiring any lookup fails and the list is the evidence. |
| **D4 Reusability** | State what someone facing a similar decision six months from now could take from this record, specifically. "It explains the change" is not an answer; name the transferable claim or say there is none. |

Scoring is boolean per dimension with a quoted justification, following the
existing judge output contract: evidence must be a quotation or a specific
statement of what was searched for and not found, no partial credit, and a
critique channel where the judge says which expectations a clearly bad record
would also have passed.

**What is graded.** Only the five sections whose template instructions have never
changed: `Success and non-goals`, `Existing responsibilities searched`,
`System and data flow`, `Failure, security, and recovery`, and
`Known limits and learning gaps`. The template was rewritten four times, and the
two oldest records were authored against materially different instructions —
scoring the sections that moved would measure the template, not the writing.

For records with more than one commit, the text graded is the version at the
add commit, not at HEAD. Six records were retro-edited during a later audit;
grading HEAD would score that audit rather than the original work.

## Layer 3 — reach

Three reader journeys walked with real commands, counting the steps to an
answer: someone who wants to know why a mechanism exists but knows no change id;
a reviewer asking which paths carry the highest risk tier and why; an outsider
asking what the project currently claims. Reported as steps, dead ends, and any
point where the reader must already know an id or an unadvertised flag.

This measures the structure around the records, not their prose, which is why a
record can score well in layer 2 and still be unreachable.

## How each layer announces that it has stopped working

- **Layer 1** — a guard that fires on every commit is miscalibrated, not
  vigilant. A guard that has never fired since admission, and whose surface has
  since grown, should be re-measured against the corpus rather than trusted.
- **Layer 2** — any dimension that all records pass or all fail is removed at the
  next round. That check is mandatory and its result is reported whether or not
  anything is removed.
- **Layer 3** — journeys are rewritten when the ones in use start passing
  trivially. A reach measurement that only ever reports success is measuring a
  path someone already fixed.

## What this rubric does not do

It does not produce a number for publication. Results live in
`docs/validation/`, and no score from them appears in `README.md` or any release
note until there is something defensible to claim — the same discipline this
project applies to efficacy figures, applied to its own report card.
