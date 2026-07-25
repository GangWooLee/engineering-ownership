# The same scenario on a repository this skill does not manage

One run per configuration. Not a measurement, and its pass rates are not
comparable with `iteration-3`: an expectation was split between the two runs, so
the denominators differ (four against five).

## Why it was run

`iteration-3` used a fixture that carried this skill's own artifacts, including
a decision document matching its template section for section with an empty
supersession field. That is a fill-in-the-blank for the very expectation the
scenario grades, and it is the likeliest reason the baseline scored as well as
it did. This run repeats the scenario on a repository with ordinary engineering
conventions and none of this skill's machinery, to see how much of the earlier
result came from the fixture.

## What it showed instead

The skill did not engage. `skill_loaded` is false for the treatment even though
the preflight in this same iteration records the plugin loaded and the skill
visible. The treatment took three actions and wrote nothing; the baseline took
thirteen and wrote three files.

So the question this run was built to answer - how much of the earlier result
came from the fixture - is not answered here. On a repository this skill does
not already manage, there was nothing to compare, because the skill was not
part of the run.

That is a single observation and should not be treated as more. What makes it
worth keeping is that it is visible at all: the runner records whether the skill
was actually invoked, so a run where the treatment did not take can be told
apart from one where it did and did not help.
