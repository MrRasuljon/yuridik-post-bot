# -*- coding: utf-8 -*-
"""Post uchun brend kartochka (rasm) yasash va Telegramga yuborish."""
import io
import os
import subprocess
import sys
import uuid

# --- Ranglar ---
BG_TOP = (11, 18, 32)
BG_BOTTOM = (20, 31, 54)
GOLD = (201, 162, 39)
WHITE = (245, 247, 250)
MUTED = (148, 163, 184)

W, H = 1200, 675
PAD = 80

FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation",
    "/usr/share/fonts",
]


def _pil():
    """Pillow'ni import qiladi, bo'lmasa o'rnatadi."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        return Image, ImageDraw, ImageFont
    except ImportError:
        print("[card] Pillow o'rnatilyapti...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", "pillow"],
            check=True, timeout=300,
        )
        from PIL import Image, ImageDraw, ImageFont
        return Image, ImageDraw, ImageFont


def _font(ImageFont, size, bold=True):
    names = (
        ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"] if bold
        else ["DejaVuSans.ttf", "LiberationSans-Regular.ttf"]
    )
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
    for root, _dirs, files in os.walk("/usr/share/fonts"):
        for f in files:
            if f.lower().endswith((".ttf", ".otf")):
                try:
                    return ImageFont.truetype(os.path.join(root, f), size)
                except Exception:
                    pass
    return ImageFont.load_default()


def _tarozi(d, cx, cy, s=1.0):
    """Adolat tarozisi — xira suv belgisi sifatida chiziladi."""
    c = (30, 44, 68)
    w = max(2, int(4 * s))
    h = int(120 * s)
    arm = int(95 * s)
    # ustun va poydevor
    d.line([(cx, cy - h), (cx, cy + h)], fill=c, width=w)
    d.line([(cx - int(55 * s), cy + h), (cx + int(55 * s), cy + h)], fill=c, width=w)
    # ko'ndalang balka
    d.line([(cx - arm, cy - h), (cx + arm, cy - h)], fill=c, width=w)
    # ikkita tovoq
    for sx in (-arm, arm):
        x = cx + sx
        d.line([(x, cy - h), (x, cy - h + int(38 * s))], fill=c, width=w)
        d.arc(
            [x - int(45 * s), cy - h + int(10 * s), x + int(45 * s), cy - h + int(68 * s)],
            start=0, end=180, fill=c, width=w,
        )


def _wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def yasash(sarlavha, rubrika):
    """Sarlavha va rubrikadan PNG kartochka yasaydi, baytlarni qaytaradi."""
    Image, ImageDraw, ImageFont = _pil()

    img = Image.new("RGB", (W, H), BG_TOP)
    d = ImageDraw.Draw(img)

    # Gradient fon
    for y in range(H):
        k = y / H
        d.line(
            [(0, y), (W, y)],
            fill=tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * k) for i in range(3)),
        )

    # Chap tomondagi oltin chiziq
    d.rectangle([0, 0, 10, H], fill=GOLD)

    # O'ng tomonda xira tarozi belgisi (suv belgisi)
    _tarozi(d, cx=W - 225, cy=H // 2 + 15, s=1.15)

    # Yuqori yorliq
    small = _font(ImageFont, 26, bold=True)
    d.text((PAD, PAD - 10), "Y U R I D I K   M A S L A H A T", font=small, fill=GOLD)
    d.line([(PAD, PAD + 34), (PAD + 300, PAD + 34)], fill=GOLD, width=3)

    # Sarlavha — joyiga sig'guncha kichraytiramiz, vertikal markazda
    sarlavha = (sarlavha or "").strip()
    max_w = W - PAD * 2 - 210          # o'ngdagi tarozi uchun joy
    top, bot = PAD + 90, H - 150       # sarlavha maydoni
    for size in (72, 64, 58, 52, 46, 40, 36):
        f = _font(ImageFont, size, bold=True)
        lines = _wrap(d, sarlavha, f, max_w)[:5]
        lh = int(size * 1.26)
        if len(lines) * lh <= (bot - top):
            break
    y = top + ((bot - top) - len(lines) * lh) // 2
    for ln in lines:
        d.text((PAD, y), ln, font=f, fill=WHITE)
        y += lh

    # Pastki qator
    bottom = _font(ImageFont, 28, bold=False)
    d.line([(PAD, H - 130), (W - PAD, H - 130)], fill=(40, 55, 80), width=2)
    d.text((PAD, H - 100), rubrika or "", font=bottom, fill=MUTED)
    kanal = "@yuridik_maslahat_kanali"
    d.text((W - PAD - d.textlength(kanal, font=bottom), H - 100),
           kanal, font=bottom, fill=GOLD)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


# ---------- Telegramga rasm yuborish ----------

def _multipart(fields, files):
    """multipart/form-data tanasini qo'lda yig'ish."""
    b = uuid.uuid4().hex
    out = []
    for k, v in fields.items():
        out.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    for k, (name, data, ctype) in files.items():
        out.append(
            f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{name}\"\r\n"
            f"Content-Type: {ctype}\r\n\r\n".encode()
        )
        out.append(data)
        out.append(b"\r\n")
    out.append(f"--{b}--\r\n".encode())
    return b"".join(out), f"multipart/form-data; boundary={b}"


def send_photo(chat_id, photo, caption, keyboard=None):
    """photo — PNG baytlari yoki Telegram file_id (matn)."""
    import json
    import urllib.request
    import urllib.error
    from config import BOT_TOKEN

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    fields = {"chat_id": str(chat_id), "caption": caption, "parse_mode": "HTML"}
    if keyboard:
        fields["reply_markup"] = json.dumps({"inline_keyboard": keyboard})

    if isinstance(photo, (bytes, bytearray)):
        body, ctype = _multipart(fields, {"photo": ("card.png", bytes(photo), "image/png")})
    else:
        fields["photo"] = photo
        body, ctype = _multipart(fields, {})

    req = urllib.request.Request(url, data=body, headers={"Content-Type": ctype})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", "replace")
        print(f"[card] sendPhoto HTTP {e.code}: {txt[:300]}")
        try:
            return json.loads(txt)
        except Exception:
            return {"ok": False, "description": txt}
    except Exception as e:
        print(f"[card] sendPhoto xato: {e}")
        return {"ok": False, "description": str(e)}


def file_id_ol(resp):
    """sendPhoto javobidan eng katta o'lchamdagi rasmning file_id sini oladi."""
    try:
        photos = resp["result"]["photo"]
        return max(photos, key=lambda p: p.get("file_size", 0))["file_id"]
    except Exception:
        return None
