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
ADMIN_ID = 7948989650
BOT_TOKEN = os.getenv("TOKEN") 

PRICES_FILE = "prices.json"
ORDERS_FILE = "orders.json"

(
    CONTACT, PACKAGE_SELECT, DATE_INPUT, EVENT_TYPE, 
    LOCATION, ADDRESS_INPUT, ADMIN_MAIN, 
    EDIT_PRICE_SELECT, EDIT_PRICE_VALUE, CHAT_WITH_ADMIN
) = range(10)

# ===================== FILE FUNCTIONS =====================
def load_prices():
    if os.path.exists(PRICES_FILE):
        with open(PRICES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "p1": {"name": "💍 Paket 1", "price": "700,000 so'm", "desc": "1 kun • 1 ta kamera"},
        "p2": {"name": "💎 Paket 2", "price": "1,400,000 so'm", "desc": "2 kun • 1 ta kamera"},
        "p3": {"name": "👑 Paket 3", "price": "2,000,000 so'm", "desc": "1-kun 1 ta kamera • 2-kun 2 ta kamera"},
        "p4": {"name": "🎬 Paket 4 (VIP)", "price": "300$", "desc": "1-kun 1 ta • 2-kun 2 ta + Kran kamera"}
    }

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
    if update.effective_user.id == ADMIN_ID:
        kb = ReplyKeyboardMarkup([["📋 Zakazlar", "✏️ Narxlarni tahrirlash"]], resize_keyboard=True)
        await update.message.reply_text("👨‍💼 Admin panelga xush kelibsiz!", reply_markup=kb)
        return ADMIN_MAIN

    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)], ["📞 Admin bilan bog'lanish"]],
        resize_keyboard=True
    )
    await update.message.reply_text("📸 Sadaf Media bot\n\nDavom etish uchun raqamingizni yuboring yoki admin bilan bog'laning:", reply_markup=kb)
    return CONTACT

# --- ADMIN CHAT LOGIC ---
async def start_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Admin uchun xabaringizni yozing (Chiqish uchun /cancel):", reply_markup=ReplyKeyboardRemove())
    return CHAT_WITH_ADMIN

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = f"👤 Mijoz: {user.full_name}\n🆔 ID: {user.id}\n\n✍️ Xabar: {update.message.text}"
    await context.bot.send_message(ADMIN_ID, text)
    await update.message.reply_text("✅ Xabar adminlarga yuborildi.")
    return ConversationHandler.END

async def admin_reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        try:
            replied_text = update.message.reply_to_message.text
            user_id = int(replied_text.split("🆔 ID: ")[1].split("\n")[0])
            await context.bot.send_message(user_id, f"👨‍💼 Admin javobi:\n{update.message.text}")
            await update.message.reply_text("✅ Javob yuborildi.")
        except Exception as e:
            await update.message.reply_text(f"❌ Xatolik: {e}")

# --- ORDER LOGIC ---
async def contact_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "📞 Admin bilan bog'lanish":
        return await start_chat(update, context)
        
    context.user_data["name"] = update.message.contact.first_name
    context.user_data["phone"] = update.message.contact.phone_number
    prices = load_prices()
    kb = InlineKeyboardMarkup([[InlineKeyboardButton(v["name"], callback_data=k)] for k, v in prices.items()])
    await update.message.reply_text("📦 Paketni tanlang:", reply_markup=kb)
    return PACKAGE_SELECT

async def package_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["package"] = load_prices()[q.data]["name"]
    await q.edit_message_reply_markup(reply_markup=None)
    await q.message.reply_text("📅 Sanani kiriting (05.04.2026):")
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
    await update.message.reply_text("🏠 Manzil yozing:", reply_markup=ReplyKeyboardRemove())
    return ADDRESS_INPUT

async def address_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = context.user_data
    order = {"name": u["name"], "phone": u["phone"], "package": u["package"], "date": u["date"], "event": u["event"], "address": update.message.text, "lat": u["lat"], "lon": u["lon"]}
    orders = load_orders()
    orders.append(order)
    save_orders(orders)
    await context.bot.send_message(ADMIN_ID, f"🔔 YANGI ZAKAZ!\n👤 {order['name']}\n📱 {order['phone']}\n📦 {order['package']}")
    await update.message.reply_text("✅ Zakaz qabul qilindi!")
    return ConversationHandler.END

# --- ADMIN HANDLERS ---
async def admin_main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📋 Zakazlar":
        orders = load_orders()
        if not orders:
            await update.message.reply_text("Zakazlar yo'q.")
            return ADMIN_MAIN
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"{o['package']} | {o['date']}", callback_data=f"order_{i}")] for i, o in enumerate(orders)])
        await update.message.reply_text("📋 Zakazlar ro'yxati:", reply_markup=kb)
    elif text == "✏️ Narxlarni tahrirlash":
        prices = load_prices()
        kb = InlineKeyboardMarkup([[InlineKeyboardButton(f"{v['name']}", callback_data=f"price_{k}")] for k, v in prices.items()])
        await update.message.reply_text("✏️ Tanlang:", reply_markup=kb)
        return EDIT_PRICE_SELECT
    return ADMIN_MAIN

async def view_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    i = int(q.data.split("_")[1])
    orders = load_orders()
    if i >= len(orders): return
    o = orders[i]
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🗑 O'chirish", callback_data=f"delete_{i}")]])
    text = f"👤 {o['name']}\n📱 {o['phone']}\n📦 {o['package']}\n📅 {o['date']}\n🎉 {o['event']}\n🏠 {o['address']}"
    await q.message.reply_text(text, reply_markup=kb)
    await q.message.reply_venue(o["lat"], o["lon"], title=o['name'], address=o['address'])
    return ADMIN_MAIN

async def delete_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    i = int(q.data.split("_")[1])
    orders = load_orders()
    if i < len(orders):
        removed = orders.pop(i)
        save_orders(orders)
        await q.edit_message_text(f"✅ {removed['name']} ning zakazi o'chirildi.")
    return ADMIN_MAIN

async def edit_price_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["edit_key"] = q.data.split("_")[1]
    await q.edit_message_text("💰 Yangi narxni yozing:")
    return EDIT_PRICE_VALUE

async def edit_price_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.user_data["edit_key"]
    prices = load_prices()
    prices[key]["price"] = update.message.text
    save_prices(prices)
    await update.message.reply_text("✅ Narx yangilandi!")
    return ADMIN_MAIN

# ===================== MAIN =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CONTACT: [
                MessageHandler(filters.CONTACT, contact_received),
                MessageHandler(filters.TEXT("📞 Admin bilan bog'lanish"), start_chat)
            ],
            CHAT_WITH_ADMIN: [
                CommandHandler("cancel", start),
                MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin)
            ],
            PACKAGE_SELECT: [CallbackQueryHandler(package_selected)],
            DATE_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_received)],
            EVENT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, event_type_received)],
            LOCATION: [MessageHandler(filters.LOCATION, location_received)],
            ADDRESS_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, address_received)],
            ADMIN_MAIN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_main_handler),
                CallbackQueryHandler(view_order, pattern="^order_"),
                CallbackQueryHandler(delete_order, pattern="^delete_"),
                MessageHandler(filters.REPLY & filters.TEXT, admin_reply_to_user)
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
