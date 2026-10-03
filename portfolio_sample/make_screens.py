"""Build dark-UI 'screenshot' mockups of the claims export and audit summary for the gallery."""
from PIL import Image, ImageDraw, ImageFont
import csv, openpyxl

FONTS = "C:/Windows/Fonts/"
W, H = 1600, 900

BG = (12, 24, 31)
HEADER_BG = (8, 17, 22)
ROW_A = (16, 32, 40)
ROW_B = (12, 26, 33)
AMBER = (227, 163, 61)
GREEN = (76, 190, 147)
RED = (224, 97, 84)
TEXT = (233, 238, 239)
MUTED = (140, 163, 171)

def f(path, size):
    return ImageFont.truetype(FONTS + path, size)

f_label = f("consola.ttf", 16)
f_title = f("corbelb.ttf", 30)
f_th = f("corbelb.ttf", 15)
f_cell = f("corbel.ttf", 17)
f_pill = f("corbelb.ttf", 14)

def rounded(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)

# ============================================================ IMAGE 1: raw claims export
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
d.text((40, 24), "PORTFOLIO SAMPLE", font=f_label, fill=AMBER)
d.text((40, 52), "Raw Claims Export", font=f_title, fill=TEXT)
d.text((W - 230, 30), "Claims_Sample.csv", font=f_label, fill=MUTED)

cols = ["CLAIM ID", "PATIENT", "NPI", "CPT", "ICD-10", "DOS", "BILLED", "STATUS"]
col_x = [40, 190, 330, 520, 640, 780, 920, 1040]
col_x.append(W - 40)

rows = list(csv.DictReader(open("Claims_Sample.csv", encoding="utf-8")))
wb = openpyxl.load_workbook("Claims_Audit_Report_SAMPLE.xlsx", data_only=True)
ws = wb["Audit_Report"]
headers = [c.value for c in ws[1]]
status_by_claim = {}
for r in ws.iter_rows(min_row=2, values_only=True):
    rec = dict(zip(headers, r))
    status_by_claim[rec.get("Claim ID") or rec.get("Claim_Id")] = rec.get("Validation_Status")

header_y = 110
d.rectangle([0, header_y, W, header_y + 40], fill=HEADER_BG)
for i, c in enumerate(cols):
    d.text((col_x[i], header_y + 11), c, font=f_th, fill=MUTED)

row_h = 38
y0 = header_y + 40
shown = rows[:19]
for i, r in enumerate(shown):
    ry = y0 + i * row_h
    d.rectangle([0, ry, W, ry + row_h], fill=(ROW_A if i % 2 == 0 else ROW_B))
    status = status_by_claim.get(r["Claim ID"], "READY_TO_SUBMIT")
    vals = [r["Claim ID"], r["Patient ID"], r["NPI"], r["CPT"], r["ICD-10"],
            r["Date of Service"], r["Billed Amount"]]
    for ci, v in enumerate(vals):
        d.text((col_x[ci], ry + 9), str(v), font=f_cell, fill=TEXT)
    is_ready = status == "READY_TO_SUBMIT"
    pill_text = "READY" if is_ready else "FLAG"
    pill_col = GREEN if is_ready else RED
    tw = d.textlength(pill_text, font=f_pill)
    px0, py0 = col_x[7], ry + 7
    pad = 10
    rounded(d, [px0, py0, px0 + tw + 2 * pad, py0 + 24], 12, (*pill_col, 255) if False else pill_col)
    d.text((px0 + pad, py0 + 4), pill_text, font=f_pill, fill=(10, 20, 16) if is_ready else (40, 10, 8))

d.rectangle([0, y0 + len(shown) * row_h, W, H], fill=BG)
more = len(rows) - len(shown)
d.text((40, y0 + len(shown) * row_h + 14), f"+ {more} more rows in the full file \u2014 142 claims total",
       font=f_label, fill=MUTED)

img.save("Claims_1_RawClaims.png")
print("saved Claims_1_RawClaims.png")

# ============================================================ IMAGE 2: audit summary
img2 = Image.new("RGB", (W, H), BG)
d2 = ImageDraw.Draw(img2)
d2.text((40, 24), "PORTFOLIO SAMPLE", font=f_label, fill=AMBER)
d2.text((40, 52), "Audit Summary", font=f_title, fill=TEXT)

sws = wb["Summary"]
vals = {row[0]: row[1] for row in sws.iter_rows(min_row=1, max_row=9, values_only=True) if row[0]}

stats = [
    ("CLAIMS PROCESSED", str(int(vals["Total claims"])), MUTED),
    ("CLEAN CLAIM RATE", f"{vals['Clean claim rate %']}%", GREEN),
    ("READY TO SUBMIT", str(int(vals["Ready to submit"])), GREEN),
    ("REJECTED", str(int(vals["Rejected"])), RED),
]
tile_w = (W - 80 - 3 * 20) / 4
ty = 120
for i, (label, value, col) in enumerate(stats):
    tx = 40 + i * (tile_w + 20)
    d2.rounded_rectangle([tx, ty, tx + tile_w, ty + 120], radius=10, outline=col, width=2)
    d2.text((tx + 18, ty + 20), label, font=f_label, fill=MUTED)
    d2.text((tx + 18, ty + 50), value, font=f("georgiab.ttf", 40), fill=TEXT)

money_y = ty + 150
money = [
    ("Total billed", f"${vals['Total billed (all)']:,.2f}"),
    ("Expected insurance payable", f"${vals['Expected insurance payable']:,.2f}"),
    ("Expected patient responsibility", f"${vals['Expected patient responsibility']:,.2f}"),
]
mw = (W - 80 - 2 * 20) / 3
for i, (label, value) in enumerate(money):
    mx = 40 + i * (mw + 20)
    d2.text((mx, money_y), label.upper(), font=f_label, fill=MUTED)
    d2.text((mx, money_y + 24), value, font=f("corbelb.ttf", 26), fill=TEXT)

ry0 = money_y + 90
d2.text((40, ry0), "TOP REJECTION REASONS", font=f_label, fill=AMBER)
ws3 = wb["Summary"]
reasons = []
grab = False
for row in ws3.iter_rows(values_only=True):
    if row[0] == "TOP REJECTION REASONS":
        grab = True
        continue
    if grab and row[0]:
        reasons.append((row[0], row[1]))

ry = ry0 + 30
bar_x0 = 480
max_c = max(c for _, c in reasons) if reasons else 1
for label, count in reasons[:6]:
    d2.text((40, ry), label, font=f_cell, fill=TEXT)
    bw = 160 * (count / max_c)
    d2.rounded_rectangle([bar_x0, ry + 4, bar_x0 + max(bw, 8), ry + 18], radius=6, fill=AMBER)
    d2.text((bar_x0 + 175, ry), str(count), font=f_cell, fill=MUTED)
    ry += 34

img2.save("Claims_2_AuditSummary.png")
print("saved Claims_2_AuditSummary.png")
