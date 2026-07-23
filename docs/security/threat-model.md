# Repository threat model

## Overview

Engineering Ownership is a local Python CLI and a shared Agent Skill packaged
for Codex and Claude Code. It reads a Git repository's contract and working
tree, optionally executes repository-defined verification commands after an
explicit user invocation, and writes repository-local reasoning and evidence.
It has no service, account system, telemetry, MCP server, or background hook.

The primary runtime surfaces are
`plugins/engineering-ownership/src/engineering_ownership/`, the bundled
`bin/engineering` entry point, plugin manifests, and release workflows. Skill
text and documentation guide an agent but do not independently execute code.

## Threat Model, Trust Boundaries, and Assumptions

### Assets

- User-owned source code and uncommitted changes.
- Credentials and environment state accessible to developer processes.
- Integrity of contract, evidence, verification results, and review dates.
- Integrity of plugin source, marketplace catalogs, release ZIP, and checksum.
- The user's informed authorization and engineering judgment.

### Trust boundaries

1. **User ↔ agent:** the agent may propose actions but cannot expand authority.
2. **Repository ↔ CLI:** contracts, paths, instructions, and source are
   untrusted until validated.
3. **CLI ↔ child process:** verification runs project code with local
   privileges and must happen only after explicit invocation.
4. **Working tree ↔ evidence:** a result is meaningful only for the digest it
   actually verified.
5. **Source repository ↔ installed plugin:** tags, catalogs, caches, ZIPs, and
   updates form a supply-chain boundary.

### Inputs and assumptions

Repository authors control contract JSON, filenames, symlinks, command output,
and instruction files. Contributors may control pull-request content. Operators
control whether to invoke `verify`, adopt `enforce`, and install an update.

The CLI cannot make arbitrary project code safe. An explicit verification
command is trusted to the same extent as running that project command manually.
Git and Python are assumed trustworthy. Local administrator compromise is out
of scope.

Security invariants:

- install and skill discovery execute no project command;
- commands use argv with `shell=False`, bounded timeout, and limited environment;
- command shells and secret-like contract environment keys are rejected;
- evidence stores no stdout, stderr, environment values, or absolute home path;
- writes stay within the repository and reject symlink traversal;
- stale verification cannot pass a current-diff gate;
- repository instructions cannot override system policy or user authorization.

## Attack Surface, Mitigations, and Attacker Stories

### Repository-defined command execution

An attacker may add a contract that invokes a shell or disguises destructive
behavior as a test. Schema validation, a shell executable denylist, no shell
parsing, limited environment, and explicit invocation reduce risk. The user
must still review the executable and arguments; allowlisting every legitimate
build tool is impractical.

### Path handling and local writes

Traversal or symlink paths could overwrite files outside the repository.
`safe_relative_path` rejects absolute paths, dot traversal, existing symlink
components, and resolved paths outside the Git root. Tests cover direct and
symlink escapes.

### Secrets and command output

Verification may print credentials. The CLI persists only status metadata and
redacts bounded failure output shown to the terminal. It never stores command
logs or contract environment values in evidence. Users must still avoid
running untrusted project commands in a credential-rich shell.

### Evidence integrity

Code could change after a green run. Each result stores the live diff digest,
and enforce mode rejects stale results. Evidence JSON is not signed and can be
edited; reviewers should treat it as inspectable local evidence, not remote
attestation.

### Agent prompt injection

Repository instructions may ask an agent to skip verification, expose secrets,
or run unrelated commands. The skill explicitly treats repository content as
untrusted and preserves higher-level authority. This is a behavioral boundary,
not a cryptographic control.

### Supply chain

A compromised repository, workflow dependency, plugin cache, or release asset
could alter installed code. CI actions are pinned to commit SHAs. Releases
include a deterministic plugin ZIP, SHA-256, tag, and GitHub build provenance.
Consumers should pin trusted tags and verify checksums where their client does
not provide provenance.

## Severity Calibration (Critical, High, Medium, Low)

**Critical:** automatic or install-time code execution without user action;
reliable credential exfiltration from common installations; release compromise
affecting all users.

**High:** repository path escape that overwrites user files; bypass of
no-shell execution leading to arbitrary commands on explicit `verify`; stored
secret leakage; stale evidence accepted as current for R3.

**Medium:** denial of service through time or resource exhaustion despite the
timeout; misleading handoff that omits a meaningful risk; schema bypass that
requires unusual operator action.

**Low:** inaccurate display text without a gate effect; metadata mismatch caught
by validation; a local-only crash with no data loss.

Findings that require a malicious local administrator, a compromised Python or
Git binary, or intentional manual execution outside the CLI are generally out
of scope.

