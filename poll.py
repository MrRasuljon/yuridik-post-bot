# -*- coding: utf-8 -*-
"""Admin buyruqlari va tugmalarini qayta ishlash.
GitHub Actions har 5 daqiqada ishga tushiradi."""
import sys

import tg
import core
import store
import generate
from config import ADMIN_ID, CHANNEL_ID

YORDAM = (
    "🤖 <b>Yuridik maslahat — post boti</b>\n\n"
    "Postlar har kuni <b>09:00</b> da avtomatik chiqadi — tasdiqlash kerak emas.\n"
    "Post chiqqanda sizga xabar keladi, yoqmasa 🗑 tugmasi bilan o'chirasiz.\n\n"
    "/post — hoziroq yangi post chiqarish\n"
    "/holat — nechta post chiqqani\n"
    "/help — shu yordam"
)


def callback(cb, state):
    data = cb.get("data", "")
    tg.answer_cb(cb["id"])

    if data.startswith("del:"):
        mid = data.split(":", 1)[1]
        r = tg.call("deleteMessage", chat_id=CHANNEL_ID, message_id=int(mid))
        if r.get("ok"):
            h = [x for x in store.load_history() if str(x.get("message_id")) != str(mid)]
            store.save_history(h)
            tg.send(ADMIN_ID, "🗑 Post kanaldan o'chirildi.")
        else:
            tg.send(
                ADMIN_ID,
                "❌ O'chirilmadi (Telegram 48 soatdan eski postni o'chirishga ruxsat "
                f"bermaydi).\n<code>{str(r.get('description'))[:200]}</code>",
            )
        return

    # Eski tasdiqlash rejimidan qolgan tugmalar
    if data in ("pub", "imp", "new", "fb"):
        tg.send(ADMIN_ID, "ℹ️ Bu eski draft tugmasi. Tizim endi avtomatik ishlaydi.")


def message(msg, state):
    text = (msg.get("text") or "").strip()
    if not text:
        return

    if text.startswith("/post"):
        tg.send(ADMIN_ID, "⏳ Post yozilyapti, 30-60 soniya kuting...")
        generate.chiqar(state)

    elif text.startswith("/holat"):
        h = store.load_history()
        oxirgi = h[-1] if h else None
        tg.send(
            ADMIN_ID,
            "📊 <b>Holat</b>\n"
            f"Jami postlar: {len(h)}\n"
            f"Oxirgisi: {oxirgi['date'] + ' · ' + oxirgi['topic'] if oxirgi else '—'}\n"
            f"Navbatdagi rubrika: {core.RUBRICS[state.get('rubric_index', 0) % len(core.RUBRICS)]['name']}",
        )

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
