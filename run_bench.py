import json
import re
import time
import urllib.request
from tasks import TASKS

MODEL = "llama3.1:8b"
SEED = 7
API = "http://localhost:11434/api/generate"


def call(prompt, max_tokens=300):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0, "seed": SEED, "num_predict": max_tokens},
    }
    req = urllib.request.Request(
        API, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    elapsed = time.time() - t0
    prompt_tokens = data.get("prompt_eval_count", 0)
    output_tokens = data.get("eval_count", 0)
    return data.get("response", ""), prompt_tokens + output_tokens, elapsed


def extract_json(text):
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except Exception:
        return {}


def grade(answer, keywords):
    if not answer:
        return False
    a = answer.lower()
    return any(k.lower() in a for k in keywords)


def run_condition_a(task):
    prompt = (
        "Read the incident report and extract three fields as JSON only, "
        'with keys "root_cause", "affected_component", "fix_action". '
        "No explanation, just the JSON object.\n\nReport:\n" + task["report"]
    )
    text, tokens, elapsed = call(prompt)
    parsed = extract_json(text)
    return parsed, tokens, elapsed


def run_condition_b(task):
    total_tokens = 0
    total_time = 0.0

    planner_prompt = (
        "You are investigating an incident. Write a short investigation note "
        "(2-3 sentences) describing what to look for, based on this report. "
        "Do not answer yet, just describe your investigation plan.\n\nReport:\n"
        + task["report"]
    )
    plan_text, tok, el = call(planner_prompt, max_tokens=150)
    total_tokens += tok
    total_time += el

    focus_hint = plan_text.split(".")[0][:60] if plan_text else ""

    executor_prompt = (
        "Read the incident report and extract three fields as JSON only, "
        'with keys "root_cause", "affected_component", "fix_action". '
        f'Investigation focus hint: "{focus_hint}". '
        "No explanation, just the JSON object.\n\nReport:\n" + task["report"]
    )
    exec_text, tok, el = call(executor_prompt)
    total_tokens += tok
    total_time += el
    exec_json = extract_json(exec_text)

    reviewer_prompt = (
        "Here is an incident report and a draft extraction. Check the draft against "
        "the report and correct any field that is incomplete or wrong. Return corrected "
        'JSON only, with keys "root_cause", "affected_component", "fix_action".\n\n'
        "Report:\n" + task["report"] + "\n\nDraft JSON:\n" + json.dumps(exec_json)
    )
    rev_text, tok, el = call(reviewer_prompt)
    total_tokens += tok
    total_time += el
    rev_json = extract_json(rev_text)
    if not rev_json:
        rev_json = exec_json

    return rev_json, total_tokens, total_time, focus_hint, plan_text, exec_json


def main():
    results = []
    a_correct = 0
    a_tasks_all3 = 0
    a_tokens = 0
    a_time = 0.0

    b_correct = 0
    b_tasks_all3 = 0
    b_tokens = 0
    b_time = 0.0

    for task in TASKS:
        a_answer, a_tok, a_el = run_condition_a(task)
        a_fields = {
            f: grade(a_answer.get(f, ""), task[f])
            for f in ("root_cause", "affected_component", "fix_action")
        }
        a_correct += sum(a_fields.values())
        a_tasks_all3 += 1 if all(a_fields.values()) else 0
        a_tokens += a_tok
        a_time += a_el

        b_answer, b_tok, b_el, focus_hint, plan_text, exec_answer = run_condition_b(task)
        b_fields = {
            f: grade(b_answer.get(f, ""), task[f])
            for f in ("root_cause", "affected_component", "fix_action")
        }
        exec_fields = {
            f: grade(exec_answer.get(f, ""), task[f])
            for f in ("root_cause", "affected_component", "fix_action")
        }
        b_correct += sum(b_fields.values())
        b_tasks_all3 += 1 if all(b_fields.values()) else 0
        b_tokens += b_tok
        b_time += b_el

        dropped = len(plan_text) > len(focus_hint) if plan_text else False

        results.append(
            {
                "id": task["id"],
                "condition_a": {"answer": a_answer, "fields_correct": a_fields},
                "condition_b": {
                    "answer": b_answer,
                    "fields_correct": b_fields,
                    "executor_answer": exec_answer,
                    "executor_fields_correct": exec_fields,
                    "plan_text": plan_text,
                    "focus_hint": focus_hint,
                    "dropped_from_handoff": dropped,
                    "plan_len": len(plan_text) if plan_text else 0,
                    "hint_len": len(focus_hint) if focus_hint else 0,
                },
            }
        )
        print(f"done: {task['id']}  A_all3={all(a_fields.values())}  B_all3={all(b_fields.values())}")

    summary = {
        "condition_a": {
            "field_accuracy": f"{a_correct}/{len(TASKS)*3}",
            "field_accuracy_pct": round(100 * a_correct / (len(TASKS) * 3), 1),
            "tasks_all3_correct": f"{a_tasks_all3}/{len(TASKS)}",
            "total_tokens": a_tokens,
            "total_time_s": round(a_time, 1),
        },
        "condition_b": {
            "field_accuracy": f"{b_correct}/{len(TASKS)*3}",
            "field_accuracy_pct": round(100 * b_correct / (len(TASKS) * 3), 1),
            "tasks_all3_correct": f"{b_tasks_all3}/{len(TASKS)}",
            "total_tokens": b_tokens,
            "total_time_s": round(b_time, 1),
        },
        "handoff_loss_tasks": sum(1 for r in results if r["condition_b"]["dropped_from_handoff"]),
        "total_tasks": len(TASKS),
    }

    with open("raw_results.jsonl", "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    with open("summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
