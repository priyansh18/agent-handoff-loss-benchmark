# retry-storm: wrong under single call, right under pipeline (reviewer stage specifically)

**Report:** The billing worker queue backed up for twenty minutes during a downstream outage. A
retry storm formed because failed jobs were retried immediately with no backoff. Adding
exponential backoff to the retry logic stopped the storm.

**Single call:** `root_cause = "downstream outage"` -- missing "retry storm" / "no backoff".
Graded wrong.

**Pipeline, executor's answer:** `root_cause = "downstream outage"` -- same gap, still wrong.
The 60-character `focus_hint` it received did not help.

**Pipeline, reviewer's final answer:** `root_cause = "downstream outage caused a retry storm"` --
corrected. The reviewer was given the full original report a second time, independent of the
planner's note or the executor's first answer, and that second read is what fixed it.

**Takeaway:** this is the one flip in the whole run that is specifically attributable to the
reviewer step, not the executor or the (broken) hint. It is also the clearest single piece of
evidence for the article's claim that the reviewer's value came from re-reading the source, not
from critiquing the executor's JSON in isolation.
