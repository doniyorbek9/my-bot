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
USERS_FILE = "users.json"

(
    CONTACT, PACKAGE_SELECT, DATE_INPUT, EVENT_TYPE,
    LOCATION, ADDRESS_INPUT, ADMIN_MAIN,
    EDIT_PRICE_SELECT, EDIT_PRICE_VALUE,
    ADMIN_CHAT_SELECT, ADMIN_CHATTING, CHAT_WITH_ADMIN
) = range(12)

# ===================== DEFAULT PRICES =====================
DEFAULT_PRICES = {
    "p1": {
        "name": "1️⃣ Paket — 700,000 so'm",
        "price": "700,000 so'm",
        "desc": "1-kun: 1 ta kamera"
    },
    "p2": {
        "name": "2️⃣ Paket — 1,400,000 so'm",
        "price": "1,400,000 so'm",
        "desc": "1-kun: 1 ta kamera | 2-kun: 1 ta kamera"
    },
    "p3": {
        "name": "3️⃣ Paket — 2,000,000 so'm",
        "price": "2,000,000 so'm",
        "desc": "1-kun: 1 ta kamera | 2-kun: 2 ta kamera"
    },
    "p4": {
        "name": "4️⃣ VIP Paket — 300$",
        "price": "300$",
        "desc": "1-kun: 1 ta kamera | 2-kun: 2 ta kamera + Kran kamera"
    }
}

# ===================== HELPERS =====================
def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    if filename == PRICES_FILE:
        save_json(PRICES_FILE, DEFAULT_PRICES)
        return DEFAULT_PRICES.copy()
    return []

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_user(user_id, name):
    if user_id == ADMIN_ID:
        return
    users = load_json(USERS_FILE)
    if not any(u['id'] == user_id for u in users):
        users.append({"id": user_id, "name": name})
        save_json(USERS_FILE, users)

# ===================== START =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.full_name)

    if user.id == ADMIN_ID:
        kb = ReplyKeyboardMarkup(
            [["📋 Zakazlar", "✏️ Narxlarni tahrirlash"], ["💬 Chat"]],
            resize_keyboard=True
        )
        await update.message.reply_text("👨‍💼 Admin panel.", reply_markup=kb)
        return ADMIN_MAIN

    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True
    )
    await update.message.reply_text(
        "📸 *Sadaf Media* botga xush kelibsiz!\n\nDavom etish uchun telefon raqamingizni yuboring 👇",
        parse_mode="Markdown",
        reply_markup=kb
    )
    return CONTACT

