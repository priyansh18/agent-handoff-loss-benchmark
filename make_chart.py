import json
from PIL import Image, ImageDraw, ImageFont

summary = json.load(open("summary.json"))
a = summary["condition_a"]
b = summary["condition_b"]

W, H = 1600, 900
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

try:
    font_big = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 34)
    font_mid = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
    font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
except Exception:
    font_big = font_mid = font_small = ImageFont.load_default()

d.text((50, 30), "Single call vs. three-step pipeline, same 12 tasks", fill="black", font=font_big)

metrics = [
    ("Field accuracy (%)", a["field_accuracy_pct"], b["field_accuracy_pct"], 100),
    ("Total tokens", a["total_tokens"], b["total_tokens"], max(a["total_tokens"], b["total_tokens"]) * 1.1),
    ("Wall-clock time (s)", a["total_time_s"], b["total_time_s"], max(a["total_time_s"], b["total_time_s"]) * 1.1),
]

panel_w = W // 3
bar_max_h = 550
base_y = 780

for i, (label, va, vb, scale) in enumerate(metrics):
    cx = i * panel_w + panel_w // 2
    d.text((cx - 140, 110), label, fill="black", font=font_mid)

    ha = int(bar_max_h * (va / scale))
    hb = int(bar_max_h * (vb / scale))

    xa = cx - 110
    xb = cx + 10
    bar_w = 90

    d.rectangle([xa, base_y - ha, xa + bar_w, base_y], fill=(70, 110, 180))
    d.rectangle([xb, base_y - hb, xb + bar_w, base_y], fill=(200, 90, 60))

    d.text((xa, base_y - ha - 30), str(va), fill="black", font=font_small)
    d.text((xb, base_y - hb - 30), str(vb), fill="black", font=font_small)

    d.text((xa, base_y + 10), "single", fill="black", font=font_small)
    d.text((xb, base_y + 10), "pipeline", fill="black", font=font_small)

d.text((50, 850), "Image by author, generated from the run's own summary.json (llama3.1:8b, local, $0).", fill=(90, 90, 90), font=font_small)

img.save("results-single-vs-pipeline.png")
print("saved results-single-vs-pipeline.png")
