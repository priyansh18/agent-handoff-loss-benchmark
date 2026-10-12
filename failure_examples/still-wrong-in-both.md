# Tasks that stayed wrong in both conditions

Three tasks graded wrong under both the single call and the pipeline: `url-shortener`,
`dns-caching`, and `feature-flag-leak`. In all three cases the failure was the same shape: the
model's `affected_component` answer was factually reasonable but did not contain any of the
specific keyword(s) the grader required (a precision-vs-completeness gap in the keyword grader
itself, named honestly in `methodology.md`, not hidden).

- **`url-shortener`**: both conditions answered `affected_component = "Transactional emails"` /
  "Transactional email delivery and URL shortener integration" -- the grader required
  "password-reset" / "password reset" / "auth", none of which appeared, even though the answer is
  substantively about the right thing.
- **`dns-caching`**: both conditions answered `affected_component = "application pods"`, which is
  accurate per the report, but the grader's required list ("search service", "search-service")
  targeted the service name specifically, not the pods the report also names.
- **`feature-flag-leak`**: both conditions answered `affected_component = "cache"`, correct but
  too general for the grader's required "feature-flag evaluator" / "session" keywords.

**Why this matters for the result, stated plainly:** the pipeline's extra calls did not fix a
grader-precision gap like this, because no amount of re-reading the source changes whether the
model's phrasing happens to contain a specific required substring. This is the keyword grader's
own limitation, not a claim that the pipeline is weaker here than it looks -- it is a reminder that
83.3% and 91.7% are scores against a mechanical rubric, not a ground-truth human judgment of
correctness.
