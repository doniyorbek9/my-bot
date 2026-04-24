#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
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

# ===================== CONFIG =====================
ADMIN_ID = 7948989650
BOT_TOKEN = os.getenv("TOKEN")

PRICES_FILE = "prices.json"
ORDERS_FILE = "orders.json"
USERS_FILE  = "users.json"

(
    LANG_SELECT, CONTACT, PACKAGE_SELECT, DATE_INPUT, EVENT_TYPE,
    LOCATION, ADDRESS_INPUT, ADMIN_MAIN,
    EDIT_PRICE_SELECT, EDIT_PRICE_VALUE,
    ADMIN_CHAT_SELECT, ADMIN_CHATTING,
    BROADCAST_INPUT
) = range(13)

# ===================== TARJIMALAR =====================
T = {
    "uz": {
        "welcome":        "📸 *Sadaf Media*ga xush kelibsiz!\n\nDavom etish uchun telefon raqamingizni yuboring 👇",
        "send_contact":   "📱 Telefon raqamni yuborish",
        "contact_admin":  "📞 Admin bilan bog'lanish",
        "choose_package": "📦 *Paketni tanlang:*\n\n1️⃣ *700,000 so'm* — 1-kun: 1 ta kamera\n2️⃣ *1,400,000 so'm* — 1-kun va 2-kun: 1 ta kamera\n3️⃣ *2,000,000 so'm* — 1-kun: 1 ta | 2-kun: 2 ta kamera\n4️⃣ *VIP 300$* — 1-kun: 1 ta | 2-kun: 2 ta + Kran\n\n👇 Tanlang:",
        "chosen":         "✅ Tanlangan: *{name}* — {price}\n\n📅 *Toy sanasini kiriting:*\nMisol: `25.04.2026`",
        "enter_date":     "📅 Toy sanasini kiriting:\nMisol: `25.04.2026`",
        "choose_event":   "🎉 *Tadbir turini tanlang:*",
        "events":         ["💍 Nikoh","👶 Chaqaloq","👦 Xatna","🎉 Banket","🕋 Xaj/Umra","🔤 Alifbe","🎂 Tug'ilgan kun"],
        "send_location":  "📍 Toy bo'ladigan *joylashuvni* yuboring:",
        "loc_btn":        "📍 Lokatsiya yuborish",
        "enter_address":  "🏠 Toy bo'ladigan *manzilni* yozing:\n(Misol: Yunusobod 12-mavze, Oq oltin restoran)",
        "order_done":     "✅ *Zakazingiz qabul qilindi!*\n\nTez orada siz bilan bog'lanamiz. Rahmat! 🙏",
        "admin_notified": "✅ *Admin bilan bog'landingiz!*\n\nTez orada javob berishadi. 🙏\n\nYoki zakaz qilish uchun telefon raqamingizni yuboring 👇",
        "new_contact":    "📞 *Yangi murojaat!*\n\n👤 {name}\n🆔 `{uid}`\n@{username}\n\nJavob: /reply_{uid} xabar",
    },
    "ru": {
        "welcome":        "📸 Добро пожаловать в *Sadaf Media*!\n\nОтправьте номер телефона для продолжения 👇",
        "send_contact":   "📱 Отправить номер телефона",
        "contact_admin":  "📞 Связаться с администратором",
        "choose_package": "📦 *Выберите пакет:*\n\n1️⃣ *700 000 сум* — 1 день: 1 камера\n2️⃣ *1 400 000 сум* — 1-й и 2-й день: 1 камера\n3️⃣ *2 000 000 сум* — 1-й день: 1 | 2-й день: 2 камеры\n4️⃣ *VIP 300$* — 1-й день: 1 | 2-й день: 2 камеры + Кран\n\n👇 Выберите:",
        "chosen":         "✅ Выбрано: *{name}* — {price}\n\n📅 *Введите дату торжества:*\nПример: `25.04.2026`",
        "enter_date":     "📅 Введите дату торжества:\nПример: `25.04.2026`",
        "choose_event":   "🎉 *Выберите тип мероприятия:*",
        "events":         ["💍 Никох","👶 Чақалоқ","👦 Хатна","🎉 Банкет","🕋 Хаж/Умра","🔤 Алифбе","🎂 День рождения"],
        "send_location":  "📍 Отправьте *местоположение* торжества:",
        "loc_btn":        "📍 Отправить локацию",
        "enter_address":  "🏠 Напишите *адрес* торжества:\n(Пример: Юнусабад, 12-квартал, ресторан Ок олтин)",
        "order_done":     "✅ *Заказ принят!*\n\nМы свяжемся с вами в ближайшее время. Спасибо! 🙏",
        "admin_notified": "✅ *Сообщение отправлено администратору!*\n\nОжидайте ответа. 🙏\n\nИли отправьте номер телефона для оформления заказа 👇",
        "new_contact":    "📞 *Новое обращение!*\n\n👤 {name}\n🆔 `{uid}`\n@{username}\n\nОтвет: /reply_{uid} текст",
    },
    "en": {
        "welcome":        "📸 Welcome to *Sadaf Media*!\n\nPlease share your phone number to continue 👇",
        "send_contact":   "📱 Share phone number",
        "contact_admin":  "📞 Contact admin",
        "choose_package": "📦 *Choose a package:*\n\n1️⃣ *700,000 UZS* — Day 1: 1 camera\n2️⃣ *1,400,000 UZS* — Day 1 & 2: 1 camera\n3️⃣ *2,000,000 UZS* — Day 1: 1 | Day 2: 2 cameras\n4️⃣ *VIP $300* — Day 1: 1 | Day 2: 2 cameras + Crane\n\n👇 Select:",
        "chosen":         "✅ Selected: *{name}* — {price}\n\n📅 *Enter the event date:*\nExample: `25.04.2026`",
        "enter_date":     "📅 Enter the event date:\nExample: `25.04.2026`",
        "choose_event":   "🎉 *Select event type:*",
        "events":         ["💍 Wedding","👶 Baby","👦 Circumcision","🎉 Banquet","🕋 Hajj/Umrah","🔤 Alifbe","🎂 Birthday"],
        "send_location":  "📍 Send the *location* of the event:",
        "loc_btn":        "📍 Send location",
        "enter_address":  "🏠 Write the *address* of the event:\n(Example: Yunusobod district, Oq oltin restaurant)",
        "order_done":     "✅ *Order received!*\n\nWe will contact you shortly. Thank you! 🙏",
        "admin_notified": "✅ *Message sent to admin!*\n\nWe will reply soon. 🙏\n\nOr share your phone to place an order 👇",
        "new_contact":    "📞 *New inquiry!*\n\n👤 {name}\n🆔 `{uid}`\n@{username}\n\nReply: /reply_{uid} message",
    },
}

