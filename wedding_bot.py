#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, os
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler,
    filters, ContextTypes
)

# ═══════════════════════════════════════════
ADMIN_ID    = 7948989650
BOT_TOKEN   = os.getenv("TOKEN")
PRICES_FILE = "prices.json"
ORDERS_FILE = "orders.json"
USERS_FILE  = "users.json"
# ═══════════════════════════════════════════

(
    S_LANG, S_CONTACT, S_ADMIN_MSG,
    S_PKG, S_DATE, S_EVENT, S_LOC, S_ADDR,
    S_ADMIN, S_EPKG_SEL, S_EPKG_VAL,
    S_CHAT_SEL, S_CHAT_MSG, S_BROADCAST,
) = range(14)

# ═══════════════════ MATNLAR ════════════════
TX = {
    "uz": {
        "flag": "🇺🇿 O'zbek (Lotin)",
        "welcome": (
            "🎬 *Sadaf Media* — Professional to'y videografiya xizmati!\n\n"
            "📹 Biz sizning eng muhim kunlaringizni\n"
            "    abadiy xotirada saqlaymiz.\n"
            "    Har bir kadr — yurakdan ❤️\n\n"
            "📱 Davom etish uchun *telefon raqamingizni* yuboring:"
        ),
        "btn_phone":  "📱 Telefon raqamni yuborish",
        "btn_admin":  "📞 Admin bilan aloqa",
        "btn_lang":   "🌐 Tilni o'zgartirish",
        "ask_msg": (
            "💬 *Admin bilan aloqa*\n\n"
            "Xabaringizni yozing — tez orada javob beramiz.\n\n"
            "✍️ Xabaringizni yozing:"
        ),
        "msg_sent": (
            "✅ *Xabaringiz yuborildi!*\n\n"
            "📞 Tez orada bog'lanamiz.\n"
            "⏰ Ish vaqti: 09:00 — 22:00\n\n"
            "👇 Zakaz qilish uchun telefon yuboring:"
        ),
        "pkgs": (
            "✅ Rahmat! Raqamingiz qabul qilindi.\n\n"
            "📦 *Paketni tanlang:*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "1️⃣  *700 000 so'm* — 1-kun: 1 ta kamera\n"
            "2️⃣  *1 400 000 so'm* — 2 kun: 1 ta kamera\n"
            "3️⃣  *2 000 000 so'm* — 1-kun:1 ta | 2-kun:2 ta\n"
            "4️⃣  *VIP 300$* — 1-kun:1 ta | 2-kun:2 ta + Kran\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        "pkg_ok": "✅ Tanlandi: *{pkg}*\n\n📅 Toy sanasini yozing:\n📌 Format: `05.06.2026`",
        "ask_event": "✅ Sana: *{date}*\n\n🎊 Tadbir turini tanlang:",
        "events": ["💍 Nikoh","🎂 Tug'ilgan kun","👦 Xatna","🎉 Banket","🕋 Xaj/Umra","🔤 Alifbe","👶 Chaqaloq"],
        "ask_loc": "✅ Tadbir: *{event}*\n\n📍 Lokatsiyani yuboring:",
        "btn_loc": "📍 Lokatsiyani yuborish",
        "ask_addr": "✅ Lokatsiya qabul qilindi!\n\n🏠 Manzilni yozing:\n📌 Misol: Yunusobod, Oq oltin restoran",
        "done": (
            "🎉 *Zakaz qabul qilindi!*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👤 {name}\n📱 {phone}\n📦 {pkg}\n"
            "📅 {date}\n🎊 {event}\n🏠 {address}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📞 Tez orada bog'lanamiz! Rahmat 🙏"
        ),
    },
    "uzc": {
        "flag": "🇺🇿 Ўзбек (Кирилл)",
        "welcome": (
            "🎬 *Садаф Медиа* — Профессионал тўй видеография!\n\n"
            "📹 Ҳар бир кадр — юракдан ❤️\n\n"
            "📱 Давом этиш учун *телефон рақамингизни* юборинг:"
        ),
        "btn_phone":  "📱 Телефон рақамни юбориш",
        "btn_admin":  "📞 Админ билан алоқа",
        "btn_lang":   "🌐 Тилни ўзгартириш",
        "ask_msg": "💬 *Админ билан алоқа*\n\nХабарингизни ёзинг:\n\n✍️ Хабарингизни ёзинг:",
        "msg_sent": "✅ *Хабарингиз юборилди!*\n\n📞 Тез орада боғланамиз.\n\n👇 Телефон юборинг:",
        "pkgs": (
            "✅ Раҳмат! Рақамингиз қабул қилинди.\n\n"
            "📦 *Пакетни танланг:*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "1️⃣  *700 000 сўм* — 1-кун: 1 та камера\n"
            "2️⃣  *1 400 000 сўм* — 2 кун: 1 та камера\n"
            "3️⃣  *2 000 000 сўм* — 1-кун:1 та | 2-кун:2 та\n"
            "4️⃣  *VIP 300$* — 1-кун:1 та | 2-кун:2 та + Кран\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        "pkg_ok": "✅ Танланди: *{pkg}*\n\n📅 Тўй санасини ёзинг:\n📌 Формат: `05.06.2026`",
        "ask_event": "✅ Сана: *{date}*\n\n🎊 Тадбир турини танланг:",
        "events": ["💍 Никоҳ","🎂 Туғилган кун","👦 Хатна","🎉 Банкет","🕋 Ҳаж/Умра","🔤 Алифбе","👶 Чақалоқ"],
        "ask_loc": "✅ Тадбир: *{event}*\n\n📍 Локацияни юборинг:",
        "btn_loc": "📍 Локацияни юбориш",
        "ask_addr": "✅ Локация қабул қилинди!\n\n🏠 Манзилни ёзинг:",
        "done": (
            "🎉 *Заказ қабул қилинди!*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👤 {name}\n📱 {phone}\n📦 {pkg}\n"
            "📅 {date}\n🎊 {event}\n🏠 {address}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📞 Тез орада боғланамиз! Раҳмат 🙏"
        ),
    },
    "ru": {
        "flag": "🇷🇺 Русский",
        "welcome": (
            "🎬 *Sadaf Media* — Профессиональная видеосъёмка!\n\n"
            "📹 Каждый кадр — от сердца ❤️\n\n"
            "📱 Для продолжения отправьте *номер телефона:*"
        ),
        "btn_phone":  "📱 Отправить номер телефона",
        "btn_admin":  "📞 Связаться с администратором",
        "btn_lang":   "🌐 Сменить язык",
        "ask_msg": "💬 *Связь с администратором*\n\nНапишите сообщение:\n\n✍️ Введите сообщение:",
        "msg_sent": "✅ *Сообщение отправлено!*\n\n📞 Свяжемся в ближайшее время.\n\n👇 Отправьте номер:",
        "pkgs": (
            "✅ Спасибо! Номер принят.\n\n"
            "📦 *Выберите пакет:*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "1️⃣  *700 000 сум* — 1 день: 1 камера\n"
            "2️⃣  *1 400 000 сум* — 2 дня: 1 камера\n"
            "3️⃣  *2 000 000 сум* — день1:1 | день2:2\n"
            "4️⃣  *VIP 300$* — день1:1 | день2:2 + Кран\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        "pkg_ok": "✅ Выбрано: *{pkg}*\n\n📅 Введите дату:\n📌 Формат: `05.06.2026`",
        "ask_event": "✅ Дата: *{date}*\n\n🎊 Выберите тип мероприятия:",
        "events": ["💍 Свадьба","🎂 День рождения","👦 Хатна","🎉 Банкет","🕋 Хадж/Умра","🔤 Алифбе","👶 Новорождённый"],
        "ask_loc": "✅ Мероприятие: *{event}*\n\n📍 Отправьте геолокацию:",
        "btn_loc": "📍 Отправить геолокацию",
        "ask_addr": "✅ Геолокация принята!\n\n🏠 Напишите адрес:",
        "done": (
            "🎉 *Заказ принят!*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👤 {name}\n📱 {phone}\n📦 {pkg}\n"
            "📅 {date}\n🎊 {event}\n🏠 {address}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📞 Свяжемся скоро! Спасибо 🙏"
        ),
    },
    "en": {
        "flag": "🇬🇧 English",
        "welcome": (
            "🎬 *Sadaf Media* — Professional Wedding Videography!\n\n"
            "📹 Every frame — from the heart ❤️\n\n"
            "📱 Please share your *phone number* to continue:"
        ),
        "btn_phone":  "📱 Share phone number",
        "btn_admin":  "📞 Contact admin",
        "btn_lang":   "🌐 Change language",
        "ask_msg": "💬 *Contact Admin*\n\nWrite your message:\n\n✍️ Type your message:",
        "msg_sent": "✅ *Message sent!*\n\n📞 We will reply soon.\n\n👇 Share your phone:",
        "pkgs": (
            "✅ Thank you! Number received.\n\n"
            "📦 *Choose a package:*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "1️⃣  *700,000 UZS* — Day 1: 1 camera\n"
            "2️⃣  *1,400,000 UZS* — 2 days: 1 camera\n"
            "3️⃣  *2,000,000 UZS* — day1:1 | day2:2\n"
            "4️⃣  *VIP $300* — day1:1 | day2:2 + Crane\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        "pkg_ok": "✅ Selected: *{pkg}*\n\n📅 Enter event date:\n📌 Format: `05.06.2026`",
        "ask_event": "✅ Date: *{date}*\n\n🎊 Select event type:",
        "events": ["💍 Wedding","🎂 Birthday","👦 Circumcision","🎉 Banquet","🕋 Hajj/Umrah","🔤 Alifbe","👶 Baby"],
        "ask_loc": "✅ Event: *{event}*\n\n📍 Send venue location:",
        "btn_loc": "📍 Send location",
        "ask_addr": "✅ Location received!\n\n🏠 Write venue address:",
        "done": (
            "🎉 *Order received!*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👤 {name}\n📱 {phone}\n📦 {pkg}\n"
            "📅 {date}\n🎊 {event}\n🏠 {address}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📞 We will contact you! Thanks 🙏"
        ),
    },
}

def tx(lang, key, **kw):
    t = TX.get(lang, TX["uz"]).get(key, TX["uz"].get(key, ""))
    return t.format(**kw) if kw else t

# ═══════════════════ JSON ════════════════════
DEFAULT_PRICES = {
    "p1": {"label":"1️⃣ Paket — 700 000 so'm",   "price":"700 000 so'm",   "desc":"1-kun: 1 ta kamera"},
    "p2": {"label":"2️⃣ Paket — 1 400 000 so'm", "price":"1 400 000 so'm", "desc":"2 kun: 1 ta kamera"},
    "p3": {"label":"3️⃣ Paket — 2 000 000 so'm", "price":"2 000 000 so'm", "desc":"1-kun:1 ta | 2-kun:2 ta"},
    "p4": {"label":"4️⃣ VIP Paket — 300$",        "price":"300$",           "desc":"1-kun:1 ta | 2-kun:2 ta + Kran"},
}

def load_json(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f: return json.load(f)
    if path == PRICES_FILE:
        save_json(path, DEFAULT_PRICES); return dict(DEFAULT_PRICES)
    return []

def save_json(path, data):
    with open(path,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2)

def save_user(uid, name, lang):
    if uid == ADMIN_ID: return
    users = load_json(USERS_FILE)
    u = next((x for x in users if x["id"]==uid), None)
    if u: u["lang"]=lang; u["name"]=name
    else: users.append({"id":uid,"name":name,"lang":lang})
    save_json(USERS_FILE, users)

def saved_lang(uid):
    users = load_json(USERS_FILE)
    u = next((x for x in users if x["id"]==uid), None)
    return u["lang"] if u and "lang" in u else None

def gl(ctx): return ctx.user_data.get("lang","uz")

def lang_ikb():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🇺🇿 O'zbek",  callback_data="LG:uz"),
        InlineKeyboardButton("🇺🇿 Кирилл", callback_data="LG:uzc"),
    ],[
        InlineKeyboardButton("🇷🇺 Русский", callback_data="LG:ru"),
        InlineKeyboardButton("🇬🇧 English", callback_data="LG:en"),
    ]])

def contact_kb(lang):
    """Telefon, admin, til tugmalari"""
    return ReplyKeyboardMarkup([
        [KeyboardButton(tx(lang,"btn_phone"), request_contact=True)],
        [KeyboardButton(tx(lang,"btn_admin"))],
        [KeyboardButton(tx(lang,"btn_lang"))],
    ], resize_keyboard=True, one_time_keyboard=False)

# ═══════════════════ START ═══════════════════
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    user = update.effective_user

    if user.id == ADMIN_ID:
        await update.message.reply_text(
            "👨‍💼 *Admin panel*",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup([
                ["📋 Zakazlar","✏️ Narxlar"],
                ["💬 Mijozga yoz","📤 Broadcast"],
            ], resize_keyboard=True)
        )
        return S_ADMIN

    lang = saved_lang(user.id)
    if lang:
        ctx.user_data["lang"] = lang
        await update.message.reply_text(
            tx(lang,"welcome"), parse_mode="Markdown",
            reply_markup=contact_kb(lang)
        )
        return S_CONTACT

    await update.message.reply_text(
        "🌐 Tilni tanlang / Язык / Language / Тилни танланг:",
        reply_markup=lang_ikb()
    )
    return S_LANG

# ═══════════════════ TIL ═════════════════════
async def cb_lang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = q.data.split(":")[1]
    ctx.user_data["lang"] = lang
    save_user(q.from_user.id, q.from_user.full_name, lang)
    try: await q.edit_message_reply_markup(reply_markup=None)
    except: pass
    await update.effective_chat.send_message(
        tx(lang,"welcome"), parse_mode="Markdown",
        reply_markup=contact_kb(lang)
    )
    return S_CONTACT

async def change_lang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 Tilni tanlang / Язык / Language / Тилни танланг:",
        reply_markup=lang_ikb()
    )
    return S_LANG

# ═══════════ ADMIN BILAN ALOQA ═══════════════
async def ask_admin_msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = gl(ctx)
    await update.message.reply_text(
        tx(lang,"ask_msg"), parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return S_ADMIN_MSG

async def send_admin_msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang  = gl(ctx)
    user  = update.effective_user
    uname = f"@{user.username}" if user.username else "—"
    flag  = TX.get(lang,{}).get("flag","?")

    await ctx.bot.send_message(
        ADMIN_ID,
        f"📞 *YANGI MUROJAAT!*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 {user.full_name}\n"
        f"🆔 `{user.id}`\n"
        f"📲 {uname}\n"
        f"🌐 {flag}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💬 {update.message.text}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📩 Javob uchun:",
        parse_mode="Markdown"
    )
    await ctx.bot.send_message(ADMIN_ID, f"/reply_{user.id}")
    await update.message.reply_text(
        tx(lang,"msg_sent"), parse_mode="Markdown",
        reply_markup=contact_kb(lang)
    )
    return S_CONTACT

# ═══════════════ TELEFON → PAKET ═════════════
async def got_contact(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = gl(ctx)
    c    = update.message.contact
    ctx.user_data["name"]  = c.first_name or update.effective_user.full_name
    ctx.user_data["phone"] = c.phone_number

    prices = load_json(PRICES_FILE)
    btns = [[InlineKeyboardButton(
        f"{p['label']}\n📹 {p.get('desc','')}",
        callback_data=f"PK:{k}"
    )] for k,p in prices.items()]

    await update.message.reply_text(
        tx(lang,"pkgs"), parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(btns)
    )
    return S_PKG

# ═══════════════ PAKET ═══════════════════════
async def cb_pkg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = gl(ctx)
    key  = q.data.split(":")[1]
    p    = load_json(PRICES_FILE)[key]
    ctx.user_data["package"] = f"{p['label']} | {p.get('desc','')}"
    try: await q.edit_message_reply_markup(reply_markup=None)
    except: pass
    await q.message.reply_text(
        tx(lang,"pkg_ok", pkg=p['label']), parse_mode="Markdown"
    )
    return S_DATE

# ═══════════════ SANA ════════════════════════
async def got_date(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = gl(ctx)
    ctx.user_data["date"] = update.message.text.strip()
    events = tx(lang,"events")
    await update.message.reply_text(
        tx(lang,"ask_event", date=ctx.user_data["date"]), parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(e)] for e in events],
            resize_keyboard=True, one_time_keyboard=True
        )
    )
    return S_EVENT

# ═══════════════ TADBIR ══════════════════════
async def got_event(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = gl(ctx)
    ctx.user_data["event"] = update.message.text
    await update.message.reply_text(
        tx(lang,"ask_loc", event=update.message.text), parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(tx(lang,"btn_loc"), request_location=True)]],
            resize_keyboard=True
        )
    )
    return S_LOC

