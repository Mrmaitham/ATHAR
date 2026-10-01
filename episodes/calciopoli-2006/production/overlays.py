"""Render BY ATHAR overlay PNGs (1920x1080 RGBA) for every scene.

Style follows references/documentary_format.md §4:
navy #1F2A3A, gold #E8A317, black #111111, white; Playfair Display for
titles/quotes, Montserrat for names/numbers.
"""
import json, os, re, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H = 1920, 1080
NAVY, GOLD, BLACK, WHITE = (31, 42, 58), (232, 163, 23), (17, 17, 17), (255, 255, 255)
FD = "/home/user/ATHAR/assets/fonts/"


def font(name, size, weight=None):
    f = ImageFont.truetype(FD + name, size)
    if weight:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def mont(size, w=700): return font("Montserrat.ttf", size, w)
def play(size, w=600): return font("Playfair.ttf", size, w)
def playi(size, w=500): return font("PlayfairItalic.ttf", size, w)


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines


def parse(o):
    m = re.match(r'^(big number|number|name|names|place|date|quote|list)\s+"(.*?)"\s*(?:—\s*(.*))?$', o)
    if m: return m.group(1), m.group(2), m.group(3)
    m = re.match(r'^"(.*)"$', o)
    if m: return "title", m.group(1), None
    return None, o, None


def lower_third(img, main, sub, y=880):
    d = ImageDraw.Draw(img)
    f1, f2 = mont(44, 800), mont(28, 700)
    w1 = d.textlength(main, font=f1) + 48
    d.rectangle([80, y, 80 + w1, y + 72], fill=BLACK + (235,))
    d.text((104, y + 12), main, font=f1, fill=WHITE)
    if sub:
        w2 = d.textlength(sub, font=f2) + 36
        d.rectangle([80, y + 72, 80 + w2, y + 72 + 46], fill=GOLD + (245,))
        d.text((98, y + 80), sub, font=f2, fill=BLACK)


def date_tag(img, text):
    d = ImageDraw.Draw(img); f = mont(30, 700)
    w = d.textlength(text, font=f) + 40
    d.rectangle([80, 80, 80 + w, 130], fill=GOLD + (245,))
    d.text((100, 87), text, font=f, fill=BLACK)


def stat(img, big, small, size=120):
    d = ImageDraw.Draw(img)
    fb, fs = mont(size, 800), mont(30, 600)
    lines = wrap(d, small, fs, 640) if small else []
    bw = max(d.textlength(big, font=fb), *(d.textlength(l, font=fs) for l in lines or [""])) + 80
    bh = size + 60 + 40 * len(lines)
    x, y = 100, H // 2 - bh // 2
    d.rectangle([x, y, x + bw, y + bh], fill=NAVY + (235,), outline=GOLD, width=4)
    d.text((x + 40, y + 20), big, font=fb, fill=GOLD)
    for i, l in enumerate(lines):
        d.text((x + 40, y + size + 40 + 40 * i), l, font=fs, fill=WHITE)


