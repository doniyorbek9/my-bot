#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler,
    filters, ContextTypes
)

ADMIN_ID    = 7948989650
BOT_TOKEN   = os.getenv("TOKEN")

PRICES_FILE = "prices.json"
ORDERS_FILE = "orders.json"
USERS_FILE  = "users.json"

(
    LANG_SELECT,
    CONTACT,
    ADMIN_MSG_INPUT,
    PKG_SELECT,
    DATE_INPUT,
    EVENT_SELECT,
    LOCATION_INPUT,
    ADDRESS_INPUT,
    ADMIN_HOME,
    EDIT_PKG_SELECT,
    EDIT_PKG_VALUE,
    CHAT_USER_SELECT,
    CHAT_SEND,
    BROADCAST_WAIT,
) = range(14)

TEXTS = {
    "uz": {
        "flag":            "🇺🇿 O'zbek (Lotin)",
        "welcome": (
            "🎬 *Sadaf Media* — Professional to'y videografiya xizmati!\n\n"
            "📹 Biz sizning eng muhim kunlaringizni\n"
            "    abadiy xotirada saqlaymiz.\n"
            "    har bir kadr yurakdan ❤️\n\n"
            "📱 Davom etish uchun *telefon raqamingizni* yuboring:"
        ),
        "btn_contact":     "📱 Telefon raqamni yuborish",
        "btn_call_admin":  "📞 Admin bilan bog'lanish",
        "btn_change_lang": "🌐 Tilni o'zgartirish",
        "ask_admin_msg": (
            "💬 *Admin bilan bog'lanish*\n\n"
            "Xabaringizni yozing — admin tez orada javob beradi.\n\n"
            "✍️ Xabaringizni shu yerga yozing:"
        ),
        "admin_msg_sent": (
            "✅ *Xabaringiz adminga yuborildi!*\n\n"
            "📞 Tez orada javob berishadi.\n"
            "⏰ Ish vaqti: 09:00 — 22:00\n\n"
            "Zakaz qilish uchun 👇\n"
            "Telefon raqamingizni yuboring:"
        ),
        "contact_sent": (
            "✅ Rahmat! Raqamingiz qabul qilindi.\n\n"
            "👇 Endi quyidagi *paketlardan birini tanlang:*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "1️⃣  *700 000 so'm*\n"
            "      📹 1-kun • 1 ta kamera\n\n"
            "2️⃣  *1 400 000 so'm*\n"
            "      📹 1-kun va 2-kun • 1 ta kamera\n\n"
            "3️⃣  *2 000 000 so'm*\n"
            "      📹 1-kun: 1 kamera | 2-kun: 2 kamera\n\n"
            "4️⃣  *VIP — 300$*\n"
            "      📹 1-kun: 1 kamera | 2-kun: 2 kamera\n"
            "      🎥 + Professional Kran kamera\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        "pkg_chosen": (
            "✅ Siz tanladingiz:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "{pkg}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📅 Endi *toy sanasini* yozing.\n\n"
            "📌 *Format:* `05.06.2026`\n"
            "    (kun.oy.yil)"
        ),
        "ask_event": (
            "✅ Sana qabul qilindi: *{date}*\n\n"
            "🎊 Endi *tadbir turini* tanlang:\n"
            "    (Quyidagi tugmalardan birini bosing)"
        ),
        "events": [
            "💍 Nikoh toyi", "🎂 Tug'ilgan kun", "👦 Xatna toyi",
            "🎉 Banket", "🕋 Xaj / Umra", "🔤 Alifbe bayrami", "👶 Chaqaloq toyi",
        ],
        "ask_location": (
            "✅ Tadbir: *{event}*\n\n"
            "📍 Endi *toy bo'ladigan joyning lokatsiyasini* yuboring.\n\n"
            "💡 *Qanday yuborish kerak?*\n"
            "    Quyidagi tugmani bosing ↓"
        ),
        "btn_location": "📍 Lokatsiyani yuborish",
        "ask_address": (
            "✅ Lokatsiya qabul qilindi!\n\n"
            "🏠 Endi *manzilni so'z bilan* yozing.\n\n"
            "📌 *Misol:*\n"
            "    Toshkent, Yunusobod tumani,\n"
            "    Navruz ko'chasi 15, «Oq oltin» restoran"
        ),
        "order_done": (
            "🎉 *Zakazingiz muvaffaqiyatli qabul qilindi!*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👤 Ism:       {name}\n"
            "📱 Telefon:   {phone}\n"
            "📦 Paket:     {pkg}\n"
            "📅 Sana:      {date}\n"
            "🎊 Tadbir:    {event}\n"
            "🏠 Manzil:    {address}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📞 Tez orada siz bilan bog'lanamiz!\n"
            "⏰ Ish vaqti: 09:00 — 22:00\n\n"
            "Rahmat! 🙏"
        ),
    },

    "uz_cyr": {
        "flag":            "🇺🇿 Ўзбек (Кирилл)",
        "welcome": (
            "🎬 *Садаф Медиа* — Профессионал тўй видеография хизмати!\n\n"
            "📹 Биз сизнинг энг муҳим кунларингизни\n"
            "    абадий хотирада сақлаймиз.\n"
            "    ҳар бир кадр юракдан ❤️\n\n"
            "📱 Давом этиш учун *телефон рақамингизни* юборинг:"
        ),
        "btn_contact":     "📱 Телефон рақамни юбориш",
        "btn_call_admin":  "📞 Админ билан боғланиш",
        "btn_change_lang": "🌐 Тилни ўзгартириш",
        "ask_admin_msg": (
            "💬 *Админ билан боғланиш*\n\n"
            "Хабарингизни ёзинг — админ тез орада жавоб беради.\n\n"
            "✍️ Хабарингизни шу ерга ёзинг:"
        ),
        "admin_msg_sent": (
            "✅ *Хабарингиз админга юборилди!*\n\n"
            "📞 Тез орада жавоб беришади.\n"
            "⏰ Иш вақти: 09:00 — 22:00\n\n"
            "Заказ қилиш учун 👇\n"
            "Телефон рақамингизни юборинг:"
        ),
        "contact_sent": (
            "✅ Раҳмат! Рақамингиз қабул қилинди.\n\n"
            "👇 Энди қуйидаги *пакетлардан бирини танланг:*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "1️⃣  *700 000 сўм*\n"
            "      📹 1-кун • 1 та камера\n\n"
            "2️⃣  *1 400 000 сўм*\n"
            "      📹 1-кун ва 2-кун • 1 та камера\n\n"
            "3️⃣  *2 000 000 сўм*\n"
            "      📹 1-кун: 1 камера | 2-кун: 2 камера\n\n"
            "4️⃣  *VIP — 300$*\n"
            "      📹 1-кун: 1 камера | 2-кун: 2 камера\n"
            "      🎥 + Профессионал Кран камера\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        "pkg_chosen": (
            "✅ Сиз танладингиз:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "{pkg}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📅 Энди *тўй санасини* ёзинг.\n\n"
            "📌 *Формат:* `05.06.2026`\n"
            "    (кун.ой.йил)"
        ),
        "ask_event": (
            "✅ Сана қабул қилинди: *{date}*\n\n"
            "🎊 Энди *тадбир турини* танланг:\n"
            "    (Қуйидаги тугмалардан бирини босинг)"
        ),
        "events": [
            "💍 Никоҳ тўйи", "🎂 Туғилган кун", "👦 Хатна тўйи",
            "🎉 Банкет", "🕋 Ҳаж / Умра", "🔤 Алифбе байрами", "👶 Чақалоқ тўйи",
        ],
        "ask_location": (
            "✅ Тадбир: *{event}*\n\n"
            "📍 Энди *тўй бўладиган жойнинг локациясини* юборинг.\n\n"
            "💡 *Қандай юбориш керак?*\n"
            "    Қуйидаги тугмани босинг ↓"
        ),
        "btn_location": "📍 Локацияни юбориш",
        "ask_address": (
            "✅ Локация қабул қилинди!\n\n"
            "🏠 Энди *манзилни сўз билан* ёзинг.\n\n"
            "📌 *Мисол:*\n"
            "    Тошкент, Юнусобод тумани,\n"
            "    Навруз кўчаси 15, «Оқ олтин» ресторан"
        ),
        "order_done": (
            "🎉 *Заказингиз муваффақиятли қабул қилинди!*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👤 Исм:       {name}\n"
            "📱 Телефон:   {phone}\n"
            "📦 Пакет:     {pkg}\n"
            "📅 Сана:      {date}\n"
            "🎊 Тадбир:    {event}\n"
            "🏠 Манзил:    {address}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📞 Тез орада сиз билан боғланамиз!\n"
            "⏰ Иш вақти: 09:00 — 22:00\n\n"
            "Раҳмат! 🙏"
        ),
    },

    "ru": {
        "flag":            "🇷🇺 Русский",
        "welcome": (
            "🎬 *Sadaf Media* — Профессиональная видеосъёмка свадеб!\n\n"
            "📹 Мы сохраним ваши самые важные моменты\n"
            "    навсегда в памяти.\n"
            "    каждый кадр — от сердца ❤️\n\n"
            "📱 Для продолжения отправьте *номер телефона:*"
        ),
        "btn_contact":     "📱 Отправить номер телефона",
        "btn_call_admin":  "📞 Связаться с администратором",
        "btn_change_lang": "🌐 Сменить язык",
        "ask_admin_msg": (
            "💬 *Связь с администратором*\n\n"
            "Напишите ваше сообщение — администратор скоро ответит.\n\n"
            "✍️ Введите ваше сообщение:"
        ),
        "admin_msg_sent": (
            "✅ *Ваше сообщение отправлено администратору!*\n\n"
            "📞 Вам ответят в ближайшее время.\n"
            "⏰ Время работы: 09:00 — 22:00\n\n"
            "Для оформления заказа 👇\n"
            "Отправьте номер телефона:"
        ),
        "contact_sent": (
            "✅ Спасибо! Номер принят.\n\n"
            "👇 Выберите один из *пакетов:*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "1️⃣  *700 000 сум*\n"
            "      📹 1 день • 1 камера\n\n"
            "2️⃣  *1 400 000 сум*\n"
            "      📹 1-й и 2-й день • 1 камера\n\n"
            "3️⃣  *2 000 000 сум*\n"
            "      📹 1-й день: 1 | 2-й день: 2 камеры\n\n"
            "4️⃣  *VIP — 300$*\n"
            "      📹 1-й день: 1 | 2-й день: 2 камеры\n"
            "      🎥 + Профессиональная крановая камера\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        "pkg_chosen": (
            "✅ Вы выбрали:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "{pkg}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📅 Введите *дату торжества.*\n\n"
            "📌 *Формат:* `05.06.2026`\n"
            "    (день.месяц.год)"
        ),
        "ask_event": (
            "✅ Дата принята: *{date}*\n\n"
            "🎊 Выберите *тип мероприятия:*\n"
            "    (Нажмите одну из кнопок ниже)"
        ),
        "events": [
            "💍 Свадьба", "🎂 День рождения", "👦 Хатна",
            "🎉 Банкет", "🕋 Хадж / Умра", "🔤 Алифбе", "👶 Рождение ребёнка",
        ],
        "ask_location": (
            "✅ Мероприятие: *{event}*\n\n"
            "📍 Отправьте *геолокацию* места проведения.\n\n"
            "💡 *Как отправить?*\n"
            "    Нажмите кнопку ниже ↓"
        ),
        "btn_location": "📍 Отправить геолокацию",
        "ask_address": (
            "✅ Геолокация принята!\n\n"
            "🏠 Напишите *адрес* словами.\n\n"
            "📌 *Пример:*\n"
            "    Ташкент, Юнусабадский р-н,\n"
            "    ул. Навруз 15, ресторан «Ок Олтин»"
        ),
        "order_done": (
            "🎉 *Ваш заказ успешно принят!*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👤 Имя:        {name}\n"
            "📱 Телефон:    {phone}\n"
            "📦 Пакет:      {pkg}\n"
            "📅 Дата:       {date}\n"
            "🎊 Событие:    {event}\n"
            "🏠 Адрес:      {address}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📞 Мы свяжемся с вами в ближайшее время!\n"
            "⏰ Время работы: 09:00 — 22:00\n\n"
            "Спасибо! 🙏"
        ),
    },

    "en": {
        "flag":            "🇬🇧 English",
        "welcome": (
            "🎬 *Sadaf Media* — Professional Wedding Videography!\n\n"
            "📹 We capture your most important moments\n"
            "    and preserve them forever.\n"
            "    every frame — from the heart ❤️\n\n"
            "📱 Please share your *phone number* to continue:"
        ),
        "btn_contact":     "📱 Share phone number",
        "btn_call_admin":  "📞 Contact admin",
        "btn_change_lang": "🌐 Change language",
        "ask_admin_msg": (
            "💬 *Contact Admin*\n\n"
            "Write your message — admin will reply shortly.\n\n"
            "✍️ Type your message:"
        ),
        "admin_msg_sent": (
            "✅ *Your message has been sent to admin!*\n\n"
            "📞 We will reply shortly.\n"
            "⏰ Working hours: 09:00 — 22:00\n\n"
            "To place an order 👇\n"
            "Share your phone number:"
        ),
        "contact_sent": (
            "✅ Thank you! Number received.\n\n"
            "👇 Please choose one of our *packages:*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "1️⃣  *700,000 UZS*\n"
            "      📹 Day 1 • 1 camera\n\n"
            "2️⃣  *1,400,000 UZS*\n"
            "      📹 Day 1 & Day 2 • 1 camera\n\n"
            "3️⃣  *2,000,000 UZS*\n"
            "      📹 Day 1: 1 cam | Day 2: 2 cams\n\n"
            "4️⃣  *VIP — $300*\n"
            "      📹 Day 1: 1 cam | Day 2: 2 cams\n"
            "      🎥 + Professional Crane camera\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        "pkg_chosen": (
            "✅ You selected:\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "{pkg}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📅 Now enter the *event date.*\n\n"
            "📌 *Format:* `05.06.2026`\n"
            "    (day.month.year)"
        ),
        "ask_event": (
            "✅ Date accepted: *{date}*\n\n"
            "🎊 Now select the *type of event:*\n"
            "    (Tap one of the buttons below)"
        ),
        "events": [
            "💍 Wedding", "🎂 Birthday", "👦 Circumcision",
            "🎉 Banquet", "🕋 Hajj / Umrah", "🔤 Alifbe", "👶 Baby Shower",
        ],
        "ask_location": (
            "✅ Event: *{event}*\n\n"
            "📍 Please send the *location* of the venue.\n\n"
            "💡 *How to send?*\n"
            "    Tap the button below ↓"
        ),
        "btn_location": "📍 Send location",
        "ask_address": (
            "✅ Location received!\n\n"
            "🏠 Now write the *venue address* in words.\n\n"
            "📌 *Example:*\n"
            "    Tashkent, Yunusobod district,\n"
            "    15 Navruz St, Oq Oltin restaurant"
        ),
        "order_done": (
            "🎉 *Your order has been received!*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👤 Name:      {name}\n"
            "📱 Phone:     {phone}\n"
            "📦 Package:   {pkg}\n"
            "📅 Date:      {date}\n"
            "🎊 Event:     {event}\n"
            "🏠 Address:   {address}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📞 We will contact you shortly!\n"
            "⏰ Working hours: 09:00 — 22:00\n\n"
            "Thank you! 🙏"
        ),
    },
}

