# -*- coding: utf-8 -*-
"""Barcha sozlamalar shu yerda. Maxfiy ma'lumotlar GitHub Secrets'dan olinadi."""
import os

# --- Maxfiy (GitHub Secrets) ---
BOT_TOKEN = os.environ["BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

# --- Kanal sozlamalari ---
CHANNEL_ID = os.environ.get("CHANNEL_ID", "-1004310493387")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "8412545378"))

CHANNEL_USERNAME = "@yuridik_maslahat_kanali"
ADMIN_CONTACT = "@yurist_expert_admin"

# --- AI model ---
GEMINI_MODELS = ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-2.5-pro"]

# --- Post oxiriga qo'shiladigan matn ---
FOOTER = (
    "\n\n━━━━━━━━━━━━━━━\n"
    "ℹ️ <i>Bu umumiy huquqiy ma'lumot. Aniq holatingiz bo'yicha yurist bilan "
    "maslahatlashing.</i>\n"
    f"📩 Murojaat: {ADMIN_CONTACT}\n"
    f"👉 {CHANNEL_USERNAME}"
)

# --- Rubrikalar (navbat bilan aylanadi) ---
RUBRICS = [
    {
        "name": "Mehnat huquqi",
        "hint": "ishga qabul, mehnat shartnomasi, ishdan bo'shatish, ish haqi, "
                "ta'til, ortiqcha ish vaqti, mehnat nizolari",
    },
    {
        "name": "Tadbirkorlik va soliq",
        "hint": "YaTT va MChJ, soliq rejimlari, hisobot muddatlari, litsenziya, "
                "tekshiruvlar, jarimalar, shartnoma tuzish",
    },
    {
        "name": "Oila huquqi",
        "hint": "nikoh va ajrim, aliment, bolaning huquqlari, mol-mulkni bo'lish, "
                "nikoh shartnomasi",
    },
    {
        "name": "Uy-joy va ko'chmas mulk",
        "hint": "kvartira sotib olish, ijara, meros, kadastr, qo'shnilar bilan nizo, "
                "ipoteka",
    },
    {
        "name": "Iste'molchi huquqlari va firibgarlikdan himoya",
        "hint": "sifatsiz tovarni qaytarish, kafolat, onlayn firibgarlik, "
                "soxta qarz, telefon orqali aldov, nasiya savdo",
    },
    {
        "name": "Namuna hujjat",
        "hint": "ariza, shartnoma, ishonchnoma, da'vo arizasi — qanday to'g'ri "
                "yozish, qaysi ma'lumotlar bo'lishi shart, tipik xatolar",
    },
    {
        "name": "Savol-javob",
        "hint": "fuqarolar eng ko'p beradigan bitta aniq savol va unga to'liq javob",
    },
]

# Bir draft uchun maksimal qayta urinish
MAX_ATTEMPTS = 6
