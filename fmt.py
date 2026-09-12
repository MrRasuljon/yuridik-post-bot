# -*- coding: utf-8 -*-
"""Matnni Telegram HTML uchun tozalash."""
import re

ALLOWED = ("b", "strong", "i", "em", "u", "s", "code", "pre")
TAG_RE = re.compile(r"</?([a-zA-Z0-9]+)[^>]*>")


def tozala(text):
    """Ruxsat etilmagan teglarni olib tashlaydi, yolg'iz < > belgilarni escape qiladi."""
    if not text:
        return ""
    # Markdown qoldiqlarini tozalash
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text, flags=re.S)
    text = re.sub(r"(?m)^#{1,6}\s*", "", text)

    parts = []
    last = 0
    for m in TAG_RE.finditer(text):
        parts.append(_esc(text[last:m.start()]))
        tag = m.group(1).lower()
        parts.append(m.group(0) if tag in ALLOWED else "")
        last = m.end()
    parts.append(_esc(text[last:]))
    out = "".join(parts)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip()


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def yalang(text):
    """Barcha teglarni olib tashlash (parse xatosi bo'lsa zaxira variant)."""
    text = TAG_RE.sub("", text)
    return (text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")).strip()