def quote(img, text, attr):
    # dark gradient band at bottom + italic serif quote in gold
    band = Image.new("RGBA", (W, 420), (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
    for i in range(420):
        bd.line([(0, i), (W, i)], fill=(10, 12, 18, int(210 * i / 420)))
    img.alpha_composite(band, (0, H - 420))
    d = ImageDraw.Draw(img); fq, fa = playi(50, 500), mont(26, 600)
    lines = wrap(d, "“" + text + "”", fq, 1500)
    y = H - 110 - 64 * len(lines) - (40 if attr else 0)
    for l in lines:
        d.text((W // 2 - d.textlength(l, font=fq) / 2, y), l, font=fq, fill=GOLD); y += 64
    if attr:
        a = "— " + attr
        d.text((W // 2 - d.textlength(a, font=fa) / 2, y + 14), a, font=fa, fill=WHITE)


def list_panel(img, title, items, full=False):
    d = ImageDraw.Draw(img)
    if full:
        x0, x1 = 360, W - 360
    else:
        x0, x1 = W - 760, W - 80
    ft, fi = play(52, 700), mont(34, 600)
    h = 140 + 70 * len(items)
    y0 = H // 2 - h // 2
    d.rectangle([x0, y0, x1, y0 + h], fill=NAVY + (240,))
    d.ellipse([x0 + 40, y0 + 36, x0 + 90, y0 + 86], fill=GOLD)
    d.text((x0 + 110, y0 + 34), title, font=ft, fill=WHITE)
    d.line([x0 + 40, y0 + 112, x1 - 40, y0 + 112], fill=GOLD, width=3)
    for i, it in enumerate(items):
        yy = y0 + 140 + 70 * i
        d.ellipse([x0 + 50, yy + 10, x0 + 74, yy + 34], fill=GOLD)
        d.text((x0 + 96, yy), it, font=fi, fill=WHITE)


def chapter_card(title, sub):
    img = Image.new("RGBA", (W, H), NAVY + (255,))
    # subtle vignette
    v = Image.new("L", (W, H), 0); vd = ImageDraw.Draw(v)
    vd.ellipse([-400, -300, W + 400, H + 300], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(200))
    dark = Image.new("RGBA", (W, H), (12, 16, 24, 255))
    img = Image.composite(img, dark, v)
    d = ImageDraw.Draw(img); ft, fs = play(104, 700), mont(34, 600)
    d.text((W // 2 - d.textlength(title, font=ft) / 2, H // 2 - 110), title, font=ft, fill=WHITE)
    d.line([W // 2 - 140, H // 2 + 40, W // 2 + 140, H // 2 + 40], fill=GOLD, width=3)
    if sub:
        d.text((W // 2 - d.textlength(sub, font=fs) / 2, H // 2 + 66), sub, font=fs, fill=GOLD)
    return img


def badge():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = mont(24, 800); t = "BY ATHAR"; w = d.textlength(t, font=f) + 28
    d.rectangle([W - 60 - w, 50, W - 60, 92], fill=GOLD + (230,))
    d.text((W - 60 - w + 14, 57), t, font=f, fill=BLACK)
    return img


def dark_bg(path):
    im = Image.open(path).convert("RGB").resize((W, H))
    im = im.filter(ImageFilter.GaussianBlur(6))
    im = ImageEnhance.Brightness(im).enhance(0.35)
    return im.convert("RGBA")


if __name__ == "__main__":
    sc = json.load(open("scenes.json"))
    os.makedirs("overlays", exist_ok=True); os.makedirs("cards", exist_ok=True)
    badge().save("overlays/badge.png")
    last_img = None
    for s in sc:
        sid, i = s["id"], int(s["id"][1:])
        imgs = sorted(glob.glob(f"images/I{i:03d}*.png")) if False else sorted(glob.glob(f"images/I{i*10+1:04d}.png") + glob.glob(f"images/I{i*10+2:04d}.png") + glob.glob(f"images/I{i*10+3:04d}.png") + glob.glob(f"images/I{i*10+4:04d}.png"))
        if s["type"] == "CARD":
            ov = s["overlay"][0] if s["overlay"] else ""
            kind, text, attr = parse(ov) if ov else (None, "", None)
            vis = s["visual"].strip('"')
            if sid == "S010":
                card = chapter_card("CALCIOPOLI", "The Summer Italian Football Was Convicted and Crowned")
            elif sid == "S107":
                card = chapter_card("BY ATHAR", "Thank you for watching")
            elif " · Chapter " in vis:
                parts = vis.split(" · ")
                card = chapter_card(parts[0], " · ".join(parts[1:]))
            else:
                card = dark_bg(last_img)
                if vis.startswith("list"):
                    body = re.match(r'list "(.*)"', s["visual"]).group(1)
                    head, rest = body.split(": ", 1)
                    list_panel(card, head, [x.strip() for x in rest.split(" · ")], full=True)
                elif kind in ("number", "big number"):
                    big, *small = text.split(" · ")
                    stat(card, big, " · ".join(small), size=150 if kind == "big number" else 130)
                elif kind == "quote":
                    quote(card, text, attr)
            card.convert("RGB").save(f"cards/{sid}.png")
            continue
        if imgs: last_img = imgs[-1]
        if not s["overlay"]: continue
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for o in s["overlay"]:
            kind, text, attr = parse(o)
            parts = text.split(" · ")
            if kind in ("name", "place"):
                lower_third(ov, parts[0], " · ".join(parts[1:]))
            elif kind == "names":
                lower_third(ov, parts[0] + "  ·  " + parts[1], " · ".join(parts[2:]))
            elif kind == "date":
                date_tag(ov, text)
            elif kind in ("number", "big number"):
                stat(ov, parts[0], " · ".join(parts[1:]))
            elif kind == "quote":
                quote(ov, text, attr)
            elif kind == "list":
                list_panel(ov, "The accused clubs", parts)
        if sid == "S095":  # name + quote: move name up
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            lower_third(ov, "Giacinto Facchetti", "Inter President (died September 2006)", y=120)
            quote(ov, "Tell the coach to stay calm.", "Paolo Bergamo to Giacinto Facchetti, Feb 2005, per published transcripts")
        ov.save(f"overlays/{sid}.png")
    print("done")
