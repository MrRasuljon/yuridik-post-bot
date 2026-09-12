# -*- coding: utf-8 -*-
"""Kunlik draft yaratish. GitHub Actions cron orqali ishga tushadi."""
import sys

import tg
import core
import store
from config import ADMIN_ID


def main():
    state = store.load_state()

    if state.get("pending"):
        p = state["pending"]
        tg.send(
            ADMIN_ID,
            "⏳ Oldingi draft hali tasdiqlanmagan — yangisi yaratilmadi.\n"
            f"Mavzu: <i>{p.get('topic','')}</i>\n\n"
            "Yuqoridagi draftga javob bering (✅ / ♻️ / ❌), keyin yangisi keladi.",
        )
        print("[generate] pending draft bor, to'xtatildi")
        return 0

    try:
        d = core.yangi_draft(state)
    except Exception as e:
        tg.send(ADMIN_ID, f"❌ Post yaratilmadi.\n<code>{str(e)[:500]}</code>")
        print("[generate] xato:", e)
        return 1

    core.adminga_yubor(d, state)
    print(f"[generate] draft yuborildi: {d['topic']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