def tx(lang, key, **kw):
    base = TEXTS.get(lang, TEXTS["uz"])
    text = base.get(key, TEXTS["uz"].get(key, ""))
    return text.format(**kw) if kw else text


# ╔══════════════════════════════════════╗
# ║           JSON YORDAMCHILAR          ║
# ╚══════════════════════════════════════╝
DEFAULT_PRICES = {
    "p1": {"label": "1️⃣  Paket — 700 000 so'm",   "price": "700 000 so'm",   "desc": "1-kun: 1 ta kamera"},
    "p2": {"label": "2️⃣  Paket — 1 400 000 so'm", "price": "1 400 000 so'm", "desc": "2 kun: 1 ta kamera"},
    "p3": {"label": "3️⃣  Paket — 2 000 000 so'm", "price": "2 000 000 so'm", "desc": "1-kun: 1 ta | 2-kun: 2 ta kamera"},
    "p4": {"label": "4️⃣  VIP Paket — 300$",        "price": "300$",           "desc": "1-kun: 1 ta | 2-kun: 2 ta + Kran kamera"},
}

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    if path == PRICES_FILE:
        save_json(path, DEFAULT_PRICES)
        return dict(DEFAULT_PRICES)
    return []

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def register_user(uid, name, lang):
    if uid == ADMIN_ID:
        return
    users = load_json(USERS_FILE)
    found = next((u for u in users if u["id"] == uid), None)
    if found:
        found["lang"] = lang
        found["name"] = name
    else:
        users.append({"id": uid, "name": name, "lang": lang})
    save_json(USERS_FILE, users)

