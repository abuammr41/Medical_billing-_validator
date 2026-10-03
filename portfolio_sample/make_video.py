"""Build a ~60s mp4 project video for the Medical Billing Audit Upwork listing."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

W, H = 1600, 900
FONTS = "C:/Windows/Fonts/"
OUTDIR = os.path.dirname(os.path.abspath(__file__))

BG_DEEP  = (10, 22, 28)
BG_PANEL = (16, 38, 46)
AMBER    = (227, 163, 61)
AMBER_HI = (241, 191, 107)
GREEN    = (76, 190, 147)
RED      = (224, 97, 84)
TEXT     = (243, 239, 230)
MUTED    = (150, 176, 184)

def font(path, size):
    return ImageFont.truetype(FONTS + path, size)

f_eyebrow = font("consola.ttf", 24)
f_h1 = font("georgiab.ttf", 78)
f_h1i = font("georgiaz.ttf", 78)
f_tag = font("corbel.ttf", 30)
f_small = font("consola.ttf", 20)
f_check = font("corbel.ttf", 26)
f_body = font("corbel.ttf", 24)

def base_bg():
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
    return Image.alpha_composite(img.convert("RGBA"), dots).convert("RGB")

def eyebrow_tr(draw, text):
    tw = draw.textlength(text, font=f_small)
    draw.text((W - 100 - tw, 70), text, font=f_small, fill=MUTED)

def framed_screenshot(path, caption, eyebrow_text):
    img = base_bg()
    draw = ImageDraw.Draw(img, "RGBA")
    draw.text((100, 70), eyebrow_text, font=f_eyebrow, fill=AMBER)
    shot = Image.open(path).convert("RGB")
    max_w, max_h = W - 240, H - 300
    ratio = min(max_w / shot.width, max_h / shot.height)
    nw, nh = int(shot.width * ratio), int(shot.height * ratio)
    shot = shot.resize((nw, nh), Image.LANCZOS)
    x = (W - nw) // 2
    y = 135
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rectangle([x - 14, y - 14 + 16, x + nw + 14, y + nh + 14 + 16], fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([x - 4, y - 4, x + nw + 4, y + nh + 4], outline=AMBER, width=3)
    img.paste(shot, (x, y))
    draw = ImageDraw.Draw(img, "RGBA")
    cap_w = draw.textlength(caption, font=f_tag)
    draw.text(((W - cap_w) / 2, y + nh + 30), caption, font=f_tag, fill=MUTED)
    return img

def title_card():
    img = base_bg()
    draw = ImageDraw.Draw(img, "RGBA")
    draw.text((120, 150), "MEDICAL  BILLING  \u2022  CLAIM  AUDITS", font=f_eyebrow, fill=AMBER)
    draw.text((118, 225), "Claims,", font=f_h1, fill=TEXT)
    draw.text((118, 225 + 90), "Audit-Ready", font=f_h1i, fill=AMBER_HI)
    draw.line([(122, 440), (122 + 150, 440)], fill=AMBER, width=4)
    draw.text((120, 470), "NPI, CPT, and ICD-10 checked before you submit \u2014",
               font=f_tag, fill=MUTED)
    draw.text((120, 505), "fewer denials, faster payment.", font=f_tag, fill=MUTED)
    return img

def checks_card():
    img = base_bg()
    draw = ImageDraw.Draw(img, "RGBA")
    draw.text((100, 70), "WHAT  GETS  CHECKED", font=f_eyebrow, fill=AMBER)
    checks = [
        ("NPI check digit", "Official Luhn / 80840-prefix validation"),
        ("CPT / HCPCS format", "Category I, II, III, and HCPCS Level II"),
        ("ICD-10-CM format", "With or without the decimal point"),
        ("Modifiers & units", "Up to 4 modifiers, positive whole units"),
        ("Dates & amounts", "Future dates, timely filing, negative charges"),
        ("Duplicate claims", "Same patient + provider + code + date"),
    ]
    col_w = (W - 200) // 2
    row_h = 115
    for i, (title, desc) in enumerate(checks):
        col = i // 3
        row = i % 3
        cx = 100 + col * col_w
        cy = 170 + row * row_h
        draw.rounded_rectangle([cx, cy, cx + 34, cy + 34], radius=8, outline=GREEN, width=3)
        draw.line([(cx + 7, cy + 18), (cx + 14, cy + 26)], fill=GREEN, width=4)
        draw.line([(cx + 14, cy + 26), (cx + 27, cy + 8)], fill=GREEN, width=4)
        draw.text((cx + 50, cy - 4), title, font=f_check, fill=TEXT)
        draw.text((cx + 50, cy + 30), desc, font=f_small, fill=MUTED)
    return img

def rejected_detail_card():
    img = base_bg()
    draw = ImageDraw.Draw(img, "RGBA")
    draw.text((100, 70), "EVERY  REJECTION,  EXPLAINED", font=f_eyebrow, fill=AMBER)
    draw.text((98, 150), "Not just", font=f_h1, fill=TEXT)
    draw.text((98, 150 + 90), "\u201cREJECTED.\u201d", font=f_h1i, fill=RED)

    # mini example row card
    bx, by, bw, bh = 850, 260, 650, 150
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=14, outline=MUTED, width=2)
    draw.text((bx + 24, by + 18), "CLM0134", font=f_small, fill=MUTED)
    tw = draw.textlength("FLAG", font=f_small)
    draw.rounded_rectangle([bx + bw - 24 - tw - 20, by + 14, bx + bw - 24, by + 42], radius=10, fill=RED)
    draw.text((bx + bw - 24 - tw - 10, by + 19), "FLAG", font=f_small, fill=(40, 10, 8))
    draw.text((bx + 24, by + 60), "CPT 'ABC12'", font=f_check, fill=TEXT)
    draw.text((bx + 24, by + 96), "Invalid CPT/HCPCS format", font=f_body, fill=AMBER_HI)

    draw.text((120, 470), "The audit report names the exact issue on every flagged claim \u2014",
               font=f_tag, fill=MUTED)
    draw.text((120, 505), "so your team fixes it once, not after a denial.", font=f_tag, fill=MUTED)
    return img

def compliance_card():
    img = base_bg()
    draw = ImageDraw.Draw(img, "RGBA")
    draw.text((100, 70), "SCOPE  \u2022  HANDLING", font=f_eyebrow, fill=AMBER)
    draw.text((98, 150), "Pre-submission", font=f_h1, fill=TEXT)
    draw.text((98, 150 + 90), "check, not payment.", font=f_h1i, fill=AMBER_HI)
    lines = [
        "Validates claim format and data quality before you submit.",
        "Does not verify payer-specific edits, eligibility, or adjudication.",
        "Claim files are handled as PHI \u2014 shared only through secure channels.",
    ]
    ly = 460
    for line in lines:
        draw.ellipse([120, ly + 8, 130, ly + 18], fill=AMBER)
        draw.text((145, ly), line, font=f_tag, fill=MUTED)
        ly += 44
    return img

def pricing_card():
    img = base_bg()
    draw = ImageDraw.Draw(img, "RGBA")
    draw.text((100, 70), "PRICING", font=f_eyebrow, fill=AMBER)
    tiers = [
        ("STARTER", "$25", "Up to 100 claims", "2-day delivery", MUTED),
        ("STANDARD", "$55", "Up to 500 claims", "3-day delivery", GREEN),
        ("ADVANCED", "$110", "Up to 2,000 claims", "4-day delivery", AMBER_HI),
    ]
    col_w, gap = 420, 50
    total_w = 3 * col_w + 2 * gap
    x0 = (W - total_w) // 2
    y0 = 240
    ch = 320
    for i, (name, price, scope, delivery, col) in enumerate(tiers):
        cx = x0 + i * (col_w + gap)
        draw.rounded_rectangle([cx, y0, cx + col_w, y0 + ch], radius=16, outline=col, width=3)
        draw.text((cx + 30, y0 + 36), name, font=f_small, fill=col)
        draw.text((cx + 28, y0 + 70), price, font=f_h1, fill=TEXT)
        draw.text((cx + 30, y0 + 180), scope, font=f_tag, fill=MUTED)
        draw.text((cx + 30, y0 + 220), delivery, font=f_tag, fill=MUTED)
    return img

def closing_card():
    img = base_bg()
    draw = ImageDraw.Draw(img, "RGBA")

    photo_path = "C:/Users/M Bilal/Desktop/my_photo_cropped.jpg"
    photo = Image.open(photo_path).convert("RGB")
    photo = photo.crop((85, 15, 555, 485))
    DIA = 220
    SS = 4
    photo = photo.resize((DIA * SS, DIA * SS), Image.LANCZOS)
    mask = Image.new("L", (DIA * SS, DIA * SS), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, DIA * SS, DIA * SS], fill=255)
    photo.putalpha(mask)
    photo = photo.resize((DIA, DIA), Image.LANCZOS)
    px, py = 150, (H - DIA) // 2
    ring_w = 8
    draw.ellipse([px - ring_w, py - ring_w, px + DIA + ring_w, py + DIA + ring_w], fill=AMBER)
    img.paste(photo, (px, py), photo)
    draw = ImageDraw.Draw(img, "RGBA")

    tx = px + DIA + 90
    draw.text((tx, 250), "Claims,", font=f_h1, fill=TEXT)
    draw.text((tx, 250 + 90), "Audit-Ready", font=f_h1i, fill=AMBER_HI)
    draw.line([(tx + 2, 460), (tx + 150, 460)], fill=AMBER, width=4)
    draw.text((tx, 490), "Starting at $25  \u2022  2-day delivery", font=f_tag, fill=MUTED)
    return img

frames = [
    (title_card(), 7.5),
    (framed_screenshot(os.path.join(OUTDIR, "Claims_1_RawClaims.png"), "Your claims export, as-is", "YOUR  DATA  IN"), 8.5),
    (checks_card(), 8.5),
    (framed_screenshot(os.path.join(OUTDIR, "Claims_2_AuditSummary.png"), "Clean-claim rate, totals, top issues", "AUDIT  SUMMARY"), 8.5),
    (rejected_detail_card(), 7.5),
    (compliance_card(), 7.5),
    (pricing_card(), 8.0),
    (closing_card(), 7.5),
]

for i, (im, _) in enumerate(frames):
    im.save(os.path.join(OUTDIR, f"_frame_{i}.png"))

from moviepy import ImageClip, concatenate_videoclips
from moviepy.video.fx import CrossFadeIn

FADE = 0.5
clips = []
for i, (im, dur) in enumerate(frames):
    path = os.path.join(OUTDIR, f"_frame_{i}.png")
    clip = ImageClip(path).with_duration(dur)
    if i > 0:
        clip = clip.with_effects([CrossFadeIn(FADE)])
    clips.append(clip)

video = concatenate_videoclips(clips, method="compose", padding=-FADE)
out_path = os.path.join(OUTDIR, "Project_Video_MedicalBilling_silent.mp4")
video.write_videofile(out_path, fps=24, codec="libx264", audio=False, preset="medium", bitrate="3500k")
print("saved", out_path, video.duration)

for i in range(len(frames)):
    os.remove(os.path.join(OUTDIR, f"_frame_{i}.png"))
