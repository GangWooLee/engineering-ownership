# Record quality rubric

Status: Current
Checked: 2026-07-29
Corrected: 2026-07-29 — the layer-1 denominator was written as 56 with no commit
pinned; it was 58 at this document's own commit, and the retro-edit count was 6
when written and is 9 now.

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

Every item was measured against the whole record set before being admitted.
Violation counts are recorded so a later reader can tell a tripwire from a
discriminator.

**The denominator below is 56 and is pinned to the moment of measurement, not
to a commit** — which is the defect this note exists to name. At `dca835c`, the
commit that introduced this document, the four record directories held **58**
files. The measurement ran before the change record and ADR describing it were
created, so the corpus grew by two between the count and the commit. A count
taken against a live tree, in a repository whose records are themselves records
of the counting, is not reproducible unless the commit is stated. Later rounds
state one.

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
| **D1 Calibration** | Read only the opening section. State what it tells you about *how much to trust* what follows. FAIL if a reader who stopped there would make the same decision regardless of what the record found. **A list of deferred or excluded features does not satisfy this**, and neither does a set of success criteria that are all properties the change was built to have: at least one must state a proposition that could plausibly have resolved the other way. |
| **D2 Stated verification** | State what the record says was checked, and what that check produced. FAIL if it names no check, or names one without saying what came out of it. **A check identified only by pointing at another document — "exercised by tests", "see the threat model" — counts as naming no check.** Judge the record's account, **not** whether the subject matter is deterministically repeatable: a blinded judge run reported honestly passes; a script whose output is never stated does not. |
| **D3 Load-bearing jargon** | List the undefined terms the record's central argument *rests on* — terms a new engineer must resolve elsewhere before they can judge the claim. Exempt in-repo identifiers whose role is stated in the sentence that uses them (`save_evidence` used as "…calls `save_evidence`, which writes the record" is defined in place). FAIL if the list is non-empty; the list is the evidence. |
| **D4 Bounded takeaway** | State what someone facing a similar decision could take from this record. FAIL unless the transferable claim carries either the specific observation from *this* change that produced it, or the condition under which it stops applying. **A scope disclaimer of the form "X does not cover Y" is not a stopping condition** — the condition must name an observation a reader could make that would overturn the claim. A general property of a third-party tool, restated without saying how this change encountered it, is neither. |

Scoring is boolean per dimension with a quoted justification, following the
existing judge output contract: evidence must be a quotation or a specific
statement of what was searched for and not found, no partial credit, and a
critique channel where the judge says which expectations a clearly bad record
would also have passed.

**What is graded.** (Corrected 2026-08-05: `Verification evidence` was excluded
here and in the grader, so the first full-corpus run measured D2 without the one
section that answers it. The reason given for excluding it did not apply to that
section, and the consequence for a dimension about verification was not
considered. The run that carried the defect is reported in
[record-quality-2026-08.md](record-quality-2026-08.md).)

Six sections, in the order a reader meets them: `Success and non-goals`,
`Existing responsibilities searched`, `System and data flow`,
`Failure, security, and recovery`, `Verification evidence`, and
`Known limits and learning gaps`.

Everything else is left out because the template was rewritten four times and
the two oldest records were authored against materially different instructions —
scoring a section whose instructions moved would measure the template, not the
writing.

`Verification evidence` is included, and is the one section treated as optional.
It has never carried instruction text; it is a bare heading, as three of the
five required sections are, so nothing about it could have moved. Its heading
was renamed once, from `Verification plan`, and the two records written before
that rename have no section under the new name. Requiring it would drop those
two records from grading; excluding it, as the first run did, withholds from the
judge the one section that answers D2. Optional gives the judge the section when
it exists and lets its absence read as the absence of a reported check.

Records are graded at HEAD. An earlier draft of this rule said to grade the
version at each record's add commit, so a later audit's corrections would not
leak in; six records were retro-edited at the time of writing, and nine are now.
The rule was dropped before it was ever applied, because extracting that version
showed `change start` creates a record *before* the work is done — one sample's
add-commit text was a 252-character skeleton with template instructions still in
it. "As authored" and "at the add commit" are not the same thing in this
workflow, and HEAD is what a reader actually meets.

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
anything, and it separated on the wrong property.

## Second dry run, 2026-07-29 — the revision cleared its bar

Same six records, byte-identical extracts (verified by hash), two fresh
independent judges, revised dimensions. Because the inputs did not move, any
difference is attributable to the rubric.

Three criteria were fixed **before** the run: no dimension may be all-pass or
all-fail; agreement should hold near the first run's 22/24; D3 must be
satisfiable by at least one record, having been unsatisfiable by construction.