def get_saved_lang(uid):
    users = load_json(USERS_FILE)
    found = next((u for u in users if u["id"] == uid), None)
    return found["lang"] if found and "lang" in found else None

def get_lang(ctx):
    return ctx.user_data.get("lang", "uz")

def lang_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇺🇿 O'zbek (Lotin)",  callback_data="lang:uz"),
            InlineKeyboardButton("🇺🇿 Ўзбек (Кирилл)", callback_data="lang:uz_cyr"),
        ],
        [
            InlineKeyboardButton("🇷🇺 Русский",  callback_data="lang:ru"),
            InlineKeyboardButton("🇬🇧 English",  callback_data="lang:en"),
        ],
    ])

def main_kb(lang):
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(tx(lang, "btn_contact"), request_contact=True)],
            [KeyboardButton(tx(lang, "btn_call_admin"))],
            [KeyboardButton(tx(lang, "btn_change_lang"))],
        ],
        resize_keyboard=True
    )

# ╔══════════════════════════════════════╗
# ║     TUGMA MATNI ANIQLASH (HELPER)    ║
# ╚══════════════════════════════════════╝

# Barcha tillardagi "admin" tugma matnlari
ADMIN_BTN_TEXTS = [
    "📞 Admin bilan bog'lanish",       # uz
    "📞 Админ билан боғланиш",         # uz_cyr
    "📞 Связаться с администратором",   # ru
    "📞 Contact admin",                 # en
]

