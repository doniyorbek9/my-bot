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

# State-lar
(
    CONTACT, PACKAGE_SELECT, DATE_INPUT, EVENT_TYPE, 
    LOCATION, ADDRESS_INPUT, ADMIN_MAIN, 
    EDIT_PRICE_SELECT, EDIT_PRICE_VALUE, 
    ADMIN_CHAT_SELECT, ADMIN_CHATTING, CHAT_WITH_ADMIN
) = range(12)

# ===================== FUNKSIYALAR =====================
def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return [] if filename != PRICES_FILE else {
        "p1": {"name": "💍 Paket 1", "price": "700,000 so'm"},
        "p2": {"name": "💎 Paket 2", "price": "1,400,000 so'm"},
        "p3": {"name": "👑 Paket 3", "price": "2,000,000 so'm"},
        "p4": {"name": "🎬 Paket 4 (VIP)", "price": "300$"}
    }

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_user(user_id, name):
    users = load_json(USERS_FILE)
    if not any(u['id'] == user_id for u in users):
        users.append({"id": user_id, "name": name})
        save_json(USERS_FILE, users)

# ===================== HANDLERS =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.full_name)

    if user.id == ADMIN_ID:
        kb = ReplyKeyboardMarkup([["📋 Zakazlar", "✏️ Narxlarni tahrirlash"], ["💬 Chat"]], resize_keyboard=True)
        await update.message.reply_text("👨‍💼 Admin panel.", reply_markup=kb)
        return ADMIN_MAIN

    kb = ReplyKeyboardMarkup([[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)], ["📞 Admin bilan bog'lanish"]], resize_keyboard=True)
    await update.message.reply_text("📸 Sadaf Media botga xush kelibsiz!", reply_markup=kb)
    return CONTACT

# --- MIJOZ FLOW ---
async def contact_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.contact.first_name
    context.user_data["phone"] = update.message.contact.phone_number
    prices = load_json(PRICES_FILE)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(v["name"], callback_data=k)] for k, v in prices.items()])
    await update.message.reply_text("📦 Paketni tanlang:", reply_markup=kb)
    return PACKAGE_SELECT

async def package_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["package"] = load_json(PRICES_FILE)[q.data]["name"]
    await q.edit_message_reply_markup(reply_markup=None)
    await q.message.reply_text("📅 Sanani kiriting (masalan: 25.04.2026):")
    return DATE_INPUT

async def date_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["date"] = update.message.text
    events = ["💍 Nikoh", "👶 Chaqaloq", "👦 Xatna", "🎉 Banket", "🕋 Umra"]
    kb = ReplyKeyboardMarkup([[KeyboardButton(e)] for e in events], resize_keyboard=True)
    await update.message.reply_text("🎉 Tadbirni tanlang:", reply_markup=kb)
    return EVENT_TYPE

async def event_type_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["event"] = update.message.text
    kb = ReplyKeyboardMarkup([[KeyboardButton("📍 Lokatsiya yuborish", request_location=True)]], resize_keyboard=True)
    await update.message.reply_text("📍 Lokatsiyani yuboring:", reply_markup=kb)
    return LOCATION

async def location_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    context.user_data["lat"] = loc.latitude
    context.user_data["lon"] = loc.longitude
    await update.message.reply_text("🏠 Manzilni yozing:", reply_markup=ReplyKeyboardRemove())
    return ADDRESS_INPUT

async def address_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = context.user_data
    order = {
        "name": u["name"], "phone": u["phone"], "package": u["package"], 
        "date": u["date"], "event": u["event"], "address": update.message.text,
        "lat": u["lat"], "lon": u["lon"] # Kordinatalarni saqlash
    }
    orders = load_json(ORDERS_FILE)
    orders.append(order)
    save_json(ORDERS_FILE, orders)
    await context.bot.send_message(ADMIN_ID, f"🔔 YANGI ZAKAZ!\n👤 {order['name']}\n📱 {order['phone']}\n📦 {order['package']}")
    await update.message.reply_text("✅ Zakaz qabul qilindi!")
    return ConversationHandler.END

