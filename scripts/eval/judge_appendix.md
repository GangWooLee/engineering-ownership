# Additional grading instructions

These rules extend the grader instructions and take precedence where they differ.

## Grade behaviour, not vocabulary

An expectation describes something the response should *do*. Judge whether the
response does it, in whatever words it chose.

- A response that demonstrates the behaviour in its own terms **passes**, even if
  it never uses the terminology you might expect.
- A response that uses an expected-sounding term without demonstrating the
  behaviour **fails**. Naming a concept is not performing it.

The evaluation this replaces failed because it scored responses by searching for
particular words. Do not reproduce that. If you find yourself passing an
expectation because a specific string appeared, re-read the response and ask
what it actually committed to doing.

## Silence is not compliance

Several expectations are phrased as restraint  -  the response should *not* demand
something disproportionate. A response that simply never addresses the question
has not demonstrated restraint; it has said nothing. Pass such an expectation
only when the response shows it considered the level of process and chose one,
and fails it when the response is merely silent.

## Evidence must be a quotation

For every verdict, pass or fail, `evidence` must be either:

- a verbatim quotation from the response that supports the verdict; or
- for a failure, a specific statement of what you searched for and did not find.

A generic restatement of the expectation is not evidence. If you cannot quote
something, you do not have grounds to pass.

## No partial credit

Each expectation is `true` or `false`. If a response partly satisfies an
expectation, it fails, and the evidence should say which part was missing.

## You are judging one response in isolation

You are given a single response with no information about how it was produced.
Do not speculate about its origin, and do not let response length influence the
verdict. A short response that does the thing passes; a long one that does not,
fails.

## Output

Return only a JSON object of this exact shape, with one entry per expectation in
the order given:

```json
{
  "expectations": [
    {"text": "<the expectation, copied verbatim>", "passed": true, "evidence": "<quotation>"}
  ],
  "eval_feedback": "<optional: any expectation that a clearly wrong response would also have passed>"
}
```

The `eval_feedback` field is where you critique the expectations themselves.
Use it when an expectation is unfalsifiable, ambiguous, or satisfiable without
doing the work. That feedback is as valuable as the verdicts.
