"""Generate two branded one-page PDF sample documents for the Medical Billing Upwork listing."""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os, openpyxl

OUTDIR = os.path.dirname(os.path.abspath(__file__))
FONTS = "C:/Windows/Fonts/"

pdfmetrics.registerFont(TTFont("Georgia", FONTS + "georgia.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-Bold", FONTS + "georgiab.ttf"))
pdfmetrics.registerFont(TTFont("Corbel", FONTS + "corbel.ttf"))
pdfmetrics.registerFont(TTFont("Corbel-Bold", FONTS + "corbelb.ttf"))
pdfmetrics.registerFont(TTFont("Consolas", FONTS + "consola.ttf"))

BG_DEEP = (10/255, 22/255, 28/255)
BG_PANEL = (16/255, 38/255, 46/255)
AMBER = (227/255, 163/255, 61/255)
AMBER_HI = (241/255, 191/255, 107/255)
GREEN = (76/255, 190/255, 147/255)
RED = (224/255, 97/255, 84/255)
TEXT = (243/255, 239/255, 230/255)
MUTED = (160/255, 184/255, 192/255)

W, H = LETTER
MARGIN = 56

def bg(c):
    c.setFillColorRGB(*BG_DEEP)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColorRGB(*BG_PANEL)
    c.rect(0, H - 170, W, 170, fill=1, stroke=0)

def eyebrow(c, text, y):
    c.setFont("Consolas", 10)
    c.setFillColorRGB(*AMBER)
    c.drawString(MARGIN, y, text)

def footer(c):
    c.setFont("Consolas", 8.5)
    c.setFillColorRGB(*MUTED)
    c.drawString(MARGIN, 34, "Prepared by Muhammad B.  \u2022  Pre-submission claims auditing  \u2022  Upwork Project Catalog")
    c.setStrokeColorRGB(*AMBER)
    c.setLineWidth(1)
    c.line(MARGIN, 50, W - MARGIN, 50)

wb = openpyxl.load_workbook(os.path.join(OUTDIR, "Claims_Audit_Report_SAMPLE.xlsx"), data_only=True)
sws = wb["Summary"]
vals = {}
reasons = []
grab = False
for row in sws.iter_rows(values_only=True):
    if row[0] == "TOP REJECTION REASONS":
        grab = True
        continue
    if grab and row[0]:
        reasons.append((row[0], row[1]))
    elif row[0]:
        vals[row[0]] = row[1]

# ============================================================= DOC 1
path1 = os.path.join(OUTDIR, "Sample_Claims_Audit_Preview.pdf")
c = canvas.Canvas(path1, pagesize=LETTER)
bg(c)
eyebrow(c, "MEDICAL  BILLING  \u2022  CLAIM  AUDITS", H - 70)
c.setFont("Georgia-Bold", 28)
c.setFillColorRGB(*TEXT)
c.drawString(MARGIN, H - 112, "Sample Claims Audit Report")
c.setFont("Corbel", 11)
c.setFillColorRGB(*MUTED)
c.drawString(MARGIN, H - 140, "Fully synthetic demo claims generated for this portfolio sample \u2014 no real patient data.")

stats = [
    ("CLAIMS PROCESSED", str(int(vals["Total claims"])), MUTED),
    ("CLEAN CLAIM RATE", f"{vals['Clean claim rate %']}%", GREEN),
    ("READY TO SUBMIT", str(int(vals["Ready to submit"])), GREEN),
    ("REJECTED", str(int(vals["Rejected"])), RED),
]
tile_w = (W - 2 * MARGIN - 3 * 16) / 4
ty = H - 240
for i, (label, value, col) in enumerate(stats):
    tx = MARGIN + i * (tile_w + 16)
    c.setStrokeColorRGB(*col)
    c.setLineWidth(1.2)
    c.roundRect(tx, ty, tile_w, 80, 8, stroke=1, fill=0)
    c.setFont("Consolas", 7.4)
    c.setFillColorRGB(*MUTED)
    c.drawString(tx + 12, ty + 56, label)
    c.setFont("Georgia-Bold", 18)
    c.setFillColorRGB(*TEXT)
    c.drawString(tx + 12, ty + 26, value)

my = ty - 50
money = [
    ("Total billed", f"${vals['Total billed (all)']:,.2f}"),
    ("Expected insurance payable", f"${vals['Expected insurance payable']:,.2f}"),
    ("Expected patient responsibility", f"${vals['Expected patient responsibility']:,.2f}"),
]
mw = (W - 2 * MARGIN - 2 * 16) / 3
for i, (label, value) in enumerate(money):
    mx = MARGIN + i * (mw + 16)
    c.setFont("Consolas", 7.4)
    c.setFillColorRGB(*MUTED)
    c.drawString(mx, my, label.upper())
    c.setFont("Corbel-Bold", 16)
    c.setFillColorRGB(*TEXT)
    c.drawString(mx, my - 22, value)

