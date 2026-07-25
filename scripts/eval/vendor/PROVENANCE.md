# Vendored evaluation harness

These files are copied verbatim from the `skill-creator` plugin so that the
evaluation can be reproduced by someone who does not have that plugin installed.
Reproducibility is the point of committing the evaluation workspace, and an
in-place reference to a path under a maintainer's home directory would defeat it.

Upstream: `anthropics/claude-plugins-official`, plugin `skill-creator`
Commit: `b36fd4b753018b0b340803579399992a32e43502`
Licence: Apache-2.0 (see `LICENSE.apache-2.0.txt`)
Copied: 2026-07-25

Do not edit these files. Where the upstream behaviour is insufficient, adapt it
in our own scripts alongside, so that drift from upstream stays visible.

| File | sha256 |
| --- | --- |
| `grader.md` | `57134da0c1a4eea33fbd74a1c9c44aa814f07d6bc64de303edb586f941e5d21a` |
| `aggregate_benchmark.py` | `123ef128ea5ccc01a4b1ac212ef5567f21e9c13d3d240609780beeb3200c49aa` |
