# Whether the skill is consulted, before and after rewriting its description

Not an evaluation result. Every figure here is about invocation - whether the
skill runs at all - and none of it says whether running it helps.

Runs are filed under a digest of the description they measured.
`2fb0a4317752` is the description as it stood before this work;
`002b98ce055a` is the rewrite. They are kept apart because a trigger rate is a
property of a description, and pooling the two would answer a question nobody
asked.

The probes were committed before the description was touched. That ordering is
the only thing separating this from writing a test around an answer, and it is
checkable in git history rather than asserted here.

Six runs produced no result. Five were lost to a stretch of rate limiting -
they failed three seconds apart while working runs were fifteen to twenty
seconds apart, and the same probes succeeded on retry - and one timed out. They
are recorded as unusable rather than as non-engagement, because a run that did
not happen is not evidence that the skill declined to engage.

One unscored probe asks to fix a typo the fixture does not contain, so the
agent looks, finds none, and asks. It has been left alone: the probe set was
frozen before the description was written, and editing it now would spend the
guarantee that freeze exists to provide.
