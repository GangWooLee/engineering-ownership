# Validation records

Each document in this directory records what was actually checked, when, and
what remained unverified. These are observations, not guarantees.

Every validation document carries two header lines, and a third when it has been
replaced:

```text
Status: Current | Superseded | Withdrawn
Checked: YYYY-MM-DD
Superseded by: docs/validation/<file>.md
```

`Current` means the observation still describes the shipped version.
`Superseded` means a later document replaces it; the original is kept rather than
edited, so the change of understanding stays visible.
`Withdrawn` means the claim was found to be unsupported and is retracted; the
original claim is quoted inside the document together with the reason, because
deleting a retracted claim removes the evidence that it was retracted.

A validation document is never rewritten to hide a superseded conclusion. This
mirrors the supersession rule already used for decision records in
`docs/engineering/decisions/`.

| Document | Status | Checked | Subject |
| --- | --- | --- | --- |
| [record-quality-2026-08-rerun.md](record-quality-2026-08-rerun.md) | Current | 2026-08-05 | Full-corpus grading with the verification section included, and what moved when it was |
| [record-quality-2026-08.md](record-quality-2026-08.md) | Superseded | 2026-08-05 | First full-corpus grading; graded D2 without the section that answers it |
| [record-quality-rubric.md](record-quality-rubric.md) | Current | 2026-07-29 | How the engineering records are measured; the standard, not the scores |
| [skill-evaluation.md](skill-evaluation.md) | Withdrawn | 2026-07-25 | Paired skill/baseline comparison; retracted, rebuild in progress |
| [v0.2-host-and-skill.md](v0.2-host-and-skill.md) | Current | 2026-07-23 | v0.2 packaging, host install, and live skill routing |
| [plugin-discovery.md](plugin-discovery.md) | Superseded | 2026-07-23 | v0.1 plugin and skill discovery |
| [legacy-project-read-only.md](legacy-project-read-only.md) | Current | 2026-07-23 | Contract v1 read-only compatibility on three external repositories |

`fixtures/` holds artifacts used to validate the instruments in this
directory rather than the project. `negative-control-record.md` is a change
record written deliberately to fail the record-quality rubric; it documents no
real work and is graded blind among real records to locate what the rubric
lets through.

There is currently **no published quantitative efficacy claim** for the skill.
See [skill-evaluation.md](skill-evaluation.md) for why the previous one was
withdrawn and what replaces it.
