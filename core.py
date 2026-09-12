# -*- coding: utf-8 -*-
"""Umumiy amallar: draft yaratish, adminga yuborish, kanalga joylash."""
import datetime

import tg
import fmt
import gemini
import store
from config import ADMIN_ID, CHANNEL_ID, FOOTER, RUBRICS


def _now():
    # Toshkent vaqti (UTC+5)
    return datetime.datetime.utcnow() + datetime.timedelta(hours=5)


def draft_matni(d):
    """Adminga ko'rsatiladigan xabar."""
    ogoh = ""
    moddalar = gemini.moddalarni_top(d["post"])
    if moddalar:
        ogoh = (
            "\n\n⚠️ <b>Tekshiring:</b> postda modda raqami bor — "
            + ", ".join(f"{m}-modda" for m in moddalar)
            + ". To'g'riligiga ishonch hosil qiling."
        )
    return (
        f"📝 <b>DRAFT</b> · {d['rubric']} · urinish {d['attempt']}\n"
        f"<i>Mavzu: {fmt.tozala(d['topic'])}</i>\n"
        "━━━━━━━━━━━━━━━\n\n"
        f"{d['post']}"
        f"{FOOTER}"
        f"{ogoh}"
    )


def adminga_yubor(d, state):
    """Draftni adminga tugmalar bilan yuboradi."""
    text = draft_matni(d)
    r = tg.send(ADMIN_ID, text, tg.DRAFT_KEYBOARD)
    if not r.get("ok"):
        # HTML xato bo'lsa — teglarsiz yuboramiz
        print("[core] HTML bilan yuborilmadi, yalang matn sinaladi")
        d["post"] = fmt.yalang(d["post"])
        r = tg.send(ADMIN_ID, fmt.yalang(text), tg.DRAFT_KEYBOARD)
    if not r.get("ok"):
        raise RuntimeError(f"Adminga yuborilmadi: {r}")
    d["admin_message_id"] = r["result"]["message_id"]
    state["pending"] = d
    state["awaiting_feedback"] = False
    store.save_state(state)
    return d


def yangi_draft(state, rubric=None):
    """Navbatdagi rubrika bo'yicha yangi draft yaratadi."""
    if rubric is None:
        rubric = RUBRICS[state["rubric_index"] % len(RUBRICS)]
    data = gemini.yangi_post(rubric, store.oxirgi_mavzular())
    return {
        "rubric": rubric["name"],
        "topic": data["topic"].strip(),
        "post": fmt.tozala(data["post"]),
        "attempt": 1,
        "created_at": _now().isoformat(timespec="seconds"),
    }


def qayta_yoz(d, izoh=None, boshqa_mavzu=False):
    """Draftni yaxshilaydi yoki butunlay yangi mavzu oladi."""
    rubric = next((r for r in RUBRICS if r["name"] == d["rubric"]), RUBRICS[0])
    if boshqa_mavzu:
        mavzular = store.oxirgi_mavzular() + [d["topic"]]
        data = gemini.yangi_post(rubric, mavzular)
    else:
        data = gemini.yaxshila(rubric, d["post"], izoh)
    return {
        "rubric": d["rubric"],
        "topic": data["topic"].strip(),
        "post": fmt.tozala(data["post"]),
        "attempt": d.get("attempt", 1) + 1,
        "created_at": _now().isoformat(timespec="seconds"),
    }


def kanalga_joyla(d, state):
    """Tasdiqlangan postni kanalga joylaydi va tarixga yozadi."""
    text = d["post"] + FOOTER
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
        "message_id": mid,
    })
    store.save_history(h)

    state["pending"] = None
    state["awaiting_feedback"] = False
    state["rubric_index"] = (state.get("rubric_index", 0) + 1) % len(RUBRICS)
    store.save_state(state)
    return mid, r