# --- ADMIN LOGIKA ---
async def handle_admin_zakaz(update, context):
    orders = load_json(ORDERS_FILE)
    if not orders: await update.message.reply_text("Zakazlar yo'q."); return ADMIN_MAIN
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"{o['package']} | {o['date']}", callback_data=f"order_{i}")] for i, o in enumerate(orders)])
    await update.message.reply_text("📋 Zakazlar:", reply_markup=kb)
    return ADMIN_MAIN

async def view_order(update, context):
    q = update.callback_query
    await q.answer()
    i = int(q.data.split("_")[1])
    orders = load_json(ORDERS_FILE)
    o = orders[i]
    
    # 1. Karta (Lokatsiya)
    await context.bot.send_location(
        chat_id=update.effective_chat.id,
        latitude=o['lat'],
        longitude=o['lon']
    )
    
    # 2. Matn va tugmalar
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🗑 O'chirish", callback_data=f"delete_{i}")]])
    text = f"👤 {o['name']}\n📱 {o['phone']}\n📦 {o['package']}\n📅 {o['date']}\n🏠 {o['address']}"
    await context.bot.send_message(update.effective_chat.id, text, reply_markup=kb)
    
    return ADMIN_MAIN

async def delete_order(update, context):
    q = update.callback_query
    i = int(q.data.split("_")[1])
    orders = load_json(ORDERS_FILE)
    if i < len(orders):
        orders.pop(i)
        save_json(ORDERS_FILE, orders)
        await q.edit_message_text(f"✅ Zakaz o'chirildi.")
    return ADMIN_MAIN

# --- CHAT & PRICE HANDLERS ---
async def handle_admin_price(update, context):
    prices = load_json(PRICES_FILE)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(v['name'], callback_data=f"price_{k}")] for k, v in prices.items()])
    await update.message.reply_text("✏️ Tahrirlash:", reply_markup=kb)
    return EDIT_PRICE_SELECT

async def edit_price_select(update, context):
    q = update.callback_query
    await q.answer()
    context.user_data["edit_key"] = q.data.split("_")[1]
    await q.edit_message_text("💰 Yangi narxni yozing:")
    return EDIT_PRICE_VALUE

async def edit_price_value(update, context):
    key = context.user_data["edit_key"]
    prices = load_json(PRICES_FILE)
    prices[key]["price"] = update.message.text
    save_json(PRICES_FILE, prices)
    await update.message.reply_text("✅ Narx yangilandi!")
    return ADMIN_MAIN

async def handle_admin_chat(update, context):
    users = load_json(USERS_FILE)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(u['name'], callback_data=f"chat_{u['id']}")] for u in users])
    await update.message.reply_text("💬 Kimga yozamiz?", reply_markup=kb)
    return ADMIN_CHAT_SELECT

# ===================== MAIN =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CONTACT: [
                MessageHandler(filters.CONTACT, contact_received),
                MessageHandler(filters.Text(["📞 Admin bilan bog'lanish"]), lambda u, c: ... )
            ],
            ADMIN_MAIN: [
                MessageHandler(filters.Text(["📋 Zakazlar"]), handle_admin_zakaz),
                MessageHandler(filters.Text(["✏️ Narxlarni tahrirlash"]), handle_admin_price),
                MessageHandler(filters.Text(["💬 Chat"]), handle_admin_chat),
                CallbackQueryHandler(view_order, pattern="^order_"),
                CallbackQueryHandler(delete_order, pattern="^delete_")
            ],
            PACKAGE_SELECT: [CallbackQueryHandler(package_selected)],
            DATE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_received)],
            EVENT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, event_type_received)],
            LOCATION: [MessageHandler(filters.LOCATION, location_received)],
            ADDRESS_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_received)],
            EDIT_PRICE_SELECT: [CallbackQueryHandler(edit_price_select, pattern="^price_")],
            EDIT_PRICE_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_price_value)]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()