ry0 = my - 60
c.setFont("Corbel-Bold", 13)
c.setFillColorRGB(*TEXT)
c.drawString(MARGIN, ry0, "Top Rejection Reasons")
yy = ry0 - 26
bar_x0 = MARGIN + 260
bar_max_w = W - MARGIN - bar_x0 - 50
max_c = max(c2 for _, c2 in reasons) if reasons else 1
for label, count in reasons[:6]:
    c.setFont("Corbel", 10)
    c.setFillColorRGB(*TEXT)
    c.drawString(MARGIN, yy, label)
    bw = bar_max_w * (count / max_c)
    c.setFillColorRGB(*AMBER)
    c.roundRect(bar_x0, yy - 4, max(bw, 8), 13, 4, stroke=0, fill=1)
    c.setFont("Consolas", 9.5)
    c.setFillColorRGB(*MUTED)
    c.drawString(bar_x0 + bw + 10, yy, str(count))
    yy -= 26

note_y = yy - 20
c.setFont("Corbel", 9.5)
c.setFillColorRGB(*MUTED)
c.drawString(MARGIN, note_y, "Your delivered report also includes a full Audit_Report sheet (every claim, pass/fail, issues)")
c.drawString(MARGIN, note_y - 15, "and a Rejected_Claims sheet listing only what needs fixing before resubmission.")

footer(c)
c.showPage()
c.save()
print("saved", path1)

# ============================================================= DOC 2
path2 = os.path.join(OUTDIR, "Process_And_Pricing.pdf")
c = canvas.Canvas(path2, pagesize=LETTER)
bg(c)
eyebrow(c, "HOW  IT  WORKS", H - 70)
c.setFont("Georgia-Bold", 28)
c.setFillColorRGB(*TEXT)
c.drawString(MARGIN, H - 112, "Clean Claims, Before You Submit")
c.setFont("Corbel", 11)
c.setFillColorRGB(*MUTED)
c.drawString(MARGIN, H - 140, "A simple, four-step process \u2014 you only need to send your claims export.")

steps = [
    ("1", "Send your claims export", "CSV or Excel \u2014 any clearinghouse or EHR export, any column names."),
    ("2", "Automated validation runs", "NPI check digit, CPT/HCPCS and ICD-10 format, modifiers, duplicates, dates, amounts."),
    ("3", "You review the audit report", "Every claim flagged READY or REJECTED, with the exact issue listed."),
    ("4", "You submit clean claims", "Fix the flagged few, resubmit with confidence \u2014 fewer denials, faster payment."),
]
sy = H - 185
row_h = 54
for i, (num, title, desc) in enumerate(steps):
    ry = sy - i * row_h
    c.setStrokeColorRGB(*AMBER)
    c.setLineWidth(1.2)
    c.circle(MARGIN + 14, ry - 6, 14, stroke=1, fill=0)
    c.setFont("Consolas", 12)
    c.setFillColorRGB(*AMBER_HI)
    c.drawCentredString(MARGIN + 14, ry - 10.5, num)
    c.setFont("Corbel-Bold", 12.5)
    c.setFillColorRGB(*TEXT)
    c.drawString(MARGIN + 42, ry - 2, title)
    c.setFont("Corbel", 10)
    c.setFillColorRGB(*MUTED)
    c.drawString(MARGIN + 42, ry - 18, desc)

py0 = sy - len(steps) * row_h - 36
c.setFont("Corbel-Bold", 13)
c.setFillColorRGB(*TEXT)
c.drawString(MARGIN, py0, "Pricing")

tiers = [
    ("STARTER", "$25", "Up to 100 claims", "2-day delivery", MUTED),
    ("STANDARD", "$55", "Up to 500 claims", "3-day delivery", GREEN),
    ("ADVANCED", "$110", "Up to 2,000 claims", "4-day delivery", AMBER_HI),
]
col_w = (W - 2 * MARGIN - 2 * 16) / 3
cy0 = py0 - 120
for i, (name, price, scope, delivery, col) in enumerate(tiers):
    cx = MARGIN + i * (col_w + 16)
    c.setStrokeColorRGB(*col)
    c.setLineWidth(1.3)
    c.roundRect(cx, cy0, col_w, 100, 10, stroke=1, fill=0)
    c.setFont("Consolas", 9)
    c.setFillColorRGB(*col)
    c.drawString(cx + 14, cy0 + 76, name)
    c.setFont("Georgia-Bold", 22)
    c.setFillColorRGB(*TEXT)
    c.drawString(cx + 14, cy0 + 48, price)
    c.setFont("Corbel", 9.5)
    c.setFillColorRGB(*MUTED)
    c.drawString(cx + 14, cy0 + 28, scope)
    c.drawString(cx + 14, cy0 + 14, delivery)

cta_y = cy0 - 30
c.setFont("Corbel-Bold", 11)
c.setFillColorRGB(*AMBER_HI)
c.drawString(MARGIN, cta_y, "Message me on Upwork to get started \u2014 I'll confirm scope before you order.")
c.setFont("Corbel", 9)
c.setFillColorRGB(*MUTED)
c.drawString(MARGIN, cta_y - 18,
             "Pre-submission format/data-quality check only \u2014 not a payer-adjudication or eligibility service.")

footer(c)
c.showPage()
c.save()
print("saved", path2)
