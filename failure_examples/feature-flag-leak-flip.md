# feature-flag-leak: wrong under single call, right under pipeline, with a 100% boilerplate hint

**Report:** A small subset of logged-out users briefly saw another account's cart contents. A
feature-flag targeting rule leaked a cached user-session key across requests when the flag
evaluator reused a shared cache entry by mistake. Scoping the cache key to the session ID fixed
the leak.

**Single call:** `root_cause = "feature-flag targeting rule"` -- missing "cache key" / "shared
cache" / "leak". Graded wrong.

**Pipeline, planner's full note (552 chars):** a detailed investigation plan covering the caching
mechanism, the feature-flag targeting rule, and the shared cache entry -- genuinely relevant
content, all of it lost at the boundary below.

**Pipeline, what crossed the boundary (`focus_hint`, 60 chars, verbatim):** "Here's a short
investigation note: **Investigation Note**" -- this is 100% preamble. No task-specific content
survived at all. This is the cleanest "useless hint" case in the entire run.

**Pipeline, executor's answer (before the reviewer saw it):** `root_cause = "feature-flag
targeting rule leak due to shared cache entry reuse"` -- correct, despite the hint carrying
nothing. It got there from the full original report alone, which the executor receives in
addition to the hint.

**Pipeline, reviewer's final answer:** unchanged from the executor's -- already correct, nothing
to fix.

**Note on the `affected_component` field:** both the single call and the pipeline answered "cache"
for this field, which is accurate but too general for the grader's required "feature-flag
evaluator" / "session" keywords, so this task's overall 3-field grade stayed incomplete in both
conditions even though `root_cause` flipped. See `still-wrong-in-both.md` for the grader-precision
pattern this illustrates.

**Takeaway:** together with `redis-pool-flip.md`, this is the strongest evidence that an executor
reading the full source material can recover a correct answer even when the planner's hint
carries zero information -- the fix traces to the report, not to anything that survived the
handoff.
