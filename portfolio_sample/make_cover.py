"""Generate the square Upwork project-cover image for the Medical Billing Audit listing."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W = H = 1200
FONTS = "C:/Windows/Fonts/"

BG_DEEP  = (10, 22, 28)
BG_PANEL = (16, 38, 46)
AMBER    = (227, 163, 61)
AMBER_HI = (241, 191, 107)
GREEN    = (76, 190, 147)
TEXT     = (243, 239, 230)
MUTED    = (150, 176, 184)

def font(path, size):
    return ImageFont.truetype(FONTS + path, size)

f_eyebrow = font("consola.ttf", 24)
f_headline = font("georgiab.ttf", 128)
f_headline_i = font("georgiaz.ttf", 128)
f_tagline = font("corbel.ttf", 32)
f_tag_small = font("consola.ttf", 22)
f_check = font("corbel.ttf", 28)

img = Image.new("RGB", (W, H), BG_DEEP)
grad = Image.new("L", (W, H), 0)
gd = ImageDraw.Draw(grad)
for y in range(H):
    gd.line([(0, y), (W, y)], fill=int(255 * (y / H)))
grad = grad.filter(ImageFilter.GaussianBlur(2))
panel = Image.new("RGB", (W, H), BG_PANEL)
img = Image.composite(panel, img, grad)

dots = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dd = ImageDraw.Draw(dots)
for gx in range(60, W, 60):
    for gy in range(60, H, 60):
        dd.ellipse([gx, gy, gx + 2, gy + 2], fill=(255, 255, 255, 10))
img = Image.alpha_composite(img.convert("RGBA"), dots).convert("RGB")
draw = ImageDraw.Draw(img, "RGBA")

MARGIN = 90

draw.text((MARGIN, MARGIN), "MEDICAL BILLING  \u2022  CLAIM AUDITS", font=f_eyebrow, fill=AMBER)
tag_tr = "HIPAA-AWARE"
tw0 = draw.textlength(tag_tr, font=f_tag_small)
draw.text((W - MARGIN - tw0, MARGIN + 2), tag_tr, font=f_tag_small, fill=MUTED)

hy = MARGIN + 55
draw.text((MARGIN, hy), "Claims,", font=f_headline, fill=TEXT)
draw.text((MARGIN, hy + 130), "Audit-Ready", font=f_headline_i, fill=AMBER_HI)

ry = hy + 130 + 150
draw.line([(MARGIN, ry), (MARGIN + 150, ry)], fill=AMBER, width=4)

tagline = "NPI, CPT, and ICD-10 checked before you submit \u2014\nfewer denials, faster payment."
draw.multiline_text((MARGIN, ry + 26), tagline, font=f_tagline, fill=MUTED, spacing=12)

# ---- photo ----
photo_path = "C:/Users/M Bilal/Desktop/my_photo_cropped.jpg"
photo = Image.open(photo_path).convert("RGB")
photo = photo.crop((85, 15, 555, 485))

DIA = 340
SS = 4
photo = photo.resize((DIA * SS, DIA * SS), Image.LANCZOS)
mask = Image.new("L", (DIA * SS, DIA * SS), 0)
ImageDraw.Draw(mask).ellipse([0, 0, DIA * SS, DIA * SS], fill=255)
photo.putalpha(mask)
photo = photo.resize((DIA, DIA), Image.LANCZOS)

px, py = MARGIN, H - MARGIN - DIA

shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
pad = 30
sd.ellipse([px - pad, py - pad + 18, px + DIA + pad, py + DIA + pad + 18], fill=(0, 0, 0, 120))
shadow = shadow.filter(ImageFilter.GaussianBlur(28))
img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
draw = ImageDraw.Draw(img, "RGBA")

ring_w = 10
draw.ellipse([px - ring_w, py - ring_w, px + DIA + ring_w, py + DIA + ring_w], fill=AMBER)
img.paste(photo, (px, py), photo)
draw = ImageDraw.Draw(img, "RGBA")

bD = 80
bx = px + DIA - bD + 16
by = py + DIA - bD + 16
draw.ellipse([bx - 6, by - 6, bx + bD + 6, by + bD + 6], fill=BG_PANEL)
draw.ellipse([bx, by, bx + bD, by + bD], fill=GREEN)
cx1, cy1 = bx + bD * 0.28, by + bD * 0.52
cx2, cy2 = bx + bD * 0.44, by + bD * 0.70
cx3, cy3 = bx + bD * 0.76, by + bD * 0.32
draw.line([(cx1, cy1), (cx2, cy2)], fill=TEXT, width=7, joint="curve")
draw.line([(cx2, cy2), (cx3, cy3)], fill=TEXT, width=7, joint="curve")

# ---- checklist panel ----
checks = ["NPI check digit", "CPT / HCPCS format", "ICD-10 format", "Duplicate claims"]
clx = px + DIA + 110
cly0 = py + 10
row_h = 64
for i, label in enumerate(checks):
    cy = cly0 + i * row_h
    draw.rounded_rectangle([clx, cy, clx + 36, cy + 36], radius=8, outline=GREEN, width=3)
    draw.line([(clx + 8, cy + 19), (clx + 15, cy + 27)], fill=GREEN, width=4)
    draw.line([(clx + 15, cy + 27), (clx + 29, cy + 9)], fill=GREEN, width=4)
    draw.text((clx + 50, cy + 4), label, font=f_check, fill=TEXT)

out_path = "C:/Users/M Bilal/Desktop/medical.bill/portfolio_sample/Project_Cover_MedicalBilling.png"
img.save(out_path, "PNG")
print("saved", out_path, img.size)
