# Record quality rubric

Status: Current
Checked: 2026-07-29

Layer 2 was dry-run before automation and **failed**: three of its four
dimensions produced no signal. The dimensions below are the revised ones; the
run and what it changed are recorded at the end of this document.

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

| # | Guard | Violations when admitted | Why it is here |
| --- | --- | --- | --- |
| G1 | A record containing a correction carries a marker in its header block | **3 / 56** | A correction at the bottom means a skimming reader absorbs the withdrawn claim first. The three carried `(Corrected …)` annotations at 65%, 82% and 93% depth. |
| G2 | `Status: In progress` does not survive the change closing | **4 / 56** | Four records said in progress while every evidence record was closed. The markdown status is parsed by nothing, so nothing corrects it. |
| G3 | Relative links resolve from the record's own directory | 0 / 56 | Tripwire. Only five real links exist across the corpus, so this guards a surface about to grow, not one currently broken. |
| G4 | The artifacts the risk tier requires exist and are non-empty | 0 / 56 | Already enforced by `evidence_gaps`; listed so the layer is complete, not to add a second implementation. |

**Implemented as tests, not as CLI behaviour** (`tests/test_records.py`). These
are house rules. The CLI ships to other repositories, and an earlier decision
established that repository-specific policy belongs in the contract or in tests
rather than in shared code. Two facts made that decisive here: `check` runs in
no CI job in this repository, while the skill tells installers to run it in
enforce mode — so a guard placed there would be unenforced at home and blocking
in a stranger's pipeline. And `tests/` does not ship: the release archive is
bounded to `plugins/engineering-ownership`.

**G1's detector matches a form, not a keyword — and that is not a detail.** A
case-insensitive search for "correct" over the corpus returns 26 hits of which
**23 are false positives**: seven records discuss correction as their subject,
and one says a thing was *deliberately not corrected*. The guard matches
`(Corrected YYYY-MM-DD:`, the shape every real in-place correction uses, and a
companion test pins the false-positive set so a later loosening of the pattern
fails loudly.

**Why G1's header field is not a second `Status:`.** `Status:` was worth
removing because no code read it, so nothing kept it true. `Corrected:` has a
consumer — the guard itself reads it and fails when a body correction has no
header line. For the same reason it must **not** be added to `templates.py`: a
templated `Corrected: None` on every new record would be exactly the unread
field that G2 exists to remove.

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

**The reader is an engineer new to this repository** — competent, but with no
prior knowledge of this project's vocabulary or history. Every dimension is
judged from that seat. Naming the reader is not decoration: the first version
omitted it, and both graders reported they had to invent one.

| Dimension | Expectation |
| --- | --- |
| **D1 Calibration** | Read only the opening section. State what it tells you about *how much to trust* what follows — the result's strength, its limits, or what it does not claim. FAIL if the opening is contentless: if a reader who stopped there would make the same decision regardless of what the record found. |
| **D2 Stated verification** | State what the record says was checked, and by what. FAIL if the record names no check, or names one without saying what it produced. Judge the record's account, **not** whether the subject matter happens to be deterministically repeatable — a blinded judge run reported honestly passes, a script with fixed integers does not automatically. |
| **D3 Load-bearing jargon** | List the undefined terms the record's central argument *rests on* — terms a new engineer must resolve elsewhere before they can judge the claim. Exempt in-repo identifiers whose role is stated in the sentence that uses them (`save_evidence` used as "…calls `save_evidence`, which writes the record" is defined in place). FAIL if the list is non-empty; the list is the evidence. |
| **D4 Bounded takeaway** | State what someone facing a similar decision could take from this record. FAIL unless the transferable claim carries either the evidence that produced it or the condition under which it stops applying. A stated preference with neither is not transferable. |

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

## Dry run, 2026-07-29 — the first layer 2 failed

Six records, stratified by risk tier and revision history, graded independently
by two judges who saw only five extracted sections, no titles, no dates, and not
each other's verdicts.

**Agreement was 22 of 24 cells (92%)**, and both disagreements landed on the two
dimensions the judges independently called ambiguous. Where the rubric was
vague, the graders diverged — which is the signal inter-rater agreement is for.

**Discrimination, first version:**

| Dimension | Passed | Verdict |
| --- | --- | --- |
| D1 point first | 11 / 12 | near-constant |
| D2 completeness | 2 / 12 | the only discriminator |
| D3 comprehensibility | **0 / 12** | constant — unsatisfiable as written |
| D4 reusability | 11 / 12 | near-constant |

**What both judges found, independently:**

- **D1 was guaranteed by the template.** Every record's first section is
  `Success and non-goals`, so a coherent, self-consistent summary always exists.
  Worse, the "most consequential fact after the halfway mark" clause is
  structurally confounded: every record ends with `Known limits and learning
  gaps`, which is exactly where an honest author is instructed to put caveats.
  The clause fired on honesty. Dropped, and D1 rewritten to ask what the opening
  says about trust rather than whether it is merely non-contradictory.
- **D2 measured the subject, not the record.** Its single pass was the least
  consequential change in the set, because a script with four fixed integers is
  trivially repeatable. Records reporting a blinded judge run or rate-limited
  probes — honestly, with outcomes stated — failed for the nondeterminism of
  what they studied. Rewritten to judge the account rather than the reproducibility
  of the subject matter.
- **D3 had no defined reader**, so "PASS only if the list is empty" could not be
  satisfied by any in-repository record: such records legitimately name their own
  modules and artifacts. Both judges narrowed it themselves to survive, and both
  narrowed it differently. Rewritten with the reader named and in-repo identifiers
  exempted when their role is stated in place.
- **D4 was satisfiable by abstraction.** A rejected alternative always reads as a
  transferable claim, so an unsupported preference and a hard-won lesson scored
  identically. Rewritten to require the claim to carry its evidence or its
  boundary.
- **D3 and D4 pulled in opposite directions.** The vaguest record had the
  *shortest* honest lookup list, because it never became specific enough to
  require one. Abstraction was penalised by D2 and rewarded by D3.

**Decision: the first layer 2 was not automated.** Only one dimension separated
anything, and it separated on the wrong property. The revised dimensions above
have not themselves been dry-run; that is required before they are automated,
by the same rule.

## What this rubric does not do

It does not produce a number for publication. Results live in
`docs/validation/`, and no score from them appears in `README.md` or any release
note until there is something defensible to claim — the same discipline this
project applies to efficacy figures, applied to its own report card.
