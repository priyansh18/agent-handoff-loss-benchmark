# redis-pool: wrong under single call, right under pipeline (executor stage, not reviewer)

**Report:** Checkout API pods began returning 500s during the 14:00 feature-flag rollout. Logs
show the Redis connection pool was exhausted shortly after the flag enabled a new caching path.
The on-call engineer rolled back the flag and restarted the affected pods to recover.

**Single call:** `root_cause = "feature-flag rollout"` -- missing "redis" / "connection pool" /
"exhaust". Graded wrong.

**Pipeline, planner's full note (428 chars):** investigation plan mentioning Redis pool settings
and logs explicitly.

**Pipeline, what crossed the boundary (`focus_hint`, 60 chars):** truncated mid-sentence, before
the word "Redis" appears in the planner's note.

**Pipeline, executor's answer (before the reviewer saw it):** `root_cause = "Redis connection pool
exhaustion"` -- already correct. The executor recovered this from the full report text it was
given directly, not from the hint.

**Pipeline, reviewer's final answer:** added the feature-flag timing detail but did not change
the grade -- it was already correct at the executor stage.

**Takeaway:** this flip is not evidence the planner or the reviewer specifically fixed anything.
It is evidence that giving the model a second structured pass at the same source material (even
with a broken hint attached) can surface detail a single, less-scaffolded call missed.
