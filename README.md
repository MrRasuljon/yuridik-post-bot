# ⚖️ Yuridik maslahat — avtomatik post tizimi

Telegram kanali **@yuridik_maslahat_kanali** uchun AI post generatori.
GitHub Actions'da bepul ishlaydi — kompyuter yoqiq bo'lishi shart emas.

## Qanday ishlaydi

1. Har kuni **09:00** (Toshkent) da tizim Gemini AI orqali post yozadi
2. Post **adminga** (siz) tugmalar bilan yuboriladi
3. Siz tugmalardan birini bosasiz:
   - ✅ **Kanalga joylash** — post darhol kanalga chiqadi
   - ♻️ **Yaxshila** — o'sha mavzuni yaxshiroq qilib qayta yozadi
   - 🔄 **Boshqa mavzu** — o'sha rubrikada butunlay yangi post
   - ✍️ **Izoh bilan qayta yoz** — siz nima o'zgartirishni yozasiz, AI shunga amal qiladi
   - ❌ **Bekor** — draft o'chiriladi
4. **Siz tasdiqlamaguningizcha hech narsa kanalga chiqmaydi.**

## Rubrikalar (navbat bilan aylanadi)

1. Mehnat huquqi
2. Tadbirkorlik va soliq
3. Oila huquqi
4. Uy-joy va ko'chmas mulk
5. Iste'molchi huquqlari va firibgarlikdan himoya
6. Namuna hujjat (ariza, shartnoma, ishonchnoma)
7. Savol-javob

## Bot buyruqlari

| Buyruq | Vazifasi |
|---|---|
| `/post` | Hoziroq yangi draft yaratish |
| `/holat` | Nechta post chiqqan, kutayotgan draft bormi |
| `/help` | Yordam |

---

## O'rnatish (bir marta)

### 1. GitHub'da repo yaratish

1. github.com → **New repository**
2. Nomi: `yuridik-post-bot`
3. **Public** tanlang (bepul cheksiz Actions daqiqasi uchun)
4. **Create repository**

### 2. Fayllarni yuklash

Arxivdagi barcha fayl va papkalarni repo'ga yuklang
(**Add file → Upload files** → hammasini tashlang → **Commit changes**).

Papka tuzilmasi buzilmasligi kerak:

```
.github/workflows/draft.yml
.github/workflows/poll.yml
bot/*.py
state/state.json
state/history.json
```

### 3. Secrets qo'shish

Repo → **Settings** → **Secrets and variables** → **Actions** →
**New repository secret**. To'rttasini qo'shing:

| Name | Secret |
|---|---|
| `BOT_TOKEN` | bot tokeni (@BotFather bergan) |
| `GEMINI_API_KEY` | Gemini API kaliti |
| `CHANNEL_ID` | `-1004310493387` |
| `ADMIN_ID` | `8412545378` |

### 4. Actions'ni yoqish

Repo → **Actions** → **I understand my workflows, go ahead and enable them**

### 5. Tekshirish

**Actions** → **Kunlik draft** → **Run workflow**.
30-60 soniyada botdan sizga draft kelishi kerak.

---

## Muhim bilib qo'yish kerak

- **Tugma bosilgandan keyin javob 5-15 daqiqada keladi.** GitHub bepul rejada
  har 5 daqiqada bir marta tekshiradi va band vaqtlarda kechikishi mumkin.
  Bu normal — post yo'qolmaydi.
- **AI qonun moddalarini o'ylab topishi mumkin.** Shuning uchun tizim postda
  modda raqami bo'lsa, sizga ⚠️ ogohlantirish qo'shadi. AI'ga modda raqamini
  faqat 100% ishonchi komil bo'lsa yozish buyurilgan, lekin **oxirgi tekshiruv
  baribir sizniki.**
- **Tasdiqlanmagan draft turganda yangi draft yaratilmaydi** — to'planib
  ketmasligi uchun.
- Post oxiriga disclaimer va kanal linki avtomatik qo'shiladi.

## Sozlamalarni o'zgartirish

| Nima | Qayerda |
|---|---|
| Post vaqti | `.github/workflows/draft.yml` → `cron: "0 4 * * *"` (UTC, +5 = Toshkent) |
| Rubrikalar | `bot/config.py` → `RUBRICS` |
| Post oxiridagi matn | `bot/config.py` → `FOOTER` |
| AI yozish qoidalari | `bot/gemini.py` → `QOIDALAR` |
| AI modeli | `bot/config.py` → `GEMINI_MODELS` |
