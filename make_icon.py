#!/usr/bin/env python3
"""나와의 메모 앱 아이콘 생성 + 단일 HTML의 favicon/manifest data URL 갱신 (idempotent)"""
import re, json, base64, io, urllib.parse, pathlib
from PIL import Image, ImageDraw, ImageFilter

CREAM = (248, 242, 229)
CARAMEL = (169, 106, 59)
INK = (255, 246, 230)
GLOW = (255, 251, 240)
SHADOW = (120, 78, 45)


def make(size):
    S = size * 4
    img = Image.new("RGBA", (S, S), CREAM + (255,))

    # soft warm glow — solid light color at alpha 0, so blurring does not darken
    glow = Image.new("RGBA", (S, S), GLOW + (0,))
    ImageDraw.Draw(glow).ellipse((-S * 0.25, -S * 0.55, S * 1.25, S * 0.55), fill=GLOW + (230,))
    glow = glow.filter(ImageFilter.GaussianBlur(S * 0.05))
    img = Image.alpha_composite(img, glow)

    d = ImageDraw.Draw(img)
    pad = S * 0.06
    d.rounded_rectangle((pad, pad, S - pad, S - pad), radius=S * 0.22,
                        outline=(214, 194, 166, 120), width=max(2, int(S * 0.006)))

    bx0, by0, bx1, by1 = S * 0.17, S * 0.27, S * 0.83, S * 0.72

    sh = Image.new("RGBA", (S, S), SHADOW + (0,))
    ImageDraw.Draw(sh).rounded_rectangle((bx0, by0 + S * 0.02, bx1, by1 + S * 0.02),
                                         radius=S * 0.17, fill=SHADOW + (60,))
    sh = sh.filter(ImageFilter.GaussianBlur(S * 0.022))
    img = Image.alpha_composite(img, sh)
    d = ImageDraw.Draw(img)

    d.rounded_rectangle((bx0, by0, bx1, by1), radius=S * 0.17, fill=CARAMEL)
    d.polygon([(S * 0.33, by1 - S * 0.03), (S * 0.285, by1 + S * 0.11), (S * 0.47, by1 - S * 0.03)],
              fill=CARAMEL)

    cy = (by0 + by1) / 2
    r = S * 0.048
    for cx in (S * 0.335, S * 0.5, S * 0.665):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=INK)

    def star(cx, cy_, rr, fill):
        d.polygon([(cx, cy_ - rr), (cx + rr * 0.28, cy_ - rr * 0.28), (cx + rr, cy_),
                   (cx + rr * 0.28, cy_ + rr * 0.28), (cx, cy_ + rr),
                   (cx - rr * 0.28, cy_ + rr * 0.28), (cx - rr, cy_),
                   (cx - rr * 0.28, cy_ - rr * 0.28)], fill=fill)

    star(S * 0.78, S * 0.215, S * 0.085, (255, 244, 222))
    star(S * 0.865, S * 0.315, S * 0.042, (255, 238, 208))

    return img.resize((size, size), Image.LANCZOS).convert("RGB")


def data_url(im):
    b = io.BytesIO()
    im.save(b, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


i180, i192, i512 = make(180), make(192), make(512)
for im, name in ((i180, "icon-180.png"), (i192, "icon-192.png"), (i512, "icon-512.png")):
    im.save(name, optimize=True)

manifest = {
    "name": "나와의 메모", "short_name": "나의 메모",
    "description": "정희님 전용 채팅형 메모 웹앱",
    "start_url": "./", "scope": "./", "display": "standalone", "orientation": "portrait",
    "background_color": "#F8F2E5", "theme_color": "#F8F2E5",
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
    ],
}
murl = "data:application/manifest+json;charset=utf-8," + urllib.parse.quote(
    json.dumps(manifest, ensure_ascii=False, separators=(",", ":")))

p = pathlib.Path("index.html")
s = p.read_text(encoding="utf-8")
s = re.sub(r'<link rel="icon" href="data:image/png;base64,[^"]*">',
           '<link rel="icon" href="' + data_url(i180) + '">', s, count=1)
s = re.sub(r"<link rel=\"manifest\" href='[^']*'>",
           "<link rel=\"manifest\" href='" + murl + "'>", s, count=1)
p.write_text(s, encoding="utf-8")
print("html bytes:", len(s.encode()), "| favicon data url:", len(data_url(i180)))
