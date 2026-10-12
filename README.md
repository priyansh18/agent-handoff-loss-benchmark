# One Agent Split Into Three

Reproducibility package for the Medium article *"I Split One Agent Into Three. The Plan Never
Reached the Executor."* by Priyansh Singhal.

A local, $0, deterministic benchmark comparing a single LLM call against a three-step
planner-executor-reviewer pipeline (the shape of a LangGraph subgraph handoff) on 12 synthetic
incident-report extraction tasks.

## Headline result

| | Single call | Three-step pipeline |
|---|---|---|
| Field accuracy | 30/36 (83.3%) | 33/36 (91.7%) |
| Tasks with all 3 fields correct | 7/12 | 9/12 |
| LLM calls | 12 | 36 |
| Total tokens | 1,659 | 7,323 (4.4x) |
| Wall-clock time | 72.7s | 411.1s (5.7x) |

On **12 of 12 tasks**, the planner's full investigation notes (150-550+ characters) were
truncated to a 60-character fragment before the executor subgraph ever saw them -- a real
LangGraph state-schema mismatch, not a prompt bug. See `methodology.md` for exactly how, and
`analysis.md` for where the pipeline's accuracy gain actually came from (it is more specific than
"multi-agent wins").

## Run it yourself

Requires [Ollama](https://ollama.com) running locally with `llama3.1:8b` pulled
(`ollama pull llama3.1:8b`). No API keys, no network calls beyond `localhost:11434`.

```bash
python3 run_bench.py        # writes raw_results.jsonl and summary.json
python3 make_chart.py       # writes charts/results-single-vs-pipeline.png
python3 make_handoff_diagram.py   # writes charts/handoff-diagram-arc5.png
```

Only the Python standard library is used (`urllib`, `json`, `re`). No `requirements.txt` needed.

## Files

- `tasks.py` -- the 12 synthetic incident reports and their keyword-based grading rubric.
- `run_bench.py` -- runs both conditions against the local model and writes the raw results.
- `raw_results.jsonl` -- full per-task output for both conditions, including every truncated
  `focus_hint` and the intermediate executor answer (before the reviewer's pass).
- `summary.json` -- the aggregate numbers in the table above.
- `prompts/` -- the exact prompt templates sent to the model for each step.
- `failure_examples/` -- the tasks whose grade changed between conditions, and the tasks that
  stayed wrong in both, with the model's actual answers quoted.
- `methodology.md` -- the full experimental method, grading rule, and stated limitations.
- `analysis.md` -- what the result means, including the honest nuance about where the gain
  actually came from.
- `charts/` -- the two images used in the article, generated directly from this run's own data.

## Limitations (stated here, not hidden)

- One deterministic run per condition (temperature 0, fixed seed), not a repeated-trial
  distribution. A single flipped task moves the accuracy numbers by one unit either way.
- The grader is keyword-based (a field counts correct if the answer contains at least one
  required keyword). This rewards completeness over precision -- see `methodology.md`.
- The 12 tasks are synthetic fixtures written for this benchmark, not real production incidents.
- A prior run of this same experiment (logged in the article's Sunday draft) used a task set that
  was never saved to durable storage and was lost before this repo existed. This repo's numbers
  are the real, saved, re-runnable ones; see `analysis.md`'s note on that process failure.

## License

MIT, see `LICENSE`.
