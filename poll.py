# -*- coding: utf-8 -*-
"""Admin tugmalari va xabarlarini qayta ishlash.
GitHub Actions har 5 daqiqada ishga tushiradi."""
import sys

import tg
import core
import store
from config import ADMIN_ID, CHANNEL_USERNAME, MAX_ATTEMPTS

YORDAM = (
    "🤖 <b>Yuridik maslahat — post boti</b>\n\n"
    "/post — hoziroq yangi draft yarat\n"
    "/holat — tizim holati\n\n"
    "Draft kelganda tugmalardan birini bosing."
)


def _qayta(state, izoh=None, boshqa=False):
    """Draftni qayta yozib, adminga yuboradi."""
    d = state.get("pending")
    if not d:
        tg.send(ADMIN_ID, "Hozir kutayotgan draft yo'q. /post buyrug'ini yuboring.")
        return
    if d.get("attempt", 1) >= MAX_ATTEMPTS:
        tg.send(ADMIN_ID, f"⚠️ {MAX_ATTEMPTS} marta qayta yozildi. "
                          "❌ Bekor qilib, /post bilan noldan boshlang.")
        return
    tg.strip_buttons(ADMIN_ID, d["admin_message_id"])
    tg.send(ADMIN_ID, "♻️ Qayta yozilyapti, 20-40 soniya kuting...")
    try:
        yangi = core.qayta_yoz(d, izoh=izoh, boshqa_mavzu=boshqa)
    except Exception as e:
        tg.send(ADMIN_ID, f"❌ Qayta yozilmadi.\n<code>{str(e)[:400]}</code>")
        return
    core.adminga_yubor(yangi, state)


def callback(cb, state):
    data = cb.get("data", "")
    tg.answer_cb(cb["id"])
    d = state.get("pending")

    if data == "pub":
        if not d:
            tg.send(ADMIN_ID, "Draft topilmadi (ehtimol allaqachon joylangan).")
            return
        tg.strip_buttons(ADMIN_ID, d["admin_message_id"])
        mid, r = core.kanalga_joyla(d, state)
        if mid:
            tg.send(ADMIN_ID, f"✅ Kanalga joylandi!\n"
                              f"🔗 https://t.me/{CHANNEL_USERNAME.lstrip('@')}/{mid}")
        else:
            tg.send(ADMIN_ID, f"❌ Joylanmadi.\n<code>{str(r)[:400]}</code>")

    elif data == "imp":
        _qayta(state)

    elif data == "new":
        _qayta(state, boshqa=True)

    elif data == "fb":
        if not d:
            tg.send(ADMIN_ID, "Draft topilmadi.")
            return
        state["awaiting_feedback"] = True
        store.save_state(state)
        tg.send(ADMIN_ID, "✍️ Nimani o'zgartiray? Izohingizni shu yerga yozing.")

    elif data == "del":
        if d:
            tg.strip_buttons(ADMIN_ID, d["admin_message_id"])
        state["pending"] = None
        state["awaiting_feedback"] = False
        store.save_state(state)
        tg.send(ADMIN_ID, "❌ Draft bekor qilindi. Yangisi uchun: /post")


def message(msg, state):
    text = (msg.get("text") or "").strip()
    if not text:
        return

    if state.get("awaiting_feedback") and not text.startswith("/"):
        state["awaiting_feedback"] = False
        store.save_state(state)
        _qayta(state, izoh=text)
        return

    if text.startswith("/post"):
        if state.get("pending"):
            tg.send(ADMIN_ID, "⏳ Avval kutayotgan draftga javob bering.")
            return
        tg.send(ADMIN_ID, "⏳ Post yozilyapti, 20-40 soniya kuting...")
        try:
            d = core.yangi_draft(state)
        except Exception as e:
            tg.send(ADMIN_ID, f"❌ Xato.\n<code>{str(e)[:400]}</code>")
            return
        core.adminga_yubor(d, state)

    elif text.startswith("/holat"):
        h = store.load_history()
        p = state.get("pending")
        tg.send(ADMIN_ID,
                f"📊 <b>Holat</b>\n"
                f"Joylangan postlar: {len(h)}\n"
                f"Kutayotgan draft: {'bor — ' + p['topic'] if p else 'yo‘q'}\n"
                f"Oxirgi post: {h[-1]['date'] + ' · ' + h[-1]['topic'] if h else '—'}")

    elif text.startswith("/start") or text.startswith("/help"):
        tg.send(ADMIN_ID, YORDAM)


def main():
    state = store.load_state()
    r = tg.get_updates(state.get("last_update_id", 0) + 1)
    if not r.get("ok"):
        print("[poll] getUpdates xato:", r)
        return 1

    updates = r.get("result", [])
    print(f"[poll] {len(updates)} ta yangilanish")

    for u in updates:
        state["last_update_id"] = max(state.get("last_update_id", 0), u["update_id"])
        store.save_state(state)
        try:
            if "callback_query" in u:
                cb = u["callback_query"]
                if cb.get("from", {}).get("id") == ADMIN_ID:
                    callback(cb, state)
                else:
                    tg.answer_cb(cb["id"], "Bu bot faqat admin uchun.")
            elif "message" in u:
                m = u["message"]
                if m.get("from", {}).get("id") == ADMIN_ID:
                    message(m, state)
        except Exception as e:
            print("[poll] xato:", e)
            tg.send(ADMIN_ID, f"⚠️ Ichki xato: <code>{str(e)[:300]}</code>")

    store.save_state(state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
