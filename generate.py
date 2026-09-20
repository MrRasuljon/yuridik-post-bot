# -*- coding: utf-8 -*-
"""Kunlik post: yozadi va to'g'ridan-to'g'ri kanalga joylaydi.
GitHub Actions cron orqali ishga tushadi."""
import sys

import tg
import core
import store
from config import ADMIN_ID


def chiqar(state):
    """Bitta post yozib, kanalga joylaydi. True — muvaffaqiyatli."""
    try:
        d = core.yangi_post(state)
    except Exception as e:
        tg.send(ADMIN_ID, f"❌ Post yozilmadi.\n<code>{str(e)[:500]}</code>")
        print("[generate] gemini xatosi:", e)
        return False

    mid, r = core.kanalga_joyla(d, state)
    if not mid:
        tg.send(ADMIN_ID, f"❌ Kanalga joylanmadi.\n<code>{str(r)[:400]}</code>")
        print("[generate] joylanmadi:", r)
        return False

    core.adminni_xabardor(d, mid)
    print(f"[generate] chiqdi: {d['topic']} (msg {mid})")
    return True


def main():
    state = store.load_state()
    state["pending"] = None          # eski tasdiqlash rejimidan qolgan qoldiq
    return 0 if chiqar(state) else 1


if __name__ == "__main__":
    sys.exit(main())
