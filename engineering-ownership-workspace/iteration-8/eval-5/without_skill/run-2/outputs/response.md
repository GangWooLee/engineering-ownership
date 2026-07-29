Everything's in place and no other files were touched. Here's the state:

**Added:**
- `.github/workflows/tests.yml` — runs `unittest discover` on every push/PR to `main`
- `.github/pull_request_template.md` — checklist for the two rules already in AGENTS.md/CONTRIBUTING.md
- Small `CONTRIBUTING.md` update pointing at both

I haven't committed anything — let me know if you'd like these committed, and separately, whether you want me to look at fixing the `partner_adapter.py` / settlement-note mismatch (undocumented right now, and not covered by the existing test).