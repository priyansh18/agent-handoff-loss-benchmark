# retry-storm: wrong under single call AND executor, right only after the reviewer

**Report:** The billing worker queue backed up for twenty minutes during a downstream outage. A
retry storm formed because failed jobs were retried immediately with no backoff. Adding
exponential backoff to the retry logic stopped the storm.

**Single call:** `root_cause = "downstream outage"` -- missing "retry storm" / "no backoff" /
"immediate retry". Graded wrong.

**Pipeline, planner's full note (447 chars, verbatim):** "Here's a short investigation note:
'Review the system logs to identify the timing and duration of the downstream outage and its
impact on the billing worker queue. Investigate the retry logic to determine why the system did
not implement exponential backoff initially, and examine the configuration or code changes that
were made to implement backoff. Additionally, assess whether the retry storm caused any data
inconsistencies or other issues.'"

**Pipeline, what crossed the boundary (`focus_hint`, 60 chars, verbatim):** "Here's a short
investigation note: 'Review the system logs" -- cut before "retry storm" or "backoff" ever
appear, despite both words being present in the planner's full note just beyond the cutoff.

**Pipeline, executor's answer:** `root_cause = "downstream outage"` -- same gap as the single
call, still wrong. The hint did not help, and could not have, since it is pure preamble by the
point it gets cut.

**Pipeline, reviewer's final answer:** `root_cause = "downstream outage caused a retry storm"` --
corrected. The reviewer was given the full original report a second time, independent of the
planner's note or the executor's first answer, and that second read is what fixed it.

**Takeaway:** this is the one flip in the whole run that is specifically attributable to the
reviewer step, not the executor or the (broken) hint, and the clearest single piece of evidence
for the article's claim that a review step's value comes from re-reading the source, not from
critiquing the prior step's JSON in isolation.