# Barcha tillardagi "til o'zgartirish" tugma matnlari
LANG_BTN_TEXTS = [
    "🌐 Tilni o'zgartirish",   # uz
    "🌐 Тилни ўзгартириш",     # uz_cyr
    "🌐 Сменить язык",          # ru
    "🌐 Change language",        # en
]

def is_admin_btn(text: str) -> bool:
    return text.strip() in ADMIN_BTN_TEXTS

def is_lang_btn(text: str) -> bool:
    return text.strip() in LANG_BTN_TEXTS


# ╔══════════════════════════════════════╗
# ║              /START                  ║
# ╚══════════════════════════════════════╝
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    user = update.effective_user

    if user.id == ADMIN_ID:
        kb = ReplyKeyboardMarkup(
            [
                ["📋 Zakazlar",       "✏️ Narxlarni tahrirlash"],
                ["💬 Mijozga yozish", "📤 Broadcast"],
            ],
            resize_keyboard=True
        )
        await update.message.reply_text(
            "👨‍💼 *Admin panelga xush kelibsiz!*\n\n"
            "Quyidagi tugmalardan birini tanlang 👇",
            parse_mode="Markdown",
            reply_markup=kb
        )
        return ADMIN_HOME

    saved = get_saved_lang(user.id)
    if saved:
        ctx.user_data["lang"] = saved
        await update.message.reply_text(
            tx(saved, "welcome"),
            parse_mode="Markdown",
            reply_markup=main_kb(saved)
        )
        return CONTACT

    await update.message.reply_text(
        "🌐 *Tilni tanlang*\n"
        "Выберите язык\n"
        "Choose your language\n"
        "Тилни танланг (Кирилл)",
        parse_mode="Markdown",
        reply_markup=lang_kb()
    )
    return LANG_SELECT