# ═══════════════ LOKATSIYA ═══════════════════
async def got_location(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = gl(ctx)
    loc  = update.message.location
    ctx.user_data["lat"] = loc.latitude
    ctx.user_data["lon"] = loc.longitude
    await update.message.reply_text(
        tx(lang,"ask_addr"), parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return S_ADDR

# ═══════════════ MANZIL → ZAKAZ ══════════════
async def got_address(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = gl(ctx)
    d    = ctx.user_data
    addr = update.message.text
    flag = TX.get(lang,{}).get("flag","?")

    order = {
        "user_id": update.effective_user.id, "lang": lang,
        "name":d["name"],"phone":d["phone"],"package":d["package"],
        "date":d["date"],"event":d["event"],"address":addr,
        "lat":d["lat"],"lon":d["lon"],
    }
    orders = load_json(ORDERS_FILE); orders.append(order); save_json(ORDERS_FILE,orders)

    await ctx.bot.send_message(ADMIN_ID,
        f"🔔 *YANGI ZAKAZ!*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 {order['name']}\n📱 `{order['phone']}`\n"
        f"📦 {order['package']}\n📅 {order['date']}\n"
        f"🎊 {order['event']}\n🏠 {addr}\n🌐 {flag}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n📍 Lokatsiya 👇",
        parse_mode="Markdown"
    )
    await ctx.bot.send_location(ADMIN_ID, latitude=d["lat"], longitude=d["lon"])
    await update.message.reply_text(
        tx(lang,"done",name=order["name"],phone=order["phone"],
           pkg=order["package"],date=order["date"],
           event=order["event"],address=addr),
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# ═══════════════ ADMIN PANEL ═════════════════
async def admin_orders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    orders = load_json(ORDERS_FILE)
    if not orders:
        await update.message.reply_text("📭 Zakazlar yo'q."); return S_ADMIN
    btns = [[InlineKeyboardButton(f"#{i+1} {o['event']} | {o['date']} | {o['name']}", callback_data=f"ORD:{i}")] for i,o in enumerate(orders)]
    await update.message.reply_text(f"📋 *{len(orders)} ta zakaz:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(btns))
    return S_ADMIN

async def cb_view_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    i = int(q.data.split(":")[1])
    orders = load_json(ORDERS_FILE)
    if i >= len(orders): await q.edit_message_text("❌ Topilmadi"); return S_ADMIN
    o = orders[i]
    await ctx.bot.send_location(update.effective_chat.id, latitude=o["lat"], longitude=o["lon"])
    await ctx.bot.send_message(update.effective_chat.id,
        f"📋 *Zakaz #{i+1}*\n━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 {o['name']}\n📱 `{o['phone']}`\n📦 {o['package']}\n"
        f"📅 {o['date']}\n🎊 {o['event']}\n🏠 {o['address']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🗑 O'chirish", callback_data=f"DEL:{i}")]])
    )
    return S_ADMIN

async def cb_del_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    i = int(q.data.split(":")[1])
    orders = load_json(ORDERS_FILE)
    if i < len(orders): name=orders.pop(i)["name"]; save_json(ORDERS_FILE,orders); await q.edit_message_text(f"✅ {name} zakazi o'chirildi.")
    return S_ADMIN

async def admin_prices(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    prices = load_json(PRICES_FILE)
    btns = [[InlineKeyboardButton(p["label"], callback_data=f"EP:{k}")] for k,p in prices.items()]
    await update.message.reply_text("✏️ *Narxlar:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(btns))
    return S_EPKG_SEL

async def cb_epkg_sel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    key = q.data.split(":")[1]; ctx.user_data["ekey"] = key
    p = load_json(PRICES_FILE)[key]
    await q.edit_message_text(
        f"✏️ *{p['label']}*\n\n💰 {p['price']}\n📝 {p.get('desc','')}\n\n"
        f"Yangi: `narx | tavsif`\nMisol: `800 000 so'm | 1 kun`", parse_mode="Markdown"
    )
    return S_EPKG_VAL

async def got_epkg_val(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip(); key = ctx.user_data.get("ekey")
    prices = load_json(PRICES_FILE)
    if "|" in text: p,d=text.split("|",1); prices[key]["price"]=p.strip(); prices[key]["desc"]=d.strip()
    else: prices[key]["price"]=text
    save_json(PRICES_FILE,prices)
    await update.message.reply_text(f"✅ *{prices[key]['label']}* yangilandi!\n💰 {prices[key]['price']}\n📝 {prices[key].get('desc','')}", parse_mode="Markdown")
    return S_ADMIN

async def admin_chat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    users = [u for u in load_json(USERS_FILE) if u["id"]!=ADMIN_ID]
    if not users: await update.message.reply_text("👥 Foydalanuvchi yo'q."); return S_ADMIN
    btns = [[InlineKeyboardButton(f"👤 {u['name']} | {TX.get(u.get('lang','uz'),{}).get('flag','?')}", callback_data=f"CH:{u['id']}")] for u in users]
    await update.message.reply_text(f"💬 *{len(users)} ta foydalanuvchi. Kimga?*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(btns))
    return S_CHAT_SEL

async def cb_chat_sel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    ctx.user_data["ctarget"] = int(q.data.split(":")[1])
    await q.edit_message_text("✍️ Xabar yozing (matn/rasm/video):"); return S_CHAT_MSG

async def got_chat_msg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    tid = ctx.user_data.get("ctarget")
    try:
        if update.message.photo: await ctx.bot.send_photo(tid,update.message.photo[-1].file_id,caption=f"📩 *Admin:*\n{update.message.caption or ''}",parse_mode="Markdown")
        elif update.message.video: await ctx.bot.send_video(tid,update.message.video.file_id,caption=f"📩 *Admin:*\n{update.message.caption or ''}",parse_mode="Markdown")
        else: await ctx.bot.send_message(tid,f"📩 *Admin xabari:*\n\n{update.message.text}",parse_mode="Markdown")
        await update.message.reply_text("✅ Yuborildi!")
    except Exception as e: await update.message.reply_text(f"❌ {e}")
    return S_ADMIN

async def broadcast_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    users = [u for u in load_json(USERS_FILE) if u["id"]!=ADMIN_ID]
    await update.message.reply_text(
        f"📤 *Broadcast*\n\n👥 {len(users)} ta foydalanuvchi\n\nXabar yozing yoki /cancel:",
        parse_mode="Markdown"
    )
    return S_BROADCAST

async def broadcast_send(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    users = [u for u in load_json(USERS_FILE) if u["id"]!=ADMIN_ID]
    prog = await update.message.reply_text(f"⏳ 0/{len(users)}")
    sent=failed=0
    for i,u in enumerate(users,1):
        try:
            if update.message.photo: await ctx.bot.send_photo(u["id"],update.message.photo[-1].file_id,caption=update.message.caption or "")
            elif update.message.video: await ctx.bot.send_video(u["id"],update.message.video.file_id,caption=update.message.caption or "")
            else: await ctx.bot.send_message(u["id"],update.message.text)
            sent+=1
        except: failed+=1
        if i%5==0 or i==len(users):
            try: await prog.edit_text(f"⏳ {i}/{len(users)}")
            except: pass
    await prog.edit_text(f"✅ *Broadcast tugadi!*\n\n✔️ {sent} ta\n❌ {failed} ta", parse_mode="Markdown")
    return S_ADMIN

async def cmd_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id==ADMIN_ID: await update.message.reply_text("❌ Bekor."); return S_ADMIN
    return ConversationHandler.END

async def handle_reply(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!=ADMIN_ID: return
    text = update.message.text.strip()
    try:
        parts=text.split(" ",1); uid=int(parts[0].replace("/reply_",""))
        msg=parts[1] if len(parts)>1 else ""
        if not msg: await update.message.reply_text("Misol: `/reply_123456 Salom!`",parse_mode="Markdown"); return
        await ctx.bot.send_message(uid,f"📩 *Admin javobi:*\n\n{msg}",parse_mode="Markdown")
        await update.message.reply_text("✅ Yuborildi!")
    except Exception as e: await update.message.reply_text(f"❌ {e}")

# ═══════════════════ MAIN ════════════════════
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.Regex(r"^/reply_\d+"), handle_reply))

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", cmd_start)],
        states={
            S_LANG: [
                CallbackQueryHandler(cb_lang, pattern="^LG:"),
            ],
            S_CONTACT: [
                MessageHandler(filters.CONTACT, got_contact),
                MessageHandler(filters.Text(["📞 Admin bilan aloqa","📞 Связаться с администратором","📞 Contact admin","📞 Админ билан алоқа"]), ask_admin_msg),
                MessageHandler(filters.Text(["🌐 Tilni o'zgartirish","🌐 Тилни ўзгартириш","🌐 Сменить язык","🌐 Change language"]), change_lang),
                CallbackQueryHandler(cb_lang, pattern="^LG:"),
            ],
            S_ADMIN_MSG: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, send_admin_msg),
            ],
            S_PKG:  [CallbackQueryHandler(cb_pkg, pattern="^PK:")],
            S_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_date)],
            S_EVENT:[MessageHandler(filters.TEXT & ~filters.COMMAND, got_event)],
            S_LOC:  [MessageHandler(filters.LOCATION, got_location)],
            S_ADDR: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_address)],
            S_ADMIN:[
                MessageHandler(filters.Text(["📋 Zakazlar"]), admin_orders),
                MessageHandler(filters.Text(["✏️ Narxlar"]), admin_prices),
                MessageHandler(filters.Text(["💬 Mijozga yoz"]), admin_chat),
                MessageHandler(filters.Text(["📤 Broadcast"]), broadcast_start),
                CallbackQueryHandler(cb_view_order, pattern="^ORD:"),
                CallbackQueryHandler(cb_del_order,  pattern="^DEL:"),
            ],
            S_EPKG_SEL:[CallbackQueryHandler(cb_epkg_sel, pattern="^EP:")],
            S_EPKG_VAL:[MessageHandler(filters.TEXT & ~filters.COMMAND, got_epkg_val)],
            S_CHAT_SEL:[CallbackQueryHandler(cb_chat_sel, pattern="^CH:")],
            S_CHAT_MSG:[MessageHandler((filters.TEXT|filters.PHOTO|filters.VIDEO)&~filters.COMMAND, got_chat_msg)],
            S_BROADCAST:[
                CommandHandler("cancel", cmd_cancel),
                MessageHandler((filters.TEXT|filters.PHOTO|filters.VIDEO)&~filters.COMMAND, broadcast_send),
            ],
        },
        fallbacks=[CommandHandler("start",cmd_start), CommandHandler("cancel",cmd_cancel)],
    )
    app.add_handler(conv)
    print("✅ Bot ishga tushdi...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