def tr(lang, key, **kwargs):
    text = T.get(lang, T["uz"]).get(key, T["uz"].get(key, key))
    return text.format(**kwargs) if kwargs else text

# ===================== HELPERS =====================
def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    if filename == PRICES_FILE:
        default = {
            "p1": {"name": "1️⃣ Paket — 700,000 so'm",    "price": "700,000 so'm",    "desc": "1-kun: 1 ta kamera"},
            "p2": {"name": "2️⃣ Paket — 1,400,000 so'm",  "price": "1,400,000 so'm",  "desc": "1-kun: 1 ta | 2-kun: 1 ta kamera"},
            "p3": {"name": "3️⃣ Paket — 2,000,000 so'm",  "price": "2,000,000 so'm",  "desc": "1-kun: 1 ta | 2-kun: 2 ta kamera"},
            "p4": {"name": "4️⃣ VIP Paket — 300$",         "price": "300$",             "desc": "1-kun: 1 ta | 2-kun: 2 ta kamera + Kran"},
        }
        save_json(PRICES_FILE, default)
        return default
    return []

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_user(user_id, name, lang="uz"):
    if user_id == ADMIN_ID:
        return
    users = load_json(USERS_FILE)
    existing = next((u for u in users if u["id"] == user_id), None)
    if existing:
        existing["lang"] = lang
    else:
        users.append({"id": user_id, "name": name, "lang": lang})
    save_json(USERS_FILE, users)

def get_lang(context):
    return context.user_data.get("lang", "uz")

# ===================== START — TIL TANLASH =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data.clear()

    if user.id == ADMIN_ID:
        kb = ReplyKeyboardMarkup(
            [["📋 Zakazlar", "✏️ Narxlarni tahrirlash"],
             ["💬 Chat", "📤 Broadcast"]],
            resize_keyboard=True
        )
        await update.message.reply_text("👨‍💼 Admin panel.", reply_markup=kb)
        return ADMIN_MAIN

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇺🇿 O'zbek",   callback_data="lang_uz"),
            InlineKeyboardButton("🇷🇺 Русский",  callback_data="lang_ru"),
            InlineKeyboardButton("🇬🇧 English",  callback_data="lang_en"),
        ]
    ])
    await update.message.reply_text(
        "🌐 Tilni tanlang / Выберите язык / Choose language:",
        reply_markup=kb
    )
    return LANG_SELECT