# ╔══════════════════════════════════════╗
# ║           TIL TANLASH CB             ║
# ╚══════════════════════════════════════╝
async def cb_lang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = q.data.split(":")[1]
    ctx.user_data["lang"] = lang
    user = q.from_user
    register_user(user.id, user.full_name, lang)

    try:
        await q.edit_message_reply_markup(reply_markup=None)
    except Exception:
        pass

    await q.message.reply_text(
        tx(lang, "welcome"),
        parse_mode="Markdown",
        reply_markup=main_kb(lang)
    )
    return CONTACT

async def msg_change_lang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐 *Yangi tilni tanlang:*\n"
        "Выберите новый язык:\n"
        "Choose new language:\n"
        "Янги тилни танланг:",
        parse_mode="Markdown",
        reply_markup=lang_kb()
    )
    return LANG_SELECT


# ╔══════════════════════════════════════╗
# ║     ADMIN BILAN BOG'LANISH           ║
# ╚══════════════════════════════════════╝
async def msg_ask_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(ctx)
    await update.message.reply_text(
        tx(lang, "ask_admin_msg"),
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return ADMIN_MSG_INPUT

async def msg_send_to_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(ctx)
    user = update.effective_user
    user_msg = update.message.text
    uname = f"@{user.username}" if user.username else "username yo'q"
    flag  = TEXTS.get(lang, {}).get("flag", lang)

    await ctx.bot.send_message(
        ADMIN_ID,
        f"📞 *YANGI MUROJAAT KELDI!*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Ism:      {user.full_name}\n"
        f"🆔 ID:       `{user.id}`\n"
        f"📲 Telegram: {uname}\n"
        f"🌐 Til:      {flag}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💬 Xabar:\n{user_msg}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📩 Javob berish uchun quyidagini bosing 👇",
        parse_mode="Markdown"
    )
    await ctx.bot.send_message(ADMIN_ID, f"/reply_{user.id}")

    await update.message.reply_text(
        tx(lang, "admin_msg_sent"),
        parse_mode="Markdown",
        reply_markup=main_kb(lang)
    )
    return CONTACT


# ╔══════════════════════════════════════╗
# ║         KONTAKT → PAKET              ║
# ╚══════════════════════════════════════╝
async def msg_contact(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(ctx)

    # ── Tugma matnlari kelganda (kontakt emas) ──────────────────────────────
    if update.message.text:
        text = update.message.text.strip()
        if is_admin_btn(text):
            return await msg_ask_admin(update, ctx)
        if is_lang_btn(text):
            return await msg_change_lang(update, ctx)
        # Boshqa matn — eslatma
        await update.message.reply_text(
            "⚠️ Iltimos quyidagi tugmani bosib telefon raqamingizni yuboring 👇",
            reply_markup=main_kb(lang)
        )
        return CONTACT

    # ── Kontakt keldi ────────────────────────────────────────────────────────
    if update.message.contact:
        contact = update.message.contact
        ctx.user_data["name"]  = contact.first_name or update.effective_user.full_name
        ctx.user_data["phone"] = contact.phone_number

        prices = load_json(PRICES_FILE)
        btns = []
        for key, p in prices.items():
            btns.append([InlineKeyboardButton(
                f"{p['label']}\n📹 {p.get('desc', '')}",
                callback_data=f"pkg:{key}"
            )])

        await update.message.reply_text(
            tx(lang, "contact_sent"),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(btns)
        )
        return PKG_SELECT

    # ── Location yoki boshqa media keldi ────────────────────────────────────
    await update.message.reply_text(
        "⚠️ Iltimos quyidagi tugmani bosib telefon raqamingizni yuboring 👇",
        reply_markup=main_kb(lang)
    )
    return CONTACT


# ╔══════════════════════════════════════╗
# ║         PAKET TANLASH                ║
# ╚══════════════════════════════════════╝
async def cb_pkg(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang  = get_lang(ctx)
    key   = q.data.split(":")[1]
    prices = load_json(PRICES_FILE)
    p = prices[key]
    ctx.user_data["package"] = f"{p['label']} | {p.get('desc', '')}"

    await q.edit_message_reply_markup(reply_markup=None)
    await q.message.reply_text(
        tx(lang, "pkg_chosen", pkg=f"{p['label']}\n📹 {p.get('desc', '')}"),
        parse_mode="Markdown"
    )
    return DATE_INPUT


# ╔══════════════════════════════════════╗
# ║           SANA KIRITISH              ║
# ╚══════════════════════════════════════╝
async def msg_date(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(ctx)
    ctx.user_data["date"] = update.message.text.strip()
    events = tx(lang, "events")
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton(e)] for e in events],
        resize_keyboard=True, one_time_keyboard=True
    )
    await update.message.reply_text(
        tx(lang, "ask_event", date=ctx.user_data["date"]),
        parse_mode="Markdown",
        reply_markup=kb
    )
    return EVENT_SELECT


# ╔══════════════════════════════════════╗
# ║         TADBIR TURI                  ║
# ╚══════════════════════════════════════╝
async def msg_event(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(ctx)
    ctx.user_data["event"] = update.message.text
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton(tx(lang, "btn_location"), request_location=True)]],
        resize_keyboard=True
    )
    await update.message.reply_text(
        tx(lang, "ask_location", event=update.message.text),
        parse_mode="Markdown",
        reply_markup=kb
    )
    return LOCATION_INPUT


