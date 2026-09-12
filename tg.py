# -*- coding: utf-8 -*-
"""Telegram Bot API bilan ishlash."""
import json
import urllib.request
import urllib.error

from config import BOT_TOKEN

API = f"https://api.telegram.org/bot{BOT_TOKEN}/"


def call(method, **params):
    data = json.dumps(params).encode("utf-8")
    req = urllib.request.Request(
        API + method,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        print(f"[tg] {method} HTTP {e.code}: {body}")
        try:
            return json.loads(body)
        except Exception:
            return {"ok": False, "description": body}
    except Exception as e:
        print(f"[tg] {method} xato: {e}")
        return {"ok": False, "description": str(e)}


def send(chat_id, text, keyboard=None, preview=False):
    p = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "link_preview_options": {"is_disabled": not preview},
    }
    if keyboard:
        p["reply_markup"] = {"inline_keyboard": keyboard}
    return call("sendMessage", **p)


def edit(chat_id, message_id, text, keyboard=None):
    p = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML",
        "link_preview_options": {"is_disabled": True},
    }
    if keyboard is not None:
        p["reply_markup"] = {"inline_keyboard": keyboard}
    return call("editMessageText", **p)


def strip_buttons(chat_id, message_id):
    return call(
        "editMessageReplyMarkup",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup={"inline_keyboard": []},
    )


def answer_cb(cb_id, text=""):
    return call("answerCallbackQuery", callback_query_id=cb_id, text=text)


def get_updates(offset):
    return call(
        "getUpdates",
        offset=offset,
        timeout=0,
        allowed_updates=["message", "callback_query"],
    )


DRAFT_KEYBOARD = [
    [
        {"text": "✅ Kanalga joylash", "callback_data": "pub"},
    ],
    [
        {"text": "♻️ Yaxshila", "callback_data": "imp"},
        {"text": "🔄 Boshqa mavzu", "callback_data": "new"},
    ],
    [
        {"text": "✍️ Izoh bilan qayta yoz", "callback_data": "fb"},
        {"text": "❌ Bekor", "callback_data": "del"},
    ],
]
