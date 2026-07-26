# Contract v1 read-only compatibility

Status: Current
Checked: 2026-07-23

Scope limit: this was checked with the v0.1 CLI. The v0.2 release notes assert
that contract v2 and evidence v1 remain readable without migration, but no v0.2
run against these three repositories is recorded here.

Checked on 2026-07-23 with the v0.1 CLI. Each repository's complete
`git status --porcelain=v1 -z --untracked-files=all` digest was captured before
and after `audit` plus local `check --mode advise`; all three were unchanged.
No contract migration or application command was executed.

| Repository | Contract | Observed risk | Result |
| --- | --- | --- | --- |
| KeyBox | v1 | R1 from existing engineering setup files | Advise: migrate explicitly before enforce |
| COOA web | v1 | R1 from existing engineering setup files | Advise: migrate explicitly before enforce |
| Undrew | v1 | R3 because the existing dirty tree includes credentials/auth-related paths | Advise: migrate explicitly before enforce |

The result demonstrates backward-compatible reading and non-mutating checks.
It does not claim that the existing application changes are correct or ready to
merge.