# ╔══════════════════════════════════════╗
# ║           LOKATSIYA                  ║
# ╚══════════════════════════════════════╝
async def msg_location(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(ctx)
    loc  = update.message.location
    ctx.user_data["lat"] = loc.latitude
    ctx.user_data["lon"] = loc.longitude
    await update.message.reply_text(
        tx(lang, "ask_address"),
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return ADDRESS_INPUT


# ╔══════════════════════════════════════╗
# ║        MANZIL → ZAKAZ TAYYOR         ║
# ╚══════════════════════════════════════╝
async def msg_address(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang    = get_lang(ctx)
    d       = ctx.user_data
    address = update.message.text

    order = {
        "user_id": update.effective_user.id,
        "lang":    lang,
        "name":    d["name"],    "phone":   d["phone"],
        "package": d["package"], "date":    d["date"],
        "event":   d["event"],   "address": address,
        "lat":     d["lat"],     "lon":     d["lon"],
    }
    orders = load_json(ORDERS_FILE)
    orders.append(order)
    save_json(ORDERS_FILE, orders)

    flag = TEXTS.get(lang, {}).get("flag", lang)
    await ctx.bot.send_message(
        ADMIN_ID,
        f"🔔 *YANGI ZAKAZ KELDI!*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Ism:     {order['name']}\n"
        f"📱 Tel:     `{order['phone']}`\n"
        f"📦 Paket:   {order['package']}\n"
        f"📅 Sana:    {order['date']}\n"
        f"🎊 Tadbir:  {order['event']}\n"
        f"🏠 Manzil:  {order['address']}\n"
        f"🌐 Til:     {flag}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 Lokatsiya quyida 👇",
        parse_mode="Markdown"
    )
    await ctx.bot.send_location(ADMIN_ID, latitude=order["lat"], longitude=order["lon"])

    await update.message.reply_text(
        tx(lang, "order_done",
           name=order["name"],    phone=order["phone"],
           pkg=order["package"],  date=order["date"],
           event=order["event"],  address=address),
        parse_mode="Markdown"
    )
    return ConversationHandler.END


# ╔══════════════════════════════════════╗
# ║           ADMIN — ZAKAZLAR           ║
# ╚══════════════════════════════════════╝
async def admin_orders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    orders = load_json(ORDERS_FILE)
    if not orders:
        await update.message.reply_text(
            "📭 *Hozircha zakazlar yo'q.*\n\nMijozlar zakaz qilganda shu yerda ko'rinadi.",
            parse_mode="Markdown"
        )
        return ADMIN_HOME
    btns = []
    for i, o in enumerate(orders):
        btns.append([InlineKeyboardButton(
            f"#{i+1} | {o['event']} | {o['date']} | {o['name']}",
            callback_data=f"order:{i}"
        )])
    await update.message.reply_text(
        f"📋 *Zakazlar ro'yxati*\n\nJami: *{len(orders)} ta zakaz*\n\nKo'rish uchun tanlang 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(btns)
    )
    return ADMIN_HOME

async def cb_view_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    i = int(q.data.split(":")[1])
    orders = load_json(ORDERS_FILE)
    if i >= len(orders):
        await q.edit_message_text("❌ Bu zakaz topilmadi.")
        return ADMIN_HOME
    o    = orders[i]
    flag = TEXTS.get(o.get("lang", "uz"), {}).get("flag", "?")
    await ctx.bot.send_location(update.effective_chat.id, latitude=o["lat"], longitude=o["lon"])
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("🗑 Zakazni o'chirish", callback_data=f"del:{i}")
    ]])
    await ctx.bot.send_message(
        update.effective_chat.id,
        f"📋 *Zakaz #{i+1}*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Ism:     {o['name']}\n"
        f"📱 Tel:     `{o['phone']}`\n"
        f"📦 Paket:   {o['package']}\n"
        f"📅 Sana:    {o['date']}\n"
        f"🎊 Tadbir:  {o['event']}\n"
        f"🏠 Manzil:  {o['address']}\n"
        f"🌐 Til:     {flag}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="Markdown",
        reply_markup=kb
    )
    return ADMIN_HOME

async def cb_delete_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    i = int(q.data.split(":")[1])
    orders = load_json(ORDERS_FILE)
    if i < len(orders):
        name = orders[i]["name"]
        orders.pop(i)
        save_json(ORDERS_FILE, orders)
        await q.edit_message_text(f"✅ *{name}* ning zakazi o'chirildi.", parse_mode="Markdown")
    return ADMIN_HOME