| | First run | Second run |
| --- | --- | --- |
| Inter-rater agreement | 22 / 24 (92%) | **24 / 24 (100%)** |
| Constant dimensions | 1 (D3 at 0/12) | **none** |
| Pass counts | 11 / 2 / 0 / 11 | 10 / 10 / 8 / 10 |

All three criteria met. But the honest reading is narrower than that table, and
both judges reached it independently: **the instrument currently resolves two
bands, not six.** One record fails all four dimensions; one other fails only
D3; the remaining four pass everything. As one judge put it, the run "mostly
measured one outlier and told me little about the other five."

What each dimension still lets through, per the judges:

- **D1** detects the *presence* of a non-goals section rather than calibration.
  Both judges failed the outlier by drawing a line the rubric does not draw —
  between features not built ("no PyPI yet") and limits on what the evidence
  supports ("this does not show Y"). One said plainly: "That distinction is
  mine, not the rubric's."
- **D2** cannot distinguish a reported outcome from a definition of done.
  "The full suite passes" written in a success clause is indistinguishable in
  form from a criterion never run. The stricter bar both judges proposed:
  require an outcome that *could have been otherwise*. Only three records clear
  it — a repo-wide check that came back BLOCKED, a falsified hypothesis, and a
  judge verdict that went against the author.
- **D4** collapses toward "did you give a reason". A record appending
  "because X" to each preference passes.
- **D3 was the only dimension whose failures could not be faked** by adding a
  section header — but it depends on the judge's read of which term is central,
  and the same undefined term produced opposite verdicts in two records for
  defensible reasons.

**What this run cannot settle, and what would.** Five of six records passing
almost everything is consistent with two very different worlds: a lenient
rubric, or a genuinely uniform corpus. Nothing in a sample of six real records
separates those. The next validation needs a **negative control** — a
deliberately poor record written to fail — because both judges could only
answer "what would a clearly bad document also pass?" speculatively, having
never been shown one.

**Decision: the revised dimensions may be used for a full pass**, with the
two-band limitation reported alongside any result rather than discovered later.

## Third dry run, 2026-07-29 — with a negative control

The previous run could not distinguish a lenient rubric from a uniform corpus,
because no bad record existed to try. One was written:
`fixtures/negative-control-record.md`, built to game the three leniencies the
judges had named — a non-goals list made only of features not built, a
verification claim phrased as a success criterion never run, and preferences
with a bare `because` clause. It deliberately does **not** game D3; every
identifier is glossed in place, so a D3 pass isolates the other three.

Prediction, fixed before the run: the control should fail D1, D2 and D4 and pass
D3. Seven documents, the control unlabelled among six real records, two blind
judges.

| | Verdict |
| --- | --- |
| Control | **6 of 8 cells failed** — D1, D2, D4 by both judges; D3 passed by both |
| Agreement | 26 / 28 (93%) |
| Prediction | met exactly |

**The rubric catches a record built to beat it.** The leniencies the previous
run could only speculate about are narrower than feared.

**But the run found something the control was not designed to test.** Asked —
separately from the rubric — which document they would least want to inherit,
both judges named the same one, and it was **not** the control. It was a real
record that scores *better* than the control on the rubric. One judge:

> "The rubric over-penalizes legible thinness and under-penalizes abstraction
> with no referent."

The control is thin but concrete: every identifier is glossed, and a reader
could reconstruct the change from the diff in an afternoon. The record both
judges rejected covers an entire release, names no file it touched, no command
it ran, no number, and delegates its whole assurance story to "exercised by
tests" — and it passed D1 and D4. Its opacity scales with its subject; the
control's does not.

**Three tightenings applied**, each proposed independently by a judge who then
checked it against all seven documents and named which would still pass:

- **D1** — a deferred-feature list no longer satisfies calibration, and success
  criteria that are all properties the change was built to have fail. Verified
  safe against the strong records, which keep passing on "publishing any
  number", pre-registered numeric thresholds, per-path classifications, and
  byte-identical behaviour that could have broken.
- **D2** — a check identified only by pointing at another document counts as
  naming no check. This is the tightening that catches verification-by-reference,
  the rejected record's defining flaw.
- **D4** — a scope disclaimer ("X does not cover Y") is not a stopping
  condition, and a general property of a third-party tool restated without
  saying how this change met it is neither evidence nor boundary.

These tightenings carry **predicted verdicts** rather than measured ones: each
judge stated which records their edit would newly fail. The full pass is what
tests those predictions, and any that miss is a finding about the rubric rather
than about the record.

## What this rubric does not do

It does not produce a number for publication. Results live in
`docs/validation/`, and no score from them appears in `README.md` or any release
note until there is something defensible to claim — the same discipline this
project applies to efficacy figures, applied to its own report card.
