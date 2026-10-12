import json
import textwrap
from PIL import Image, ImageDraw, ImageFont

rows = {json.loads(l)["id"]: json.loads(l) for l in open("raw_results.jsonl")}
r = rows["retry-storm"]
plan_text = r["condition_b"]["plan_text"]
hint = r["condition_b"]["focus_hint"]
plan_len = r["condition_b"]["plan_len"]
hint_len = r["condition_b"]["hint_len"]
exec_root_cause = r["condition_b"]["executor_answer"]["root_cause"]
final_root_cause = r["condition_b"]["answer"]["root_cause"]

W, H = 1600, 950
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

try:
    f_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
    f_label = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    f_body = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
except Exception:
    f_title = f_label = f_body = ImageFont.load_default()

d.text((50, 30), "Planner notes truncated at the subgraph boundary (retry-storm task, real logged text)", fill="black", font=f_title)

# Planner box
d.rounded_rectangle([50, 110, 780, 400], radius=12, outline=(70, 110, 180), width=3)
d.text((70, 125), f"PLANNER output, verbatim ({plan_len} chars)", fill=(70, 110, 180), font=f_label)
wrapped_plan = "\n".join(textwrap.wrap(plan_text, width=58))
d.multiline_text((70, 165), wrapped_plan, fill="black", font=f_body, spacing=7)

# Arrow + boundary
d.line([780, 250, 930, 250], fill="black", width=3)
d.polygon([(930, 240), (960, 250), (930, 260)], fill="black")
d.text((785, 260), "state schema\nboundary:\nplan[:60]", fill=(180, 60, 60), font=f_body)

# Executor box
d.rounded_rectangle([980, 110, 1550, 400], radius=12, outline=(200, 90, 60), width=3)
d.text((1000, 125), f"What crosses the boundary ({hint_len} chars)", fill=(200, 90, 60), font=f_label)
wrapped_hint = "\n".join(textwrap.wrap(hint, width=48))
d.multiline_text((1000, 165), wrapped_hint, fill="black", font=f_body, spacing=7)
d.text((1000, 320), "No mention of \"retry storm\" or\n\"backoff\" -- cut before either appears.", fill=(180, 60, 60), font=f_body, spacing=6)

# Results box
d.rounded_rectangle([50, 450, 1550, 700], radius=12, outline=(70, 160, 90), width=3)
d.text((70, 465), "What each step answered for root_cause (ground truth needs \"retry storm\" or \"no backoff\")", fill=(70, 160, 90), font=f_label)
res_text = (
    f"Executor (saw the truncated hint above, but also the full report): \"{exec_root_cause}\" -- WRONG, same gap as the single call.\n\n"
    f"Reviewer (re-read the full original report a second time): \"{final_root_cause}\" -- CORRECT.\n\n"
    "The fix traces to the reviewer re-reading the source report, not to anything in the hint above."
)
wrapped_res = "\n".join(
    "\n".join(textwrap.wrap(line, width=110)) if line.strip() else ""
    for line in res_text.split("\n")
)
d.multiline_text((70, 510), wrapped_res, fill="black", font=f_body, spacing=8)

d.text((50, 900), "Image by author, generated directly from this run's raw_results.jsonl (make_handoff_diagram.py).", fill=(90, 90, 90), font=f_body)

img.save("handoff-diagram-arc5.png")
print("saved handoff-diagram-arc5.png")
print("plan_len", plan_len, "hint_len", hint_len)
print("exec root_cause:", exec_root_cause)
print("final root_cause:", final_root_cause)
