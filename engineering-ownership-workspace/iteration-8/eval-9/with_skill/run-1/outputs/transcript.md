Bash
{"command":"ls ~/.claude/projects/-private-var-folders-p1-j0wyrz8117sg39nkjhwx2k-00000gn-T-engo-eval-lxt37awx-eval-9-with-skill-1/memory/ 2>/dev/null","description":"List memory directory contents"}

I found the adapter and the decision doc that explains why this rounding exists. There's a mismatch worth flagging before I change anything:

**Current code** (`src/api/partner_adapter.py`):
```python
WHOLE_UNIT_PARTNERS = frozenset({"p-1", "p-7"})
```
Only `p-1` and `p-7` are forced to whole-unit rounding — every other partner already receives the raw (fractional) `amount_cents` value untouched.

**The decision doc** explicitly anticipated this exact change and warns:
> "This holds only while every partner settles in whole units. If one starts accepting fractional amounts, the conversion stops being a property of the adapter and becomes a property of the partner..."

So making *every* partner fractional (e.g., dropping `WHOLE_UNIT_PARTNERS` entirely) would also stop rounding for whichever of `p-1`/`p-7` is *not* your largest partner — silently breaking their integration again (rejected payloads), which is the exact failure this code was built to prevent.

Could you confirm: which partner ID is the "largest partner" now requiring fractional amounts — `p-1` or `p-7`? I'll remove just that one from `WHOLE_UNIT_PARTNERS` so the other whole-unit partner keeps working correctly.