async def lang_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = q.data.replace("lang_", "")
    context.user_data["lang"] = lang

    user = update.effective_user
    add_user(user.id, user.full_name, lang)

    kb = ReplyKeyboardMarkup(
        [
            [KeyboardButton(tr(lang, "send_contact"), request_contact=True)],
            [KeyboardButton(tr(lang, "contact_admin"))],
        ],
        resize_keyboard=True
    )
    await q.edit_message_text(
        tr(lang, "welcome"),
        parse_mode="Markdown"
    )
    await q.message.reply_text("👇", reply_markup=kb)
    return CONTACT

# ===================== MIJOZ FLOW =====================
async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    user = update.effective_user
    uname = user.username or "username yoq"

    await context.bot.send_message(
        ADMIN_ID,
        tr("uz", "new_contact", name=user.full_name, uid=user.id, username=uname),
        parse_mode="Markdown"
    )
    await update.message.reply_text(tr(lang, "admin_notified"), parse_mode="Markdown")
    return CONTACT

async def contact_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    context.user_data["name"]  = update.message.contact.first_name
    context.user_data["phone"] = update.message.contact.phone_number

    prices = load_json(PRICES_FILE)
    buttons = []
    for k, v in prices.items():
        label = f"{v['name']}\n📹 {v.get('desc','')}"
        buttons.append([InlineKeyboardButton(label, callback_data=k)])

    await update.message.reply_text(
        tr(lang, "choose_package"),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return PACKAGE_SELECT

async def package_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = get_lang(context)
    prices = load_json(PRICES_FILE)
    pkg = prices[q.data]
    context.user_data["package"] = f"{pkg['name']} ({pkg.get('desc','')})"
    await q.edit_message_reply_markup(reply_markup=None)
    await q.message.reply_text(
        tr(lang, "chosen", name=pkg["name"], price=pkg["price"]),
        parse_mode="Markdown"
    )
    return DATE_INPUT

async def date_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    context.user_data["date"] = update.message.text
    events = tr(lang, "events")
    kb = ReplyKeyboardMarkup([[KeyboardButton(e)] for e in events], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(tr(lang, "choose_event"), parse_mode="Markdown", reply_markup=kb)
    return EVENT_TYPE

async def event_type_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    context.user_data["event"] = update.message.text
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton(tr(lang, "loc_btn"), request_location=True)]],
        resize_keyboard=True
    )
    await update.message.reply_text(tr(lang, "send_location"), parse_mode="Markdown", reply_markup=kb)
    return LOCATION