# ===================== MIJOZ FLOW =====================
async def contact_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.contact.first_name
    context.user_data["phone"] = update.message.contact.phone_number

    prices = load_json(PRICES_FILE)
    buttons = []
    for k, v in prices.items():
        label = f"{v['name']}\n📹 {v.get('desc', '')}"
        buttons.append([InlineKeyboardButton(label, callback_data=k)])

    await update.message.reply_text(
        "📦 *Paketni tanlang:*\n\n"
        "1️⃣ *700,000 so\'m* — 1-kun: 1 ta kamera\n"
        "2️⃣ *1,400,000 so\'m* — 1-kun va 2-kun: 1 ta kamera\n"
        "3️⃣ *2,000,000 so\'m* — 1-kun: 1 ta | 2-kun: 2 ta kamera\n"
        "4️⃣ *VIP 300$* — 1-kun: 1 ta | 2-kun: 2 ta kamera + Kran kamera\n\n"
        "👇 Tanlang:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return PACKAGE_SELECT

async def package_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    prices = load_json(PRICES_FILE)
    pkg = prices[q.data]
    context.user_data["package"] = f"{pkg['name']} — {pkg['price']} ({pkg.get('desc', '')})"
    await q.edit_message_reply_markup(reply_markup=None)
    await q.message.reply_text(
        f"✅ Tanlangan: *{pkg['name']}* — {pkg['price']}\n\n"
        "📅 *Toy sanasini kiriting:*\n"
        "Misol: `25.04.2026` yoki `4.4.2026`",
        parse_mode="Markdown"
    )
    return DATE_INPUT

async def date_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["date"] = update.message.text
    events = ["💍 Nikoh", "👶 Chaqaloq", "👦 Xatna", "🎉 Banket", "🕋 Xaj/Umra", "🔤 Alifbe", "🎂 Tug'ilgan kun"]
    kb = ReplyKeyboardMarkup([[KeyboardButton(e)] for e in events], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("🎉 *Tadbir turini tanlang:*", parse_mode="Markdown", reply_markup=kb)
    return EVENT_TYPE

async def event_type_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["event"] = update.message.text
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📍 Lokatsiya yuborish", request_location=True)]],
        resize_keyboard=True
    )
    await update.message.reply_text(
        "📍 Toy bo'ladigan *joylashuvni* yuboring:",
        parse_mode="Markdown",
        reply_markup=kb
    )
    return LOCATION

async def location_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    context.user_data["lat"] = loc.latitude
    context.user_data["lon"] = loc.longitude
    await update.message.reply_text(
        "🏠 Toy bo'ladigan *manzilni* yozing:\n(Misol: Yunusobod 12-mavze, Oq oltin restoran)",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return ADDRESS_INPUT

async def address_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = context.user_data
    order = {
        "user_id": update.effective_user.id,
        "name": u["name"], "phone": u["phone"],
        "package": u["package"], "date": u["date"],
        "event": u["event"], "address": update.message.text,
        "lat": u["lat"], "lon": u["lon"]
    }
    orders = load_json(ORDERS_FILE)
    orders.append(order)
    save_json(ORDERS_FILE, orders)

    admin_msg = (
        f"🔔 *YANGI ZAKAZ KELDI!*\n\n"
        f"👤 Ism: {order['name']}\n"
        f"📱 Tel: `{order['phone']}`\n"
        f"🎉 Tadbir: {order['event']}\n"
        f"📦 Paket: {order['package']}\n"
        f"📅 Sana: {order['date']}\n"
        f"🏠 Manzil: {order['address']}\n\n"
        f"📍 Lokatsiya quyida 👇"
    )
    await context.bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
    await context.bot.send_location(ADMIN_ID, latitude=order["lat"], longitude=order["lon"])

    await update.message.reply_text(
        "✅ *Zakazingiz qabul qilindi!*\n\nTez orada siz bilan bog'lanamiz. Rahmat! 🙏",
        parse_mode="Markdown"
    )
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
    await context.bot.send_location(update.effective_chat.id, latitude=o['lat'], longitude=o['lon'])
    text = (
        f"📋 *Zakaz #{i+1}*\n\n"
        f"👤 Ism: {o['name']}\n"
        f"📱 Tel: `{o['phone']}`\n"
        f"🎉 Tadbir: {o['event']}\n"
        f"📦 Paket: {o['package']}\n"
        f"📅 Sana: {o['date']}\n"
        f"🏠 Manzil: {o['address']}"
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
    buttons = [[InlineKeyboardButton(f"{v['name']} — {v['price']}", callback_data=f"price_{k}")] for k, v in prices.items()]
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
        f"✏️ *{pkg['name']}* tahrirlash\n\n"
        f"Joriy narx: {pkg['price']}\n"
        f"Joriy tavsif: {pkg.get('desc', '')}\n\n"
        "Yangi ma'lumotni yuboring:\n"
        "`narx | tavsif`\n\n"
        "Misol: `900,000 so'm | 1 kun, 1 ta kamera`",
        parse_mode="Markdown"
    )
    return EDIT_PRICE_VALUE

async def edit_price_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    key = context.user_data.get("edit_key")
    prices = load_json(PRICES_FILE)
    if "|" in text:
        parts = text.split("|", 1)
        prices[key]["price"] = parts[0].strip()
        prices[key]["desc"] = parts[1].strip()
    else:
        prices[key]["price"] = text
    save_json(PRICES_FILE, prices)
    await update.message.reply_text(
        f"✅ *{prices[key]['name']}* yangilandi!\n"
        f"💰 Narx: {prices[key]['price']}\n"
        f"📝 Tavsif: {prices[key].get('desc', '')}",
        parse_mode="Markdown"
    )
    return ADMIN_MAIN

async def handle_admin_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_json(USERS_FILE)
    users = [u for u in users if u['id'] != ADMIN_ID]
    if not users:
        await update.message.reply_text("👥 Hozircha foydalanuvchilar yo'q.")
        return ADMIN_MAIN
    buttons = [[InlineKeyboardButton(u['name'], callback_data=f"chat_{u['id']}")] for u in users]
    await update.message.reply_text("💬 *Kimga xabar yubormoqchisiz?*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(buttons))
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

# ===================== MAIN =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CONTACT: [MessageHandler(filters.CONTACT, contact_received)],
            ADMIN_MAIN: [
                MessageHandler(filters.Text(["📋 Zakazlar"]), handle_admin_zakaz),
                MessageHandler(filters.Text(["✏️ Narxlarni tahrirlash"]), handle_admin_price),
                MessageHandler(filters.Text(["💬 Chat"]), handle_admin_chat),
                CallbackQueryHandler(view_order, pattern="^order_"),
                CallbackQueryHandler(delete_order, pattern="^delete_"),
            ],
            PACKAGE_SELECT: [CallbackQueryHandler(package_selected)],
            DATE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_received)],
            EVENT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, event_type_received)],
            LOCATION: [MessageHandler(filters.LOCATION, location_received)],
            ADDRESS_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_received)],
            EDIT_PRICE_SELECT: [CallbackQueryHandler(edit_price_select, pattern="^price_")],
            EDIT_PRICE_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_price_value)],
            ADMIN_CHAT_SELECT: [CallbackQueryHandler(admin_chat_select, pattern="^chat_")],
            ADMIN_CHATTING: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_send_message)],
        },
        fallbacks=[CommandHandler("start", start)]
    )
    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()
