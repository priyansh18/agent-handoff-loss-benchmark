# Methodology

## Model and environment

- Model: `llama3.1:8b`, served locally by Ollama (`localhost:11434`).
- Temperature: 0. Seed: 7. Same machine, same session, both conditions run back to back.
- Zero API cost, zero external network calls.

## Task set

12 synthetic incident reports, written as test fixtures (not real production incidents), each
2-3 sentences describing one bug and its fix. Each has a ground-truth keyword list for three
fields: `root_cause`, `affected_component`, `fix_action`. See `tasks.py` for the full set and the
exact keyword lists.

## Grading

A field counts correct if the model's answer contains at least one of the required keywords for
that field, case-insensitive substring match. This is a deliberately mechanical rule so scoring
is reproducible and not a matter of judgment call. It rewards completeness over precision: an
answer that restates extra correct detail can pass even if it also includes something irrelevant,
and an answer that is correct but phrased without any of the listed keywords (a genuine synonym)
will fail. Both directions of this limitation are visible in `failure_examples/`.

## Condition A: single call

One prompt per task, asking the model to extract all three fields as JSON in one shot. See
`prompts/single_call.txt`.

## Condition B: three-step pipeline

Three calls per task, modeling a LangGraph planner -> executor subgraph -> reviewer flow:

1. **Planner** (`prompts/planner.txt`): given the report, writes a short investigation note (2-3
   sentences) describing what to look for. Does not answer yet.
2. **Executor** (`prompts/executor.txt`): given the full report again, plus a `focus_hint` derived
   from the planner's note, extracts the three fields as JSON.
3. **Reviewer** (`prompts/reviewer.txt`): given the full report and the executor's draft JSON,
   checks and corrects it, returning the final JSON.

## The handoff truncation, as code

```python
focus_hint = plan_notes.split(".")[0][:60] if plan_notes else ""
```

This is the one deliberately engineered detail in the whole experiment. It models a real LangGraph
subgraph boundary: a subgraph's own state schema is what crosses the parent/child boundary, and a
key the parent step produced but the child's schema never declared is simply absent on the other
side -- no exception, no warning. The planner's full notes run 150 to 550+ characters per task;
`focus_hint` caps what survives at 60, cut at the first period and then hard-truncated. This is
not a bug found by accident. It is written to model a team wiring a narrow state schema under
deadline pressure, before thinking hard about what actually needs to survive the handoff.

Importantly, the **original incident report is given in full to every step**, including the
executor and reviewer. What gets lost at the boundary is specifically the planner's own analysis,
not the source material itself. This is what makes the result in `analysis.md` possible to
interpret precisely: any accuracy gain in Condition B has to come from somewhere, and it is not
from the hint.

## Stated limitations

- **One run per condition.** Temperature 0 and a fixed seed make this deterministic on the same
  model/hardware, but it is still a single trial, not a distribution. A single flipped task moves
  the accuracy numbers by one unit (1/36 = 2.8 percentage points) either way.
- **Keyword grading rewards completeness over precision.** See `failure_examples/` for the exact
  cases where this cuts both ways.
- **12 tasks, synthetic.** This is a small, fabricated-but-realistic benchmark, not a production
  incident corpus. The finding (handoff loss at the subgraph boundary; the gain tracing to
  re-reading the source, not the planner's hint) is a mechanism demonstration, not a claim about
  effect size on real incidents.
- **One model family.** Only tested against `llama3.1:8b`. Larger or different-family models may
  compress less aggressively, or the planner's hint may matter more if the executor is not also
  given the full source report (a design choice this benchmark deliberately avoided, see above).