# ╔══════════════════════════════════════╗
# ║        ADMIN — NARX TAHRIRLASH       ║
# ╚══════════════════════════════════════╝
async def admin_prices(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    prices = load_json(PRICES_FILE)
    btns = [[InlineKeyboardButton(p["label"], callback_data=f"epkg:{k}")] for k, p in prices.items()]
    await update.message.reply_text(
        "✏️ *Narxlarni tahrirlash*\n\nQaysi paketni o'zgartirmoqchisiz? 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(btns)
    )
    return EDIT_PKG_SELECT

async def cb_edit_pkg_select(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    key = q.data.split(":")[1]
    ctx.user_data["edit_key"] = key
    prices = load_json(PRICES_FILE)
    p = prices[key]
    await q.edit_message_text(
        f"✏️ *{p['label']}* — tahrirlash\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Joriy narx:   {p['price']}\n"
        f"📝 Joriy tavsif: {p.get('desc', '')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Yangi ma'lumot yuboring:\n`yangi narx | yangi tavsif`\n\n"
        f"📌 Misol:\n`800 000 so'm | 1 kun, 1 ta kamera`",
        parse_mode="Markdown"
    )
    return EDIT_PKG_VALUE

async def msg_edit_pkg_value(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text   = update.message.text.strip()
    key    = ctx.user_data.get("edit_key")
    prices = load_json(PRICES_FILE)
    if "|" in text:
        parts = text.split("|", 1)
        prices[key]["price"] = parts[0].strip()
        prices[key]["desc"]  = parts[1].strip()
    else:
        prices[key]["price"] = text
    save_json(PRICES_FILE, prices)
    await update.message.reply_text(
        f"✅ *{prices[key]['label']}* yangilandi!\n\n"
        f"💰 Narx:   {prices[key]['price']}\n"
        f"📝 Tavsif: {prices[key].get('desc', '')}",
        parse_mode="Markdown"
    )
    return ADMIN_HOME


# ╔══════════════════════════════════════╗
# ║        ADMIN — MIJOZGA YOZISH        ║
# ╚══════════════════════════════════════╝
async def admin_chat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    users = [u for u in load_json(USERS_FILE) if u["id"] != ADMIN_ID]
    if not users:
        await update.message.reply_text(
            "👥 *Hozircha ro'yxatda foydalanuvchi yo'q.*",
            parse_mode="Markdown"
        )
        return ADMIN_HOME
    btns = [[InlineKeyboardButton(
        f"👤 {u['name']} | {TEXTS.get(u.get('lang','uz'),{}).get('flag','?')}",
        callback_data=f"chat:{u['id']}"
    )] for u in users]
    await update.message.reply_text(
        f"💬 *Mijozga xabar*\n\n{len(users)} ta foydalanuvchi. Kimga? 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(btns)
    )
    return CHAT_USER_SELECT

async def cb_chat_select(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    ctx.user_data["chat_target"] = int(q.data.split(":")[1])
    await q.edit_message_text(
        "✍️ *Xabaringizni yozing:*\n\nMatn, rasm yoki video yuborishingiz mumkin.",
        parse_mode="Markdown"
    )
    return CHAT_SEND

async def msg_chat_send(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    target = ctx.user_data.get("chat_target")
    if not target:
        return ADMIN_HOME
    try:
        if update.message.photo:
            await ctx.bot.send_photo(target, update.message.photo[-1].file_id,
                caption=f"📩 *Admin xabari:*\n\n{update.message.caption or ''}",
                parse_mode="Markdown")
        elif update.message.video:
            await ctx.bot.send_video(target, update.message.video.file_id,
                caption=f"📩 *Admin xabari:*\n\n{update.message.caption or ''}",
                parse_mode="Markdown")
        else:
            await ctx.bot.send_message(target,
                f"📩 *Admin xabari:*\n\n{update.message.text}",
                parse_mode="Markdown")
        await update.message.reply_text("✅ *Xabar yuborildi!*", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Yuborib bo'lmadi: {e}")
    return ADMIN_HOME


# ╔══════════════════════════════════════╗
# ║            BROADCAST                 ║
# ╚══════════════════════════════════════╝
async def admin_broadcast_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    users = [u for u in load_json(USERS_FILE) if u["id"] != ADMIN_ID]
    await update.message.reply_text(
        f"📤 *Ommaviy xabar yuborish*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Jami foydalanuvchilar: *{len(users)} ta*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 Xabar yozing yoki rasm/video yuboring.\n"
        f"❌ Bekor qilish: /cancel",
        parse_mode="Markdown"
    )
    return BROADCAST_WAIT

async def admin_broadcast_send(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    users = [u for u in load_json(USERS_FILE) if u["id"] != ADMIN_ID]
    total = len(users)
    prog  = await update.message.reply_text(
        f"⏳ *Yuborilmoqda...* 0 / {total}", parse_mode="Markdown"
    )
    sent = failed = 0
    for i, u in enumerate(users, 1):
        try:
            if update.message.photo:
                await ctx.bot.send_photo(u["id"], update.message.photo[-1].file_id,
                    caption=update.message.caption or "", parse_mode="Markdown")
            elif update.message.video:
                await ctx.bot.send_video(u["id"], update.message.video.file_id,
                    caption=update.message.caption or "", parse_mode="Markdown")
            else:
                await ctx.bot.send_message(u["id"], update.message.text, parse_mode="Markdown")
            sent += 1
        except Exception:
            failed += 1
        if i % 5 == 0 or i == total:
            try:
                await prog.edit_text(f"⏳ *Yuborilmoqda...* {i} / {total}", parse_mode="Markdown")
            except Exception:
                pass
    await prog.edit_text(
        f"✅ *Broadcast yakunlandi!*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✔️ Yuborildi:    *{sent} ta*\n"
        f"❌ Yuborilmadi:  *{failed} ta*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )
    return ADMIN_HOME

async def cmd_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("❌ *Bekor qilindi.*", parse_mode="Markdown")
        return ADMIN_HOME
    return ConversationHandler.END


# ╔══════════════════════════════════════╗
# ║     /reply_ID — ADMINGA JAVOB        ║
# ╚══════════════════════════════════════╝
async def handle_reply(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    text = update.message.text.strip()
    try:
        parts   = text.split(" ", 1)
        user_id = int(parts[0].replace("/reply_", ""))
        msg     = parts[1] if len(parts) > 1 else ""
        if not msg:
            await update.message.reply_text(
                "⚠️ Xabar bo'sh!\n\n📌 Misol:\n`/reply_123456789 Salom! Tez orada qo'ng'iroq qilamiz.`",
                parse_mode="Markdown"
            )
            return
        await ctx.bot.send_message(
            user_id,
            f"📩 *Admin javobi:*\n\n{msg}",
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ *Xabar mijozga yuborildi!*", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {e}")


# ╔══════════════════════════════════════╗
# ║               MAIN                   ║
# ╚══════════════════════════════════════╝
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # /reply_ID — conversation tashqarisida ishlaydi
    app.add_handler(MessageHandler(filters.Regex(r"^/reply_\d+"), handle_reply))

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", cmd_start),
        ],
        states={
            # Til tanlash
            LANG_SELECT: [
                CallbackQueryHandler(cb_lang, pattern="^lang:"),
                # Agar foydalanuvchi biror matn yozsa — lang_kb qayta ko'rsatiladi
                MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: u.message.reply_text(
                    "🌐 Iltimos tilni tanlang 👆", reply_markup=lang_kb()
                )),
            ],

            # ── CONTACT state: kontakt + tugmalar + inline lang ──────────────
            CONTACT: [
                # 1) Kontakt (request_contact tugmasi)
                MessageHandler(filters.CONTACT, msg_contact),
                # 2) Barcha matnli xabarlar — ichida tugma tekshiruvi bor
                MessageHandler(filters.TEXT & ~filters.COMMAND, msg_contact),
                # 3) Til tanlash inline callback (agar til o'zgartirish bosilsa)
                CallbackQueryHandler(cb_lang, pattern="^lang:"),
            ],

            # Mijoz admin xabarini yozadi
            ADMIN_MSG_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, msg_send_to_admin),
            ],

            # Paket, sana, tadbir, lokatsiya, manzil
            PKG_SELECT:     [CallbackQueryHandler(cb_pkg, pattern="^pkg:")],
            DATE_INPUT:     [MessageHandler(filters.TEXT & ~filters.COMMAND, msg_date)],
            EVENT_SELECT:   [MessageHandler(filters.TEXT & ~filters.COMMAND, msg_event)],
            LOCATION_INPUT: [MessageHandler(filters.LOCATION, msg_location)],
            ADDRESS_INPUT:  [MessageHandler(filters.TEXT & ~filters.COMMAND, msg_address)],

            # Admin panel
            ADMIN_HOME: [
                MessageHandler(filters.Regex("Zakazlar"),        admin_orders),
                MessageHandler(filters.Regex("Narxlarni"),       admin_prices),
                MessageHandler(filters.Regex("Mijozga"),         admin_chat),
                MessageHandler(filters.Regex("Broadcast"),       admin_broadcast_start),
                CallbackQueryHandler(cb_view_order,   pattern="^order:"),
                CallbackQueryHandler(cb_delete_order, pattern="^del:"),
            ],
            EDIT_PKG_SELECT:  [CallbackQueryHandler(cb_edit_pkg_select, pattern="^epkg:")],
            EDIT_PKG_VALUE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, msg_edit_pkg_value)],
            CHAT_USER_SELECT: [CallbackQueryHandler(cb_chat_select, pattern="^chat:")],
            CHAT_SEND: [
                MessageHandler(
                    (filters.TEXT | filters.PHOTO | filters.VIDEO) & ~filters.COMMAND,
                    msg_chat_send
                )
            ],
            BROADCAST_WAIT: [
                CommandHandler("cancel", cmd_cancel),
                MessageHandler(
                    (filters.TEXT | filters.PHOTO | filters.VIDEO) & ~filters.COMMAND,
                    admin_broadcast_send
                )
            ],
        },
        fallbacks=[
            CommandHandler("start", cmd_start),
            CommandHandler("cancel", cmd_cancel),
        ],
    )

    app.add_handler(conv)
    print("✅ Bot ishga tushdi...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
