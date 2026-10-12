# Analysis

## Where the accuracy gain actually came from

Three individual fields, across three different tasks, flipped from wrong to right between
Condition A (single call) and Condition B (the pipeline): `redis-pool`, `retry-storm`, and
`feature-flag-leak`. `raw_results.jsonl` logs the executor's intermediate answer separately from
the reviewer's final answer for every task, specifically so it is possible to check which step
produced each fix rather than assuming.

The executor stage alone, before the reviewer ever runs, already scores **32/36 (88.9%)** --
measured directly from the saved `executor_answer` field, not inferred. The reviewer's final pass
adds exactly one more field, to 33/36 (91.7%). Two of the three fixes happened at the executor
stage; one needed the reviewer.

They also did not all resolve the same way with respect to the planner's hint:

- **`feature-flag-leak`** (see `failure_examples/feature-flag-leak-flip.md`): the hint that
  crossed the boundary was 100% boilerplate preamble -- zero task-specific content. The executor
  still got `root_cause` right, from reading the full original report.
- **`retry-storm`** (see `failure_examples/retry-storm-flip.md`): the hint was semi-generic
  ("review the system logs"), not pure boilerplate but not specific either. The executor still
  got it wrong. The reviewer, re-reading the full report a second time, corrected it. This is the
  one fix that specifically needed the reviewer.
- **`redis-pool`** (see `failure_examples/redis-pool-flip.md`): the honest complication. This
  hint happened to contain "Redis connection pool" -- the exact phrase the grader needed --
  because the planner's sentence led with it before the 60-character cutoff landed. This fix
  cannot be cleanly attributed to "re-reading beat the hint," since the hint itself carried the
  right words this time, by accident of sentence structure rather than by design.

## What this does and does not support

Put together: two of the three fixes happened with hints that demonstrably contributed nothing,
and the executor's own full-report read (independent of the hint) already accounts for most of
the pipeline's total gain (32/36 of the 33/36 final score). The planner step, measured honestly,
did not earn anything *reliable* this run -- its one plausible contribution (`redis-pool`)
depended on where a sentence happened to break, not on the architecture working as designed.

A 12-task local run on one model is not evidence that multi-agent pipelines are generally good or
bad. What it does support, narrowly: a step that gives a model a second, focused look at the
original source material can catch mistakes a first pass makes, and that effect is real here
(83.3% -> 91.7% field accuracy) -- paid for at 4.4x the tokens and 5.7x the latency. A planning
step whose output does not survive its own pipeline's state schema is not free: it still costs a
full LLM call, and in this run it demonstrably changed nothing reliable.

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
beats single-call; handoff loss on every task; the gain traces mostly to source re-reading, not
the planner) held across both runs. The specific percentages did not, which is exactly why they
are not worth trusting unless they are saved somewhere durable the first time.

## A second process note: an independent fact-check caught real errors here too

An independent Codex pass fact-checked this experiment's first write-up (before this file's
current version) and found genuine problems beyond the numbers: the retry-storm planner note and
hint quoted in the draft and diagram were hand-paraphrased to match the fixture's theme instead of
pulled verbatim from `raw_results.jsonl`; a third flipped field (`feature-flag-leak`) was missed
because only tasks that flipped to "all 3 fields correct" were checked, not every individual field
delta; and the claim that the `redis-pool` hint was "useless" was flatly wrong -- it contains the
exact phrase needed. All three are fixed in this version: the diagram (`make_handoff_diagram.py`)
now reads `raw_results.jsonl` programmatically instead of hardcoding quoted text, all three flips
have their own `failure_examples/` file, and `redis-pool-flip.md` states the complication plainly
instead of silently dropping it.
