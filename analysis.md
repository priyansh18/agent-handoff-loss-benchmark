# Analysis

## Where the accuracy gain actually came from

Two tasks flipped from wrong (missing `root_cause`) under the single call to fully correct under
the pipeline: `redis-pool` and `retry-storm`. `raw_results.jsonl` logs the executor's intermediate
answer separately from the reviewer's final answer, so it is possible to check exactly which step
produced each fix rather than assuming it was the reviewer.

- **`redis-pool`**: the executor's own answer (before the reviewer ever saw it) already named
  "Redis connection pool exhaustion" correctly. The 60-character `focus_hint` it received was cut
  off mid-sentence and contributed nothing useful -- the executor recovered the right answer by
  reading the full original report, which it was given in addition to the degraded hint.
- **`retry-storm`**: the executor's answer was wrong ("downstream outage", missing "retry storm").
  The reviewer step, re-reading the full report a second time, corrected it to "downstream outage
  caused a retry storm" and passed.

So the two flips are not both "the reviewer did it." One flip happened at the executor stage
despite the broken hint, and one needed the reviewer's second pass. What they share is the real
finding: **both corrections trace to a step reading the original source report closely, never to
anything the planner's truncated note carried across the subgraph boundary.** The planner step,
measured against what it produced, earned nothing this run -- not because planning is inherently
useless, but because this pipeline's state schema discarded the planner's output before the next
step could use it.

## What this does and does not support

A 12-task local run on one model is not evidence that multi-agent pipelines are generally good or
bad. What it does support, narrowly: a step that gives a model a second, focused look at the
original source material can catch mistakes a first pass makes, and that is a real, measurable
effect here (83.3% -> 91.7% field accuracy) -- paid for at 4.4x the tokens and 5.7x the latency.
A planning step whose output does not survive its own pipeline's state schema is not free: it
still costs a full LLM call, and in this run it demonstrably changed nothing.

Before adding a planning step to any real pipeline, the concrete, checkable question is not
"would more structure help" -- it is "what, specifically, needs to survive from this step to the
next one, and does the state schema actually carry it." `focus_hint`'s 60-character cap is that
question answered badly, on purpose, to make the failure visible and measurable instead of
theoretical.

## A process note on reproducibility, not swept under the rug

An earlier run of this same experiment (used in the article's first Sunday draft) produced
slightly different numbers (91.7% vs 97.2% field accuracy) using a different, non-identical set of
12 synthetic tasks. That run's raw output was only ever saved to `/tmp/`, which does not persist
across sessions on this machine -- it was gone before this repository existed, and could not be
recovered or verified. Rather than publish numbers that can no longer be substantiated, the
article was updated to use this run's numbers, which are the ones in this repository, fully
re-runnable from `tasks.py` and `run_bench.py`. The direction and shape of the finding (pipeline
beats single-call; handoff loss on every task; the gain traces to source re-reading, not the
planner) held across both runs. The specific percentages did not, which is exactly why they are
not worth trusting unless they are saved somewhere durable the first time.
