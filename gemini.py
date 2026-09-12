# -*- coding: utf-8 -*-
"""Gemini API orqali post yozish."""
import json
import re
import urllib.request
import urllib.error

from config import GEMINI_API_KEY, GEMINI_MODELS

BASE = "https://generativelanguage.googleapis.com/v1beta/models/"

SCHEMA = {
    "type": "object",
    "properties": {
        "topic": {"type": "string"},
        "post": {"type": "string"},
    },
    "required": ["topic", "post"],
}

QOIDALAR = """Sen "⚖️ YURIDIK MASLAHAT 🇺🇿" Telegram kanali uchun post yozuvchi muharrirsan.
Shior: "Huquqni bilgan yutqazmaydi".
Auditoriya: O'zbekistondagi oddiy fuqarolar va kichik tadbirkorlar.

QAT'IY QOIDALAR:
1. Faqat o'zbek tilida (lotin alifbosi). Sodda, tushunarli til. Yuridik jargon minimal.
2. MODDA RAQAMLARI: modda yoki qonun raqamini FAQAT 100% ishonching komil bo'lsa yoz.
   Zarracha shubha bo'lsa — raqamni umuman yozma, "qonunchilikka ko'ra" yoki
   "amaldagi tartibga ko'ra" deb yoz. Noto'g'ri modda raqami — eng og'ir xato.
3. Sana, foiz, summa va muddatlarni ham faqat ishonching komil bo'lsa yoz.
4. Uzunlik: 600-1100 belgi. Qisqa abzaslar, bo'sh qatorlar bilan ajratilgan.
5. Tuzilishi:
   - 1-qator: emoji + qisqa, aniq sarlavha (<b>qalin</b> tegda)
   - hayotiy holat yoki muammo (1-2 gap)
   - "Nima qilish kerak" — 3-5 ta qisqa punkt
   - oxirida 1-2 gap amaliy maslahat yoki ogohlantirish
6. Faqat shu HTML teglar: <b>, <i>, <u>, <code>. Markdown (**, ##) ISHLATMA.
7. Reklama, mubolag'a, "biz eng yaxshimiz" kabi gaplar yo'q.
8. Oxiriga disclaimer yoki kanal linkini yozma — tizim o'zi qo'shadi.
9. Post o'zi yakuniy holatda bo'lsin: "quyida", "keyingi postda" kabi gaplar yo'q."""


def _extract(resp):
    """Gemini javobidan matnni ajratib olish (thinking qismini tashlab)."""
    out = []
    for cand in resp.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            if part.get("thought"):
                continue
            if "text" in part:
                out.append(part["text"])
    return "".join(out).strip()


def ask(prompt, temperature=0.9):
    body = json.dumps({
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": 8192,
            "responseMimeType": "application/json",
            "responseSchema": SCHEMA,
        },
    }).encode("utf-8")

    last_err = None
    for model in GEMINI_MODELS:
        req = urllib.request.Request(
            BASE + model + ":generateContent",
            data=body,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": GEMINI_API_KEY,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                resp = json.loads(r.read().decode("utf-8"))
            text = _extract(resp)
            if not text:
                last_err = f"{model}: bo'sh javob"
                continue
            data = json.loads(text)
            if data.get("post"):
                print(f"[gemini] {model} ishladi")
                return data
            last_err = f"{model}: post bo'sh"
        except urllib.error.HTTPError as e:
            last_err = f"{model}: HTTP {e.code} {e.read().decode('utf-8','replace')[:200]}"
            print("[gemini]", last_err)
        except Exception as e:
            last_err = f"{model}: {e}"
            print("[gemini]", last_err)

    raise RuntimeError(f"Gemini javob bermadi. Oxirgi xato: {last_err}")


def yangi_post(rubric, oxirgi_mavzular):
    tarix = "\n".join(f"- {t}" for t in oxirgi_mavzular) or "- (hali post yo'q)"
    return ask(f"""{QOIDALAR}

BUGUNGI RUBRIKA: {rubric['name']}
Shu rubrika doirasidagi mavzular: {rubric['hint']}

YAQINDA CHIQQAN MAVZULAR (bularni TAKRORLAMA, boshqa mavzu tanla):
{tarix}

Vazifa: shu rubrikada bitta yangi, amaliy, odamlar uchun foydali post yoz.
"topic" — mavzuning 3-6 so'zlik nomi. "post" — to'liq post matni.""")


def yaxshila(rubric, post, izoh=None):
    qoshimcha = f"\n\nADMIN IZOHI (albatta bajar):\n{izoh}" if izoh else ""
    return ask(f"""{QOIDALAR}

Quyidagi post tayyorlangan edi. Uni YAXSHILA: aniqroq, foydaliroq va
o'qishga qulayroq qil. Mavzu o'sha bo'lib qolsin.{qoshimcha}

ESKI POST:
{post}

Vazifa: yaxshilangan to'liq postni qaytar.""", temperature=0.8)


MODDA_RE = re.compile(r"\b(\d{1,4})\s*-\s*modda|\bmodda\s*(\d{1,4})\b", re.I)


def moddalarni_top(text):
    """Postdagi modda raqamlarini topadi — admin tekshirishi uchun."""
    found = []
    for m in MODDA_RE.finditer(text):
        num = m.group(1) or m.group(2)
        if num and num not in found:
            found.append(num)
    return found
