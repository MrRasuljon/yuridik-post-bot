# -*- coding: utf-8 -*-
"""Umumiy amallar: post yaratish, kanalga joylash, adminni xabardor qilish."""
import datetime

import tg
import fmt
import card
import gemini
import store
from config import ADMIN_ID, CHANNEL_ID, CHANNEL_USERNAME, FOOTER, RUBRICS

CAPTION_LIMIT = 1024


def _now():
    # Toshkent vaqti (UTC+5)
    return datetime.datetime.utcnow() + datetime.timedelta(hours=5)


def _ogohlantirish(post):
    moddalar = gemini.moddalarni_top(post)
    if not moddalar:
        return ""
    return (
        "\n\n⚠️ <b>Tekshiring:</b> postda modda raqami bor — "
        + ", ".join(f"{m}-modda" for m in moddalar)
        + "."
    )


def _sarlavha(d):
    s = (d.get("sarlavha") or d.get("topic") or "").strip()
    return fmt.yalang(s)[:70]


def _dan_post(data, rubric_nomi):
    return {
        "rubric": rubric_nomi,
        "topic": (data.get("topic") or "").strip(),
        "sarlavha": (data.get("sarlavha") or "").strip(),
        "rasm_kerak": bool(data.get("rasm_kerak")),
        "post": fmt.tozala(data["post"]),
        "created_at": _now().isoformat(timespec="seconds"),
    }


def yangi_post(state, rubric=None):
    """Navbatdagi rubrika bo'yicha yangi post yozadi."""
    if rubric is None:
        rubric = RUBRICS[state.get("rubric_index", 0) % len(RUBRICS)]
    data = gemini.yangi_post(rubric, store.oxirgi_mavzular())
    return _dan_post(data, rubric["name"])


def kanalga_joyla(d, state):
    """Postni kanalga joylaydi (kerak bo'lsa kartochka bilan) va tarixga yozadi."""
    text = d["post"] + FOOTER
    sigadi = len(fmt.yalang(text)) <= CAPTION_LIMIT
    rasmli = False
    r = None

    if d.get("rasm_kerak") and sigadi:
        try:
            png = card.yasash(_sarlavha(d), d["rubric"])
            r = card.send_photo(CHANNEL_ID, png, text)
            if r.get("ok"):
                rasmli = True
            else:
                r = None
        except Exception as e:
            print("[core] kartochka yasalmadi:", e)
            r = None

    if r is None:
        r = tg.send(CHANNEL_ID, text)
    if not r.get("ok"):
        r = tg.send(CHANNEL_ID, fmt.yalang(text))
    if not r.get("ok"):
        return None, r

    mid = r["result"]["message_id"]

    h = store.load_history()
    h.append({
        "date": _now().strftime("%Y-%m-%d %H:%M"),
        "rubric": d["rubric"],
        "topic": d["topic"],
        "rasm": rasmli,
        "message_id": mid,
    })
    store.save_history(h)

    state["pending"] = None
    state["rubric_index"] = (state.get("rubric_index", 0) + 1) % len(RUBRICS)
    store.save_state(state)
    return mid, r


def adminni_xabardor(d, mid, rasmli=None):
    """Post chiqqani haqida adminga xabar + o'chirish tugmasi."""
    link = f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}/{mid}"
    matn = (
        f"✅ <b>Post chiqdi</b> · {d['rubric']}\n"
        f"<i>{fmt.tozala(d['topic'])}</i>\n"
        f"🔗 {link}"
        + _ogohlantirish(d["post"])
    )
    kb = [[{"text": "🗑 Kanaldan o'chirish", "callback_data": f"del:{mid}"}]]
    return tg.send(ADMIN_ID, matn, kb)
