from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 900
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

try:
    f_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
    f_label = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
    f_body = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
except Exception:
    f_title = f_label = f_body = ImageFont.load_default()

d.text((50, 30), "Planner notes truncated at the subgraph state-schema boundary", fill="black", font=f_title)

# Planner box
d.rounded_rectangle([50, 120, 750, 320], radius=12, outline=(70, 110, 180), width=3)
d.text((70, 135), "PLANNER (full notes, retry-storm task)", fill=(70, 110, 180), font=f_label)
plan_text = (
    "\"Investigate the billing worker queue\n"
    "backlog. Check whether failed jobs are\n"
    "being retried immediately without backoff,\n"
    "causing a retry storm during the\n"
    "downstream outage window.\""
)
d.multiline_text((70, 175), plan_text, fill="black", font=f_body, spacing=8)
d.text((70, 290), "447 characters", fill=(120, 120, 120), font=f_body)

# Arrow + boundary
d.line([750, 220, 900, 220], fill="black", width=3)
d.polygon([(900, 210), (930, 220), (900, 230)], fill="black")
d.text((755, 230), "state schema\nboundary", fill=(180, 60, 60), font=f_body)

# Executor box
d.rounded_rectangle([950, 120, 1550, 320], radius=12, outline=(200, 90, 60), width=3)
d.text((970, 135), "EXECUTOR (what crosses the boundary)", fill=(200, 90, 60), font=f_label)
hint_text = '"Investigate the billing worker queue\nbacklog'
d.multiline_text((970, 175), hint_text, fill="black", font=f_body, spacing=8)
d.text((970, 230), "60 characters -- cut mid-word, mid-sentence", fill=(180, 60, 60), font=f_body)
d.text((970, 290), "focus_hint = plan_notes.split('.')[0][:60]", fill=(120, 120, 120), font=f_body)

# Reviewer box
d.rounded_rectangle([50, 420, 1550, 620], radius=12, outline=(70, 160, 90), width=3)
d.text((70, 435), "REVIEWER (re-reads the ORIGINAL REPORT, not the planner's notes)", fill=(70, 160, 90), font=f_label)
rev_text = (
    "Executor (missed \"retry storm\"): root_cause = \"downstream outage\"\n"
    "Reviewer, after re-reading the full report: root_cause = \"downstream outage caused a retry storm\"\n\n"
    "The fix came from a second read of the source report -- not from anything the planner's\n"
    "truncated hint carried across the boundary."
)
d.multiline_text((70, 480), rev_text, fill="black", font=f_body, spacing=10)

d.text((50, 850), "Image by author, generated from this run's own raw_results.jsonl.", fill=(90, 90, 90), font=f_body)

img.save("handoff-diagram-arc5.png")
print("saved handoff-diagram-arc5.png")
