# redis-pool: wrong under single call, right under pipeline (executor stage)

**Report:** Checkout API pods began returning 500s during the 14:00 feature-flag rollout. Logs
show the Redis connection pool was exhausted shortly after the flag enabled a new caching path.
The on-call engineer rolled back the flag and restarted the affected pods to recover.

**Single call:** `root_cause = "feature-flag rollout"` -- missing "redis" / "connection pool" /
"exhaust". Graded wrong.

**Pipeline, planner's full note (428 chars):** "Review the Redis connection pool configuration
and logs to determine if the exhaustion was caused by a sudden increase in traffic or a
misconfiguration. Check the caching path configuration and its interaction with the Redis
connection pool to identify any potential issues. Also, examine the pod restart and rollback
process to ensure it was executed correctly and didn't introduce any additional errors."

**Pipeline, what crossed the boundary (`focus_hint`, 60 chars, verbatim):** "Review the Redis
connection pool confi" (truncated mid-word).

**Honest complication, stated plainly:** unlike `retry-storm` and `feature-flag-leak` below, this
hint is NOT useless -- it happens to contain "Redis connection pool," the exact phrase the grader
needed, because the planner's sentence led with that phrase before the 60-character cutoff
landed. This is an accident of where a sentence break fell, not something the pipeline's schema
was designed to guarantee.

**Pipeline, executor's answer (before the reviewer saw it):** `root_cause = "Redis connection pool
exhaustion"` -- already correct.

**Pipeline, reviewer's final answer:** added the feature-flag timing detail but did not change
the grade -- it was already correct at the executor stage.

**Takeaway:** this flip cannot be cleanly attributed to "re-reading beat the hint," because the
hint itself happened to carry the right words this time. It is included here specifically so the
repository does not quietly drop the one case that complicates the article's main claim. See
`retry-storm-flip.md` and `feature-flag-leak-flip.md` for the two cases where the hint
demonstrably contributed nothing.