async def location_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    loc = update.message.location
    context.user_data["lat"] = loc.latitude
    context.user_data["lon"] = loc.longitude
    await update.message.reply_text(
        tr(lang, "enter_address"),
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return ADDRESS_INPUT

async def address_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    u = context.user_data
    order = {
        "user_id":  update.effective_user.id,
        "name":     u["name"],
        "phone":    u["phone"],
        "package":  u["package"],
        "date":     u["date"],
        "event":    u["event"],
        "address":  update.message.text,
        "lat":      u["lat"],
        "lon":      u["lon"],
        "lang":     lang,
    }
    orders = load_json(ORDERS_FILE)
    orders.append(order)
    save_json(ORDERS_FILE, orders)

    await context.bot.send_message(
        ADMIN_ID,
        f"🔔 *YANGI ZAKAZ!*\n\n"
        f"👤 {order['name']}\n"
        f"📱 `{order['phone']}`\n"
        f"🎉 {order['event']}\n"
        f"📦 {order['package']}\n"
        f"📅 {order['date']}\n"
        f"🏠 {order['address']}\n"
        f"🌐 Til: {lang.upper()}\n\n"
        f"📍 Lokatsiya quyida 👇",
        parse_mode="Markdown"
    )
    await context.bot.send_location(ADMIN_ID, latitude=order["lat"], longitude=order["lon"])
    await update.message.reply_text(tr(lang, "order_done"), parse_mode="Markdown")
    return ConversationHandler.END

# ===================== ADMIN PANEL =====================
async def handle_admin_zakaz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    orders = load_json(ORDERS_FILE)
    if not orders:
        await update.message.reply_text("📭 Hozircha zakazlar yo'q.")
        return ADMIN_MAIN
    buttons = []
    for i, o in enumerate(orders):
        label = f"#{i+1} | {o['event']} | {o['date']} | {o['name']}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"order_{i}")])
    await update.message.reply_text("📋 *Zakazlar:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))
    return ADMIN_MAIN

async def view_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    i = int(q.data.split("_")[1])
    orders = load_json(ORDERS_FILE)
    if i >= len(orders):
        await q.edit_message_text("❌ Zakaz topilmadi.")
        return ADMIN_MAIN
    o = orders[i]
    await context.bot.send_location(update.effective_chat.id, latitude=o["lat"], longitude=o["lon"])
    text = (
        f"📋 *Zakaz #{i+1}*\n\n"
        f"👤 {o['name']}\n"
        f"📱 `{o['phone']}`\n"
        f"🎉 {o['event']}\n"
        f"📦 {o['package']}\n"
        f"📅 {o['date']}\n"
        f"🏠 {o['address']}"
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🗑 O'chirish", callback_data=f"delete_{i}")]])
    await context.bot.send_message(update.effective_chat.id, text, parse_mode="Markdown", reply_markup=kb)
    return ADMIN_MAIN

async def delete_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    i = int(q.data.split("_")[1])
    orders = load_json(ORDERS_FILE)
    if i < len(orders):
        orders.pop(i)
        save_json(ORDERS_FILE, orders)
        await q.edit_message_text("✅ Zakaz o'chirildi.")
    return ADMIN_MAIN

async def handle_admin_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prices = load_json(PRICES_FILE)
    buttons = [[InlineKeyboardButton(f"{v['name']}", callback_data=f"price_{k}")] for k, v in prices.items()]
    await update.message.reply_text("✏️ *Qaysi paketni tahrirlaysiz?*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))
    return EDIT_PRICE_SELECT

async def edit_price_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    key = q.data.replace("price_", "")
    context.user_data["edit_key"] = key
    prices = load_json(PRICES_FILE)
    pkg = prices[key]
    await q.edit_message_text(
        f"✏️ *{pkg['name']}*\n\n"
        f"Joriy narx: {pkg['price']}\n"
        f"Joriy tavsif: {pkg.get('desc','')}\n\n"
        "Yangi ma'lumot yuboring:\n`narx | tavsif`\n\n"
        "Misol: `900,000 so'm | 1 kun, 1 ta kamera`",
        parse_mode="Markdown"
    )
    return EDIT_PRICE_VALUE

async def edit_price_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    key  = context.user_data.get("edit_key")
    prices = load_json(PRICES_FILE)
    if "|" in text:
        parts = text.split("|", 1)
        prices[key]["price"] = parts[0].strip()
        prices[key]["desc"]  = parts[1].strip()
    else:
        prices[key]["price"] = text
    save_json(PRICES_FILE, prices)
    await update.message.reply_text(
        f"✅ *{prices[key]['name']}* yangilandi!\n"
        f"💰 {prices[key]['price']}\n"
        f"📝 {prices[key].get('desc','')}",
        parse_mode="Markdown"
    )
    return ADMIN_MAIN

async def handle_admin_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_json(USERS_FILE)
    users = [u for u in users if u["id"] != ADMIN_ID]
    if not users:
        await update.message.reply_text("👥 Hozircha foydalanuvchilar yo'q.")
        return ADMIN_MAIN
    buttons = [[InlineKeyboardButton(u["name"], callback_data=f"chat_{u['id']}")] for u in users]
    await update.message.reply_text("💬 *Kimga xabar?*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))
    return ADMIN_CHAT_SELECT

async def admin_chat_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["chat_target"] = int(q.data.split("_")[1])
    await q.edit_message_text("✍️ Xabaringizni yozing:")
    return ADMIN_CHATTING

async def admin_send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_id = context.user_data.get("chat_target")
    if target_id:
        try:
            await context.bot.send_message(target_id, f"📩 *Admin xabari:*\n\n{update.message.text}", parse_mode="Markdown")
            await update.message.reply_text("✅ Xabar yuborildi!")
        except Exception as e:
            await update.message.reply_text(f"❌ Yuborib bo'lmadi: {e}")
    return ADMIN_MAIN

# ===================== BROADCAST =====================
async def handle_broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_json(USERS_FILE)
    users = [u for u in users if u["id"] != ADMIN_ID]
    count = len(users)
    await update.message.reply_text(
        f"📤 *Ommaviy xabar yuborish*\n\n"
        f"👥 Jami foydalanuvchilar: *{count} ta*\n\n"
        f"Xabaringizni yozing (matn, rasm yoki video yuborishingiz mumkin):\n\n"
        f"Bekor qilish: /cancel",
        parse_mode="Markdown"
    )
    return BROADCAST_INPUT

async def handle_broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_json(USERS_FILE)
    users = [u for u in users if u["id"] != ADMIN_ID]

    sent = 0
    failed = 0

    status_msg = await update.message.reply_text(f"⏳ Yuborilmoqda... 0/{len(users)}")

    for i, user in enumerate(users):
        try:
            if update.message.photo:
                await context.bot.send_photo(
                    user["id"],
                    update.message.photo[-1].file_id,
                    caption=update.message.caption or "",
                    parse_mode="Markdown"
                )
            elif update.message.video:
                await context.bot.send_video(
                    user["id"],
                    update.message.video.file_id,
                    caption=update.message.caption or "",
                    parse_mode="Markdown"
                )
            else:
                await context.bot.send_message(
                    user["id"],
                    update.message.text,
                    parse_mode="Markdown"
                )
            sent += 1
        except Exception:
            failed += 1

        if (i + 1) % 5 == 0 or (i + 1) == len(users):
            try:
                await status_msg.edit_text(f"⏳ Yuborilmoqda... {i+1}/{len(users)}")
            except Exception:
                pass

    await status_msg.edit_text(
        f"✅ *Broadcast tugadi!*\n\n"
        f"✔️ Yuborildi: {sent} ta\n"
        f"❌ Yuborilmadi: {failed} ta",
        parse_mode="Markdown"
    )
    return ADMIN_MAIN

async def cancel_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("❌ Bekor qilindi.")
        return ADMIN_MAIN
    return ConversationHandler.END

# ===================== MAIN =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_ID:
            return
        text = update.message.text
        try:
            parts = text.split(" ", 1)
            user_id = int(parts[0].replace("/reply_", ""))
            message = parts[1] if len(parts) > 1 else ""
            if not message:
                await update.message.reply_text("Misol: /reply_123456 Salom!")
                return
            await context.bot.send_message(user_id, f"📩 *Admin javobi:*\n\n{message}", parse_mode="Markdown")
            await update.message.reply_text("✅ Yuborildi!")
        except Exception as e:
            await update.message.reply_text(f"❌ Xato: {e}")

    app.add_handler(MessageHandler(filters.Regex(r"^/reply_\d+"), handle_reply))

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG_SELECT: [
                CallbackQueryHandler(lang_selected, pattern="^lang_"),
            ],
            CONTACT: [
                MessageHandler(filters.CONTACT, contact_received),
                MessageHandler(filters.Regex("Admin bilan|администратором|admin"), contact_admin),
            ],
            ADMIN_MAIN: [
                MessageHandler(filters.Regex("Zakazlar"),           handle_admin_zakaz),
                MessageHandler(filters.Regex("Narxlarni"),          handle_admin_price),
                MessageHandler(filters.Regex("^💬 Chat$"),           handle_admin_chat),
                MessageHandler(filters.Regex("Broadcast"),          handle_broadcast_start),
                CallbackQueryHandler(view_order,    pattern="^order_"),
                CallbackQueryHandler(delete_order,  pattern="^delete_"),
            ],
            PACKAGE_SELECT:    [CallbackQueryHandler(package_selected)],
            DATE_INPUT:        [MessageHandler(filters.TEXT & ~filters.COMMAND, date_received)],
            EVENT_TYPE:        [MessageHandler(filters.TEXT & ~filters.COMMAND, event_type_received)],
            LOCATION:          [MessageHandler(filters.LOCATION, location_received)],
            ADDRESS_INPUT:     [MessageHandler(filters.TEXT & ~filters.COMMAND, address_received)],
            EDIT_PRICE_SELECT: [CallbackQueryHandler(edit_price_select, pattern="^price_")],
            EDIT_PRICE_VALUE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_price_value)],
            ADMIN_CHAT_SELECT: [CallbackQueryHandler(admin_chat_select, pattern="^chat_")],
            ADMIN_CHATTING:    [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_send_message)],
            BROADCAST_INPUT:   [
                CommandHandler("cancel", cancel_broadcast),
                MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO, handle_broadcast_send),
            ],
        },
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()
