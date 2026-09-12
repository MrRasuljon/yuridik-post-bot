# -*- coding: utf-8 -*-
"""Holat (state) fayllari bilan ishlash. Fayllar repo ichida saqlanadi."""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state")
STATE = os.path.join(ROOT, "state.json")
HISTORY = os.path.join(ROOT, "history.json")

DEFAULT_STATE = {
    "pending": None,        # tasdiqlanmagan draft
    "last_update_id": 0,    # Telegram getUpdates offset
    "rubric_index": 0,      # rubrika navbati
    "awaiting_feedback": False,
}


def _read(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return json.loads(json.dumps(default))


def _write(path, data):
    os.makedirs(ROOT, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_state():
    s = _read(STATE, DEFAULT_STATE)
    for k, v in DEFAULT_STATE.items():
        s.setdefault(k, v)
    return s


def save_state(s):
    _write(STATE, s)


def load_history():
    return _read(HISTORY, [])


def save_history(h):
    _write(HISTORY, h[-200:])


def oxirgi_mavzular(n=25):
    return [x.get("topic", "") for x in load_history()[-n:] if x.get("topic")]
