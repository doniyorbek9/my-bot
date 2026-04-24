#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

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
# ADMIN_ID ni o'z ID raqamingizga o'zgartiring
ADMIN_ID = 7948989650
BOT_TOKEN = os.getenv("TOKEN") # Railway'da Variables qismiga TOKEN qo'shishni unutmang!

PRICES_FILE = "prices.json"
ORDERS_FILE = "orders.json"

(
    CONTACT,
    PACKAGE_SELECT,
    DATE_INPUT,
    EVENT_TYPE,
    LOCATION,
    ADDRESS_INPUT,
    ADMIN_MAIN,
    EDIT_PRICE_SELECT,
    EDIT_PRICE_VALUE
) = range(9)

# ===================== DEFAULT PRICES =====================
DEFAULT_PRICES = {
    "p1": {"name": "💍 Paket 1", "price": "700,000 so'm", "desc": "1 kun • 1 ta kamera"},
    "p2": {"name": "💎 Paket 2", "price": "1,400,000 so'm", "desc": "2 kun • 1 ta kamera"},
    "p3": {"name": "👑 Paket 3", "price": "2,000,000 so'm", "desc": "1-kun 1 ta kamera • 2-kun 2 ta kamera"},
    "p4": {"name": "🎬 Paket 4 (VIP)", "price": "300$", "desc": "1-kun 1 ta • 2-kun 2 ta + Kran kamera"}
}

# ===================== FILE FUNCTIONS =====================
def load_prices():
    if os.path.exists(PRICES_FILE):
        with open(PRICES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_PRICES

def save_prices(data):
    with open(PRICES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_orders(data):
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ===================== HANDLERS =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Admin tekshiruvi
    if update.effective_user.id == ADMIN_ID:
        kb = ReplyKeyboardMarkup(
            [["📋 Zakazlar", "✏️ Narxlarni tahrirlash"]],
            resize_keyboard=True
        )
        await update.message.reply_text("👨‍💼 Admin panelga xush kelibsiz!", reply_markup=kb)
        return ADMIN_MAIN

    kb = ReplyKeyboardMarkup(
        [["📱 Telefon raqamni yuborish"]], # request_contact=True bo'lishi kerak
        one_time_keyboard=True,
        resize_keyboard=True
    )
    # KeyboardButton to'g'irlangan
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True
    )

    await update.message.reply_text(
        "📸 Sadaf Media bot\n\nDavom etish uchun raqamingizni yuboring 👇",
        reply_markup=kb
    )
    return CONTACT

async def contact_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.contact.first_name
    context.user_data["phone"] = update.message.contact.phone_number

    await update.message.reply_text(
        "📦 Paketlar yuklanmoqda...",
        reply_markup=ReplyKeyboardRemove()
    )

    prices = load_prices()
    text = "📦 Paketlar:\n\n"
    for v in prices.values():
        text += f"{v['name']}\n💰 {v['price']}\n📄 {v['desc']}\n\n"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(v["name"], callback_data=k)]
        for k, v in prices.items()
    ])

    await update.message.reply_text(text, reply_markup=kb)
    return PACKAGE_SELECT

async def package_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    pkg = load_prices()[q.data]
    context.user_data["package"] = pkg["name"]
    await q.edit_message_reply_markup(reply_markup=None)
    await q.message.reply_text("📅 Sanani kiriting (kun.oy.yil masalan: 05.04.2026):")
    return DATE_INPUT

async def date_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        datetime.strptime(update.message.text, "%d.%m.%Y")
        context.user_data["date"] = update.message.text
        events = ["💍 Nikoh", "👶 Chaqaloq", "👦 Xatna", "🎉 Banket", "🕋 Umra"]
        kb = ReplyKeyboardMarkup([[KeyboardButton(e)] for e in events], resize_keyboard=True)
        await update.message.reply_text("🎉 Tadbirni tanlang:", reply_markup=kb)
        return EVENT_TYPE
    except ValueError:
        await update.message.reply_text("❌ Sana xato kiritildi. Qayta urinib ko'ring (masalan: 05.04.2026):")
        return DATE_INPUT

async def event_type_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["event"] = update.message.text
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📍 Lokatsiya yuborish", request_location=True)]],
        resize_keyboard=True
    )
    await update.message.reply_text("📍 Lokatsiyani yuboring:", reply_markup=kb)
    return LOCATION

async def location_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    context.user_data["lat"] = loc.latitude
    context.user_data["lon"] = loc.longitude
    await update.message.reply_text("🏠 Manzil yozing:", reply_markup=ReplyKeyboardRemove())
    return ADDRESS_INPUT

async def address_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = context.user_data
    order = {
        "name": u["name"], "phone": u["phone"], "package": u["package"],
        "date": u["date"], "event": u["event"], "address": update.message.text,
        "lat": u["lat"], "lon": u["lon"]
    }
    orders = load_orders()
    orders.append(order)
    save_orders(orders)

    await context.bot.send_message(
        ADMIN_ID,
        f"🔔 YANGI ZAKAZ!\n\n👤 {order['name']}\n📱 {order['phone']}\n📦 {order['package']}\n📅 {order['date']}\n🎉 {order['event']}\n🏠 {order['address']}"
    )
    await update.message.reply_text("✅ Zakaz qabul qilindi!")
    return ConversationHandler.END

# Admin handlerlar
async def admin_main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📋 Zakazlar":
        orders = load_orders()
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"{o['package']} | {o['date']}", callback_data=f"order_{i}")] for i, o in enumerate(orders)])
        await update.message.reply_text("📋 Zakazlar:", reply_markup=kb)
    elif text == "✏️ Narxlarni tahrirlash":
        prices = load_prices()
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"{v['name']} — {v['price']}", callback_data=f"price_{k}")] for k, v in prices.items()])
        await update.message.reply_text("✏️ Qaysi paketni o‘zgartirasiz?", reply_markup=kb)
        return EDIT_PRICE_SELECT
    return ADMIN_MAIN

async def edit_price_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["edit_key"] = q.data.split("_")[1]
    await q.edit_message_reply_markup(reply_markup=None)
    await q.message.reply_text("💰 Yangi narxni kiriting:")
    return EDIT_PRICE_VALUE

async def edit_price_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data["edit_key"]
    prices = load_prices()
    prices[key]["price"] = update.message.text
    save_prices(prices)
    await update.message.reply_text("✅ Narx yangilandi!")
    return ADMIN_MAIN

async def view_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    i = int(q.data.split("_")[1])
    o = load_orders()[i]
    await q.message.reply_text(f"👤 {o['name']}\n📱 {o['phone']}\n📦 {o['package']}\n📅 {o['date']}\n🎉 {o['event']}\n🏠 {o['address']}")
    await q.message.reply_venue(o["lat"], o["lon"], title=f"{o['name']} - Zakaz", address=o["address"])
    return ADMIN_MAIN

# ===================== MAIN =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CONTACT: [MessageHandler(filters.CONTACT, contact_received)],
            PACKAGE_SELECT: [CallbackQueryHandler(package_selected)],
            DATE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_received)],
            EVENT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, event_type_received)],
            LOCATION: [MessageHandler(filters.LOCATION, location_received)],
            ADDRESS_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_received)],
            ADMIN_MAIN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_main_handler),
                CallbackQueryHandler(view_order, pattern="^order_")
            ],
            EDIT_PRICE_SELECT: [CallbackQueryHandler(edit_price_select, pattern="^price_")],
            EDIT_PRICE_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_price_value)]
        },
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(conv)
    print("🚀 Bot ishlayapti...")
    app.run_polling()

if __name__ == "__main__":
    main()
